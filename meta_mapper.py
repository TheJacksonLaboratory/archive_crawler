"""
    Given a metadata file in an old format, and an archived.json file,
    populate a document in a new format.
"""

import configparser
from datetime import datetime
import dateutil.parser as date_parser
import json
import os
from pathlib import Path
import re

from metadata_mongo_ingester import MetadataMongoIngester
#import MetadataMongoIngester
from system_groups_finder import SystemGroupsFinder

class MetaMapper:

    """
    Given a metadata file in an old format, and an archived.json file,
    populate a document in a new format.
    """

    def __init__(self):

        """

        Load new document example and get field mapping from config file.

        """

        # Get the source directory where this script resides. Look for a config file in it.
        root_dir = os.path.dirname(os.path.realpath(__file__))
        config_filename = str(Path(root_dir, "meta_mapper_config.cfg"))
        assert os.path.isfile(config_filename)

        self.config = configparser.ConfigParser()
        self.config.read(config_filename)

        # Get all the keys in the new format, discarding the values in the template's example file.
        new_format_template = self.config["format"]["template"]
        with open (new_format_template) as f:
            self.template = dict.fromkeys(json.load(f).keys(), None)
        self.user_metadata_key = self.config["format"]["user_metadata_key"]        
        self.defaults_tag = self.config["format"]["defaults_tag"]

        # The categories section of the config maps file path patterns to the various 
        # kinds of metadata. Patterns to be excluded are found in a comma-delimited list in the config.
        self.categories = self.config["categories"]
        self.exclude_patterns = self.categories["exclude_patterns"].split(',')

        # The dates section tells uys how to recognize date fields and how to format them.
        self.date_key_pattern = self.config["dates"]["date_key_pattern"]
        self.date_format = self.config["dates"]["date_format"]
 
        # Get an instance of the SystemGroupsFinder
        self.system_groups_finder = SystemGroupsFinder.SystemGroupsFinder()
        self.system_groups_key = self.config["format"]["system_groups_key"]

        # Save the name of the user_id and manager_user_id key
        self.manager_user_id_key = self.config["format"]["manager_user_id_key"]
        self.user_id_key = self.config["format"]["user_id_key"]
        self.sgf_manager_userid = self.config["format"]["sgf_manager_user_id_key"]

        # Save the name of the date key
        self.date_key = self.config["format"]["date_key"]        

        # Save the name of the archive root
        self.archive_path_key = self.config["format"]["archive_path_key"]
        self.archive_root = self.config["format"]["archive_root"]


        # Get an instance of the MetadataMongoIngester and open a MongoDB collection
        self.metadata_ingester = MetadataMongoIngester.MetadataMongoIngester()
        self.metadata_ingester.open_connection()


    def create_new_document(self, archive_dir):

        """

        Build a new metadata document from jsons in an archive directory.

        The document will contain keys in the template, with values populated by searching 
        the jsons in the given directory.

        Parameters: archive_dir (str): Absolute path to a directory in the archive.

        Returns: new metadata document as a dict.

        """

        # Copy the template into the new doc that will be returned after it's populated. 
        new_doc = self.template.copy()

        # Find which kind of metadata to expect from the directory path.
        category_tag = self.__get_category_tag(archive_dir)
        if not category_tag:
            return # This kind of metadata is not yet handled.

        # Seek and read any metadata docs in the directory named in the config file.
        for doc_tag, doc_filename in self.config["doc_names"].items():
            
            # Load json doc with keys converted to snake_case.
            curr_doc = self.__get_curr_doc(archive_dir, doc_filename)
            if not curr_doc:
                # doc not found in this directory
                continue

            # Get the section of the config file to seek by combining the category and doc tags.
            section_tag = category_tag + '_' + doc_tag
            if section_tag not in self.config:
                # This kind of metadata doc is not yet handled for this category
                continue

            # Add vals from curr doc to new doc
            try:
                self.__add_vals_from_curr_doc(new_doc, section_tag, curr_doc)
            except ValueError as e:
                print(f"Key error for {archive_dir}:new_doc {str(e)}")
             
            # Tuck curr doc into user_data field, if specified in the config file.
            self.__add_user_metadata(new_doc, section_tag, curr_doc)

            # Add the system groups
            new_doc[self.system_groups_key] = self.system_groups_finder.get_groups_from_entire_doc(curr_doc)

        # Add archive_path if needed
        self.__add_archive_path(new_doc, archive_dir)

        # Add date if needed
        self.__add_date(new_doc, archive_dir)

        # Add any known constants
        self.__add_default_vals(new_doc)

        # Ingest the document into mongo collection
        self.metadata_ingester.ingest_document(new_doc)

        return new_doc



    """
    
    PRIVATE METHODS

    """

    def __add_archive_path(self, new_doc, archive_dir):

        """

        Add a given archive directory to the doc if it doesn't already have an archive_path
        
        Parameters:
            new_doc (dict): The new dictionary being populated.
            archive_dir (str): A directory in the archive

        Returns: None
        
        """

        # If the doc already has an archive_path, do nothing
        if new_doc[self.archive_path_key]:
            return

        # If the directory doesn't start with the archive root or isn't a valid directory, do nothing.
        if not archive_dir.startswith(self.archive_root) or not os.path.isdir(archive_dir):
            return

        new_doc[self.archive_path_key] = archive_dir


    def __add_date(self, new_doc, archive_dir):

        """

        If the doc doesn't have a date, the last modified date of the given archive dir.

        Parameters:
            new_doc (dict): The new dictionary being populated.
            archive_dir (str): A directory in the archive

        Returns: None

        """

        # If the doc already has a date, do nothing
        if new_doc[self.date_key]:
            return        

        # If the directory doesn't start with the archive root or isn't a valid directory, do nothing.
        if not archive_dir.startswith(self.archive_root) or not os.path.isdir(archive_dir):
            return

        # Get the directory's lat modified, convert to datetime as a string
        mod_date = str(datetime.fromtimestamp(os.path.getmtime(archive_dir)))

        # Convert the date to the desired format and assign it to the new_doc's date key
        new_doc[self.date_key] = self.__get_converted_date(mod_date)
        

    def __add_default_vals(self, new_doc):

        """

        Parse defaults from config, add to new doc.

        Parses the default values in the "default_vals" section of the config file. Values in that section are
        actually pairs delimited by a colon, in the form type:val. E.g., "int:0" means the value would
        be zero as an integer, while "str:None" means the value is the string "None", not just None.
        Will not add the value if the doc aalready has one.

        Parameters:
            new_doc (dict): The new dictionary being populated.

        Returns: None

        """

        for curr_key, packed_val in self.config[self.defaults_tag].items():

            # Don't add the vaule if the doc already has a value for this key.
            if curr_key in new_doc and new_doc[curr_key]:
                continue

            val_type,val = packed_val.split(':')

            if val_type == "int":
                new_doc[curr_key] = int(val)

            if val_type == "float":
                new_doc[curr_key] = float(val)

            if val_type == "str":
                new_doc[curr_key] = str(val)

            if val_type == None:
                new_doc[curr_key] = None

            if val_type == "dict":
                new_doc[curr_key] = dict()

            if val_type == bool:
                if val.lower() == "true":
                    new_doc[curr_key] = True
                else:
                    new_doc[curr_key] = False
        

    def __add_user_metadata(self, new_doc, section_tag, curr_doc):

        """
        
        Tuck an old metadata doc into the user_metadata field of the new doc.

        Parameters:
            new_doc (dict). The new document being created.
            old_doc (dict). The old document being scanned.

        Returns: None

        """

        # If the user_data field is set to True in the config section for the old metadata
        # file, tuck its contents into the user_data field of the new doc.
        try:
            if self.config[section_tag][self.user_metadata_key].lower() == "true":
                new_doc[self.user_metadata_key] = curr_doc
        except KeyError as e:
            # user_metadata key not found in the section of the config for this doc. Do nothing.
            pass


    def __add_vals_from_curr_doc(self, new_doc, section_tag, curr_doc):

        """
        Add values to the new doc from fields in the current doc specified in the config file.

        Parameters:
            new_doc: (dict):     The new document being created.
            category_tag: (str): The category of metadata this document matches.
            doc_tag: (str):      The section tag in the config file for this document.
            curr_doc: (dict):    The current document loaded from a json file.

        Returns: new_doc as dict, with vals added, if any.

        """

        # Check this doc's section in the config file to determine which of its keys we want.
        for template_key, doc_key in self.config[section_tag].items():

            # Hack: we don't want to process the user_metadata key here.
            if template_key == self.user_metadata_key:
                continue

            # Get the value of the doc_key in the current document.
            curr_doc_val = self.__get_curr_doc_val(curr_doc, doc_key)

            # If the new doc already has a value for this key, but the curr doc has a different
            # value, and both are not None, raise a ValueError (To be caught and logged, not to
            # crash the program.) 
            if ((template_key in new_doc and new_doc[template_key] != None) and
                curr_doc_val != None and 
                new_doc[template_key] != curr_doc_val):
                raise ValueError(f"Error: conflicting values for {template_key}")
 
 
            # If the new doc doesn't already have a value for this key, use the value from the
            # current doc.

            if template_key in new_doc and new_doc[template_key] == None:

                # Any dates must converted into a uniform format
                if re.match(self.date_key_pattern, template_key):
                    curr_doc_val = self.__get_converted_date(curr_doc_val)

                # Manager user_id must be looked up in the SystemGroupsFinder
                if template_key == self.manager_user_id_key or template_key == self.user_id_key:
                    target_key = self.sgf_manager_userid

                    new_doc[template_key] = self.system_groups_finder.get_other_info_from_group(
                        target_key, curr_doc_val, target_key)

                else:
                    new_doc[template_key] = curr_doc_val


    def __get_category_tag(self, archive_dir):

        """

        Match the directory path to category of metadata.

        Match the directory path against each pattern in the categories map to
        determine which kind of metadata we should expect.

        Parameters: archive_dir (str):         

        Returns: category_tag as a string, or None if no match.

        """

        found_category = None
        for pattern, category_tag in self.categories.items():
            # Config parser loads keys as lowercase by default. Easiest fix is a 
            # case-insensitive match.
            if re.match(pattern, archive_dir, re.IGNORECASE):
                found_category = category_tag
                break

        # Ignore any directory that matches any of the exclude patterns
        for exclude_pattern in self.exclude_patterns:
            if re.search(exclude_pattern, archive_dir):
                return None
    
        return found_category
      

    def __get_converted_date(self, init_date):

        """

        Convert date strings into a uniform format.

        Parameters:
            init_date (str): The date string we're starting with.

        Returns:
            new_date (str): The date string in the desired format.

        """

        new_dt = date_parser.parse(init_date).replace(hour=12, minute=0, second=0, microsecond=0)
        new_dt_str = new_dt.strftime(self.date_format)
        return new_dt_str


    def __get_curr_doc(self, archive_dir, doc_filename):

        """"
        
        Seek the given file and load it as json with snake_case keys.

        Parameters:
            archive_dir (str): Absolute path of the directory being searched.
            doc_filename (str): Name of metadata json file to look for in the directory.

        Returns: dict of file contents with keys in snake_case, or None if not found.

        """

        # Look for doc
        doc_filepath = os.path.join(archive_dir, doc_filename)
        if not os.path.isfile(doc_filepath):
            # Directory does not have a metadata doc with this name.
            return None

        # Load as json
        with open(doc_filepath) as f:
            curr_doc = json.load(f)

        # Convert keys to snake_case using list comprehension
        curr_doc = { self.__to_snake_case(k): v for k, v in curr_doc.items() }

        # Clear any saved sub-dictionaries from previous documents
        self.sub_dicts = {}

        return curr_doc
        

    def __get_curr_doc_val(self, curr_doc, doc_key):

        """

        Get the value for a key in a given document.

        Parameters:
            curr_doc (dict): The current document.
            doc_key (str): The document key from the config file.

        Returns: Value of the key in the doc as a str, or None if key not in doc.

        """

        # If the key we want is nested in a sub-dictionary within the document, this will
        # be denoted by a '>' symbol in the doc_key. 

        if '>' not in doc_key:
            # No nesting involved, just get the value.
            try:
                return curr_doc[doc_key]
            except KeyError:
                # doc_key not in current document
                return None            

        # From here we're dealing with a nested dict. For now, we'll only handle one
        # level of nesting. Split on the '>' and trim any whitespace.
        top_key, sub_key = [val.strip() for val in doc_key.split('>')]
        
        # If the curr doc doesn't actually have the top_key, or it does but the value isn't
        # a dictionary, stop.
        if top_key not in curr_doc or type(curr_doc[top_key]) != dict:
            return None

   
        # We'll need to load the sub-dict with alll its keys in snake_case. Also, we may need
        # this sub_dict on subsequent calls, so we want to save the results.
        if top_key not in self.sub_dicts:
            self.sub_dicts[top_key] = { self.__to_snake_case(k): v for k, v in curr_doc[top_key].items() }        

        val = self.sub_dicts[top_key][sub_key]
        return val


    def __to_snake_case(self, val):

        """

        Convert a string to snake_case.

        Parameters: val (str): string to be converted.

        Returns: input string in snake_case.

        """

        # Insert an underscore after every lower case letter that is immediately followed
        # by an uppercase letter. 
        new_val = val[0].lower()
        for i in range(1, len(val)):
            if val[i].isupper() and val[i-1].islower():
                new_val += '_'
            new_val += val[i].lower()
        
        return new_val

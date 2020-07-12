"""
    Given a metadata file in an old format, and an archived.json file,
    populate a document in a new format.
"""

import configparser
import dateutil.parser as date_parser
import json
import os
from pathlib import Path
import re


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
        # kinds of metadata.
        self.categories = self.config["categories"]

        # The dates section tells uys how to recognize date fields and how to format them.
        self.date_key_pattern = self.config["dates"]["date_key_pattern"]
        self.date_format = self.config["dates"]["date_format"]
 
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

            # Add vals from curr doc to new doc
            try:
                self.__add_vals_from_curr_doc(new_doc, section_tag, curr_doc)
            except ValueError as e:
                print(f"Key error for {archive_dir}: {str(e)}")
             
            # Tuck curr doc into user_data field, if specified in the config file.
            self.__add_user_metadata(new_doc, section_tag, curr_doc)

        # Add any known constants
        self.__add_default_vals(new_doc)

        return new_doc



    """
    
    PRIVATE METHODS

    """


    def __add_default_vals(self, new_doc):

        """

        Parse defaults from config, add to new doc.

        Parses the default values in the "default_vals" section of the config file. Values in that section are
        actually pairs delimited by a colon, in the form type:val. E.g., "int:0" means the value would
        be zero as an integer, while "str:None" means the value is the string "None", not just None.
        Will not add the value if the doc aalready has one.

        Parameters: new_doc (dict). The new dictionary being populated.

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

            # If the new doc already has a value for this key, but the curr doc has a different
            # value, and both are not None, raise a ValueError (To be caught and logged, not to
            # crash the program. 
            if ((template_key in new_doc and new_doc[template_key] != None) and
                (doc_key in curr_doc and curr_doc[doc_key] != None) and 
                new_doc[template_key] != curr_doc[doc_key]):
                raise ValueError(f"Error: conflicting values for {template_key}")
 
 
            # If the new doc doesn't already have a value for this key,use the value from the
            # current doc.

            if template_key in new_doc and new_doc[template_key] == None:
                new_val = curr_doc[doc_key]

                # Any dates must converted into a uniform format
                if re.match(self.date_key_pattern, template_key):
                    new_val = self.__get_converted_date(new_val)

                new_doc[template_key] = new_val


    def __get_category_tag(self, archive_dir):

        """

        Match the directory path to category of metadata.

        Match the directory path against each pattern in the categories map to
        determine which kind of metadata we should expect.

        Parameters: archive_dir (str):         

        Returns: category_tag as a string, or None if no match.

        """

        for pattern, category_tag in self.categories.items():
            # Config parser loads keys as lowercase by default. Easiest fix is a 
            # case-insensitive match.
            if re.match(pattern, archive_dir, re.IGNORECASE):
                return category_tag

        return None
      

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

        # TBD: Remove this Horrible, depressing, and embarrassing hack!!
        if doc_filename.startswith('gt'):
            curr_doc = curr_doc["project"]

        # Convert keys to snake_case using list comprehension
        curr_doc = { self.__to_snake_case(k): v for k, v in curr_doc.items() }

        return curr_doc
        

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

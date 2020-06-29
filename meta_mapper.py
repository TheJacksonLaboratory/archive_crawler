"""
    Given a metadata file in an old format, and an archived.json file,
    populate a document in a new format.
"""

import configparser
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
        self.user_data_key = self.config["format"]["user_data_key"]        
        self.defaults_tag = self.config["format"]["defaults_tag"]

        # The categories section of the config maps file path patterns to the various 
        # kinds of metadata.
        self.categories = self.config["categories"]

 
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

        # Seek and read any metadata docs in the directory named in the config file.
        for doc_tag, doc_filename in self.config["doc_names"].items():
            
            # Load json doc with keys converted to snake_case.
            curr_doc = self.__get_curr_doc(archive_dir, doc_filename)
            if not curr_doc:
                # doc not found in this directory
                continue

            # Add vals from curr doc to new doc
            self.__add_vals_from_curr_doc(new_doc, category_tag, doc_tag, curr_doc)
             
            # Tuck curr doc into user_data field, if specified in the config file.
            self.__add_user_data(new_doc, curr_doc)

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
        

    def __add_user_data(self, new_doc, curr_doc):

        """
        
        Tuck an old into the user_data field of the new doc.

        Parameters:
            new_doc (dict). The new document being created.
            old_doc (dict). The old document being scanned.

        Returns: None

        """

        # If the user_data field is set to True in the config section for the old metadata
        # file, tuck its contents into the user_data field of the new doc.
        if self.user_data_key in curr_doc and curr_doc[self.user_data_key].lower() == "true":
            new_doc[self.user_data_key] = curr_doc


    def __add_vals_from_curr_doc(self, new_doc, category_tag, doc_tag, curr_doc):

        """
        Add values to the new doc from fields in the current doc specified in the config file.

        Parameters:
            new_doc: (dict):     The new document being created.
            category_tag: (str): The category of metadata this document matches.
            doc_tag: (str):      The section tag in the config file for this document.
            curr_doc: (dict):    The current document loaded from a json file.

        Returns: new_doc as dict, with vals added, if any.

        """

        # Get the section of the config file to seek by combining the category and doc tags.
        section_tag = category_tag + '_' + doc_tag

        # Check this doc's section in the config file to determine which of its keys we want.
        for template_key, doc_key in self.config[section_tag].items():

            # If the new doc doesn't already have a value for this key,use the value from the
            # current doc.

            if template_key in new_doc and new_doc[template_key] == None:
                new_doc[template_key] = curr_doc[doc_key]


    def __get_category_tag(self, archive_dir):

        """

        Match the directory path to category of metadata.

        Match the directory path against each pattern in the categories map to
        determine which kind of metadata we should expect.

        Parameters: archive_dir (str):         

        Returns: category_tag as a string.

        """

        for pattern, category_tag in self.categories.items():
            # Config parser loads keys as lowercase by default. Easiest fix is a 
            # case-insensitive match.
            if re.match(pattern, archive_dir, re.IGNORECASE):
                return category_tag
      

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

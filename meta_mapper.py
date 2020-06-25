"""
    Given a metadata file in an old format, and an archived.json file,
    populate a document in a new format.
"""

import configparser
import json
import os
from pathlib import Path

class MetaMapper(self)

    """
    Given a metadata file in an old format, and an archived.json file,
    populate a document in a new format.
    """

    def __init__(self):

        """
        Load new document example and get field mapping from config file.
        """

        # Get the source directory where this script resides. Look for a config file with it.
        root_dir = os.path.dirname(os.path.realpath(__file__))
        config_filename = str(Path(root_dir, "meta_mapper_config.cfg"))
        assert os.path.isfile(config_filename)

        self.config = configparser.ConfigParser()
        self.config.read(config_filename)

        # Get all the keys in the new format
        new_format_document = self.config["doc_names"]["new_format"]
        with open (new_format_document) as f:
            self.new_keys = json.load(f).keys()

        

    def get_new_document(self, archive_dir):

        """

        Build a new metadata document from jsons in an archive directory.

        Parameters: archive_dir (str): Absolute path to a directory in the archive.

        Returns: dict 
      

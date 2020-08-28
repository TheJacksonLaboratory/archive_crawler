import configparser
from datetime import datetime
import dateutil.parser as date_parser
import json
import os
from pathlib import Path
import re
import subprocess

from meta_mapper import MetaMapper
from metadata_mongo_ingester import MetadataMongoIngester

class KompOmeroSplitter:

    def __init__(self, mapper, ingester):

        """

        Split a KOMP omero document into separate docs, map to
        our new template, and ingest them.

        Parameters:
            mapper (MetaMapper): An instance of the MetaMapper
            ingester (MetadataMongoIngester): An instance of the ingester with an
                open connection


        Returns:
            None

        """

        # Get the source directory where this script resides. Find and read the named 
        # config file.
        root_dir = os.path.dirname(os.path.realpath(__file__))
        config_filename = str(Path(root_dir, "omero_config.cfg"))
        assert os.path.isfile(config_filename)
        self.config = configparser.ConfigParser()
        self.config.read(config_filename)

        # Save the omero root path, as well as the pattern we'll use to split it later.
        self.omero_path = self.config["omero"]["omero_path"]
        self.omero_pattern = self.config["omero"]["omero_pattern"]

        # Save handles to the mapper and ingester.
        self.ingester = ingester
        self.mapper = mapper


    def is_komp_omero_dir(self, archive_dir):

        """
    
        Test whether a given archive dir is Komp Omero data

        Parameters:
            archive_dir (str): A directory in the archive

        Returns:
            bool: True if this dir is KOMP omero, false o/w.

        """

        # Return True if the archive_dir starts with the omero root path.
        if archive_dir.startswith(self.omero_path):
            return True

        return False

    
    def split_doc(self, archive_dir):

        """

        Split the doc and ingest it as separate docs

        Parameters:
            archive_dir (str): A directory in the archive

        """

        # First find and load the master json file.
        md_filename = os.path.join(archive_dir, 
            self.config["omero"]["omero_filename"])
        assert os.path.isfile(md_filename)
        with open(md_filename) as f:
            main_doc = json.load(f)

        # Get the mtime of the archive_dir in the desired format.
        mtime_str = self.__get_date_str(archive_dir)

        # The archived_size will be the size of the archived directory divided by the 
        # number of keys we found in the main doc. This is not exactly right, as there could be 
        # some variation in size of the sub-docs, but we have no way to know that or what the 
        # variance would be, so this will have to suffice.
        archived_size= int(int(subprocess.check_output(
            ["du", "-sb", archive_dir]).split()[0].decode("utf-8")) / len(main_doc))

        # Split the doc by its keys
        for omero_key, sub_doc in main_doc.items():
            if not re.match(self.omero_pattern, omero_key):
                print(f"No pattern match for key {omero_key}")
                continue        

            # The val for each key is a dictionary, which is what we want to ingest
            # as a sub-doc. Add they key to the directory where the file was found, and 
            # use it as our archivedPath. Turn the ': " in the key to an underscore.
            new_path = os.path.join(archive_dir.replace('/archive', '/bharchive'),
                omero_key.replace(": ", "_"))
            
            # Get a fresh copy of the template from the mapper.
            new_doc = self.mapper.get_blank_template()

            new_doc["archival_status"] = "completed"
            new_doc["archived_path"] = new_path
            new_doc["archived_size"] = archived_size
            new_doc["classification"] = ""
            new_doc["date_archived"] = mtime_str
            new_doc["grant_id"] = ""
            new_doc["manager_user_id"] = ""
            new_doc["notes"] = ""
            new_doc["project_name"] = ""
            new_doc["source_path"] = ""
            new_doc["source_size"] = None
            # The omero data is considered communal. As such, "jaxuser" is the correct group.
            new_doc["system_groups"] = ["jaxuser"]
            new_doc["user_metadata"] = sub_doc
            new_doc["user_id"] = ""

            self.ingester.ingest_document(new_doc)
    

    def __get_date_str(self, archive_dir):

        """

        Get the mtime of the archive dir and convert it to the desired format.
        Parameters:
            init_date (str): The date string we're starting with.
        Returns:
            new_date (str): The date string in the desired format.

        """

        # Get the directory's lat modified, convert to datetime as a string
        mod_date = str(datetime.fromtimestamp(os.path.getmtime(archive_dir)))

        new_dt = date_parser.parse(mod_date).replace(hour=12, minute=0, second=0, microsecond=0)
        new_dt_str = new_dt.strftime("%Y-%m-%d")
        return new_dt_str



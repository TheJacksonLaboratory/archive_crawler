import argparse
import datetime
import json
import os
from pathlib import Path
import logging
import socket
import sys

from meta_mapper import MetaMapper
from metadata_mongo_ingester import MetadataMongoIngester
from KompOmeroSplitter import KompOmeroSplitter

class ArchiveCrawler:

    def __init__(self, mode, root_dir):

        """

        Construct the ArchiveCrawler.

        Parameters:
            mode (str) : Either "dev" or "prod" for development or production. Default is "dev".

        Returns:
            None

        """

        # Check that mode is "dev" or "prod" and the given root dir is valid 
        assert mode in ["dev", "prod"]
        assert os.path.isdir(root_dir)
        self.root_dir = root_dir

        # Get an instance of the MetadataMongoIngester and open a MongoDB collection
        self.ingester = MetadataMongoIngester.MetadataMongoIngester()
        self.ingester.open_connection(mode=mode)

        # Get an instance of the meta_mapper
        self.meta_mapper = MetaMapper.MetaMapper()

        # Get an instance of the KompOmeroSplitter
        self.omero_splitter = KompOmeroSplitter(self.meta_mapper, self.ingester)

        # Initialize the logger
        self.setup_logger()


    def crawl_archive(self):

        """

        Crawl all directories beneath the root, map any jsons found to a template, and ingest them.

        Parameters:
            None

        Returns:
            None

        """

        for dir in self.get_json_dirs(self.root_dir):

            logging.info(f"Scanning dir {dir}")

            if self.skip_directory(dir):
                logging.info(f"Skipping directory {dir}")
                continue

            # Handle the omero data separately
            if self.omero_splitter.is_komp_omero_dir(dir):
                logging.info("Splitting Omero doc")
                self.omero_splitter.split_doc(dir)
                continue

            # Get a document in our new template format populated with values from any
            # metadata found in this directory. If no document is made, skip this directory.
            new_doc = self.meta_mapper.create_new_document(dir)
            if not new_doc:
                logging.error(f"Could not create new document from directory {dir}")
                continue

            # Adjust the archive path if we're on a BH server
            if socket.gethostname().startswith('bh'):
                new_doc["archived_path"] = new_doc["archived_path"].replace('/archive', '/bharchive')

            ###
            # Ingest the document into mongo the collection
            err_msg = self.ingester.ingest_document(new_doc)
            if err_msg:
                # The ingester only returns a message if there was an error.
                logging.error(f"Could not ingest document to mongo for directory {dir}, error was {err_msg}")
                logging.debug(f"{json.dumps(json.loads(new_doc, indent = 4))}")
            else:
                logging.info(f"Successfully ingested document for directory {dir}")
            ###


    def get_json_dirs(self, root_dir):

        """

        Get a set of all directories beneath the root containing json files.

        Parameters:
            root_dir (str): The root directory, such as "/archive".

        Returns:
            json_dirs (set): The set of directories with jsons files.

        """

        json_dirs = set()
        logging.debug("Seeking archive directories with JSON files...")
        json_filenames = Path(root_dir).rglob("*.json")
        for filename in json_filenames:
            dir = os.path.dirname(filename)
            logging.debug(f"Found directory {dir}")
            json_dirs.add(dir)
        return json_dirs


    def setup_logger(self):

        """
        Setup logger.

        Parameters: None

        Returns: None

        """

        # TBD: This could be configurable instead of hard-coded.
        home_dir = str(Path.home())
        log_dir = os.path.join(home_dir, "archive_crawler_logs")

        # If the directory doesn't exist, make it
        if not os.path.isdir(log_dir):
            try:
                Path(log_dir).mkdir(parents = True, exist_ok = True)
            except Exception as e:
                sys.exit(f"Attempt to make logging directory {log_dir} failed, received exception {str(e)}")


        # Create the log file, with a timestamp in its name, and get its full path
        log_file = "archive_crawler_log_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
        log_path = os.path.join(log_dir, log_file)
        print(f"Log file located at {log_path}")

        # TBD: The desired log level should also be configurable
        log_level = "DEBUG"

        # Now configure the logger with the established parameters.
        logging.basicConfig(filename=log_path, filemode='w', level=log_level,
            format='%(asctime)s %(levelname)s: %(message)s')


    def skip_directory(self, dir):

        """
        Determine whether to skip a given directory

        Parameters:
            dir (str): A directory in the archive

        Returns:
            val (bool): True if the dir should be skipped, false if not.

        """

        # TBD: We could read a list of regular expressions from a config file instead of these
        # hard-coded values
        
        # Skip any test directories or expired accounts
        if dir.startswith("/archive/test") or dir.startswith("/archive/expired-accounts"):
            return True

        # Skip any sub-dirs named "test" or "testing", and any dirs beneath those
        if "/test/" in dir or "/testing/" in dir:
            return True

        # Skip all .old dirs
        if dir.endswith(".old") or ".old/" in dir:
            return True

        # The pbcoretools dirs having nothing of interest to us.
        if "pbcoretools.tasks" in dir:
            return True

        return False



if __name__ == "__main__":

    #  Allow command line arguments for mode and root directory
    parser = argparse.ArgumentParser(
        description="Crawl archive directories, map metadata into a standardized format, and ingest into MongoDB",
        prog="ArchiveCrawler.py", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-m", "--mode", help="dev or prod for development or production DB", type=str,
        default="dev")
    parser.add_argument("-d", "--root-dir", help="root directory to begin crawl", type=str, default="/archive")
    args = parser.parse_args()

    crawler = ArchiveCrawler(args.mode, args.root_dir)
    crawler.crawl_archive()
        
    

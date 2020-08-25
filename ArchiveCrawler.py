import argparse
import json
import os
from pathlib import Path
import socket

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

       

    def crawl_archive(self):

        """

        Crawl all directories beneath the root, map any jsons found to a template, and ingest them.

        Parameters:
            None

        Returns:
            None

        """

        for dir in self.get_json_dirs(self.root_dir):

            # Handle the omero data separately
            if self.omero_splitter.is_komp_omero_dir(dir):
                self.omero_splitter.split_doc(dir)
                continue

            # Get a document in our new template format populated with values from any
            # metadata found in this directory. If no document is made, skip this directory.
            new_doc = self.meta_mapper.create_new_document(dir)
            if not new_doc:
                continue

            # Adjust the archive path if we're on a BH server
            if socket.gethostname().startswith('bh'):
                new_doc["archived_path"] = new_doc["archived_path"].replace('/archive', '/bharchive')

            # Ingest the document into mongo the collection
            self.ingester.ingest_document(new_doc)


    def get_json_dirs(self, root_dir):

        """

        Get a set of all directories beneath the root containing json files.

        Parameters:
            root_dir (str): The root directory, such as "/archive".

        Returns:
            json_dirs (set): The set of directories with jsons files.

        """

        json_dirs = set()
        json_filenames = Path(root_dir).rglob("*.json")
        for filename in json_filenames:
            dir = os.path.dirname(filename)
            json_dirs.add(dir)
        return json_dirs



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
        
    

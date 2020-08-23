import argparse
import json
import os
from pathlib import Path

from meta_mapper import MetaMapper
from metadata_mongo_ingester import MetadataMongoIngester
from KompOmeroSplitter import KompOmeroSplitter

#dirs = [ "/archive/GT/legacy/150611_D00138_0249_AHMMHKADXX_Project_15NGS-001-jxb/CHU1351",
#         "/archive/GT/2020/JacquesBanchereau_Lab_CT/20200106_19-banchereau-049"]

mapper = MetaMapper()


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

        # Get an instance of the MetadataMongoIngester and open a MongoDB collection
        self.ingester = MetadataMongoIngester.MetadataMongoIngester()
        self.ingester.open_connection(mode=mode)

        # Get an instance of the meta_mapper
        self.meta_mapper = MetaMapper.MetaMapper()

        # Get an instance of the KompOmeroSplitter
        self.omero_splitter = KompOmeroSplitter(mapper, ingester)


    def crawl_archive(self):


        for dir in self.get_json_dirs(root_dir):

            # Get a document in our new template format populated with values from any
            # metadata found in this directory. If no document is made, skip this directory.
            new_doc = self.meta_mapper.create_new_document(dir)
            if not new_doc:
                continue

            # Handle the omero data separately
            if self.omero_splitter.is_komp_omero_dir(dir):
                self.omero_splitter.split_doc(dir)
                continue
               
            # Ingest the document into mongo the collection
            self.metadata_ingester.ingest_document(new_doc)


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
        description="Crawl archive directories, map metadata into a new format, and ingest it into MongoDB",
        prog="ArchiveCrawler.py"
    )
    parser.add_argument("-m", "--mode", help="dev or prod for development or production DB", type=str,
        default="dev")
    parser.add_argument("-d", "--root-dir", help="root directory to begin crawl", type=str, default="/archive")
    args = parser.parse_args()

    crawler = ArcihveCrawler(args.mode, args.root_dir)
        
    

# archive_crawler
Crawl the archive, create standardized metadata from existing documents, and ingest it into MongoDB.

## Description
Given a root archive directory, the crawler will seek all sub-directories containing potential metadata (json files). It will use the [meta_mapper](https://github.com/TheJacksonLaboratory/meta_mapper) to map the contents of these files into a standardized format, as well as the [system_groups_finder](https://github.com/TheJacksonLaboratory/system_groups_finder) to establish ownership, i.e., the PI or lab group to whom the data belongs. It will then use the [metadata_mongo_ingester](https://github.com/TheJacksonLaboratory/metadata_mongo_ingester) to ingest the newly formatted and populated document into a MongoDB collection.

## Setup / Run Environment

To use the archive crawler, three other JAX github repositories **MUST** be installed in a virtual environment that uses python 3.6+. These are the [system_groups_finder](https://github.com/TheJacksonLaboratory/system_groups_finder), the [meta_mapper](https://github.com/TheJacksonLaboratory/meta_mapper), and the [metadata_mongo_ingester](https://github.com/TheJacksonLaboratory/metadata_mongo_ingester). On most of our servers, you can do this with the following commands:
```
$ python3 -m venv myenv
$ source myenv/bin/activate
(myenv) $ python -m pip install git+https://<github_username>:<access_token>@github.com/TheJacksonLaboratory/system_groups_finder
(myenv) $ python -m pip install git+https://<github_username>:<access_token>@github.com/TheJacksonLaboratory/meta_mapper
(myenv) $ python -m pip install git+https://<github_username>:<access_token>@github.com/TheJacksonLaboratory/metadata_mongo_ingester
```


## Usage
```
(myenv) $ python ArchiveCrawler.py --help
usage: ArchiveCrawler.py [-h] [-m MODE] [-d ROOT_DIR]

Crawl archive directories, map metadata into a standardized format, and ingest
into MongoDB

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  "dev" or "prod" for development or production DB (default:
                        dev)
  -d ROOT_DIR, --root-dir ROOT_DIR
                        root directory to begin crawl (default: /archive)
```



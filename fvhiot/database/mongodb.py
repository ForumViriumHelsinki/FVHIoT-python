import logging
import os
from typing import Tuple

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


def get_mongoclient_by_envs() -> MongoClient:
    """
    Use env MONGODB_DATABASE_URI to create and return a MongoClient instance
    """
    database_uri = os.getenv("MONGODB_DATABASE_URI", "mongodb://localhost:27017/")
    logging.info(f"Connecting to MongoDB: {database_uri}")
    client: MongoClient = MongoClient(database_uri, tz_aware=True)
    return client


def get_database(client: MongoClient, db_name: str) -> Database:
    """
    Use MongoClient and db_name to return a db handle.
    Raises pymongo.errors.InvalidName if an invalid database name is used.
    """
    db: Database = client.__getattr__(db_name)
    return db


def get_timeseries_collection(
        db: Database, collection_name: str, granularity: str = "minutes"
) -> Tuple[Collection, bool]:
    """
    Use MongoDB Database instance db and collection_name to get and return a collection.
    If it doesn't exist, it will be created with timeseries parameters {"timeField": "time", "metaField": "meta"}.
    """
    if collection_name in db.list_collection_names():
        coll = db[collection_name]
        created = False
    else:
        logging.info(f"Collection {collection_name} didn't exist, creating a new one.")
        coll = db.create_collection(
            collection_name, timeseries={"timeField": "time", "metaField": "meta", "granularity": granularity}
        )
        # coll = db.command(
        #     "create", collection_name, timeseries={"timeField": "time", "metaField": "meta", "granularity": granularity}
        # )
        created = True
    return coll, created

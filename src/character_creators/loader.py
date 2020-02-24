import logging
from math import ceil
import sys
import time

from peewee import *
from tqdm import tqdm

from character_creators.settings import PRIVATE_KEY as pr, PUBLIC_KEY as pb, API_BASE as base
from character_creators.models import (Character, CharacterSeries, Creator, CreatorSeries,
        CharacterCreators, database as db)
from character_creators.marvel import MarvelApi

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class Loader:
    """
    Database loader: Loads data onto Database.

    :param api: The API client to collect data from
    """

    def __init__(self, api):
        self.api = api
        self._create_tables()

    def _create_tables(self):
        """
        Create all required tables, if they don't exist.
        """
        with db:
            db.create_tables([Character, CharacterSeries, Creator,
                             CreatorSeries, CharacterCreators], safe=True)

    def load_characters(self):
        """
        Load data into the characters table.
        """
        total = self.api.get_total("characters")
        data = self.api.get_characters()
        logger.info("Load characters...")
        db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        with db.atomic(), tqdm(total=total, \
                              desc="Loading",
                              ncols=100) as pbar:
            for character in data:
                (Character
                 .insert_many(character[0])
                 .execute())
                for series in character[1]:
                    (CharacterSeries
                     .insert_many(series)
                     .on_conflict_replace()
                     .execute())
                pbar.update()
        db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        logger.info("Load characters completed")

    def load_creators(self):
        """
        Load data into the creators table.
        """
        total = self.api.get_total("creators")
        data = self.api.get_creators()
        logger.info("Load creators...")
        db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        with db.atomic(), tqdm(total=total, \
                              desc="Loading",
                              ncols=100) as pbar:
            for creator in data:
                (Creator
                 .insert_many(creator[0])
                 .execute())
                for series in creator[1]:
                    (CreatorSeries
                     .insert_many(series)
                     .on_conflict_replace()
                     .execute())
                pbar.update()
        db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        logger.info("Load creators completed")

    def load_character_creators(self):
        """
        Load data into the character_creators table.
        """
        data = self.get_normalize_relation()
        total = data.count()
        logger.info("Load character_creators...")
        db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        chunk_size = 10000
        total_batches = ceil(total / chunk_size)
        with db.atomic(), tqdm(total=total, desc="Loading", \
                    postfix=f"batch 0/{total_batches}", ncols=100) as pbar:
            for idx, batch in enumerate(chunked(data, chunk_size)):
                CharacterCreators.insert_many(batch).execute()
                pbar.set_postfix_str(f"batch {idx + 1}/{total_batches}")
                pbar.update(chunk_size)

        db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        logger.info("Load character_creators completed")

    def get_normalize_relation(self):
        """
        Get the normalize the relation between Characters and Creators via
        their respective series tables.

        :return: Returns query indict format
        :rtype: dict
        """
        query = (CharacterSeries
                 .select(
                     CharacterSeries.character,
                     CreatorSeries.creator
                  )
                 .join(CreatorSeries, on=(CharacterSeries.series_id == CreatorSeries.series_id))
                 .group_by(CharacterSeries.character, CreatorSeries.creator)
                 .order_by(CharacterSeries.character, CreatorSeries.creator))

        return query.dicts()


if __name__ == "__main__":
    print("Waiting for db (ctrl + c to exit) ", end="")
    while True:
        try:
            if db.connect():
                print(" success")
                db.close()
            break;
        except DatabaseError:
            print(".", end="", flush=True)
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit()

    marvel = MarvelApi(base, pb, pr)
    loader = Loader(marvel)
    if (not Character.table_exists()) or (not len(Character)):
        loader.load_characters()
    else:
        logger.info("characters table exist and loaded")

    if (not Creator.table_exists()) or (not len(Creator)):
        loader.load_creators()
    else:
        logger.info("creators table exist and loaded")

    if (not CharacterCreators.table_exists()) or (not len(CharacterCreators)):
        loader.load_character_creators()
    else:
        logger.info("character_creators table exist and loaded")

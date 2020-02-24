from datetime import datetime
import json

from peewee import *
from stringcase import camelcase
from character_creators.models import Character, CharacterSeries, Creator, CreatorSeries, CharacterCreators


def info_wrapper(method):
    """
    Info Wrapper: Wraps the API resource with some helpful data.
    """
    info_array = {}
    now = datetime.now()
    def _info_wrapper(*args):
        query = method(*args)
        total = query.count()
        info_array["code"] = 200
        info_array["attributionText"] = f"Data provided by Marvel. © {now.year} MARVEL"
        info_array["totalCreators"] = total
        data = {}
        if total:
            query = query.dicts()

            if "character_id" in query[0]:
                data["characterId"] = query[0]["character_id"]
                data["characterName"] = query[0]["character_name"]

            data["creators"] = []

            for qry in query.dicts():
                corrected_keys = {}
                for k, v in qry.items():
                    if "character" not in k:
                        k = "resourceURI" if k == "resource_uri" else camelcase(k)
                        v = json.loads(v) if k == "thumbnail" else v
                        corrected_keys[k] = v
                data["creators"].append(corrected_keys)
        info_array["data"] = data
        return info_array
    return _info_wrapper

class Resource:
    """
    Get API resource
    """

    @info_wrapper
    def get_creators_by_character_id(self, id):
        """
        Get creators by character id

        :param int id: Character id to search for
        """
        query = (Character
                 .select(Character.id.alias("character_id"), Character.name.alias("character_name"), Creator)
                 .join(CharacterCreators)
                 .join(Creator)
                 .where(Character.id == id)
                 .order_by(Character.id, Creator.id, Creator.full_name))

        return query

    @info_wrapper
    def get_creators(self):
        """
        Get all creators.
        """
        query = (Creator
                 .select()
                 .order_by(Creator.id, Creator.full_name))

        return query

    @info_wrapper
    def get_creators_by_character_name(self, name):
        """
        Get creators by character name.

        :param str name: Character name to search for
        """
        query = (Character
                 .select(Character.id.alias("character_id"), Character.name.alias("character_name"), Creator)
                 .join(CharacterCreators)
                 .join(Creator)
                 .where(Character.name == name)
                 .order_by(Character.id, Creator.id, Creator.full_name))

        return query

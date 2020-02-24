from peewee import *

from character_creators.settings import DB_PASS, DB_USER, DB_HOST

database = MySQLDatabase("character_creators", host=DB_HOST, user=DB_USER, password=DB_PASS)

class BaseModel(Model):
    class Meta:
        database = database

class Character(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()

    class Meta:
        table_name = "characters"


class CharacterSeries(BaseModel):
    series_id = IntegerField()
    character = ForeignKeyField(column_name="character_id",
                                field="id",
                                model=Character,
                                null=True,
                                backref="character_serieses")
    class Meta:
        table_name = "character_series"
        indexes = (
            (("series_id", "character"), True),
        )
        primary_key = False

class Creator(BaseModel):
    id = IntegerField(primary_key=True)
    suffix = CharField(null=True)
    first_name = CharField(null=True)
    middle_name = CharField(null=True)
    last_name = CharField(null=True)
    full_name = CharField(null=True)
    thumbnail = TextField(null=True)
    resource_uri = CharField(null=True)

    class Meta:
        table_name = "creators"

class CreatorSeries(BaseModel):
    series_id = IntegerField()
    creator = ForeignKeyField(column_name="creator_id",
                              field="id",
                              model=Creator,
                              null=True,
                              backref="creator_serieses")

    class Meta:
        table_name = "creator_series"
        indexes = (
            (("series_id", "creator"), True),
        )
        primary_key = False


class CharacterCreators(BaseModel):
    character = ForeignKeyField(column_name="character_id",
                                field="id",
                                model=Character,
                                backref="character_series")
    creator = ForeignKeyField(column_name="creator_id",
                                field="id",
                                model=Creator,
                                backref="creator_series")

    class Meta:
        table_name = "character_creators"
        indexes = (
            (("character", "creator"), True),
        )
        primary_key = False

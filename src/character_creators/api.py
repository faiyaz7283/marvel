from flask import Flask, escape
from flask_caching import Cache
from flask_limiter import Limiter
from flask_restful import reqparse, abort, Api
from flask.views import MethodView
import logging
from playhouse.flask_utils import FlaskDB

from character_creators.models import database as db
from character_creators.resource import Resource
from character_creators.settings import SECRET_KEY, CACHE_HOST, CACHE_PREFIX

# Initialize the application
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# App secret key is used as a unique identifier for rate limiter.
app.config["SECRET_KEY"] = SECRET_KEY

# Initialize the RESTful API helper package. Add couple of custom errors.
errors = {'BadRequest': {'code': 400}, 'NotFound': {'code': 404}}
api = Api(app, errors=errors, catch_all_404s=True)

# Wrap database connection within app context 
db_wrapper = FlaskDB(app, db)

# Setup and initialize Redis Cache server
cache = Cache(config={"CACHE_TYPE": "redis",
                      "CACHE_REDIS_HOST": CACHE_HOST,
                      "CACHE_REDIS_PORT": "6379",
                      "CACHE_KEY_PREFIX": CACHE_PREFIX,
                      "CACHE_DEFAULT_TIMEOUT": 300})
cache.init_app(app)

# Initialize app rate limiter using the 'fixed-window-elastic-expiry' strategy.
limiter = Limiter(
    app,
    headers_enabled=True,
    storage_uri=f"redis://{CACHE_HOST}:6379",
    strategy="fixed-window-elastic-expiry",
    key_prefix=CACHE_PREFIX,
    application_limits=["100/hour", "1000/day"],
    key_func=(lambda : SECRET_KEY),
)


class CharacterCreators(MethodView):
    """
    The /characters/<id>/creators entity.
    """

    def get(self, id):
        """
        Method GET:

        Get all character creators that matches the character ID.

        :param int id: The character ID
        :return res: Returns cached or live db record
        """
        cache_key = str(id)
        res = cache.get(cache_key)
        if not res:
            res = Resource().get_creators_by_character_id(id)
            cache.set(cache_key, res)
        return res


class Creators(MethodView):
    """
    The /creators entity. Accepts 'character_name' query param ONLY.
    All other query params will return 404.
    """

    def get(self):
        """
        Method GET:

        Get all available creators. If a query param 'character_name'
        is given, then return creators for that character.

        :return res: Returns cached or live db record
        """
        parser = reqparse.RequestParser()
        parser.add_argument("character_name", location="args")
        args = parser.parse_args(strict=True)
        c_name = str(args["character_name"]).lower()
        cache_key = f"characters_{c_name}"
        res = cache.get(cache_key)
        if not res:
            if c_name == "none":
                res = Resource().get_creators()
            else:
                if not c_name:
                    abort(400, message="character_name argument cannot be empty")
                else:
                    res = Resource().get_creators_by_character_name(c_name)
            cache.set(cache_key, res)
        return res

# Resource routing
api.add_resource(CharacterCreators, "/api/v1/characters/<int:id>/creators")
api.add_resource(Creators, "/api/v1/creators")

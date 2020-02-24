import pytest

from character_creators import api
from character_creators.settings import SECRET_KEY


@pytest.fixture
def client():
    api.app.config["TESTING"] = True

    with api.app.test_client() as client:
        yield client

def _common_assertions(res):
    """
    Common asseriomns that should pass for all endpoints

    All reponse should conatin the following fields
    - attributionText: A string containing Marvel copyright
    - totalCreators: An int containing total creators found
    - data: A dictionary object
    - creators: A list object found in data

    :param dict res: The response object in dict
    """
    assert "code" in res
    assert type(res["code"]) is int
    assert "attributionText" in res
    assert "totalCreators" in res
    assert type(res["totalCreators"]) is int
    assert res["totalCreators"] > 0
    assert "data" in res
    assert type(res["data"]) is dict
    assert "creators" in res["data"]
    assert type(res["data"]["creators"]) is list

def _character_assertions(res, **kwargs):
    r"""
    Common character assertions

    :param dict res: The response object in dict
    :param \**kwargs: name or id params
    """
    if ("name" not in kwargs) and ("_id" not in kwargs):
        assert "characterId" in res["data"]
        assert type(res["data"]["characterId"]) is int
        assert "characterName" in res["data"]
        assert type(res["data"]["characterName"]) is str

    if "name" in kwargs:
        assert type(res["data"]["characterName"]) is str
        assert res["data"]["characterName"].lower() == kwargs["name"]

    if "_id" in kwargs:
        assert type(res["data"]["characterId"]) is int
        assert res["data"]["characterId"] == kwargs["_id"]

def test_creators(client):
    """
    Test /api/v1/creators endpoint

    :param FlaskClient client: The api app flask client
    """
    res = client.get("/api/v1/creators").get_json()
    _common_assertions(res)

def test_creators_with_name(client):
    """
    Test /api/v1/creators?character_name=<name> endpoint

    :param FlaskClient client: The api app flask client
    """
    characters = {1009610: "spider-man", 1009351: "hulk"}

    for _id, character in characters.items():
        base = f"/api/v1/creators?character_name={character}"
        res = client.get(base).get_json()
        _common_assertions(res)
        _character_assertions(res)
        _character_assertions(res, name=character, _id=_id)

def test_character_creators_by_id(client):
    """
    Test /api/v1/characters/<int:id>/creators endpoint

    :param FlaskClient client: The api app flask client
    """
    characters = {1009610: "spider-man", 1009351: "hulk"}

    for _id, character in characters.items():
        base = f"/api/v1/characters/{_id}/creators"
        res = client.get(base).get_json()
        _common_assertions(res)
        _character_assertions(res)
        _character_assertions(res, name=character, _id=_id)

import hashlib
import json
import requests
import time

from stringcase import snakecase


class MarvelApi:
    """
    A class to extract data from Marvel's public API.

    :param str api_base: The api base for entities
    :param str public_key: The public key for authorization
    :param str private_key: The private key for authorization
    :param int batch:  The total items per batch, defaults to 100
    """

    def __init__(self, api_base, public_key, private_key, batch=100):
        self.calls = 0
        self.api_base = api_base
        self.pb_key = public_key
        self.pr_key = private_key
        self.batch = batch

    def _get_md5_digest(self, ts):
        """
        Create and get md5 digest as per marvels documentation.
        Doc at developer.marvel.com/documentation/authorization

        :param float ts: Time in seconds since epoch
        :returns: An md5 hexdigest
        :rtype: str
        """
        comb = str(ts) + self.pr_key + self.pb_key
        return hashlib.md5(comb.encode("utf-8")).hexdigest()

    def _get_payload(self, **kwargs):
        r"""
        Get the payload setup for an API request.

        :param \**kwargs: Add or replace keyword args for payload
        :returns: The complete payload
        :rtype: ``dict``
        """
        ts = time.time()
        payload = {"ts": ts,
                   "apikey": self.pb_key,
                   "hash": self._get_md5_digest(ts),
                   "limit": self.batch,
                   "offset": 0}
        payload.update(kwargs)
        return payload

    def get_response(self, entity, limit=None, offset=None):
        """
        Get API response for an entity.

        :param str entity: The marvel entity
        :param int limit: Limit the result, defaults to None
        :param int offset: Offset the result, defaults to None
        :returns: Returns a dictionary
        :rtype: dict
        """
        self.calls += 1
        entity_endpoint = f"{self.api_base}/{entity}"
        params=self._get_payload()
        headers = {"Accept-Encoding": "gzip"}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        return requests.get(entity_endpoint, params=params, headers=headers)

    def get_total(self, entity):
        """
        Get the total count of an entity.

        :param str entity: The marvel entity
        :returns: Total count
        :rtype: int or bool
        """
        result = False
        response = self.get_response(entity, limit=1)
        if response.status_code == 200:
            result = response.json()["data"]["total"]
        return result

    def get_entity(self, entity, keys):
        """
        Get results with the keys for given entity.

        :param str entity: The marvel entity
        :param list keys: The keys that should be captured
        :returns: Returns a generator
        :rtype: dict
        """
        response = self.get_response(entity)

        if response.status_code == 200:
            r1 = response.json()
            if (("data" in r1) and
                ("total" in r1["data"]) and
                ("results" in r1["data"])
            ):
                data = r1["data"]
                total = data["total"]
                results = data["results"]
                for result in results:
                    yield {key: result[key] for key in keys}
                if total > self.batch:
                    offsets = self._get_offsets(total)
                    total_batches = len(offsets)
                    for ofs in offsets:
                        response = self.get_response(entity, offset=ofs)
                        if response.status_code == 200:
                            r2 = response.json()
                            if ("data" in r2) and ("results" in r2["data"]):
                                results = r2["data"]["results"]
                                for result in results:
                                    yield {key: result[key] for key in keys}


    def _extract_ids(self, item, entity):
        """
        Extract associated entity ids from given item.

        :param dict item: A dictionary API result
        :param str entity: The marvel entity
        :returns: Returns a generator
        :rtype: list
        """
        ntt = item[entity]
        total = ntt["available"]
        collection_uri = ntt["collectionURI"].rsplit("/", 3)[1:]
        ntt_uri = "/".join(map(str, collection_uri))
        if total and total <= 20:
            for item in ntt["items"]:
                yield item["resourceURI"].rsplit("/", 1)[-1]
        elif total > 20:
            response = self.get_entity(ntt_uri, ["id"])
            for res in response:
                yield res["id"]

    def get_characters(self):
        """
        Get characters entity.

        :returns: Returns a generator
        :rtype: tuple
        """
        keys = ["id", "name", "series"]
        response = self.get_entity("characters", keys)

        for res in response:
            character = {key:res[key] for key in keys[:-1]}
            s_ids = self._extract_ids(res, "series")
            series = [{"series_id": s_id, "character_id": res["id"]} for s_id in s_ids]
            yield (character, series)

    def get_creators(self):
        """
        Get creators entity.

        :returns: Returns a generator
        :rtype: tuple
        """
        keys = ["id", "firstName", "middleName", "lastName", "suffix",
                "fullName", "thumbnail", "resourceURI", "series"]
        response = self.get_entity("creators", keys)

        for res in response:
            creator = {}
            for key in keys[:-1]:
                if key == "thumbnail":
                    creator[key] = json.dumps(res[key])
                elif key == "resourceURI":
                    creator["resource_uri"] = res[key]
                else:
                    creator[snakecase(key)] = res[key]

            s_ids = self._extract_ids(res, "series")
            series = [{"series_id": s_id, "creator_id": res["id"]} for s_id in s_ids]
            yield (creator, series)

    def _get_offsets(self, total):
        """
        Get offset values from total count.

        :param int total: The total number to calculate offset for
        :returns: Returns a list
        :rtype: list
        """
        offsets = []
        for count in range(1, total + 1):
            if not count % self.batch:
                if count <= total:
                    offsets.append(count)
        return offsets

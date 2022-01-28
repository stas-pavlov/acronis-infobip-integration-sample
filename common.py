#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import os.path
from time import time
from typing import Any

# Define additional authentication class for requests
# for API Key authentication
class APIKeyAuth(requests.auth.AuthBase):

    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["Authorization"] = "App " + self.api_key
        return r

# Define additional authentication class for requests
# for Bearer authentication
class BearerAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r

# Config class to store all needed values and init all needed stuff
class Config:

    __cfg = None

    infobip_base_url = None
    infobip_api_key = None

    acronis_base_url = None
    acronis_client_id = None
    acronis_clint_secret = None

    header = None

    acronis_token = None
    acronis_token_expires_on = time()

    def __init__(self):
        self.__read_config()
        self.infobip_base_url = self.__cfg.get("infobip_base_url", None)
        self.infobip_api_key = self.__cfg.get("infobip_api_key", None)

        self.acronis_base_url = self.__cfg.get("acronis_base_url", None)
        self.acronis_client_id = self.__cfg.get("cronis_client_id", None)
        self.acronis_clint_secret = self.__cfg.get(
            "acronis_clint_secret", None)

        self.header = {"User-Agent": "Acronis Infobip Integration Examples"}

        self.__check_acronis_token()

    def __read_config(self):
        if os.path.exists('config.json'):
            with open('config.json') as сfg_file:
                self.__cfg = json.load(сfg_file)

    def __issue_acronis_token(self):
        response = requests.post(
            f'{self.base_url}api/2/idp/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            auth=(self.acronis_client_id, self.acronis_clint_secret),
            data={'grant_type': 'client_credentials'}
        )

        if response.ok:
            self.acronis_token = response.json()["access_token"]
            self.acronis_token_expires_on = response.json()["expires_on"]

    def __check_acronis_token(self):
        if self.acronis_token_expires_on - time() < 900:
            self.__issue_acronis_token()

# Class to simplify calling Acronis REST API
class Acronis:

    __cfg = None
    __auth = None

    def __init__(self, cfg: Config):
        self.__cfg = cfg
        self.__auth = BearerAuth(self.__cfg.acronis_token)

    def get(self, uri: str, data: Any = None):
        return requests.get(
            f'{self.__cfg.acronis_base_url}{uri}',
            params=data,
            headers=self.__cfg.header,
            auth=self.__auth
        )

    def delete(self, uri: str, data: Any = None):
        return requests.delete(
            f'{self.__cfg.acronis_base_url}{uri}',
            params=data,
            headers=self.__cfg.header,
            auth=self.__auth
        )

    def post(self, uri: str, data: Any = None):
        return requests.post(
            f'{self.__cfg.acronis_base_url}{uri}',
            headers={**self.__cfg.header, **
                     {'Content-Type': 'application/json'}},
            auth=self.__auth,
            data=data
        )

    def put(self, uri: str, data: Any = None):
        return requests.put(
            f'{self.__cfg.acronis_base_url}{uri}',
            headers={**self.__cfg.header, **
                     {'Content-Type': 'application/json'}},
            auth=self.__auth,
            data=data
        )

# Class to simplify calling Infobip REST API
class Infobip:

    __cfg = None
    __auth = None

    def __init__(self, cfg: Config):
        self.__cfg = cfg
        self.__auth = APIKeyAuth(self.__cfg.infobip_api_key)

    def get(self, uri: str, data: Any = None):
        return requests.get(
            f'{self.__cfg.infobip_base_url}{uri}',
            params=data,
            headers=self.__cfg.header,
            auth=self.__auth
        )

    def delete(self, uri: str, data: Any = None):
        return requests.delete(
            f'{self.__cfg.infobip_base_url}{uri}',
            params=data,
            headers=self.__cfg.header,
            auth=self.__auth
        )

    def post(self, uri: str, data: Any = None):
        return requests.post(
            f'{self.__cfg.infobip_base_url}{uri}',
            headers={**self.__cfg.header, **
                     {'Content-Type': 'application/json'}},
            auth=self.__auth,
            data=data
        )

    def put(self, uri: str, data: Any = None):
        return requests.put(
            f'{self.__cfg.infobip_base_url}{uri}',
            headers={**self.__cfg.header, **
                     {'Content-Type': 'application/json'}},
            auth=self.__auth,
            data=data
        )

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
    acronis_client_secret = None

    header = None

    acronis_token = None
    acronis_token_expires_on = time()

    whats_app_from_number = None
    sms_from_number = None
    viber_from_account = None
    to_notify = None
    
    omni_viber_scenario = None
    omni_whatsapp_scenario = None
    
    def __init__(self):
        self.__read_config()
        self.infobip_base_url = self.__cfg.get("infobip_base_url", None)
        self.infobip_api_key = self.__cfg.get("infobip_api_key", None)

        self.acronis_base_url = self.__cfg.get("acronis_base_url", None)
        self.acronis_client_id = self.__cfg.get("acronis_client_id", None)
        self.acronis_client_secret = self.__cfg.get(
            "acronis_client_secret", None)

        self.whats_app_from_number = self.__cfg.get(
            "whats_app_from_number", None)
        self.sms_from_number = self.__cfg.get("sms_from_number", None)
        self.viber_from_account = self.__cfg.get("viber_from_account", None)
        self.to_notify = self.__cfg.get("to_notify", None)

        self.header = {"User-Agent": "Acronis Infobip Integration Examples"}

        self.__check_acronis_token()
        self.__load_omni_scenarios()

    def __read_config(self):
        if os.path.exists('config.json'):
            with open('config.json') as сfg_file:
                self.__cfg = json.load(сfg_file)

    def __issue_acronis_token(self):
        response = requests.post(
            f'{self.acronis_base_url}api/2/idp/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            auth=(self.acronis_client_id, self.acronis_client_secret),
            data={'grant_type': 'client_credentials'}
        )

        if response.ok:
            self.acronis_token = response.json()["access_token"]
            self.acronis_token_expires_on = response.json()["expires_on"]

    def __check_acronis_token(self):
        if self.acronis_token_expires_on - time() < 900:
            self.__issue_acronis_token()
            
    def __load_omni_scenarios(self):
        if os.path.exists('scenarios/viber-sms.json'):
            with open('scenarios/viber-sms.json') as viber_file:
                self.omni_viber_scenario = json.load(viber_file)
                
        if os.path.exists('scenarios/whatsapp-sms.json'):
            with open('scenarios/whatsapp-sms.json') as viber_file:
                self.omni_whatsapp_scenario = json.load(viber_file)


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

    def get_integration_root_tenant(self):
        response = self.get("api/2/clients/{self.__cfg.acronis_client_id}")

        if response.ok:
            return response.json()["tenant_id"]
        else:
            return None


# Class to simplify calling Infobip REST API
class Infobip:

    __cfg = None
    __auth = None
    __scenarios = dict()

    def __init__(self, cfg: Config):
        self.__cfg = cfg
        self.__auth = APIKeyAuth(self.__cfg.infobip_api_key)
        self.__ensure_omni_scenarios_exists()

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

    def send_sms_message(self, msg: str):

        sms_responses = []

        for number in self.__cfg.to_notify:
            sms = {
                "messages": [
                    {
                        "from": f"{self.__cfg.sms_app_from_number}",
                        "destinations": [
                            {
                                "to": f"{number}"
                            }
                        ],
                        "text": f"{msg}"
                    }
                ]
            }
            response = self.post("sms/2/text/advanced",
                                 data=json.dumps(sms))
            sms_responses.append(response)

        return sms_responses

    def send_whatsapp_message(self, msg: str):

        whatsapp_responses = []

        for number in self.__cfg.to_notify:

            whatsapp_msg = {
                "from": f"{self.__cfg.whats_app_from_number}",
                "to": f"{number}",
                "messageId": f"infibip-acronis-{time()}",
                "content": {
                    "text": f"{msg}"
                }
            }
            response = self.post("whatsapp/1/message/text",
                                 data=json.dumps(whatsapp_msg))
            whatsapp_responses.append(response)

        return whatsapp_responses

    def send_omni_viber_sms_message(self, msg: str, failover_msg: str):

        omni_responses = []
 
        for number in self.__cfg.to_notify:

            omni_msg = {
                "scenarioKey": f"{self.__scenarios['acronis-infobip-viber-sms-omni']}",
                "destinations": [
                    {
                        "to": {
                            "phoneNumber": f"{number}"
                        }
                    }
                ],
                "sms": {
                    "text": f"{failover_msg}"
                },
                "viber": {
                    "text": f"{msg}"
                }
            }

            response = self.post("omni/1/advanced", data=json.dumps(omni_msg))
            omni_responses.append(response)

        return omni_responses

    def send_omni_whatsapp_sms_message(self, msg: str, failover_msg: str):

        omni_responses = []

        for number in self.__cfg.to_notify:

            omni_msg = {
                "scenarioKey": f"{self.__scenarios['acronis-infobip-whatsapp-sms-omni']}",
                "destinations": [
                    {
                        "to": {
                            "phoneNumber": f"{number}"
                        }
                    }
                ],
                "sms": {
                    "text": f"{failover_msg}"
                },
                "whatsApp": {
                    "text": f"{msg}"
                }
            }

            response = self.post("omni/1/advanced", data=json.dumps(omni_msg))
            omni_responses.append(response)
        return omni_responses
    
    def __create_viber_sms_onmi_scenario(self):
        self.__cfg.omni_viber_scenario["name"] = 'acronis-infobip-viber-sms-omni'
        viber_flow = [flow for flow in self.__cfg.omni_viber_scenario["flow"] if flow["channel"] == 'VIBER']
        viber_flow[0]["from"] =  self.__cfg.viber_from_account
        response = self.post("omni/1/scenarios", data=json.dumps(self.__cfg.omni_viber_scenario))
        return response
    
    def __create_whatsapp_sms_onmi_scenario(self):
        self.__cfg.omni_whatsapp_scenario["name"] = 'acronis-infobip-whatsapp-sms-omni'
        whatsapp_flow = [flow for flow in self.__cfg.omni_whatsapp_scenario["flow"] if flow["channel"] == 'WHATSAPP']
        whatsapp_flow[0]["from"] =  self.__cfg.whats_app_from_number
        response = self.post("omni/1/scenarios", data=json.dumps(self.__cfg.omni_whatsapp_scenario))
        return response

    def __ensure_omni_scenarios_exists(self):
        response = self.get("omni/1/scenarios")
        
        if response.ok:
            viber_scenario = [scenario for scenario in response.json()["scenarios"] if scenario["name"] == 'acronis-infobip-viber-sms-omni']
            
            if len(viber_scenario)>0:
                self.__scenarios['acronis-infobip-viber-sms-omni'] = viber_scenario[0]["key"]
            else:
                self.__create_viber_sms_onmi_scenario()
                
            whatsapp_scenario = [scenario for scenario in response.json()["scenarios"] if scenario["name"] == 'acronis-infobip-whatsapp-sms-omni']
            
            if len(whatsapp_scenario)>0:
                self.__scenarios['acronis-infobip-whatsapp-sms-omni'] = whatsapp_scenario[0]["key"]
            else:
                self.__create_whatsapp_sms_onmi_scenario()
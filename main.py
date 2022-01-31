#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from common import Acronis, Config, Infobip

if __name__ == "__main__":
    cfg = Config()
    acronis = Acronis(cfg)
    infobip = Infobip(cfg)
    
    response = acronis.get("api/alert_manager/v1/resource_status?embed_alert=true")
    
    if response.ok:
       resources = response.json()["items"]
       msg = ""
       if len(resources)>0:
            for resource in resources:
               resource_id = resource["id"]
               severity = resource["severity"]
               type = resource["alert"]["type"]
               name = resource_id
               response = acronis.get(f"api/resource_management/v4/resources/{resource_id}")
               if response.ok:
                   name = response.json()["name"]
               msg = msg + f"Resource: {name}\n\rSeverity: {severity}\n\rType: {type}\r\n###\r\n"
            
            failover_msg = f"You have severe {len(resources)} alerts."
            
            if cfg.channel == "sms":
                infobip.send_sms_message(failover_msg)
            elif  cfg.channel == "whatsapp":
                infobip.send_whatsapp_message(msg)
            elif  cfg.channel == "whatsapp-sms":
                infobip.send_omni_whatsapp_sms_message(msg,failover_msg)
            elif  cfg.channel == "viber-sms":
                infobip.send_omni_viber_sms_message(msg, failover_msg)
            else:
                infobip.send_omni_viber_sms_message(msg, failover_msg)
    else:
        print("Can't retrieve alerts infomation!")
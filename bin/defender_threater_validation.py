#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Validation & Health Handler
"""

import json
import sys
import time
import requests

from splunk.persistconn.application import PersistentServerConnectionApplication
from splunk.clilib import cli_common as scc
import splunk.entity as entity


APP_NAME = "ThreatER_for_Splunk"
CONF_FILE = "threater"
CONF_STANZA = "settings"


class ThreatERValidation(PersistentServerConnectionApplication):

    def __init__(self, command_line, command_arg):
        super().__init__(command_line, command_arg)

    def handle(self, in_string):
        try:
            payload = json.loads(in_string)
            action = payload.get("action", "validate")

            if action == "validate":
                return self._validate()
            elif action == "health":
                return self._health()
            else:
                return self._error("Unsupported action")

        except Exception as e:
            return self._error(str(e))

    # ---------------------------------------------------------------------
    # Validation Logic
    # ---------------------------------------------------------------------

    def _validate(self):
        config = self._load_config()

        api_base = config.get("api_base_url")
        api_key = config.get("api_key")
        timeout = int(config.get("request_timeout", 30))
        verify_ssl = config.get("verify_ssl", "true").lower() == "true"

        if not api_base or not api_key:
            return self._error("Missing API base URL or API key")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "ThreatER-Splunk-App"
        }

        test_url = f"{api_base.rstrip('/')}/lists"

        try:
            start = time.time()
            response = requests.get(
                test_url,
                headers=headers,
                timeout=timeout,
                verify=verify_ssl
            )
            elapsed = round(time.time() - start, 2)

            if response.status_code == 200:
                return self._success({
                    "status": "connected",
                    "message": "ThreatER API connectivity validated",
                    "response_time_seconds": elapsed
                })

            return self._error(
                f"ThreatER API returned HTTP {response.status_code}",
                details=response.text
            )

        except requests.exceptions.RequestException as e:
            return self._error("ThreatER API connection failed", str(e))

    # ---------------------------------------------------------------------
    # Health Endpoint
    # ---------------------------------------------------------------------

    def _health(self):
        return self._success({
            "status": "ok",
            "message": "ThreatER validation endpoint reachable"
        })

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _load_config(self):
        try:
            return entity.getEntity(
                "configs/conf-threater",
                CONF_STANZA,
                namespace=APP_NAME,
                owner="nobody"
            )
        except Exception:
            return {}

    def _success(self, data):
        return {
            "status": 200,
            "payload": json.dumps(data)
        }

    def _error(self, message, details=None):
        payload = {"status": "error", "message": message}
        if details:
            payload["details"] = details

        return {
            "status": 500,
            "payload": json.dumps(payload)
        }


if __name__ == "__main__":
    ThreatERValidation(sys.argv, sys.stdin).handle(sys.stdin.read())

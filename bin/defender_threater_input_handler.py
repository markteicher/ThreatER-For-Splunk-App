#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input Management Handler
"""

import json
import sys
import time

from splunk.persistconn.application import PersistentServerConnectionApplication
import splunk.entity as entity

APP_NAME = "ThreatER_for_Splunk"
CONF_INPUTS = "inputs"


class ThreatERInputHandler(PersistentServerConnectionApplication):

    def __init__(self, command_line, command_arg):
        super().__init__(command_line, command_arg)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def handle(self, in_string):
        try:
            payload = json.loads(in_string)
            action = payload.get("action", "list")

            if action == "list":
                return self._list_inputs()
            elif action == "status":
                return self._input_status()
            elif action == "enable":
                return self._enable_input(payload)
            elif action == "disable":
                return self._disable_input(payload)
            else:
                return self._error("Unsupported action")

        except Exception as e:
            return self._error(str(e))

    # ------------------------------------------------------------------
    # Input Operations
    # ------------------------------------------------------------------

    def _list_inputs(self):
        inputs = self._get_inputs()
        return self._success({
            "inputs": inputs,
            "count": len(inputs)
        })

    def _input_status(self):
        inputs = self._get_inputs()
        status = []

        for name, cfg in inputs.items():
            status.append({
                "name": name,
                "disabled": cfg.get("disabled", "1") == "1",
                "interval": cfg.get("interval"),
                "sourcetype": cfg.get("sourcetype"),
                "index": cfg.get("index")
            })

        return self._success(status)

    def _enable_input(self, payload):
        input_name = payload.get("name")
        if not input_name:
            return self._error("Missing input name")

        self._set_disabled(input_name, False)
        return self._success({
            "message": f"Input '{input_name}' enabled"
        })

    def _disable_input(self, payload):
        input_name = payload.get("name")
        if not input_name:
            return self._error("Missing input name")

        self._set_disabled(input_name, True)
        return self._success({
            "message": f"Input '{input_name}' disabled"
        })

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_inputs(self):
        try:
            return entity.getEntities(
                f"configs/conf-{CONF_INPUTS}",
                namespace=APP_NAME,
                owner="nobody"
            )
        except Exception:
            return {}

    def _set_disabled(self, input_name, disabled):
        try:
            entity.setEntity(
                f"configs/conf-{CONF_INPUTS}",
                input_name,
                {"disabled": "1" if disabled else "0"},
                namespace=APP_NAME,
                owner="nobody"
            )
        except Exception as e:
            raise RuntimeError(str(e))

    def _success(self, data):
        return {
            "status": 200,
            "payload": json.dumps(data)
        }

    def _error(self, message):
        return {
            "status": 500,
            "payload": json.dumps({
                "status": "error",
                "message": message
            })
        }


if __name__ == "__main__":
    ThreatERInputHandler(sys.argv, sys.stdin).handle(sys.stdin.read())

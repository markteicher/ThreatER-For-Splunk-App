#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
defender_threater_input_handler.py

ThreatER for Splunk App
Modular Input Management REST Handler

Responsibilities:
- List available modular inputs
- Report input status
- Enable / disable inputs
- AppInspect & Splunk Cloud compliant
"""

import json

from splunk.persistconn.application import PersistentServerConnectionApplication
import splunk.entity as entity

APP_NAME = "ThreatER_for_Splunk"
CONF_NAME = "inputs"


class DefenderThreatERInputHandler(PersistentServerConnectionApplication):

    # ------------------------------------------------------------------
    # Entry point (Persistent REST handler)
    # ------------------------------------------------------------------

    def handle(self, in_string):
        try:
            payload = json.loads(in_string or "{}")
            action = payload.get("action", "list")

            if action == "list":
                return self._respond(self._list_inputs())

            if action == "status":
                return self._respond(self._input_status())

            if action == "edit":
                return self._respond(self._edit_input(payload))

            return self._error(f"Unsupported action: {action}")

        except Exception as e:
            return self._error(str(e))

    # ------------------------------------------------------------------
    # Input Operations
    # ------------------------------------------------------------------

    def _list_inputs(self):
        inputs = self._get_inputs()
        return {
            "inputs": sorted(inputs.keys()),
            "count": len(inputs)
        }

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

        return status

    def _edit_input(self, payload):
        name = payload.get("name")
        enabled = payload.get("enabled")

        if not name:
            raise ValueError("Missing input name")

        if enabled is None:
            raise ValueError("Missing enabled flag")

        self._set_disabled(name, not bool(enabled))

        return {
            "message": f"Input '{name}' {'enabled' if enabled else 'disabled'}"
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_inputs(self):
        return entity.getEntities(
            f"configs/conf-{CONF_NAME}",
            namespace=APP_NAME,
            owner="nobody"
        )

    def _set_disabled(self, name, disabled):
        entity.setEntity(
            f"configs/conf-{CONF_NAME}",
            name,
            {"disabled": "1" if disabled else "0"},
            namespace=APP_NAME,
            owner="nobody"
        )

    # ------------------------------------------------------------------
    # REST Response Helpers
    # ------------------------------------------------------------------

    def _respond(self, payload):
        return json.dumps({
            "status": 200,
            "payload": payload

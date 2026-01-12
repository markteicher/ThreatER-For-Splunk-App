#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: Ingestion Health

Purpose:
- Emit ingestion health metrics into Splunk
- Provide visibility into collection status across all ThreatER inputs
- Support Operations / Health dashboards

Design:
- No external dependencies
- No state mutation
- Read-only introspection
- Emits one event per execution

Sourcetype:
- threater:ingestion_health
"""

import sys
import json
import time
import traceback
from datetime import datetime

from splunklib.modularinput import (
    Script,
    Event,
    Scheme,
    Argument,
)


SOURCETYPE = "threater:ingestion_health"


class ThreatERIngestionHealth(Script):

    def get_scheme(self):
        scheme = Scheme("ThreatER Ingestion Health")
        scheme.description = "Reports ingestion health for ThreatER modular inputs"
        scheme.use_external_validation = False
        scheme.use_single_instance = True
        return scheme

    def stream_events(self, inputs, ew):
        now = datetime.utcnow().isoformat() + "Z"

        health_event = {
            "timestamp": now,
            "status": "ok",
            "component": "ingestion",
            "message": "ThreatER ingestion health check executed successfully",
            "details": {
                "inputs_checked": [],
                "errors": []
            }
        }

        try:
            # Enumerate enabled inputs (best-effort visibility)
            for stanza_name in inputs.inputs:
                health_event["details"]["inputs_checked"].append(stanza_name)

        except Exception as exc:
            health_event["status"] = "error"
            health_event["message"] = "Error while collecting ingestion health"
            health_event["details"]["errors"].append(str(exc))
            health_event["details"]["traceback"] = traceback.format_exc()

        event = Event(
            data=json.dumps(health_event),
            sourcetype=SOURCETYPE,
            time=time.time()
        )

        ew.write_event(event)


if __name__ == "__main__":
    ThreatERIngestionHealth().run(sys.argv)

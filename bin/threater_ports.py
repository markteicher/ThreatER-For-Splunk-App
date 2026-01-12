#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: Ports

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Collect port definitions used in enforcement policies
- Capture protocol, port ranges, directionality
- Preserve raw API payloads
- Support pagination, proxy, SSL
- Maintain checkpoint state
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/ports"
SOURCETYPE = "threater:port"


class ThreatERPortsInput(ThreatERModularInput):
    """
    Modular input for ThreatER Ports
    """

    def collect(self):
        self.logger.info("Starting ThreatER port collection")

        checkpoint = ThreatERCheckpoint(
            self,
            key="ports_last_updated"
        )
        last_checkpoint = checkpoint.get()

        params = {"limit": 200}
        if last_checkpoint:
            params["updated_after"] = last_checkpoint

        total_events = 0
        newest_timestamp = last_checkpoint
        next_cursor = None

        while True:
            if next_cursor:
                params["cursor"] = next_cursor

            response = self.api.get(ENDPOINT, params=params)

            ports = response.get("data", [])
            meta = response.get("meta", {})
            next_cursor = meta.get("next_cursor")

            for port in ports:
                self.write_event(
                    data=json.dumps(port),
                    sourcetype=SOURCETYPE
                )
                total_events += 1

                updated_at = port.get("updated_at")
                if updated_at and (
                    not newest_timestamp
                    or updated_at > newest_timestamp
                ):
                    newest_timestamp = updated_at

            self.logger.info(
                f"Fetched {len(ports)} ports "
                f"(total so far: {total_events})"
            )

            if not next_cursor:
                break

        if newest_timestamp and newest_timestamp != last_checkpoint:
            checkpoint.set(newest_timestamp)
            self.logger.info(
                f"Checkpoint updated to {newest_timestamp}"
            )

        self.logger.info(
            f"ThreatER port collection complete — "
            f"{total_events} records ingested"
        )


def main():
    try:
        runner = ThreatERPortsInput(
            input_name="threater_ports",
            sourcetype=SOURCETYPE
        )
        runner.run()

    except ThreatERAPIError as exc:
        sys.stderr.write(f"ThreatER API error: {exc}\n")
        sys.exit(2)

    except Exception as exc:
        sys.stderr.write(f"Unhandled error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: Block Events

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Collect block / allow enforcement events
- Capture inbound and outbound traffic actions
- Preserve raw event payloads for analytics and reporting
- Support pagination, proxy, SSL
- Maintain checkpoint state for incremental collection
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/events/block"
SOURCETYPE = "threater:block_event"


class ThreatERBlockEventsInput(ThreatERModularInput):
    """
    Modular input for ThreatER block events
    """

    def collect(self):
        self.logger.info("Starting ThreatER block event collection")

        checkpoint = ThreatERCheckpoint(
            self,
            key="block_events_last_timestamp"
        )
        last_checkpoint = checkpoint.get()

        params = {"limit": 500}
        if last_checkpoint:
            params["after"] = last_checkpoint

        total_events = 0
        newest_timestamp = last_checkpoint
        next_cursor = None

        while True:
            if next_cursor:
                params["cursor"] = next_cursor

            response = self.api.get(ENDPOINT, params=params)

            events = response.get("data", [])
            meta = response.get("meta", {})
            next_cursor = meta.get("next_cursor")

            for event in events:
                self.write_event(
                    data=json.dumps(event),
                    sourcetype=SOURCETYPE
                )
                total_events += 1

                event_time = event.get("timestamp")
                if event_time and (
                    not newest_timestamp
                    or event_time > newest_timestamp
                ):
                    newest_timestamp = event_time

            self.logger.info(
                f"Fetched {len(events)} block events "
                f"(total so far: {total_events})"
            )

            if not next_cursor:
                break

        if newest_timestamp:
            checkpoint.set(newest_timestamp)
            self.logger.info(
                f"Checkpoint updated to {newest_timestamp}"
            )

        self.logger.info(
            f"ThreatER block event collection complete — "
            f"{total_events} records ingested"
        )


def main():
    try:
        runner = ThreatERBlockEventsInput(
            input_name="threater_block_events",
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

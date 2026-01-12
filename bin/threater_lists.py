#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: Lists

Collects all ThreatER list objects:
- Allow Lists
- Block Lists
- Threat Lists

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Design:
- Raw JSON ingestion
- Pagination support
- Checkpointing by updated_at
- Proxy + SSL support
- Splunk modular input compliant
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/lists"
SOURCETYPE = "threater:list"


class ThreatERListsInput(ThreatERModularInput):
    """
    Modular input for ThreatER Lists
    """

    def collect(self):
        self.logger.info("Starting ThreatER list collection")

        checkpoint = ThreatERCheckpoint(self, key="lists_last_updated")
        last_checkpoint = checkpoint.get()

        params = {
            "limit": 200
        }

        if last_checkpoint:
            params["updated_after"] = last_checkpoint

        next_cursor = None
        newest_timestamp = last_checkpoint
        total_events = 0

        while True:
            if next_cursor:
                params["cursor"] = next_cursor

            response = self.api.get(ENDPOINT, params=params)

            lists = response.get("data", [])
            next_cursor = response.get("meta", {}).get("next_cursor")

            for item in lists:
                self.write_event(
                    data=json.dumps(item),
                    sourcetype=SOURCETYPE
                )
                total_events += 1

                updated_at = item.get("updated_at")
                if updated_at and (
                    not newest_timestamp or updated_at > newest_timestamp
                ):
                    newest_timestamp = updated_at

            self.logger.info(
                f"Fetched {len(lists)} lists "
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
            f"ThreatER list collection complete — "
            f"{total_events} records ingested"
        )


def main():
    try:
        runner = ThreatERListsInput(
            input_name="threater_lists",
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

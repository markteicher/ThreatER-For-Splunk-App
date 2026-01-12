#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: External Lists

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Collect External / Integrated Threat Lists
- Preserve raw API payloads
- Support pagination, proxy, SSL
- Maintain checkpointing
- No enrichment, no mutation
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/external-lists"
SOURCETYPE = "threater:external_list"


class ThreatERExternalListsInput(ThreatERModularInput):
    """
    Modular input for ThreatER External Lists
    """

    def collect(self):
        self.logger.info("Starting ThreatER external list collection")

        checkpoint = ThreatERCheckpoint(
            self,
            key="external_lists_last_updated"
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

            lists = response.get("data", [])
            meta = response.get("meta", {})
            next_cursor = meta.get("next_cursor")

            for ext_list in lists:
                self.write_event(
                    data=json.dumps(ext_list),
                    sourcetype=SOURCETYPE
                )
                total_events += 1

                updated_at = ext_list.get("updated_at")
                if updated_at and (
                    not newest_timestamp
                    or updated_at > newest_timestamp
                ):
                    newest_timestamp = updated_at

            self.logger.info(
                f"Fetched {len(lists)} external lists "
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
            f"ThreatER external list collection complete — "
            f"{total_events} records ingested"
        )


def main():
    try:
        runner = ThreatERExternalListsInput(
            input_name="threater_external_lists",
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

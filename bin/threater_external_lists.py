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
- Maintain checkpointing for incremental ingestion
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

        checkpoint = ThreatERCheckpoint(self, key="external_lists_last_updated")
        last_checkpoint = checkpoint.get()

        params = {"limit": 200}
        if last_checkpoint:
            params["updated_after"] = last_checkpoint

        total_records = 0
        newest_timestamp = last_checkpoint
        next_cursor = None

        while True:
            if next_cursor:
                params["cursor"] = next_cursor

            response = self.api.get(ENDPOINT, params=params)

            records = response.get("data") or []
            meta = response.get("meta") or {}
            next_cursor = meta.get("next_cursor") or meta.get("nextCursor")

            for record in records:
                self.write_event(
                    data=json.dumps(record),
                    sourcetype=SOURCETYPE
                )
                total_records += 1

                updated_at = (
                    record.get("updated_at")
                    or record.get("last_updated")
                    or record.get("updatedAt")
                    or record.get("timestamp")
                )

                if updated_at and (not newest_timestamp or updated_at > newest_timestamp):
                    newest_timestamp = updated_at

            self.logger.info(
                f"Fetched {len(records)} external lists (total so far: {total_records})"
            )

            if not next_cursor:
                break

        if newest_timestamp and newest_timestamp != last_checkpoint:
            checkpoint.set(newest_timestamp)
            self.logger.info(f"Checkpoint updated to {newest_timestamp}")
        else:
            self.logger.info("No checkpoint update required")

        self.logger.info(
            f"ThreatER external list collection complete — {total_records} records ingested"
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

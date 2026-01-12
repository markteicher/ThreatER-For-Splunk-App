#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: IOC Search Results

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Retrieve IOC search results (IPs, domains, indicators)
- Preserve raw IOC response payloads
- Support premium intelligence visibility
- Enable investigation and enrichment workflows in Splunk
- Maintain incremental ingestion via checkpointing
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/ioc/search"
SOURCETYPE = "threater:ioc_search"


class ThreatERIOCSearchInput(ThreatERModularInput):
    """
    Modular input for ThreatER IOC search results
    """

    def collect(self):
        self.logger.info("Starting ThreatER IOC search ingestion")

        checkpoint = ThreatERCheckpoint(
            self,
            key="ioc_search_last_timestamp"
        )
        last_checkpoint = checkpoint.get()

        params = {
            "limit": 200,
        }

        if last_checkpoint:
            params["updated_after"] = last_checkpoint

        total_records = 0
        newest_timestamp = last_checkpoint
        next_cursor = None

        while True:
            if next_cursor:
                params["cursor"] = next_cursor

            response = self.api.get(ENDPOINT, params=params)

            records = response.get("data", [])
            meta = response.get("meta", {})
            next_cursor = meta.get("next_cursor")

            for record in records:
                self.write_event(
                    data=json.dumps(record),
                    sourcetype=SOURCETYPE
                )
                total_records += 1

                timestamp = (
                    record.get("updated_at")
                    or record.get("created_at")
                    or record.get("timestamp")
                )

                if timestamp and (
                    not newest_timestamp
                    or timestamp > newest_timestamp
                ):
                    newest_timestamp = timestamp

            self.logger.info(
                f"Fetched {len(records)} IOC results "
                f"(total so far: {total_records})"
            )

            if not next_cursor:
                break

        if newest_timestamp:
            checkpoint.set(newest_timestamp)
            self.logger.info(
                f"Checkpoint updated to {newest_timestamp}"
            )

        self.logger.info(
            f"ThreatER IOC search ingestion complete — "
            f"{total_records} records ingested"
        )


def main():
    try:
        runner = ThreatERIOCSearchInput(
            input_name="threater_ioc_search",
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

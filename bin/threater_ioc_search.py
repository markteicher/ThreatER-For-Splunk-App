#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: IOC Search Results

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Ingest IOC search results (IPs, domains, indicators)
- Capture verdicts, categories, confidence, and source attribution
- Support IOC Search dashboards and investigations
- Preserve raw payloads for audit and pivoting

Design:
- Raw JSON ingestion
- Cursor-based pagination
- Checkpointing via updated_at
- Proxy + SSL support
- No enrichment
- No transformation
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/ioc/results"
SOURCETYPE = "threater:ioc_result"


class ThreatERIOCResultsInput(ThreatERModularInput):
    """
    Modular input for ThreatER IOC search results
    """

    def collect(self):
        self.logger.info("Starting ThreatER IOC results ingestion")

        checkpoint = ThreatERCheckpoint(
            self,
            key="ioc_results_last_updated"
        )
        last_checkpoint = checkpoint.get()

        params = {
            "limit": 200
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

                updated_at = (
                    record.get("updated_at")
                    or record.get("last_seen")
                    or record.get("timestamp")
                )

                if updated_at and (
                    not newest_timestamp
                    or updated_at > newest_timestamp
                ):
                    newest_timestamp = updated_at

            self.logger.info(
                f"Fetched {len(records)} IOC result records "
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
            f"ThreatER IOC results ingestion complete — "
            f"{total_records} records ingested"
        )


def main():
    try:
        runner = ThreatERIOCResultsInput(
            input_name="threater_ioc_results",
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

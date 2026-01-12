#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: Reports

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Ingest ThreatER reports (on-demand and generated reports)
- Support reporting visibility, auditability, and historical analysis
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/reports"
SOURCETYPE = "threater:report"


class ThreatERReportsInput(ThreatERModularInput):
    """
    Modular input for ThreatER reports
    """

    def collect(self):
        self.logger.info("Starting ThreatER reports ingestion")

        checkpoint = ThreatERCheckpoint(
            self,
            key="reports_last_updated"
        )
        last_checkpoint = checkpoint.get()

        params = {
            "limit": 200
        }

        if last_checkpoint:
            params["created_after"] = last_checkpoint

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
                    record.get("created_at")
                    or record.get("generated_at")
                )

                if timestamp and (
                    not newest_timestamp
                    or timestamp > newest_timestamp
                ):
                    newest_timestamp = timestamp

            self.logger.info(
                f"Fetched {len(records)} report records "
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
            f"ThreatER report ingestion complete — "
            f"{total_records} records ingested"
        )


def main():
    try:
        runner = ThreatERReportsInput(
            input_name="threater_reports",
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

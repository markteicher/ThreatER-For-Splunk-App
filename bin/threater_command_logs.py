#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: Command Logs

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Purpose:
- Ingest administrative and system command execution logs
- Provide audit visibility into configuration changes
- Support troubleshooting, compliance, and forensic review
- Preserve raw command execution payloads
- Maintain incremental ingestion using checkpoints
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/command/logs"
SOURCETYPE = "threater:command_log"


class ThreatERCommandLogsInput(ThreatERModularInput):
    """
    Modular input for ThreatER command execution logs
    """

    def collect(self):
        self.logger.info("Starting ThreatER command logs ingestion")

        checkpoint = ThreatERCheckpoint(
            self,
            key="command_logs_last_timestamp"
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
                    or record.get("executed_at")
                    or record.get("timestamp")
                )

                if timestamp and (
                    not newest_timestamp
                    or timestamp > newest_timestamp
                ):
                    newest_timestamp = timestamp

            self.logger.info(
                f"Fetched {len(records)} command logs "
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
            f"ThreatER command logs ingestion complete — "
            f"{total_records} records ingested"
        )


def main():
    try:
        runner = ThreatERCommandLogsInput(
            input_name="threater_command_logs",
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

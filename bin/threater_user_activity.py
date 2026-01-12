#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: User Activity
"""

import sys
import json

from threater_common import (
    ThreatERModularInput,
    ThreatERCheckpoint,
    ThreatERAPIError,
)

ENDPOINT = "/users/activity"
SOURCETYPE = "threater:user_activity"


class ThreatERUserActivityInput(ThreatERModularInput):
    """
    Modular input for ThreatER user activity events
    """

    def collect(self):
        self.logger.info("Starting ThreatER user activity ingestion")

        checkpoint = ThreatERCheckpoint(
            self,
            key="user_activity_last_timestamp"
        )
        last_checkpoint = checkpoint.get()

        params = {"limit": 200}
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
            next_cursor = response.get("meta", {}).get("next_cursor")

            for record in records:
                self.write_event(
                    data=json.dumps(record),
                    sourcetype=SOURCETYPE
                )
                total_records += 1

                timestamp = (
                    record.get("created_at")
                    or record.get("event_time")
                    or record.get("timestamp")
                )

                if timestamp and (
                    not newest_timestamp or timestamp > newest_timestamp
                ):
                    newest_timestamp = timestamp

            self.logger.info(
                f"Fetched {len(records)} user activity events "
                f"(total so far: {total_records})"
            )

            if not next_cursor:
                break

        if newest_timestamp and newest_timestamp != last_checkpoint:
            checkpoint.set(newest_timestamp)
            self.logger.info(
                f"Checkpoint updated to {newest_timestamp}"
            )

        self.logger.info(
            f"ThreatER user activity ingestion complete — "
            f"{total_records} records ingested"
        )


def main():
    try:
        runner = ThreatERUserActivityInput(
            input_name="threater_user_activity",
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThreatER for Splunk App
Modular Input: List Entries

Collects entries for all ThreatER lists (Allow, Block, Threat)

Source:
- ThreatER API v3
  https://portal.threater.com/api/v3/

Design:
- Raw JSON ingestion
- Cursor-based pagination
- Parent list correlation
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

LISTS_ENDPOINT = "/lists"
ENTRIES_ENDPOINT_TEMPLATE = "/lists/{list_id}/entries"
SOURCETYPE = "threater:list_entry"


class ThreatERListEntriesInput(ThreatERModularInput):
    """
    Modular input for ThreatER List Entries
    """

    def collect(self):
        self.logger.info("Starting ThreatER list entry collection")

        checkpoint = ThreatERCheckpoint(
            self,
            key="list_entries_last_updated"
        )
        last_checkpoint = checkpoint.get()

        list_params = {"limit": 200}
        lists_response = self.api.get(LISTS_ENDPOINT, params=list_params)
        lists = lists_response.get("data", [])

        total_events = 0
        newest_timestamp = last_checkpoint

        for lst in lists:
            list_id = lst.get("id")
            list_type = lst.get("type")
            list_name = lst.get("name")

            if not list_id:
                continue

            self.logger.info(
                f"Collecting entries for list "
                f"{list_name} ({list_type})"
            )

            entry_params = {"limit": 200}
            if last_checkpoint:
                entry_params["updated_after"] = last_checkpoint

            next_cursor = None

            while True:
                if next_cursor:
                    entry_params["cursor"] = next_cursor

                endpoint = ENTRIES_ENDPOINT_TEMPLATE.format(
                    list_id=list_id
                )

                response = self.api.get(endpoint, params=entry_params)
                entries = response.get("data", [])
                next_cursor = response.get("meta", {}).get("next_cursor")

                for entry in entries:
                    # Attach list context without mutation
                    payload = {
                        "list_id": list_id,
                        "list_name": list_name,
                        "list_type": list_type,
                        "entry": entry,
                    }

                    self.write_event(
                        data=json.dumps(payload),
                        sourcetype=SOURCETYPE
                    )
                    total_events += 1

                    updated_at = entry.get("updated_at")
                    if updated_at and (
                        not newest_timestamp
                        or updated_at > newest_timestamp
                    ):
                        newest_timestamp = updated_at

                self.logger.info(
                    f"Fetched {len(entries)} entries from list "
                    f"{list_name}"
                )

                if not next_cursor:
                    break

        if newest_timestamp:
            checkpoint.set(newest_timestamp)
            self.logger.info(
                f"Checkpoint updated to {newest_timestamp}"
            )

        self.logger.info(
            f"ThreatER list entry collection complete — "
            f"{total_events} records ingested"
        )


def main():
    try:
        runner = ThreatERListEntriesInput(
            input_name="threater_list_entries",
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

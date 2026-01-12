#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import splunklib.client as client
from splunklib.binding import HTTPError

APP_NAME = "ThreatER_for_Splunk"
CONF_NAME = "defender_threater"
CONF_STANZA = "settings"

API_KEY_REALM = "ThreatER"
PROXY_PASSWORD_REALM = "ThreatER_PROXY"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def read_stdin():
    """Read entire stdin once (Splunk-safe)."""
    data = sys.stdin.read()
    return data.strip()


def respond(payload):
    print(json.dumps(payload))
    sys.exit(0)


def get_service(session_key):
    return client.connect(token=session_key, app=APP_NAME)


def normalize_checkbox(value):
    return "true" if str(value).lower() in ("true", "1") else "false"


# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------

def handle_list(service):
    try:
        conf = service.confs[CONF_NAME]
        stanza = conf[CONF_STANZA]
        data = dict(stanza)
    except Exception:
        data = {}

    respond({"status": "ok", "data": data})


def handle_edit(service, args):
    conf = service.confs[CONF_NAME]

    try:
        stanza = conf[CONF_STANZA]
    except KeyError:
        stanza = conf.create(CONF_STANZA)

    # --------------------------------------------------------------
    # Secure storage: API key
    # --------------------------------------------------------------
    if args.get("api_key"):
        try:
            service.storage_passwords.create(
                args["api_key"],
                username="api_key",
                realm=API_KEY_REALM
            )
        except HTTPError as e:
            if e.status != 409:
                raise

    # --------------------------------------------------------------
    # Secure storage: Proxy password
    # --------------------------------------------------------------
    if args.get("proxy_password"):
        try:
            service.storage_passwords.create(
                args["proxy_password"],
                username="proxy_password",
                realm=PROXY_PASSWORD_REALM
            )
        except HTTPError as e:
            if e.status != 409:
                raise

    # --------------------------------------------------------------
    # Persist non-secret configuration
    # --------------------------------------------------------------
    field_map = {
        "api_base_url": args.get("api_base_url"),
        "request_timeout": args.get("request_timeout"),
        "verify_ssl": normalize_checkbox(args.get("verify_ssl")),
        "proxy_enabled": normalize_checkbox(args.get("proxy_enabled")),
        "proxy_url": args.get("proxy_url"),
        "proxy_username": args.get("proxy_username"),

        "collect_lists": normalize_checkbox(args.get("collect_lists")),
        "collect_plugins": normalize_checkbox(args.get("collect_plugins")),
        "collect_enforcers": normalize_checkbox(args.get("collect_enforcers")),
        "collect_networks": normalize_checkbox(args.get("collect_networks")),
        "collect_users": normalize_checkbox(args.get("collect_users")),
        "collect_reports": normalize_checkbox(args.get("collect_reports")),
        "collect_events": normalize_checkbox(args.get("collect_events")),
    }

    update_payload = {
        k: v for k, v in field_map.items() if v is not None
    }

    stanza.update(update_payload)

    respond({"status": "saved"})


def handle_reload(service):
    respond({"status": "reloaded"})


# ------------------------------------------------------------------
# Main dispatcher
# ------------------------------------------------------------------

def main():
    raw = read_stdin()

    if not raw:
        respond({"error": "Empty request"})

    lines = raw.splitlines()
    session_key = lines[0]
    payload = json.loads("\n".join(lines[1:]) or "{}")

    service = get_service(session_key)

    action = payload.get("action")
    args = payload.get("payload", {})

    if action == "list":
        handle_list(service)
    elif action == "edit":
        handle_edit(service, args)
    elif action == "reload":
        handle_reload(service)
    else:
        respond({"error": "Unsupported action"})


if __name__ == "__main__":
    main()

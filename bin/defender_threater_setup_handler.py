# defender_threater_setup_handler.py
#
# ThreatER for Splunk App
# Setup & Configuration Handler
#
# Responsibilities:
# - Persist setup configuration
# - Securely store API key
# - Support setup UI (list/edit)
# - AppInspect compliant

import sys
import json
import splunklib.client as client
from splunklib.binding import HTTPError

APP_NAME = "ThreatER_for_Splunk"
CONF_NAME = "defender_threater"
CONF_STANZA = "settings"
PASSWORD_REALM = "ThreatER"

def get_session_key():
    return sys.stdin.readline().strip()

def respond(payload, status=200):
    print(json.dumps(payload))
    sys.exit(0)

def get_service(session_key):
    return client.connect(token=session_key, app=APP_NAME)

def handle_list(service):
    try:
        conf = service.confs.get(CONF_NAME, {})
        stanza = conf.get(CONF_STANZA, {})
    except Exception:
        stanza = {}

    respond({"status": "ok", "data": dict(stanza)})

def handle_edit(service, args):
    conf = service.confs[CONF_NAME]

    # Create stanza if missing
    try:
        stanza = conf[CONF_STANZA]
    except KeyError:
        stanza = conf.create(CONF_STANZA)

    # Store API key securely
    if "api_key" in args and args["api_key"]:
        try:
            service.storage_passwords.create(
                args["api_key"],
                username="api_key",
                realm=PASSWORD_REALM
            )
        except HTTPError as e:
            if e.status != 409:
                raise

    # Fields to persist in conf (non-secret)
    fields = [
        "api_base_url",
        "request_timeout",
        "verify_ssl",
        "proxy_enabled",
        "proxy_url",
        "proxy_username",
        "collect_lists",
        "collect_plugins",
        "collect_enforcers",
        "collect_networks",
        "collect_users",
        "collect_reports",
        "collect_events"
    ]

    update_payload = {}
    for field in fields:
        if field in args:
            update_payload[field] = args[field]

    stanza.update(update_payload)
    respond({"status": "saved"})

def handle_reload(service):
    try:
        service.restart()
    except Exception:
        pass

    respond({"status": "reloaded"})

def main():
    session_key = get_session_key()
    service = get_service(session_key)

    payload = json.loads(sys.stdin.read() or "{}")
    action = payload.get("action")
    args = payload.get("payload", {})

    if action == "list":
        handle_list(service)
    elif action == "edit":
        handle_edit(service, args)
    elif action == "reload":
        handle_reload(service)
    else:
        respond({"error": "Unsupported action"}, status=400)

if __name__ == "__main__":
    main()

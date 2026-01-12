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


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def get_session_key():
    return sys.stdin.readline().strip()


def respond(payload, status=200):
    print(json.dumps(payload))
    sys.exit(0)


def get_service(session_key):
    return client.connect(token=session_key, app=APP_NAME)


def normalize_checkbox(value):
    """
    Splunk checkboxes arrive as:
      - 'true'
      - 'false'
      - '1'
      - None
    Normalize to 'true' / 'false'
    """
    return "true" if str(value).lower() in ("true", "1") else "false"


# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------

def handle_list(service):
    try:
        conf = service.confs.get(CONF_NAME)
        stanza = conf.get(CONF_STANZA, {})
    except Exception:
        stanza = {}

    respond({
        "status": "ok",
        "data": dict(stanza)
    })


def handle_edit(service, args):
    conf = service.confs[CONF_NAME]

    # Create stanza if missing
    try:
        stanza = conf[CONF_STANZA]
    except KeyError:
        stanza = conf.create(CONF_STANZA)

    # --------------------------------------------------------------
    # Secure API key storage
    # --------------------------------------------------------------
    if args.get("api_key"):
        try:
            service.storage_passwords.create(
                args["api_key"],
                username="api_key",
                realm=PASSWORD_REALM
            )
        except HTTPError as e:
            # 409 = already exists (acceptable)
            if e.status != 409:
                raise

    # --------------------------------------------------------------
    # Persist non-secret fields
    # --------------------------------------------------------------
    update_payload = {}

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

    for key, value in field_map.items():
        if value is not None:
            update_payload[key] = value

    stanza.update(update_payload)

    respond({"status": "saved"})


def handle_reload(service):
    # Reload is intentionally lightweight — no forced restart
    respond({"status": "reloaded"})


# ------------------------------------------------------------------
# Main dispatcher
# ------------------------------------------------------------------

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

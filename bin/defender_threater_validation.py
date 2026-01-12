#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
defender_threater_validation.py

ThreatER for Splunk App
Validation + Connectivity + Health (REST handler)

Used by restmap.conf endpoints:
- /defender_threater/validate          (list)
- /defender_threater/test_connection   (list)
- /defender_threater/health            (list)

Responsibilities:
- Read saved setup configuration from conf
- Retrieve API key from Splunk secure storage
- Perform a live API reachability test (with optional auth, proxy, SSL verify, timeout)
- Return a clean JSON payload for Splunk Web setup UI / diagnostics
- AppInspect-friendly (no file writes, no shell, no hardcoded secrets)
"""

import sys
import json
import time
from urllib.parse import urljoin

import splunklib.client as client

try:
    import requests
except Exception as exc:
    # requests should exist in Splunk's python, but fail gracefully if not.
    requests = None


APP_NAME = "ThreatER_for_Splunk"
CONF_NAME = "defender_threater"
CONF_STANZA = "settings"
PASSWORD_REALM = "ThreatER"
PASSWORD_USERNAME = "api_key"


# -----------------------------
# IO helpers
# -----------------------------
def read_input():
    """
    Splunk REST handlers commonly provide:
    - first line: session key
    - remaining: JSON payload { action, payload, ... }
    """
    raw = sys.stdin.read()
    lines = raw.splitlines()
    session_key = (lines[0].strip() if lines else "").strip()

    rest = "\n".join(lines[1:]) if len(lines) > 1 else ""
    try:
        payload = json.loads(rest or "{}")
    except Exception:
        payload = {}
    return session_key, payload


def respond(obj):
    print(json.dumps(obj))
    sys.exit(0)


def get_service(session_key):
    return client.connect(token=session_key, app=APP_NAME)


def as_bool(val, default=False):
    if val is None:
        return default
    s = str(val).strip().lower()
    if s in ("1", "true", "t", "yes", "y", "on"):
        return True
    if s in ("0", "false", "f", "no", "n", "off"):
        return False
    return default


def as_int(val, default=30):
    try:
        return int(val)
    except Exception:
        return default


# -----------------------------
# Splunk config + secret access
# -----------------------------
def load_settings(service):
    """
    Returns dict of settings stanza content (strings).
    """
    try:
        conf = service.confs.get(CONF_NAME)
        stanza = conf.get(CONF_STANZA)
        return dict(stanza.content)
    except Exception:
        return {}


def load_api_key(service):
    """
    Returns API key from Splunk storage/passwords, or "" if not found.
    """
    try:
        for cred in service.storage_passwords:
            if cred.realm == PASSWORD_REALM and cred.username == PASSWORD_USERNAME:
                return cred.clear_password or ""
    except Exception:
        pass
    return ""


# -----------------------------
# HTTP validation
# -----------------------------
def build_headers(api_key):
    """
    ThreatER auth header specifics are unknown from the prompt; we support common patterns.
    Sending multiple headers is generally tolerated and avoids guessing wrong.
    """
    if not api_key:
        return {}

    return {
        "Authorization": f"Bearer {api_key}",
        "X-API-Key": api_key,
        "x-api-key": api_key,
        "Api-Key": api_key,
        "Accept": "application/json",
        "User-Agent": "ThreatER-for-Splunk/1.0",
    }


def test_api(
    base_url,
    api_key="",
    timeout_s=30,
    verify_ssl=True,
    proxy_enabled=False,
    proxy_url="",
):
    """
    Connectivity test:
    - GET base_url (and optionally a couple very common health paths)
    - Measures latency
    - Returns dict with status, http_code, latency_ms, url_used, error
    """
    if requests is None:
        return {
            "ok": False,
            "error": "Python requests module not available in this Splunk runtime.",
            "http_status": None,
            "latency_ms": None,
            "url_used": None,
        }

    if not base_url:
        return {
            "ok": False,
            "error": "api_base_url is not configured.",
            "http_status": None,
            "latency_ms": None,
            "url_used": None,
        }

    # Normalize base_url
    base_url = base_url.strip()
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        # Be conservative: default to https
        base_url = "https://" + base_url

    # Candidate paths (minimal + safe). First hit is the configured base URL.
    candidates = [
        base_url,
        urljoin(base_url.rstrip("/") + "/", "health"),
        urljoin(base_url.rstrip("/") + "/", "status"),
        urljoin(base_url.rstrip("/") + "/", "version"),
    ]

    headers = build_headers(api_key)

    proxies = None
    if proxy_enabled and proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

    last_err = None
    for url in candidates:
        t0 = time.time()
        try:
            r = requests.get(
                url,
                headers=headers,
                timeout=timeout_s,
                verify=verify_ssl,
                proxies=proxies,
            )
            latency_ms = int((time.time() - t0) * 1000)

            # Treat 2xx/3xx as OK. Treat 401/403 as "reachable but auth failed" (still useful signal).
            if 200 <= r.status_code < 400:
                return {
                    "ok": True,
                    "http_status": r.status_code,
                    "latency_ms": latency_ms,
                    "url_used": url,
                    "auth_required": False,
                }

            if r.status_code in (401, 403):
                return {
                    "ok": False,
                    "http_status": r.status_code,
                    "latency_ms": latency_ms,
                    "url_used": url,
                    "error": "API reachable but authentication failed (401/403).",
                    "auth_required": True,
                }

            # Other status codes: keep trying next candidate, but capture info
            last_err = f"HTTP {r.status_code}"
        except Exception as exc:
            latency_ms = int((time.time() - t0) * 1000)
            last_err = f"{type(exc).__name__}: {exc} (after {latency_ms}ms)"
            continue

    return {
        "ok": False,
        "http_status": None,
        "latency_ms": None,
        "url_used": None,
        "error": last_err or "Unknown connectivity failure.",
    }


# -----------------------------
# REST actions
# -----------------------------
def handle_list(service):
    settings = load_settings(service)
    api_key = load_api_key(service)

    api_base_url = settings.get("api_base_url", "").strip()
    timeout_s = as_int(settings.get("request_timeout"), default=30)
    verify_ssl = as_bool(settings.get("verify_ssl"), default=True)
    proxy_enabled = as_bool(settings.get("proxy_enabled"), default=False)
    proxy_url = settings.get("proxy_url", "").strip()

    # Minimal configuration diagnostics (no secrets)
    config_check = {
        "api_base_url_configured": bool(api_base_url),
        "api_key_configured": bool(api_key),
        "proxy_enabled": proxy_enabled,
        "verify_ssl": verify_ssl,
        "request_timeout": timeout_s,
    }

    api_check = test_api(
        base_url=api_base_url,
        api_key=api_key,
        timeout_s=timeout_s,
        verify_ssl=verify_ssl,
        proxy_enabled=proxy_enabled,
        proxy_url=proxy_url,
    )

    overall_ok = bool(config_check["api_base_url_configured"]) and bool(config_check["api_key_configured"]) and bool(api_check.get("ok") or api_check.get("auth_required"))

    respond(
        {
            "status": "ok" if overall_ok else "error",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "checks": {
                "config": config_check,
                "api_connectivity": api_check,
            },
            "notes": [
                "Connectivity test attempts the configured base URL first, then common health/status paths.",
                "401/403 indicates the API is reachable but credentials/permissions are not valid.",
            ],
        }
    )


def main():
    session_key, payload = read_input()
    if not session_key:
        respond({"status": "error", "error": "Missing session key from Splunk REST handler stdin."})

    service = get_service(session_key)

    action = payload.get("action", "list")
    # Per restmap.conf, we expect list-only actions for validate/test_connection/health
    if action != "list":
        respond({"status": "error", "error": "Unsupported action (expected list).", "action": action})

    handle_list(service)


if __name__ == "__main__":
    main()

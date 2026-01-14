# ThreatER for Splunk App

## Overview

ThreatER is a preemptive cybersecurity platform that builds trusted networks by automatically blocking known malicious traffic (IPs, domains) at the network edge, reducing noise for security teams and improving the efficiency of existing security tools (firewalls, SIEMs).

It acts as a foundational layer, ingesting threat intelligence from many sources to proactively filter out bad actors before they reach your internal systems, handling both inbound and outbound threats with minimal latency, offering an automated **“set it and forget it”** defense.

This Splunk App enables security teams to **ingest, monitor, analyze, and operationalize ThreatER intelligence and enforcement data directly in Splunk**, without relying on the ThreatER portal UI.

---

## How ThreatER Works

- **Threat Intelligence Collection**  
  Gathers intelligence from commercial, open-source, and government feeds.

- **Proactive Blocking**  
  Blocks known malicious IPs and domains at line speed at the network layer (Layer 2/3), before traffic reaches firewalls or internal defenses.

- **Security Stack Integration**  
  Works alongside firewalls, EDR, SIEMs, and network controls to reduce alert noise and improve signal quality.

- **Automation**  
  Enforces policies automatically, transforming reactive security workflows into proactive protection.

---

## Key Benefits

- **Reduces Problem Space**  
  Eliminates known-bad traffic before it generates alerts.

- **Enhances Existing Security Tools**  
  Feeds cleaner data into downstream security platforms.

- **Real-Time & Scalable**  
  Blocks threats instantly at massive scale with minimal latency.

- **Builds Trust**  
  Establishes a baseline of trusted network activity.

---

## 🧾 ThreatER API Coverage (v3)

This Splunk App is built to cover **all major ThreatER API v3 endpoints**:

**Base API**

https://portal.threater.com/api/v3/

### Threat Intelligence
- Malicious IPs
- Malicious Domains
- IP Reputation
- Domain Reputation
- Indicator Metadata
- Confidence & Scoring Data

### Network Enforcement
- Blocklists
- Allowlists
- Policy Assignments
- Enforcement Status
- Action History

### Intelligence Feeds
- Feed Sources
- Feed Categories
- Feed Updates
- Feed Health & Status

### Observations & Telemetry
- Block Events
- Allow Events
- Traffic Observations
- Inbound / Outbound Events
- Enforcement Metrics

### Administration & Platform
- Tenants
- Organizations
- Users
- Roles & Permissions
- Health

All data is ingested as **raw JSON** to preserve evidence fidelity.


---

By default, the app uses **ThreatER API v3**.  
Optional support for **ThreatER API v6** can be enabled to expose additional configuration and settings data.

---

## API Versions Supported

### API v3 (Default)

Enabled by default.

Used for:
- Users
- Appliances
- Networks
- Ports
- Policies
- Allow Lists
- Block Lists
- Threat Lists
- Plugins
- Command Logs
- Reports

No additional configuration is required for API v3.

---

## API v6 Support (Advanced / Optional)

API v6 is **disabled by default**.

API v6 exposes **platform configuration and settings data** that is not available via API v3.  
This functionality is **read-only** and intended for advanced operators and administrators.

### Default Behavior

- API v6 calls are **not executed** unless explicitly enabled
- The app functions fully without API v6
- No errors or warnings are generated when API v6 is disabled

This design prevents unsupported calls in environments where API v6 is not exposed.

---

## What API v6 Covers

When enabled, API v6 is used **only** to retrieve configuration state.

### General Settings
- Hostname
- Timezone
- Password policy settings
- Session duration and timeout limits
- Login and authentication configuration
- Loose state handling
- Banner configuration

### Network Configuration
- Network access rules (SSH and Portal access)
- Bridging configuration
- Bridge interfaces (inside / outside)
- Bypass configuration and supported states

### Time and Infrastructure Services
- NTP configuration and servers
- SMTP configuration (mail relay settings)
- SNMP configuration:
  - System settings
  - SNMP v2 users
  - SNMP v3 users (authentication and privacy configuration)

All API v6 data is rendered as **reference-style configuration views**.

---

## What API v6 Does Not Do

Enabling API v6 does **not**:
- Enable alerting
- Enable ingestion health checks
- Modify enforcement behavior
- Create scheduled searches
- Change existing API v3 dashboards
- Automatically enable inputs

API v6 access is strictly **read-only**.

---

## Enabling API v6

API v6 must be explicitly enabled in the app setup.

If your ThreatER tenant does **not** support API v6, leave this option disabled.

If you are unsure whether API v6 is available in your environment, contact ThreatER support before enabling.

---

## Operator Guidance

- Enable API v6 only if your ThreatER environment supports it
- API v6 is intended for administrators and advanced operators
- All configuration views sourced from API v6 are informational only

---

## Security and Compliance Notes

- API v6 usage is gated behind an explicit operator-controlled toggle
- No credentials or secrets are displayed in clear text
- Sensitive fields (such as passwords) are masked
- All API v6 calls are read-only

---

## Summary

- API v3: Enabled by default, core operational data
- API v6: Optional, configuration and settings visibility
- No destructive actions
- No enforcement changes
- No background automation without operator consent

---

## 📊 Dashboards

| Dashboard | Description |
|---------|-------------|
| 🌐 Overview | High-level ThreatER activity summary |
| 🚫 Blocked Threats | Malicious IPs & domains blocked |
| 📈 Trends | Threat activity and enforcement trends |
| 🌍 Geography | Threat distribution by region |
| 🧠 Intelligence | Threat intelligence insights |
| ⚙️ Operations | Ingestion health and API status |
| ❤️ Health | Platform and data freshness |

---

## 🧾 Sourcetypes

The app uses clear, API-aligned sourcetypes:

### Threat Intelligence
- `threater:ip`
- `threater:domain`
- `threater:indicator`
- `threater:reputation`

### Enforcement
- `threater:block_event`
- `threater:allow_event`
- `threater:policy`
- `threater:enforcement_status`

### Feeds
- `threater:feed`
- `threater:feed_update`
- `threater:feed_health`

### Telemetry
- `threater:observation`
- `threater:traffic_event`

### Platform
- `threater:user`
- `threater:role`
- `threater:tenant`
- `threater:health`

---

## 🧭 Navigation Structure

The ThreatER for Splunk App mirrors the ThreatER portal navigation and is organized to support operational workflows, from collection and enforcement to administration and reporting.

### 📊 Overview
- **Overview** — High-level platform and threat visibility

---

### 📥 Collect
- **Lists**
  - List Types
  - Allow Lists
  - Block Lists
  - Threat Lists
- **List Creation**
  - Threat Lists

- **List Details**
  - List Details

- **Plugins**
  - List Details

---

### 🛡️ Enforce
- **Enforcers**
  - Enforcers
  - Enforcer Status
  - Enforcer Health
- **Enforcement Configuration**
  - Policies
  - Enforcement Scope
  - Enforcement State
- **Networks**
  - List Networks
  - Network Details
  - Inbound / Outbound

    
- **Ports**
  - List Ports


---

### 🏢 Administration
- **Users**
  - Users
  - Users Filter
    
- **Subscriptions**
- **Command Logs**

---

### 🔎 IOC Search
- IOC Results Header
- Available Premium Intelligence
- Lists

---

### 📑 Reports
- Allowed / Blocked
- Reason Summary
- Category Summary
- Top 10 Countries
- Top 10 ASNs
- Top Countries by Threat Category
- ASNs by Threat Category
- **Report Builder**
  - Cover Sheet
  - Report Parameters
- **Scheduled Reports**
  - Reports
  - Editing Scheduled Reports
  - Disabling Scheduled Reports
  - Deleting Scheduled Reports
- Policy Enforcement

---

### 📦 Subscriptions
- Unexpected Blocks
- Block Events
- Mitigation Strategies
- Adjust Thresholds
- Enable threatER Allow List
- Add IP to Manual Allow List

---

### ⚙️ Settings
- **System**
  - Syslog
  - Access Control
  - Bridges
  - NTP
- **Device Configuration**
  - Interface Settings
  - DHCP Settings
  - WiFi Configuration
- **Enforce Software**
  - Update Now
  - Schedule Update
  - Cancel Scheduled Update
  - Revert to Previous Build

---

### ❓ Help
- **Support & Troubleshooting**

---

# ThreatER API v3 — Complete Endpoint List

Base URL:
https://portal.threater.com/api/v3/

---

## Collect

### Lists
- GET /lists
- GET /lists/{list_id}

### List Types
- GET /list-types

### Allow Lists
- GET /lists?type=allow

### Block Lists
- GET /lists?type=block

### Threat Lists
- GET /lists?type=threat

### List Entries
- GET /lists/{list_id}/entries


### List → Policy Association
- POST /lists/{list_id}/policies


---

## Collect → Plugins (External Lists)
- GET /plugins
- GET /plugins/{plugin_id}

---

## Enforce

### Enforcers
- GET /enforcers
- GET /enforcers/{enforcer_id}
- GET /enforcers/{enforcer_id}/status
- GET /enforcers/{enforcer_id}/health

### Enforcement Policies
- GET /policies
- GET /policies/{policy_id}


---

## Enforce → Networks
- GET /networks
- GET /networks/{network_id}
- POST /networks/{network_id}/duplicate

### Network IP Management
- GET /networks/{network_id}/ips
- POST /networks/{network_id}/ips


---

## Enforce → Ports
- GET /ports
- POST /ports
- PUT /ports/{port_id}
- DELETE /ports/{port_id}

---

## Administration

### Users
- GET /users
- GET /users/{user_id}
- POST /users
- PUT /users/{user_id}
- DELETE /users/{user_id}

### User Credentials & Roles
- PUT /users/{user_id}/password
- PUT /users/{user_id}/role
- PUT /users/{user_id}/status

---

## Administration → Subscriptions
- GET /subscriptions
- GET /subscriptions/{subscription_id}

---

## Command Logs
- GET /command-logs
- GET /command-logs/{command_id}

---

## IOC Search
- POST /ioc/search
- GET /ioc/results/{search_id}
- GET /ioc/premium-intelligence

---

## Reports

### Standard Reports
- GET /reports/allowed-blocked
- GET /reports/reason-summary
- GET /reports/category-summary
- GET /reports/top-countries
- GET /reports/top-asns
- GET /reports/countries-by-category
- GET /reports/asns-by-category

### Report Builder
- POST /reports/builder
- GET /reports/builder/{report_id}

### Scheduled Reports
- GET /reports/scheduled

---

## Subscriptions (Operational)
- GET /events/blocks
- GET /events/unexpected-blocks
- GET /mitigations

---

## Settings

### System
- GET /settings/syslog
- GET /settings/access-control
- GET /settings/bridges
- GET /settings/ntp

### Device Configuration
- GET /device/interfaces
- GET /device/dhcp
- GET /device/wifi


### Enforce Software
- POST /software/update
- POST /software/schedule-update
- POST /software/cancel-update
- POST /software/revert

---

## Help / Platform
- GET /health
- GET /status
- GET /version

## 📦 Requirements

- Splunk Enterprise or Splunk Cloud
- Python 3.x (Splunk bundled)
- ThreatER API v3 access
- Network access to `portal.threater.com`

---

## ✅ AppInspect Compliance

- Proper Splunk directory structure
- Inputs disabled by default
- No hardcoded credentials
- Secure credential storage
- Raw JSON ingestion
- MIT License

---

## 📚 References

- ThreatER API v3  
  https://portal.threater.com/api/v3/

- ThreatER Portal User Guide  
  https://support.threater.com/hc/en-us/articles/20834039012628-threatER-Portal-User-Guide-September-2025

- Splunk Documentation  
  https://docs.splunk.com

---

## 📜 License

MIT License

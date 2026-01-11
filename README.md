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
- API Keys
- Platform Health

All data is ingested as **raw JSON** to preserve evidence fidelity.

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

### 📁 General
- **

- ## 🧭 Navigation Structure

The ThreatER for Splunk App mirrors the ThreatER Portal navigation to provide a familiar and intuitive experience.

---

### 📁 Collect

#### Lists
- List Types
- Allow Lists
- Block Lists
- Threat Lists

#### List Creation
- Creating IP Threat Lists
- Creating Manual IP Allow Lists
- Creating Manual IP Block Lists
- Creating Manual Domain Lists

#### List Details
- View List Metadata
- Add Entries
- Remove Entries
- Apply to Policies
- Create New Policy During List Creation

---

### 🧱 Enforce

#### Enforcers
- Enforcer Inventory
- Enforcement Status
- Enforcement Health

#### Enforcement Configuration
- Policy Assignment
- Enforcement Scope
- Active / Inactive Enforcement

---

### ⚙️ Settings

#### System
- Syslog
- Access Control
- Bridges
- NTP

#### Device Configuration
- Interface Settings
- DHCP Settings
- WiFi Configuration

#### Enforce Software
- Update Now
- Schedule Update
- Cancel Scheduled Update
- Revert to Previous Build

---

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

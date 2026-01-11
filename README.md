# ThreatER for Splunk App

## Overview

ThreatER is a preemptive cybersecurity platform that builds trusted networks by automatically blocking known malicious traffic (IPs, domains) at the network edge, reducing noise for security teams and improving the efficiency of existing security tools (firewalls, SIEMs).

ThreatER acts as a foundational security layer by ingesting threat intelligence from multiple commercial, open-source, and government feeds and proactively filtering malicious activity **before it reaches internal systems**. It protects against both inbound and outbound threats with minimal latency, delivering an automated “set it and forget it” defense model.

The ThreatER for Splunk App brings this intelligence and enforcement visibility directly into Splunk, enabling security teams to **monitor, analyze, audit, and operationalize ThreatER activity** without relying solely on the ThreatER Portal UI.

---

## How ThreatER Works

- **Threat Intelligence Collection**  
  Aggregates data from commercial, open-source, and government threat feeds.

- **Proactive Blocking**  
  Blocks known malicious IPs and domains at line speed at the network layer (Layer 2/3), before traffic reaches firewalls or downstream controls.

- **Security Stack Integration**  
  Integrates with existing firewalls, EDR, SIEM, and security platforms to reduce alert noise and improve detection quality.

- **Automation**  
  Automatically enforces blocking policies based on threat intelligence, transforming reactive security into proactive defense.

---

## Key Benefits

- **Reduces Problem Space**  
  Eliminates known-bad traffic, dramatically reducing alert volume.

- **Enhances Existing Security Controls**  
  Feeds cleaner data into SIEMs, firewalls, and EDR platforms.

- **Real-Time and Scalable**  
  Enforces blocking instantly at scale without impacting network performance.

- **Builds Trusted Networks**  
  Establishes a baseline of trusted activity by removing known threats at the network edge.

---

## Splunk App Capabilities

The ThreatER for Splunk App provides centralized visibility and analytics across ThreatER data and operations.

### Core Capabilities

| Feature | Description |
|------|-------------|
| Threat Intelligence Visibility | View active threat indicators (IPs, domains, metadata) |
| Enforcement Monitoring | Track blocked inbound and outbound traffic |
| Policy & Automation Auditing | Monitor automated enforcement actions |
| Operational Telemetry | Analyze ingestion, enforcement, and system health |
| Historical Analysis | Retain raw threat data for investigations and audits |

---

## Dashboards

| Dashboard | Description |
|----------|-------------|
| Overview | High-level threat activity and enforcement summary |
| Threat Intelligence | Active IPs, domains, and indicators |
| Enforcement Activity | Blocked traffic trends and volumes |
| Policy & Automation | Policy execution and automation tracking |
| Operations | Platform health, ingestion, and processing metrics |
| Audit & Compliance | Historical actions and evidence preservation |

---

## Sourcetypes

The app ingests raw JSON events using the following sourcetypes:

- `threater:threat:intel`
- `threater:blocked:ip`
- `threater:blocked:domain`
- `threater:policy`
- `threater:automation`
- `threater:telemetry`
- `threater:health`
- `threater:audit`

---

## Navigation Structure

### General
- **Overview**

### Dashboards
- **Threat Summary**
- **Threat Intelligence**
- **Enforcement Activity**
- **Policy & Automation**
- **Operations**
- **Audit & Compliance**

### Manage
- **Threat Feeds**
- **Policies**
- **Automation Rules**

### Help
- **Support & Troubleshooting**

---

## Deployment

### Step 1: Install the App

1. Download the ThreatER for Splunk App package
2. In Splunk Web, go to **Apps → Manage Apps**
3. Select **Install app from file**
4. Upload the package
5. Restart Splunk if prompted

---

### Step 2: Configure the App

Navigate to **Apps → ThreatER → Setup**

#### API Configuration
- **ThreatER API Base URL**  
  `https://portal.threater.com/api/v3/`
- **API Token**
- **Request Timeout**
- **Verify SSL Certificates**

#### Proxy Configuration (Optional)
- Enable Proxy
- Proxy URL
- Proxy Username
- Proxy Password

---

### Step 3: Validate Configuration

- Test API connectivity
- Validate authentication
- Verify permissions
- Confirm data ingestion

---

### Step 4: Verify Data Collection

Run the following search in Splunk:

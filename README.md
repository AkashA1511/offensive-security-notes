# Offensive Security Knowledge Base

A structured, continuously maintained repository of offensive security methodologies, exploitation techniques, custom tooling, and vulnerability research — built for real-world penetration testing engagements and bug bounty hunting.

---

## Repository Structure

| Directory | Contents |
|-----------|----------|
| [Application-Security](./Application-Security) | Testing methodologies for Web, API & Mobile attack surfaces |
| [Playbooks](./Playbooks) | Step-by-step exploitation playbooks organized by vulnerability class |
| [Tools](./Tools) | Custom scripts & automation for recon, exploitation, and bypass techniques |
| [Labs](./Labs) | PortSwigger & CTF solutions with root cause analysis |
| [BugBounty](./BugBounty) | Bug bounty methodology, recon workflows & target analysis |
| [security_research](./security_research) | Original vulnerability research & disclosure documentation |
| [core_knowledge](./core_knowledge) | Foundational concepts & certification-aligned study material |
| [Resources](./Resources) | Curated references, checklists & tool configurations |

---

## Playbooks

Structured, repeatable testing playbooks for high-impact vulnerability classes:

| Playbook | Focus Area |
|----------|------------|
| [IDOR](./Playbooks/IDOR.md) | Insecure Direct Object Reference — enumeration, parameter tampering, horizontal/vertical escalation |
| [Business Logic](./Playbooks/Business_logic.md) | Workflow bypass, price manipulation, state abuse, privilege misuse |
| [Race Condition](./Playbooks/Race_Condition.md) | TOCTOU flaws, limit bypass via concurrency, single-packet attacks |
| [Rate Limit Bypass](./Playbooks/Rate_Limit.md) | Header rotation, endpoint abuse, distributed bypass techniques |

---

## Custom Tooling

| Tool | Stack | Description |
|------|-------|-------------|
| [recon.sh](./Tools/recon.sh) | Bash | Automated reconnaissance pipeline — subdomain enum, port scan, endpoint discovery |
| [rate-limit-bypass.py](./Tools/rate-limit-bypass.py) | Python | Automated rate limit testing with header rotation and response analysis |
| [frida-KTOR-bypass-script.js](./Tools/frida-KTOR-bypass-script.js) | Frida/JS | SSL pinning bypass for KTOR-based Android applications |

---

## Security Research

| Report | Target Area |
|--------|-------------|
| [OAuth2 v2 Token Endpoint Analysis](./security_research/report_3_oauth2_v2_token.md) | Token endpoint misconfiguration & abuse scenarios |

---


## Usage

This repository serves as an operational reference during penetration testing engagements and bug bounty programs. Each playbook is designed to be followed step-by-step against a target, with specific test cases, payloads, and expected outcomes documented.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

*For professional inquiries, reach out via [LinkedIn](https://www.linkedin.com/in/akasha151/).*

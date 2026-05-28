# Security Policy

**Maintainer:** Lutar, Stephen P. · ORCID [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173) · SZL Holdings

## Supported Versions

Security updates are issued for the latest minor release on the default branch. Prior versions are not supported.

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| older   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in vsp-otel, please report it privately so we can investigate and remediate before public disclosure.

**Preferred channel:** [security@szlholdings.com](mailto:security@szlholdings.com)

**Alternate channel:** [Open a private security advisory](https://github.com/szl-holdings/vsp-otel/security/advisories/new) on GitHub.

**Alternate email:** [stephen@szlholdings.com](mailto:stephen@szlholdings.com)

**Response SLA:** We acknowledge all vulnerability reports within **48 hours** and provide a triage assessment within **5 business days**.

Please include in your report:

- A clear description of the issue and its potential impact.
- Steps to reproduce, including any proof-of-concept code, requests, or payloads.
- The affected version, commit SHA, or environment.
- Your name and contact details for follow-up and credit (optional).

## Disclosure Process

1. We acknowledge receipt within **48 hours**.
2. We assess severity using CVSS v3.1 and triage within **5 business days**.
3. We work on a fix and coordinate a release window with you.
4. We publish a security advisory and credit the reporter at their request.

We ask that you give us a reasonable opportunity to investigate and patch before public disclosure. We do not pursue legal action against good-faith security research.

## Scope

In scope:

- OpenTelemetry exporter logic, SZL audit fiber mappings, and Λ-axis span definitions.
- Telemetry integrity, span provenance verification, and OTEL semantic-convention compliance.
- CI/CD integrity and supply-chain risks affecting build artifacts from this repository.

Out of scope:

- Third-party dependencies (please report upstream).
- Social engineering, physical attacks, or denial-of-service against shared infrastructure.
- Findings that require physical access to a user's device.

## Doctrine v6 Compliance

All security-relevant code is scanned by the canonical Doctrine v6 scanner at `szl-holdings/platform/tools/doctrine-v6-scan.js` before release.

## Hall of Thanks

Researchers who responsibly disclose vulnerabilities will be acknowledged here.

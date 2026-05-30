# vsp-otel — Λ-Signed OpenTelemetry Exporter

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-0B1F3A.svg?style=flat-square&logo=apache&logoColor=00D4FF)](https://www.apache.org/licenses/LICENSE-2.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20424995.svg)](https://doi.org/10.5281/zenodo.20424995)
[![CI](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml)
[![Tests](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml)
[![CodeQL](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml)
[![GHAS Code Security](https://img.shields.io/badge/GHAS-Code_Security-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/vsp-otel/security/code-scanning)
[![Secret Protection](https://img.shields.io/badge/GHAS-Secret_Protection-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/vsp-otel/security/secret-scanning)
[![SBOM](https://github.com/szl-holdings/vsp-otel/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/sbom.yml)
[![SLSA L1 (SBOM + DCO)](https://img.shields.io/badge/SLSA-L1_(SBOM_%2B_DCO)-0B1F3A.svg?style=flat-square)](https://slsa.dev/spec/v1.0/levels)
[![DCO](https://github.com/szl-holdings/vsp-otel/actions/workflows/dco.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/dco.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/vsp-otel/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/vsp-otel)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39.svg?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)


> **NOTE:** SLSA Level 1 (source + build provenance documented). L2/L3 require Sigstore + isolated builders (roadmap).

> OpenTelemetry exporter for SZL audit fibers — attaches Λ-axis receipts to OTel spans with W3C trace-id compatibility and OTLP compliance.  
> Doctrine v6 · DOI [10.5281/zenodo.20424995](https://doi.org/10.5281/zenodo.20424995)

**vsp-otel** is the OpenTelemetry exporter for SZL audit fibers. It attaches Λ-axis governance receipts to OTel spans, producing W3C trace-id compatible, OTLP-compliant telemetry with governance provenance embedded in every exported span.

---

## On Hugging Face

[SZLHOLDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — 27 Spaces · 31 datasets · 2 models

| Surface | Artifact |
|---------|----------|
| Live demo | [vsp-otel-emitter](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-emitter) · [vsp-otel-platform](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-platform) |
| Deep-dive | [vsp-otel-deep-dive](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-deep-dive) |
| Source mirror | [vsp-otel-source](https://huggingface.co/datasets/SZLHOLDINGS/vsp-otel-source) |

---

## What is real today

| Metric | Count | Verify |
|--------|-------|--------|
| CI status | GREEN | [Actions](https://github.com/szl-holdings/vsp-otel/actions) |
| Open PRs | 0 | clean |
| Lean declarations (org) | 217 | [lutar-lean](https://github.com/szl-holdings/lutar-lean) |
| Lean axioms (org) | 12 | [lutar-lean](https://github.com/szl-holdings/lutar-lean) |
| HF Spaces (org) | 27 | [SZLHOLDINGS HF org](https://huggingface.co/SZLHOLDINGS) |
| HF datasets (org) | 31 | [SZLHOLDINGS HF org](https://huggingface.co/SZLHOLDINGS) |
| Zenodo DOIs (org) | 7 | [Zenodo community](https://zenodo.org/communities/szl-holdings) |

---

## Architecture

```
SZL runtime span event
        │
        ▼
vsp-otel exporter
  ├── Λ-axis receipt attachment
  ├── W3C trace-id injection
  └── OTLP export
        │
        ▼
OpenTelemetry collector → observability backend
```

---

## Quick start

```bash
pnpm install && pnpm build
pnpm test
pnpm emit:sample   # emit a sample Λ-signed span
```

---

## License

[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) — SZL Holdings

---

## Citation

```
S. P. Lutar Jr., "vsp-otel — Λ-Signed OpenTelemetry Exporter,"
Zenodo, DOI 10.5281/zenodo.20424995, 2026.
```
ORCID: [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173)

---

## Security

See [SECURITY.md](./SECURITY.md) for responsible-disclosure policy.

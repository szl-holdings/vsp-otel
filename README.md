# vsp-otel — Lambda-Signed OpenTelemetry Exporter

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-0B1F3A.svg?style=flat-square&logo=apache&logoColor=00D4FF)](https://www.apache.org/licenses/LICENSE-2.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20424995.svg)](https://doi.org/10.5281/zenodo.20424995)
[![CI](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml)
[![Tests](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml)
[![CodeQL](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml)
[![SBOM](https://github.com/szl-holdings/vsp-otel/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/sbom.yml)
[![SLSA 3](https://github.com/szl-holdings/vsp-otel/actions/workflows/slsa.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/slsa.yml)
[![DCO](https://github.com/szl-holdings/vsp-otel/actions/workflows/dco.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/dco.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/vsp-otel/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/vsp-otel)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39.svg?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)

**vsp-otel** is the OpenTelemetry exporter for SZL audit fibers. It attaches Λ-axis receipts to
OTel spans, producing W3C trace-id compatible, OTLP-compliant telemetry with governance provenance
embedded in every exported span.

---

## On Hugging Face

This repository's live demos, dataset mirror, and org showcase live on the [SZLHOLDINGS Hugging Face org](https://huggingface.co/SZLHOLDINGS):

| Surface | Hugging Face artifact |
|---------|---------------------|
| **Live demo** | [vsp-otel-emitter](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-emitter) · [vsp-otel-platform](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-platform) |
| **Deep-dive showcase** | [vsp-otel-deep-dive](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-deep-dive) |
| **Source mirror** | [vsp-otel-source](https://huggingface.co/datasets/SZLHOLDINGS/vsp-otel-source) |
| **Org showcase** | [SZLHOLDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — 22 datasets · 19+ Spaces · 2 models |

## What is real today

All counts are grep-verifiable from this repository.

| Metric | Value | How to verify |
|--------|-------|---------------|
| TypeScript modules (runtime) | 3 | `find runtime/src -name "*.ts" | wc -l` |
| Total files | 36 | `find . -not -path './.git/*' -type f \| wc -l` |
| Λ-gate axes | 9 | `evaluateAxes` from `@szl/ouroboros-lambda-gate` |
| Export format | OTLP-compatible | W3C traceparent preserved end-to-end |
| Hash function | SHA-256 | `crypto.createHash('sha256')` in `exporter.ts` |
| Zenodo DOI | 10.5281/zenodo.20424995 | https://doi.org/10.5281/zenodo.20424995 |

---

## Architecture

```
OTel AGENT (any service)
        │ OtelSpan { spanId, traceId, name, startTime, endTime, attributes, status }
        ▼
exporter.ts
  ├─ SHA-256 receipt hash (span attributes + status)
  └─ W3C traceparent preserved
        │
        ▼
Λ-GATE (@szl/ouroboros-lambda-gate)
  ├─ evaluateAxes(9): moralGrounding · measurabilityHonesty · invariance ·
  │                   fidelity · coherence · minimality · verifiability ·
  │                   energy · allegiance
  └─ gateTransit() → { pass: boolean, lambda: number, axes: Axes }
        │
     FAIL → flagged, not forwarded (recorded in audit fiber)
     PASS ↓
        ▼
LambdaSignedSpan { span, receiptHash, lambda, axes, pass: true }
        │
        ▼
OTLP collector (any OpenTelemetry-compatible backend)
```

---

## How to use

```typescript
import { exportSpan } from './runtime/src/exporter'
import type { OtelSpan, Axes } from './runtime/src/exporter'

const span: OtelSpan = {
  spanId:     'abc123def456',
  traceId:    '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01',
  name:       'governance.decision.approve',
  startTime:  Date.now(),
  endTime:    Date.now() + 120,
  attributes: { 'decision.type': 'approve', 'agent.id': 'agent-7' },
  status:     'OK'
}

const axes: Axes = {
  moralGrounding: 0.95, measurabilityHonesty: 0.88, invariance: 0.90,
  fidelity: 0.92, coherence: 0.87, minimality: 0.91,
  verifiability: 0.89, energy: 0.94, allegiance: 0.93
}

const signed = await exportSpan(span, axes)
console.log(signed.pass, signed.receiptHash, signed.lambda)

// Run tests
cd runtime && pnpm test
```

---

## What this is NOT

- Not an APM product — no dashboards, alerting, or anomaly detection
- Not a drop-in OpenTelemetry Collector replacement — sits between an OTel agent and a downstream collector, adding governance annotation
- Not production-load tested — latency overhead of Λ-gate evaluation at scale is not yet characterized

---

## Sibling repositories

| Repo | Role |
|------|------|
| [a11oy-platform](https://huggingface.co/spaces/SZLHOLDINGS/a11oy-platform) | All a11oy action spans pass through vsp-otel for Λ-gate scoring |
| [amaru](https://github.com/szl-holdings/amaru) | Receipt chain — vsp-otel receipt hashes registered in amaru chain |
| [ouroboros](https://github.com/szl-holdings/ouroboros) | Provides `evaluateAxes` + `gateTransit` that vsp-otel calls |
| [sentra](https://github.com/szl-holdings/sentra) | Security spans from sentra gate evaluations flow through vsp-otel |

---

## How to cite

```bibtex
@software{lutar_vspotel_2025,
  author    = {Lutar, Stephen Paul JR},
  title     = {vsp-otel — Lambda-Signed OpenTelemetry Exporter},
  year      = {2025},
  doi       = {10.5281/zenodo.20424995},
  url       = {https://doi.org/10.5281/zenodo.20424995},
  license   = {Apache-2.0}
}
```

---

## References

- OpenTelemetry Protocol (OTLP) Specification (CNCF, 2024): https://opentelemetry.io/docs/specs/otlp/
- W3C Trace Context Level 1 (2021): https://www.w3.org/TR/trace-context/
- SZL Holdings Doctrine v6: https://doi.org/10.5281/zenodo.19944926

---

## License + DCO

Licensed under [Apache License 2.0](./LICENSE).

All commits require Developer Certificate of Origin sign-off (`git commit -s`).
SLSA provenance, SBOM generation, and CodeQL static analysis enforced on CI.

ORCID: [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173) · Doctrine v6 compliant

Signed-off-by: Stephen Paul Lutar JR <stephen@szlholdings.com>

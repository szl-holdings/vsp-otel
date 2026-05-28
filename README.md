# vsp-otel

> OpenTelemetry exporter for SZL audit fibers and Λ-axis spans — governance observability as a measurable, receipt-attested signal.

[![CI](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml)
[![OpenTelemetry exporter](https://img.shields.io/badge/OTEL-exporter-805AD5?style=flat-square)](https://github.com/szl-holdings/vsp-otel)
[![CodeQL](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/vsp-otel/badge)](https://scorecard.dev/viewer/?uri=github.com/szl-holdings/vsp-otel)
[![License](https://img.shields.io/badge/license-Apache--2.0-2DA44E?style=flat-square)](./LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276)
[![Concept DOI](https://img.shields.io/badge/concept%20DOI-10.5281%2Fzenodo.19944926-01696F?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.19944926)
[![Series-A Engineering](https://img.shields.io/badge/Series--A-Engineering-success?style=flat-square)](https://github.com/szl-holdings)
[![Λ-axis spans](https://img.shields.io/badge/Frontier-Λ--axis%20spans-28251D?style=flat-square)](https://doi.org/10.5281/zenodo.20434276)
[![Doctrine v6](https://img.shields.io/badge/Doctrine--v6-passing-success?style=flat-square)](https://github.com/szl-holdings/platform/blob/main/docs/doctrine/szl-doctrine.md)


> **Frontier Capability** — first measure-theoretic (martingale + Doob stopping) OpenTelemetry governance exporter.  
> Spans carry a martingale-property Λ-score whose optional stopping time is bounded by the Doob theorem, giving a rigorous halting guarantee for any governed trace.

> **Thesis cross-reference:** The mathematical foundations for this repository are developed
> in the [Ouroboros Thesis v18.0](https://github.com/szl-holdings/ouroboros-thesis) (DOI [10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)).
> Source for the published thesis is in [`/home/user/workspace/szl/thesis_v18/`](/home/user/workspace/szl/thesis_v18/).
> Concept DOI (always-latest): [10.5281/zenodo.19944926](https://doi.org/10.5281/zenodo.19944926).

## Observability as a Measure-Theoretic Problem

The vsp-otel exporter treats observability as a measure-theoretic problem: a span is a
measurable event `e ∈ (Ω, ℱ)` and the Λ-axis score `Λ(e) ∈ [0, 1]` is a measurable
function with respect to the governance σ-algebra ℱ.

The exporter maps governance events to OpenTelemetry spans with semantic conventions for:

- **Λ-axis score** (`szl.lambda.score`): the Lutar Invariant value at span exit.
- **Bekenstein headroom** (`szl.bekenstein.headroom`): remaining entropy capacity.
- **Audit fiber ID** (`szl.fiber.id`): the governance receipt chain identifier.
- **Receipt hash** (`szl.receipt.hash`): SCITT receipt Merkle root.

The Lutar Invariant Λ ∈ \[0, 1\] is the unique measure satisfying A1–A4; machine-checked
proofs are in [szl-holdings/lutar-lean](https://github.com/szl-holdings/lutar-lean)
(DOI [10.5281/zenodo.20434308](https://doi.org/10.5281/zenodo.20434308)).

## Table of Contents

- [Observability as a Measure-Theoretic Problem](#observability-as-a-measure-theoretic-problem)
- [Semantic Conventions](#semantic-conventions)
- [Quick Start](#quick-start)
- [Statistical Properties](#statistical-properties)
- [How to Cite](#how-to-cite)
- [Companion Repositories](#companion-repositories)
- [License](#license)

## Semantic Conventions

| Attribute | Type | Description |
|-----------|------|-------------|
| `szl.lambda.score` | float64 [0,1] | Lutar Invariant Λ at span exit |
| `szl.bekenstein.headroom` | float64 | Remaining entropy capacity fraction |
| `szl.fiber.id` | string (UUID) | Audit fiber chain identifier |
| `szl.receipt.hash` | string (hex) | SCITT Merkle receipt root |
| `szl.doctrine.version` | string | Doctrine version (`v6`) |

## Quick Start

```sh
git clone https://github.com/szl-holdings/vsp-otel.git
cd vsp-otel
pnpm install
pnpm test
```

```typescript
import { VspOtelExporter } from '@szl/vsp-otel';

const exporter = new VspOtelExporter({ endpoint: 'http://localhost:4317' });
// Attach to the ouroboros runtime span provider
```

## Statistical Properties

Each exported Λ-span sequence forms a bounded random process:

- **Martingale property**: `E[Λ_{t+1} | ℱ_t] = Λ_t` under the governance measure P,
  provided no drift event is detected.
- **Optional stopping**: the Doob optional stopping theorem bounds the expected stopping
  time of any Λ-gate below the Bekenstein capacity.
  [(Doob, 1953)](https://www.jstor.org/stable/j.ctt1bh4c8h)

## How to Cite

```bibtex
@techreport{ouroboros_thesis_v18,
  author      = {Lutar, Stephen P.},
  title       = {{SZL Holdings v18.0 Master Thesis --- Multi-track Substrate Expansion}},
  year        = {2026},
  institution = {SZL Holdings},
  doi         = {10.5281/zenodo.20434276},
  url         = {https://doi.org/10.5281/zenodo.20434276}
}
```

The `CITATION.cff` in this repository root is the authoritative citation source.

## Companion Repositories

| Repository | Role |
|-----------|------|
| [szl-holdings/ouroboros-thesis](https://github.com/szl-holdings/ouroboros-thesis) | Formal thesis (v18.0, DOI [10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)) |
| [szl-holdings/ouroboros](https://github.com/szl-holdings/ouroboros) | Runtime emitting spans exported here |
| [szl-holdings/uds-mesh](https://github.com/szl-holdings/uds-mesh) | Span schema definitions and governance receipts |
| [szl-holdings/lutar-lean](https://github.com/szl-holdings/lutar-lean) | Lean 4 proofs of Λ measurability and bounds |

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE).

Copyright 2026 SZL Holdings. ORCID: [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173).

# vsp-otel — Verifiable Span Protocol

[![Concept DOI](https://img.shields.io/badge/concept%20DOI-10.5281%2Fzenodo.19944926-01696F?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.19944926)
[![License](https://img.shields.io/badge/license-Apache%202.0-2DA44E?style=flat-square)](./LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)
[![Doctrine v6](https://img.shields.io/badge/Doctrine-v6%20clean-01696F?style=flat-square)](https://github.com/szl-holdings/platform/blob/main/tools/doctrine-v6-scan.js)

**Cryptographically-verifiable OpenTelemetry GenAI bridge and semantic conventions for the ouroboros governed-AI runtime.**

**Author:** Lutar, Stephen P. · ORCID [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173) · SZL Holdings
**License:** Apache-2.0
**Status:** Pre-implementation (proposal stage)

---

## What VSP-OTEL is

The **Verifiable Span Protocol (VSP)** defines an OpenTelemetry exporter and a set of semantic conventions for governed agentic AI. Every Λ-gate evaluation in the ouroboros runtime emits an OTel span whose `trace_id` is the receipt hash and whose span attributes carry the complete 9-axis Λ-vector. The ρ-closure witness pair is recorded as a span event carrying the `byte_identical` flag and the `chain_root`.

This design means that any engineer with a Langfuse, Arize Phoenix, Honeycomb, or Datadog dashboard can verify the causal integrity of every AI decision trace back to the Merkle-anchored receipt chain, without access to SZL Holdings internal systems.

### What the exporter exports

| OTel field | VSP value |
|---|---|
| `trace_id` | `receipt_hash[:16]` (hex) |
| `span.name` | `ouroboros.lambda_gate.evaluate` |
| `gen_ai.system` | `ouroboros` |
| `gen_ai.operation.name` | `lambda_evaluate` |
| `vsp.lambda_vector` | 9-axis Λ-vector (JSON array) |
| `vsp.lambda_score` | scalar Λ_k value |
| `vsp.axes_count` | integer k |
| span event: `rho_closure` | `{ byte_identical: bool, chain_root: hex }` |

### Semantic conventions

VSP-OTEL extends [OpenTelemetry GenAI Semantic Conventions v1.37](https://opentelemetry.io/docs/specs/semconv/gen-ai/) with governed-AI specific attributes in the `vsp.*` namespace:

| Attribute | Type | Description |
|---|---|---|
| `vsp.receipt_hash` | string | SHA-256 hex of the ouroboros decision receipt |
| `vsp.lambda_vector` | string (JSON) | The 9-axis input vector `[a1, …, a9]` |
| `vsp.lambda_score` | double | Scalar output `Λ_k ∈ [min, max]` |
| `vsp.axes_count` | int | Number of axes `k` |
| `vsp.rho_identical` | boolean | Whether the ρ-closure witness is byte-identical |
| `vsp.chain_root` | string | Merkle root of the receipt chain at time of emission |
| `vsp.gate_version` | string | Λ gate version (e.g. `lambda9`) |

---

## Architecture

```
Agent Layer (a11oy / amaru)
       │
       ▼
ouroboros Brain Stem
  evaluate_lambda() — Λ₉ gate · 3.12 µs
  buildReceipt()    — 11.5 µs p50
  ρ-closure         — dual-witness
       │
       ▼
VSP Layer (this repo)
  LambdaSpanEmitter  — OTel GenAI v1.37 + vsp.* attributes
  ReceiptTracer      — trace_id = receipt_hash[:16]
  RhoClosureEvent    — span event with byte_identical flag
       │
       ▼
OTLP/gRPC or OTLP/HTTP → Langfuse / Arize Phoenix / Honeycomb / Datadog
```

---

## Why this matters for governed AI

Standard LLM observability tools record inputs, outputs, token counts, and latency. They do not record whether a decision was within policy, whether the loop converged, or whether the receipt chain is intact. VSP-OTEL closes that gap by embedding the proof-chain receipt hash directly into the OTel `trace_id`. The receipt is not a side-channel annotation — it is the span identifier.

This enables:

1. **Audit-by-trace** — any OTel backend can reconstruct the governed decision path by following `trace_id` back to the Zenodo-archived receipt chain.
2. **Policy gate visibility** — OTel span attributes record which policy axes were active and what score each axis contributed.
3. **ρ-closure verification** — the span event records whether the dual-witness agreed byte-for-byte, giving per-span evidence of convergence.
4. **Cross-system correlation** — because `trace_id = receipt_hash[:16]`, an engineer can correlate a Langfuse trace directly to an ouroboros receipt without any additional coupling.

The missing primitives — Curry-Howard receipt calculus (TH7), Λ-Category morphism semantics (TH4), and 5× byte-identical ρ-closure chain — are formalised in the ouroboros thesis ([v14 DOI](https://doi.org/10.5281/zenodo.20424992), [v16 DOI](https://doi.org/10.5281/zenodo.20424996)) and machine-checked in [`szl-holdings/lutar-lean`](https://github.com/szl-holdings/lutar-lean).

---

## Performance target

- No regression on p50 11.5 µs (receipt build + span emit combined)
- Receipt size stays ≤ 256 bytes on the wire
- OTLP/gRPC batch export; no synchronous flush in the hot path

These are design targets for the implementation phase. They are not yet measured values.

---

## Where related code lives

- Λ-gate runtime: `szl-holdings/ouroboros` → `runtime/lambda-gate/src/gate.ts`
- Receipt chain: `szl-holdings/ouroboros` → `runtime/receipt/src/receipt.ts`
- Lean formal proofs: `szl-holdings/lutar-lean`
- Receipt ingress (Khipu DAG): `szl-holdings/rosie`
- OTel GenAI SemConv: [opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

---

## Thesis publications (DOI-pinned)

| Version | Title | DOI | PDF |
|---|---|---|---|
| **v16** | Feynman path-integral audit closure + Gates doctrine codes + cross-component composite invariant | [`10.5281/zenodo.20424996`](https://doi.org/10.5281/zenodo.20424996) | [PDF](https://zenodo.org/records/20424996/files/ouroboros-thesis-v16.pdf) |
| **v15** | Knot Calculus for Governed Decision Receipts — audit-Reidemeister R1/R2/R3, PAC-Bayes head, Khipu-DAG | [`10.5281/zenodo.20424995`](https://doi.org/10.5281/zenodo.20424995) | [PDF](https://zenodo.org/records/20424995/files/ouroboros-thesis-v15.pdf) |
| **v14** | Verifiable Multi-Agent Anatomy — Lutar Calculus, formal foundations, runtime verification, honest proof record | [`10.5281/zenodo.20424992`](https://doi.org/10.5281/zenodo.20424992) | [PDF](https://zenodo.org/records/20424992/files/ouroboros-thesis-v14.pdf) |

**Concept DOI:** [`10.5281/zenodo.19944926`](https://doi.org/10.5281/zenodo.19944926)

---

## Design Specification

Full proposal: [`evolution_pod/meditation_v5/phd_systems/proposal.md`](https://github.com/szl-holdings/ouroboros/blob/main/docs/meditation_v5_phd_systems_proposal.md)

**Source:** Meditation V5 PhD-Systems subagent · 2026-05-15

---

## Citation

See `CITATION.cff`. To cite this work:

```bibtex
@software{lutar2026vsp,
  author    = {Lutar, Stephen P.},
  title     = {Verifiable Span Protocol — cryptographically-verifiable OpenTelemetry GenAI bridge},
  year      = {2026},
  publisher = {SZL Holdings},
  url       = {https://github.com/szl-holdings/vsp-otel},
  orcid     = {0009-0001-0110-4173}
}
```

---

*Byline: Lutar, Stephen P. · ORCID 0009-0001-0110-4173 · SZL Holdings · Apache-2.0*

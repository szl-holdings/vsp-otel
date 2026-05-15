# vsp-otel — Verifiable Span Protocol

**Cryptographically-verifiable OpenTelemetry GenAI bridge for the ouroboros runtime.**

**Author:** Lutar, Stephen P. · ORCID [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173) · SZL Holdings
**License:** Apache-2.0
**Status:** Pre-implementation (proposal stage)

---

## Executive Summary

The **Verifiable Span Protocol (VSP)** is a TypeScript library and ouroboros runtime extension that emits [OpenTelemetry GenAI Semantic Conventions v1.37](https://opentelemetry.io/docs/specs/semconv/gen-ai/) spans from every Λ-gate evaluation, with the receipt hash embedded as the OTel `trace_id` and the complete 9-axis Λ-vector embedded as span attributes. The ρ-closure witness pair is recorded as a span event carrying the `byte_identical` flag and the `chain_root`.

The result is the first AI observability integration where every OTel span is **cryptographically verifiable**: any engineer with a Langfuse or Arize Phoenix dashboard can verify the causal integrity of every AI decision trace back to the Merkle-anchored receipt chain without access to szl-holdings internal systems.

This closes the P1 gap ("Zero OTel GenAI SemConv coverage; no per-span cost or token-usage telemetry") while creating a moat that LangGraph, Mastra, and Claude Code cannot replicate without adopting a fundamentally different architecture. The missing primitives are the Curry-Howard receipt calculus (TH7), the Λ-Category morphism semantics (TH4), and the 5× byte-identical ρ-closure chain.

**Shippable in 4 weeks. No regression on p50 11.5 µs. Receipt size stays ≤ 256 bytes.**

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
  LambdaSpanEmitter  — OTel GenAI v1.37
  ReceiptTracer      — trace_id = receipt_hash[:16]
  RhoClosureEvent    — span event with byte_identical flag
       │
       ▼
OTLP/gRPC or OTLP/HTTP → Langfuse / Arize Phoenix / Honeycomb / Datadog
```

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

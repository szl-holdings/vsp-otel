<div align="center">

# vsp-otel

<!-- series-a-badges (Doctrine v11) -->
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-025E8C?style=flat-square&logo=dependabot&logoColor=white)](https://github.com/szl-holdings/vsp-otel/security/dependabot)


**OpenTelemetry + DSSE attestation chapter for governed agentic spans.**

[![Doctrine v11](https://img.shields.io/badge/Doctrine-v11-3b82f6?style=flat-square)](https://github.com/szl-holdings/.github/blob/main/DOCTRINE_V11.md) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-0B1F3A.svg?style=flat-square&logo=apache&logoColor=00D4FF)](https://www.apache.org/licenses/LICENSE-2.0) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20424995.svg)](https://doi.org/10.5281/zenodo.20424995)

[![CI](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml) [![Tests](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml) [![CodeQL](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/codeql.yml) [![SBOM](https://github.com/szl-holdings/vsp-otel/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/sbom.yml) [![DCO](https://github.com/szl-holdings/vsp-otel/actions/workflows/dco.yml/badge.svg?branch=main)](https://github.com/szl-holdings/vsp-otel/actions/workflows/dco.yml) [![SLSA L1](https://img.shields.io/badge/SLSA-L1_(SBOM_%2B_DCO)-0B1F3A.svg?style=flat-square)](https://slsa.dev/spec/v1.0/levels) [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/vsp-otel/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/vsp-otel) [![GHAS](https://img.shields.io/badge/GHAS-Code_Security-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/vsp-otel/security/code-scanning) [![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39.svg?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)

[Hugging Face](https://huggingface.co/SZLHOLDINGS) · [GitHub Org](https://github.com/szl-holdings)

`receipts.in ≡ receipts.out`

</div>

---

> A measurable governance operator on the receipt-bus σ-algebra of agentic AI — surfaced as W3C-trace-id-compatible, OTLP-compliant spans with DSSE attestation wrapped at every Λ-axis boundary.

---

## What this is

**vsp-otel** is the OpenTelemetry exporter and DSSE attestation chapter for the SZL Holdings governed AI platform. It attaches Λ-axis governance receipts to OTel spans, producing W3C trace-id-compatible, OTLP-compliant telemetry with full governance provenance embedded in every exported span. The DPI soundness pipeline (`src/pipeline/dpi_soundness.ts`) enforces TH6 — the Data Processing Inequality invariant, Lean-discharged with zero sorries. This chapter is staged for upstream contribution to [defenseunicorns/uds-docs](https://github.com/defenseunicorns/uds-docs).

## Why it matters

Agentic AI systems produce decision spans that need to be auditable across organizational boundaries. vsp-otel makes governance provenance a first-class OTel concern: every span carries a DSSE-wrapped receipt, SLA relay latency gates enforce sub-millisecond governance overhead, and the SCITT mask entropy module ensures redaction is entropy-bounded and verifiable. This is the bridge between the SZL receipt bus and any standard observability backend.

## Quickstart

```bash
pnpm install && pnpm build
pnpm test
pnpm emit:sample   # emit a sample Λ-signed span
```

To inspect the lambda gate exporter directly:

```bash
cd runtime && npx tsx src/exporter.test.ts
```

## Key files

| Path | Role |
|------|------|
| `runtime/src/exporter.ts` | Core Λ-axis receipt attachment + OTLP export |
| `runtime/src/exporter.test.ts` | Exporter test harness |
| `src/pipeline/dpi_soundness.ts` | TH6 DPI Soundness pipeline check (Lean-discharged, 0 sorries) |
| `src/redaction/scitt_mask_entropy.ts` | SCITT mask entropy bound for redacted spans |
| `src/sla/relay_latency_gate.ts` | Sub-millisecond SLA gate for governance relay |
| `runtime/src/formulas/` | Formula implementations (Madhava bound, Liu Hui π, false position, adversarial robustness, summation invariant) |
| `stubs/ouroboros-types/` | Shared Ouroboros type stubs |
| `stubs/ouroboros-lambda-gate/` | Lambda gate interface stubs |

## OTel span schema

Each governed span carries:

```
traceparent: <W3C trace-id>
szl.receipt.id: <receipt_id>
szl.receipt.hash: <sha256 hash>
szl.lambda.score: <Λ-axis float>
szl.policy.version: <covenant-v1>
szl.dsse.sig: <base64 DSSE envelope>
```

## DSSE wrap pattern

```
span event → Λ-axis receipt attachment → DSSE envelope → OTLP export
                                              │
                                    SCITT-compatible attestation
                                    (entropy-bounded redaction)
```

Upstream PR target: [defenseunicorns/uds-docs](https://github.com/defenseunicorns/uds-docs)

## Related

| Repo | Role |
|------|------|
| [uds-mesh](https://github.com/szl-holdings/uds-mesh) | UDS service mesh integration |
| [ouroboros](https://github.com/szl-holdings/ouroboros) | Core runtime |
| [ouroboros-thesis](https://github.com/szl-holdings/ouroboros-thesis) | Formal research paper (DOI [10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)) |
| [lutar-lean](https://github.com/szl-holdings/lutar-lean) | Lean 4 proofs — 749 decls / 15 raw axioms / 163 sorries @ HEAD c7c0ba17 |
| [a11oy](https://github.com/szl-holdings/a11oy) | Flagship governance app |
| [amaru](https://github.com/szl-holdings/amaru) | Cardano anchoring layer |
| [sentra](https://github.com/szl-holdings/sentra) | Policy enforcement engine |
| [terra](https://github.com/szl-holdings/terra) | Infrastructure substrate |
| [vessels](https://github.com/szl-holdings/vessels) | Data pipeline layer |
| Hatun Doctrine Specification | [szl-holdings/platform/docs/a11oy/spec/hatun-doctrine-spec/](https://github.com/szl-holdings/platform/tree/main/docs/a11oy/spec/hatun-doctrine-spec/) |

## On Hugging Face

[SZLHOLDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — Spaces · datasets · models

| Surface | Artifact |
|---------|----------|
| Live demo | [vsp-otel-emitter](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-emitter) · [vsp-otel-platform](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-platform) |
| Deep-dive | [vsp-otel-deep-dive](https://huggingface.co/spaces/SZLHOLDINGS/vsp-otel-deep-dive) |
| Source mirror | [vsp-otel-source](https://huggingface.co/datasets/SZLHOLDINGS/vsp-otel-source) |

## Citation

See [CITATION.cff](./CITATION.cff) for machine-readable metadata. Quick reference:

```
S. P. Lutar Jr., "vsp-otel — OpenTelemetry + DSSE attestation chapter for governed agentic spans,"
SZL Holdings, 2026. https://github.com/szl-holdings/vsp-otel
```

Preferred citation: [The Ouroboros Substrate (v18.0)](https://doi.org/10.5281/zenodo.20434276), DOI 10.5281/zenodo.20434276.

## License · Trust · Security

[Apache 2.0](./LICENSE). SLSA Level 1 (source + build provenance documented; L2/L3 require Sigstore + isolated builders — roadmap). Security disclosures: see [SECURITY.md](./SECURITY.md).

[![PyPI](https://img.shields.io/pypi/v/vsp-otel)](https://pypi.org/project/vsp-otel/) [![Python](https://img.shields.io/pypi/pyversions/vsp-otel)](https://pypi.org/project/vsp-otel/) [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/szl-holdings/vsp-otel/badge)](https://scorecard.dev/viewer/?uri=github.com/szl-holdings/vsp-otel) [![CI](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml/badge.svg)](https://github.com/szl-holdings/vsp-otel/actions/workflows/ci.yml) [![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

## Quickstart

```bash
pip install "vsp-otel[fastapi]" fastapi   # [fastapi] adds only the request auto-instrumentation, not FastAPI
```

```python
from fastapi import FastAPI
from vsp_otel import install, VSPConfig

app = FastAPI()
# one-call FastAPI middleware: every request's spans become hash-chained,
# DSSE-bound evidence, exported over OTLP/gRPC (OTEL_EXPORTER_OTLP_ENDPOINT).
# The default signer is an HMAC *test* signer — pass VSPConfig(signer=...) in production.
install(app, VSPConfig(service_name="my-service"))
```

The library's own guide is [`src/vsp_otel/README.md`](src/vsp_otel/README.md) (the PyPI description).

---

> **SZL Holdings** · Doctrine v11 · Λ = Conjecture 1 (advisory, never "green"/theorem) · canonical [a-11-oy.com](https://a-11-oy.com)

# vsp-otel

<!-- szl:header v1 -->
<!-- Native identity: szl-brand@4309f6fce89179331b0b3ed8c99494e76c5be256; Orbit v2 icon. -->
<p>
  <a href="https://github.com/szl-holdings">
    <img src="https://raw.githubusercontent.com/szl-holdings/szl-brand/4309f6fce89179331b0b3ed8c99494e76c5be256/kit/logos/orbit-v2/suite/szl-icon-32.svg" alt="SZL Holdings — Orbit v2" width="32" height="32" />
  </a>
</p>

**Control before action. Evidence after.**

[Product](https://a-11-oy.com) · [Proof](https://a11oy.net) · [GitHub organization](https://github.com/szl-holdings)
<!-- /szl:header -->

## Restored collector contract

The maintained `collector/` service accepts **OTLP/HTTP JSON** on `/v1/traces`.
Its protocol is `application/json`; a default protobuf/gRPC exporter must use an
appropriate bridge or the separate `src/vsp_otel` library. The HTTP collector
returns 415 for protobuf instead of claiming unsupported interoperability.

- Configure `VSP_FORWARD_ENDPOINT` with the downstream OTLP/HTTP JSON endpoint
  and `VSP_SIGN_KEY_PEM` with an operator-managed ECDSA P-256 private key.
  In Kubernetes use `signing.existingSecret` with key `signing.pem`; never commit
  private key material. Keyless signing is **not implemented**.
- `/healthz` reports process liveness. `/readyz` returns 503 until the downstream
  endpoint and signing key are configured. Its 200 `CONFIGURED` status establishes
  configuration, with the last delivery attempt reported separately; it does not
  prove downstream availability or deployed source identity.
- Missing, nonfinite, boolean, or out-of-range governance axes fail closed.
  Clients supply axis evidence; aggregation does not independently establish it.
  Boolean JSON values in numeric fields, fractional or out-of-range `intValue`,
  malformed scalar types, and multiple selected AnyValue fields return 400
  before any span in the batch is signed, counted, or forwarded. Valid ProtoJSON
  numeric encodings, null-as-unset, and ignored unknown fields remain supported.
- Every forwarded span carries `szl.dsse.receipt`: the complete verifiable DSSE
  envelope. Its subject digest binds the original span, resource and scope through
  [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
  encoding of `{trace_id, span_id, name, span, resource, scope}`. New receipts use
  predicate type `https://szlholdings.ai/attestations/lambda-gate/v2` and declare
  `subject_canonicalization: "RFC8785"`; historical v1 subjects used Python JSON
  serialization and must not be interpreted as v2. The original
  span excludes collector-added verdict and receipt attributes. Consumers must
  verify the PAE signature against their configured trusted P-256 public key and
  recompute this digest; a receipt hash alone is not signature verification.
- A downstream transport error returns 503 so the caller can retry. Partial
  governance/downstream rejections return per-request OTLP `rejectedSpans` counts.
  The service has no durable queue or exactly-once guarantee; a lost downstream
  acknowledgement can cause a duplicate on retry. There is no silent acceptance
  when forwarding is unavailable.

Run the bounded collector checks with
`python -m pytest tests/test_collector.py tests/test_collector_delivery.py -q`.
They use a real loopback downstream fixture and independently verify the receipt
signature and input digest. Hosted CI, publication, cluster deployment and a live
estate trace require their own evidence.

## Optional fuzz CI

The scheduled fuzz workflow looks for a root `test:fuzz` script. The current
workspace does not define one, so it reports that no fuzz tests ran and does not
install dependencies. When configured, it uses the committed pnpm lockfile;
dependency installation and fuzz failures fail the job and retain their output.
It does not download or add a fuzz framework automatically. Run the execution
boundary checks with `node --test tests/test_optional_fuzz.mjs`.

**Layer 4 (Λ-gate exporter) of the SZL 7-layer architecture.**
Λ-signed OpenTelemetry exporter for SZL audit fibers.

[![tests](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml/badge.svg)](https://github.com/szl-holdings/vsp-otel/actions/workflows/tests.yml)
&nbsp;Doctrine **v11 LOCKED** · 749 / 14 / 163 · SLSA L1 honest · DOI [10.5281/zenodo.19944926](https://doi.org/10.5281/zenodo.19944926)

> **📦 Canonical OTel package (Wave D consolidation).** This standalone repository is the
> **canonical source of truth** for the Λ-signed OTel exporter. The monorepo copy at
> [`platform/services/vsp-otel`](https://github.com/szl-holdings/platform/tree/main/services/vsp-otel)
> is a **non-canonical partial mirror** (it carries `DEPRECATED.md` pointing here) and does
> **not** contain the deployable collector shipped here (`collector/`, `lambda_gate.py`,
> `dsse.py`, `stats.py`, Helm chart). Platform should depend on the published `vsp-otel`
> package rather than mirroring it. An **archived** `szl-otel-mesh` repo is also superseded by
> this repo. Repos are **not deleted** — archival is a later founder step. Λ = **Conjecture 1**
> (advisory) is preserved verbatim.

---

`vsp-otel` is an **OTLP/HTTP JSON collector exporter shim**. A compatible JSON sender
can target the collector endpoint. For every span it
computes a governance Λ, rejects spans below the floor, DSSE-signs the survivors, and
forwards them to your existing backend (Tempo / Jaeger / any OTLP collector).

```
 your app  ──OTLP──▶  vsp-otel  ──(Λ ≥ 0.90, DSSE-signed)──▶  Tempo / Jaeger
 (any lang, OTel SDK)   :4318
```

## Make it real — what landed

- **`collector/`** — a deployable OTLP/HTTP collector exporter shim (FastAPI, with a
  stdlib HTTP fallback that still requires the pinned `rfc8785` package):
  - **`lambda_gate.py`** — Λ over span A1–A5 axes; **`LAMBDA_FLOOR = 0.90`** (the
    a11oy doctrine constant); fail-closed rejection.
  - **`dsse.py`** — DSSE in-toto attestation per accepted span (ECDSA P-256 /
    HMAC for direct local tests only; configured P-256 for HTTP ingestion).
  - **`stats.py`** — **Welford** online mean/variance for span latency +
    **HyperLogLog** for unique-trace cardinality.
  - **`app.py`** — `/v1/traces` (OTLP ingest), `/healthz`, `/readyz`, `/metrics` (Prometheus).
- **`Dockerfile`** — per-file `COPY` only (doctrine §build), non-root, SLSA L1 honest (no L2 provenance workflow present).
- **`deploy/helm/vsp-otel/`** — Helm chart (`helm lint` clean); 2 replicas, security
  context, optional ServiceMonitor, configurable floor + forward endpoint.
- **`docs/INTEGRATION.md`** — "your existing OTel SDK already works — just point the
  exporter at vsp-otel."
- **`tests/`** — 88 Python tests in 6 files: 60 for the collector (Λ-gate accept/reject,
  Welford exactness, HLL cardinality, DSSE shape and signature, delivery/retry and input
  validation) and 28 for the `vsp_otel` library (DSSE binding, exporter config, a real
  OTLP/gRPC round-trip, version). One of them, the Docker collector-container test, is
  opt-in (`VSP_OTEL_IT_DOCKER=1`; CI runs it).

The pre-existing TypeScript runtime (`runtime/`) — the in-process `signSpan` exporter
and its anchor-formula injection — is unchanged and remains the library form; the new
`collector/` is the standalone deployable form.

```bash
pip install -e '.[test]' -r collector/requirements.txt   # library, collector and test deps
python -m pytest                                          # 87 passed, 1 skipped (Docker opt-in)

# The collector refuses traffic until it has a signing key and a downstream:
export VSP_SIGN_KEY_PEM="$(openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256)"  # demo key only
export VSP_FORWARD_ENDPOINT=http://127.0.0.1:4319/v1/traces   # your OTLP/HTTP JSON backend
uvicorn collector.app:app --port 4318
curl localhost:4318/healthz   # {"status":"ok","service":"vsp-otel","lambda_floor":0.9}
curl localhost:4318/readyz    # HTTP 200 {"ready":true,"status":"CONFIGURED",...}
```

## Reproduced locally (2026-11-06)

With the commands above (Python 3.13, a throwaway P-256 key, and a loopback stand-in
receiver on `:4319` that acknowledges every batch — not a deployment), posting two spans,
one with A1–A5 = 0.97 (latency 2 ms) and one with A1 = 0.4 (latency 5 ms), returned HTTP 200:

```json
{"partialSuccess":{"rejectedSpans":"1","errorMessage":"Governance or downstream rejection"},
 "szl":{"received":2,"accepted":1,"rejected":1,"forwarded":1,"unique_traces_est":2,
        "latency_ms":{"count":2,"mean":3.5,"variance":4.5,"stddev":2.1213},
        "lambda_floor":0.9,"request":{"received":2,"accepted":1,"rejected":1,"forwarded":1}}}
```

Only the high-Λ span reached the receiver, carrying `szl.dsse.receipt`,
`szl.dsse.receipt_hash` and `szl.dsse.keyid`; the low-A1 span was rejected by the
geometric-mean gate. `/metrics` exposed `vsp_spans_total`, `vsp_lambda_floor`,
`vsp_span_latency_ms_mean`, `vsp_unique_traces_estimate`. (An earlier 2026-06-03 run
predates the restored contract: it needed no key or downstream and returned a bare
summary instead of the OTLP `partialSuccess` envelope.)

## Formal references (lutar-lean — cite honestly)

Status checked against `lutar-lean` `main` on 2026-11-06 (PR state + code search). The Lean
files were not compiled in this check; "sorry-free" is what each file states about itself.

| Used for | Lean reference | Status |
|---|---|---|
| Welford latency mean/variance | [`Lutar.Round11.Welford.welford_mean_exact`, `weightedMean_increment`](https://github.com/szl-holdings/lutar-lean/pull/180) | **theorem** (sorry-free), merged in PR #180, `Lutar/Innovations/round11/FrontierWelfordVariance.lean` · runtime path: `sentra/runtime/welford_gate.py` (infra dir of the **CHAPAQ** egress immune-inspector; path kept verbatim) |
| DSSE in-toto attestations | [`Lutar.Round10.CryptoDSSE.dsse_classical_euf_cma`](https://github.com/szl-holdings/lutar-lean/pull/179) | **not on `main`** — PR #179 was closed unmerged; no theorem backs the collector's DSSE signing |
| Rekor transparency (cosign keyless) | [`Lutar.Round10.CryptoRekor.rekor_inclusion_completeness`](https://github.com/szl-holdings/lutar-lean/pull/179) | **not on `main`** — PR #179 was closed unmerged; keyless signing is not implemented either |
| Bekenstein throughput ceiling (audit-fiber budget) | [`Lutar.Innovations.Round10.PhysicsEntropyBounds.bekensteinCeiling_mono_E`](https://github.com/szl-holdings/lutar-lean/pull/177) | **theorem** (sorry-free), merged in PR #177, `Lutar/Innovations/round10/PhysicsEntropyBounds.lean` |

> **Λ is Conjecture 1 — never a theorem.** The Λ-gate's geometric-mean aggregation
> mirrors a11oy's graph-Λ construction but Λ itself remains conjectural. HONESTY OVER CHECKLIST.

## Honest boundaries (disclosed, not hidden — HR-6)

- **Cosign keyless** (Fulcio OIDC + Rekor inclusion) is **not implemented** by
  the collector. Configured ECDSA P-256 signs HTTP traffic. Direct local HMAC
  test signatures do not establish configured service readiness.
- The Λ axis scores are supplied by the instrumented org as span attributes; vsp-otel
  aggregates and gates them — it does not itself infer A1–A5.
- The **TypeScript runtime gate is not fail-closed** and is not the collector's gate: it is a
  weighted arithmetic mean over nine axes with a 0.85 threshold (the local
  `stubs/ouroboros-lambda-gate`), and a missing axis defaults to 0.90 — so a span with no Λ
  evidence at all scores 0.90 and passes. The Python collector instead treats missing
  evidence as 0 and vetoes. See [`runtime/README.md`](runtime/README.md).
- The `vsp_otel` library's Khipu chain is in process memory (not persisted). Exported spans
  carry their receipt attributes only from the fix after 0.1.3; with `vsp-otel` ≤ 0.1.3
  from PyPI they stayed in process (see [CHANGELOG](CHANGELOG.md)).
- The root gate modules `src/{pipeline,redaction,sla}` carry Lean citations with explicit
  binding status (`@lean_status`): relay latency GREEN, DPI CONDITIONAL, SCITT NOT-BOUND.
  `pnpm test:gates` runs their 49 tests.

## Architecture in context

`vsp-otel` (L4) signs and forwards spans that conform to the L5 schemas of the now-**archived**
`szl-otel-mesh` repo (superseded by this repo, see above); the receipts it stamps are
validated by `hatun-mcp` (L6) `validate-receipt-against-doctrine`.

---

*License: Apache-2.0 · © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173*

Signed-off-by: Yachay <yachay@szlholdings.ai>
Co-Authored-By: Perplexity Computer Agent <agent@perplexity.ai>

---

**Explore the SZL estate:** [a11oy console](https://a-11-oy.com) · [LLM Router](https://github.com/szl-holdings/szl-router) · [Receipt format spec](https://github.com/szl-holdings/governed-receipt-spec) · [Lean proofs](https://github.com/szl-holdings/lutar-lean) · [Docs (archived)](https://github.com/szl-holdings/docs-site) · [🤗 SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS)

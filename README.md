> **SZL Holdings** · Doctrine v11 · Λ = Conjecture 1 (advisory, never "green"/theorem) · canonical [a-11-oy.com](https://a-11-oy.com)

# vsp-otel

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
- Every forwarded span carries `szl.dsse.receipt`: the complete verifiable DSSE
  envelope. Its subject digest binds the original span, resource and scope through
  canonical JSON of `{trace_id, span_id, name, span, resource, scope}`. The original
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
  zero-dependency stdlib fallback):
  - **`lambda_gate.py`** — Λ over span A1–A5 axes; **`LAMBDA_FLOOR = 0.90`** (the
    a11oy doctrine constant); fail-closed rejection.
  - **`dsse.py`** — DSSE in-toto attestation per accepted span (ECDSA P-256 /
    HMAC for direct local tests only; configured P-256 for HTTP ingestion).
  - **`stats.py`** — **Welford** online mean/variance for span latency +
    **HyperLogLog** for unique-trace cardinality.
  - **`app.py`** — `/v1/traces` (OTLP ingest), `/healthz`, `/metrics` (Prometheus).
- **`Dockerfile`** — per-file `COPY` only (doctrine §build), non-root, SLSA L1 honest (no L2 provenance workflow present).
- **`deploy/helm/vsp-otel/`** — Helm chart (`helm lint` clean); 2 replicas, security
  context, optional ServiceMonitor, configurable floor + forward endpoint.
- **`docs/INTEGRATION.md`** — "your existing OTel SDK already works — just point the
  exporter at vsp-otel."
- **`tests/`** — 9 tests: Λ-gate accept/reject, Welford exactness, HLL cardinality,
  DSSE shape, full OTLP pipeline. All passing.

The pre-existing TypeScript runtime (`runtime/`) — the in-process `signSpan` exporter
and its anchor-formula injection — is unchanged and remains the library form; the new
`collector/` is the standalone deployable form.

```bash
pip install -r collector/requirements.txt
pytest tests/ -v                                  # 9 passed
uvicorn collector.app:app --port 4318             # run the shim
curl localhost:4318/healthz                        # {"status":"ok","lambda_floor":0.9}
```

## Verified live (make-real strike, 2026-06-03)

Posting two spans (one with A1–A5 = 0.97, one with A1 = 0.4) to a running instance:

```json
{"received":2,"accepted":1,"rejected":1,"lambda_floor":0.9,
 "unique_traces_est":2,"latency_ms":{"count":2,"mean":3.5,"variance":4.5,"stddev":2.12}}
```

The high-Λ span passed and was DSSE-signed; the low-A1 span was rejected by the
geometric-mean gate. `/metrics` exposed `vsp_spans_total`, `vsp_lambda_floor`,
`vsp_span_latency_ms_mean`, `vsp_unique_traces_estimate`.

## Formal references (lutar-lean — all in OPEN PRs, cite honestly)

| Used for | Lean reference | Status |
|---|---|---|
| Welford latency mean/variance | [`Lutar.Round11.Welford.welford_mean_exact`, `weightedMean_increment`](https://github.com/szl-holdings/lutar-lean/pull/180) | **theorem** (sorry-free), PR #180 · runtime path: `sentra/runtime/welford_gate.py` (infra dir of the **CHAPAQ** egress immune-inspector; path kept verbatim) |
| DSSE in-toto attestations | [`Lutar.Round10.CryptoDSSE.dsse_classical_euf_cma`](https://github.com/szl-holdings/lutar-lean/pull/179) | conditional EUF-CMA **theorem** (0 real sorry), PR #179 |
| Rekor transparency (cosign keyless) | [`Lutar.Round10.CryptoRekor.rekor_inclusion_completeness`](https://github.com/szl-holdings/lutar-lean/pull/179) | completeness **theorem**; soundness is an honest tagged `sorry` (Conjecture 1), PR #179 |
| Bekenstein throughput ceiling (audit-fiber budget) | [`Lutar.Round10...bekensteinCeiling_mono_E`](https://github.com/szl-holdings/lutar-lean/pull/177) | **theorem** (0 real sorry), PR #177 |

> **Λ is Conjecture 1 — never a theorem.** Cited PRs are open on `lutar-lean`. The
> Λ-gate's geometric-mean aggregation mirrors a11oy's graph-Λ construction but Λ
> itself remains conjectural. HONESTY OVER CHECKLIST.

## Honest boundaries (disclosed, not hidden — HR-6)

- **Cosign keyless** (Fulcio OIDC + Rekor inclusion) is **not implemented** by
  the collector. Configured ECDSA P-256 signs HTTP traffic. Direct local HMAC
  test signatures do not establish configured service readiness.
- The Λ axis scores are supplied by the instrumented org as span attributes; vsp-otel
  aggregates and gates them — it does not itself infer A1–A5.

## Architecture in context

`vsp-otel` (L4) signs and forwards spans that conform to the `szl-otel-mesh` (L5) schemas;
the receipts it stamps are validated by `hatun-mcp` (L6) `validate-receipt-against-doctrine`.

---

*License: Apache-2.0 · © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173*

Signed-off-by: Yachay <yachay@szlholdings.ai>
Co-Authored-By: Perplexity Computer Agent <agent@perplexity.ai>

---

**Explore the SZL estate:** [a11oy console](https://a-11-oy.com) · [LLM Router](https://github.com/szl-holdings/szl-router) · [Receipt format spec](https://github.com/szl-holdings/governed-receipt-spec) · [Lean proofs](https://github.com/szl-holdings/lutar-lean) · [Docs](https://github.com/szl-holdings/docs-site) · [🤗 SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS)

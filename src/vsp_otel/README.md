# vsp-otel — Python operational layer (`vsp_otel`)

**Verifiable Span Provenance via OpenTelemetry.** This is the *operational* OTel
layer for the SZL mesh. It closes the honest gap left by the in-process TypeScript
exporter: organs could Λ-sign spans **in-process**, but there was **no real OTLP
wire export and no cross-pod broker**. `vsp_otel` ships:

- a **real OTLP/gRPC span exporter** (`opentelemetry-exporter-otlp-proto-grpc`) wired to an OpenTelemetry Collector,
- a **DSSE-aware span processor** that binds every span into the **Khipu** receipt chain. Each *exported* span carries `szl.mesh.receipt_hash`, `szl.mesh.khipu_index`, `szl.mesh.khipu_prev` and `szl.mesh.dsse_payload_type` (asserted on the OTLP/gRPC wire by `tests/test_integration.py`), plus `szl.mesh.rekor_log_index` only when a transparency-log sink is configured,
- a **drop-in middleware** (`vsp_otel.middleware.install(app)`) any organ imports,
- a **cross-pod collector config** (`deploy/otel-collector-config.yaml`) that receives from N organs and exports to Jaeger + Tempo + a SZL custom Khipu exporter.

> This file is the PyPI description of the `vsp_otel` library (`src/vsp_otel/`).
> The repository root `README.md` documents the deployable OTLP/HTTP collector
> (`collector/`), its Helm chart, and the TypeScript runtime.

## Quick start

```bash
pip install -e ".[test]"        # editable install + test extras (Python 3.10-3.14 in CI)
pytest -q                        # runs the suite incl. a real in-process OTLP/gRPC round-trip
```

In an organ's `serve.py`:

```python
import vsp_otel.middleware
status = vsp_otel.middleware.install(app)   # FastAPI/ASGI app
print(status.as_dict())                      # honest report of what was wired
```

Point organs at the collector via the standard env var:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

## Architecture

```
 organ(s) ──OTLP/gRPC──▶ OTel Collector ──▶ Jaeger (UI)
   │  DSSEKhipuSpanProcessor              ├▶ Tempo (store)
   │  (receipt_hash, DSSE envelope,       └▶ SZL Khipu exporter (DSSE receipts)
   │   Khipu hash-chain, rekor index)
   └─ BatchSpanProcessor → VSPSpanExporter (Welford fan-out variance)
```

Register `DSSEKhipuSpanProcessor` **before** the export processor (as `install()`
does): an SDK hands `on_end` an immutable span, and the processor attaches the
receipt attributes to that same span object before the exporter receives it.
The **DSSE v1 PAE** contract is documented in `vsp_otel/dsse_processor.py`. (An
`ARCH.md` spec referenced by earlier revisions is not published in this repository.)

## Formula tie-ins (honest)

- **Welford** online variance — `exporter.Welford` tracks the variance of **trace fan-out** (spans per export batch) without retaining samples. Live and tested.
- **PAC-Bayes confidence bound** on aggregated span coverage — *roadmap only*: no code in this package computes the bound or emits coverage counts.
- **Holevo bound** on a quantum-resistant channel — *roadmap/honest gap*: documented as the capacity ceiling for a future PQ-encrypted OTLP channel; **not** implemented in code.

## Honest gaps (read before claiming anything)

1. **Signer.** The default DSSE signer is a deterministic **HMAC test signer** so the chain is testable offline. It is **NOT** a cosign/ECDSA signature, and unless `VSP_OTEL_HMAC_KEY` is set its key is the public string `vsp-otel-dev-key`, so its signatures prove nothing about who produced a span. Production must inject a real signer via `VSPConfig(signer=...)` (the mesh's `szl_dsse` provides one). When no production key is present we keep an honest HMAC marker — we never claim a cosign signature we did not make.
2. **Rekor inclusion.** `szl.mesh.rekor_log_index` is stamped **only** when a `rekor_submit` callable is configured. Absent that, the attribute is **omitted** — we never fabricate a transparency-log index.
3. **Custom Khipu collector exporter.** The collector pipeline shape is real, but the `szl/khipu` custom exporter requires an `ocb`-built binary; until published, route to the `debug` exporter (the config ships commented + a working `debug` fallback).
4. **Docker integration test is opt-in.** `tests/test_integration.py` does a **real in-process OTLP/gRPC round-trip by default** (no Docker). The real-collector-**container** path is gated behind `VSP_OTEL_IT_DOCKER=1` and runs in CI (GitHub Actions has Docker).
5. **PAC-Bayes / Holevo** are not computed in code (see above).
6. **Receipt encoding.** The receipt digest is SHA-256 over Python `json.dumps(sort_keys=True, separators=(",", ":"))` of `{name, trace_id, span_id, attributes}` (minus the provenance attributes) — not RFC 8785, unlike the collector's v2 subjects. Verifiers in other languages must reproduce that encoding.
7. **In-memory chain.** `KhipuChain` lives in process memory: it is not persisted, does not survive restarts, and grows with every bound span. `bind_failures` / `stamp_failures` on the processor (and on `/api/vsp/provenance`) count spans that got no receipt or were exported without one.

## Layout

```
src/vsp_otel/__init__.py         # public API, doctrine constants, attr keys
src/vsp_otel/exporter.py         # real OTLP/gRPC exporter + Welford fan-out
src/vsp_otel/dsse_processor.py   # DSSE v1 PAE + Khipu hash-chain SpanProcessor
src/vsp_otel/middleware.py       # install(app) drop-in + honest /vsp/provenance board
tests/test_exporter.py           # mock OTLP receiver asserts export correctness
tests/test_dsse_binding.py       # DSSE v1 PAE, chain linking, receipts on real SDK spans
tests/test_integration.py        # real OTLP/gRPC round-trip (+ opt-in container)
deploy/otel-collector-config.yaml# cross-pod broker config
Dockerfile.python-lib            # per-file COPY, minimal slim image of this library
.github/workflows/python-ci.yml  # test matrix + container integration + image build
```

---

*Doctrine v11 LOCKED — 749 / 14 / 163 · replay hash c7c0ba17 · Λ = Conjecture 1 (NEVER a theorem) · SLSA L1 (no SLSA L2 provenance workflow; PyPI releases use Trusted Publishing with PEP 740 attestations) · per-file Dockerfile COPY · DCO. HONESTY OVER CHECKLIST.*

*Signed-off-by: Yachay <yachay@szlholdings.ai>*
*Co-Authored-By: Perplexity Computer Agent <agent@perplexity.ai>*

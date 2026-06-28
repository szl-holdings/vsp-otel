# OTel GenAI Semantic Convention Axis Map (CDAO Continuous-Monitoring)

> **Doctrine v11 LOCKED** · `vsp-otel` Layer 4 · Λ = Conjecture 1 (advisory, never theorem)

`vsp-otel` already gates and DSSE-signs any OTel span. This document wires the
[OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
(`gen_ai.*` attributes) to the SZL A1–A5 axis map, so every **a11oy inference call**
is observable under CDAO continuous-monitoring assurance requirements.

## Mapping: `gen_ai.*` → A1–A5 axes

| OTel GenAI attribute | SZL A1–A5 axis | Rationale |
|---|---|---|
| `gen_ai.system` | A1 `lambda.a1` (moral grounding) | Model/system identity traceability |
| `gen_ai.request.model` | A1 `lambda.a1` | Model version provenance |
| `gen_ai.response.finish_reason` | A3 `lambda.a3` (epistemic humility) | `stop` = clean; `length`/`content_filter` = partial/restricted |
| `gen_ai.usage.input_tokens` | A5 `lambda.a5` (logical coherence) | Token budget coherence |
| `gen_ai.usage.output_tokens` | A5 `lambda.a5` | Output token bound |
| `gen_ai.request.temperature` | A3 `lambda.a3` | Calibration/determinism signal |
| `gen_ai.request.top_p` | A4 `lambda.a4` (harm avoidance) | Diversity/safety trade-off |
| `gen_ai.prompt` / `gen_ai.completion` | A2 `lambda.a2` (measurability/honesty) | Input/output measurability |

## How to emit A1–A5 from an a11oy OTel SDK instrumentation

```python
# Python — add to your OTel span before export
span.set_attribute("lambda.a1", 0.95)   # moral grounding / provenance
span.set_attribute("lambda.a2", 0.93)   # measurability / honesty
span.set_attribute("lambda.a3", 0.90)   # epistemic humility / calibration
span.set_attribute("lambda.a4", 0.92)   # harm avoidance
span.set_attribute("lambda.a5", 0.94)   # logical coherence / token budget
# gen_ai semconv (automatic with OTel GenAI instrumentation):
# gen_ai.system = "openai" | "anthropic" | ...
# gen_ai.request.model = "gpt-4o" | ...
# gen_ai.response.finish_reason = "stop" | "length" | ...
```

```yaml
# OpenTelemetry Collector pipeline — route a11oy spans through vsp-otel
exporters:
  otlphttp/vsp-otel:
    endpoint: http://vsp-otel.observability.svc:4318
service:
  pipelines:
    traces:
      exporters: [otlphttp/vsp-otel]
```

## CDAO continuous-monitoring mapping

| CDAO AI Assurance requirement | vsp-otel evidence |
|---|---|
| Model traceability (§4.1) | `gen_ai.request.model` → A1; DSSE receipt stamps model ID |
| Behavioral monitoring (§4.3) | Λ-gate rejects Λ < 0.90; `/metrics` reports `vsp_spans_total{verdict=rejected}` |
| Audit trail (§4.4) | Every accepted span: `szl.dsse.receipt_hash` + `szl.dsse.keyid` in span attrs |
| Continuous assurance (§4.5) | `/metrics` Prometheus endpoint; Helm ServiceMonitor ready |
| Lineage / provenance (§4.6) | `szl.dsse.receipt_hash` → szl-lake lookup |

## Live-checkable endpoint

```bash
# Run the shim
uvicorn collector.app:app --port 4318

# Post a gen_ai span (Python OTel SDK automatically adds gen_ai.* attrs)
# Health check
curl http://localhost:4318/healthz
# → {"status":"ok","lambda_floor":0.9}

# Metrics (CDAO continuous-monitoring board)
curl http://localhost:4318/metrics
# → vsp_spans_total{verdict="accepted"} N
#   vsp_lambda_floor 0.9
```

---

*vsp-otel · Apache-2.0 · Doctrine v11 LOCKED · Λ = Conjecture 1*

Signed-off-by: Stephen Lutar <stephenlutar2@gmail.com>

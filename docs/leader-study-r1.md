# vsp-otel domain leader study r1 (propose-only)

Date: 2026-11-24. Method: web-verified leader landscape + governing-seat ratification (Kimi nonce T12-RULING-20261124-K1). Study pinned to vsp-otel HEAD e1087eaea498af61044311e8955874e8390d2fca, fetched 2026-11-24. This card is documentation only; it changes no code, CI, config, or existing PR status. All absorb actions are FUTURE PROPOSALS (non-authorizing); implementation and merges remain separately reviewed and gated. L Conjecture 1: OPEN (advisory, never a closed theorem). No speedup, energy, or proven-trust claims; upstream performance claims are labeled as upstream claims only. No unverified signing, attestation, or provenance-level claims; this study verifies nothing about this repo's artifacts.

## Domain: OTLP telemetry collection, signed-span export, and Helm-packaged deployment for the SZL estate, with runtime and forwarding acceptance verified separately from this documentation study.

## Leaders studied (web-verified 2026-11-24)
1. OpenTelemetry Collector (https://github.com/open-telemetry/opentelemetry-collector) - moat: A vendor-neutral, component-based pipeline for receiving, processing, and exporting telemetry, backed by broad protocol and ecosystem adoption.
2. Grafana (https://github.com/grafana/grafana) - moat: A mature visualization and exploration platform that connects operational telemetry to many data sources through dashboards and an extensive plugin ecosystem.
3. Jaeger (https://github.com/jaegertracing/jaeger) - moat: An established distributed-tracing system focused on trace storage, retrieval, and analysis for understanding request flows across services.

## Absorb actions (FUTURE PROPOSALS, non-authorizing)
1. (OpenTelemetry Collector) Propose a documentation-only design note comparing the collector's receiver-processor-exporter pipeline boundaries with vsp-otel's documented OTLP collection and signed-span export responsibilities, explicitly separating proposed design review from runtime acceptance and making no provenance claim without evidence. Cost: doc-only, approximately 2-4 maintainer hours; limit: note only, no code, no infra changes.
2. (Grafana) Propose a documentation-only review of dashboard and datasource documentation patterns that could help future operators distinguish collector health, export outcomes, and unverified signing or provenance states without adding telemetry or asserting observed behavior. Cost: doc-only, approximately 2-3 maintainer hours; limit: note only, no code, no infra changes.
3. (Jaeger) Propose a documentation-only design note on trace-oriented troubleshooting vocabulary and evidence links, keeping debugging guidance separate from runtime verification and avoiding any claim that spans were accepted, forwarded, signed, or attested unless independently evidenced. Cost: doc-only, approximately 2-3 maintainer hours; limit: note only, no code, no infra changes.
4. Baseline preserve honestly: preserve the repo's honest truth labels, evidence-gated signing and provenance language, restored-source-owner status, and separation of debugging documentation from independently verified runtime and forwarding acceptance; this card must not turn any of those labels into stronger claims.

## Do not do (per governing seat)

Do not merge, bypass the signature wall, or claim implementation beyond this card.

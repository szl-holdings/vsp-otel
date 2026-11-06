# vsp-otel

**Operationalizes:** VSP — Λ-signed OTel Span Exporter  
**Repo:** szl-holdings/vsp-otel  
**Path:** ./ (root)

## What it does

Wraps an OpenTelemetry span pipeline with a Λ-signing layer. Every span exported through this module receives:

1. Axis score derivation from span attributes (`lambda.*` attribute namespace)
2. Λ-gate evaluation via `@szl/ouroboros-lambda-gate`, which resolves to the in-repo stub
   `stubs/ouroboros-lambda-gate` (the upstream `ouroboros` repo is archived)
3. A SHA-256 receipt hash stored in the gate's receipt store if `pass=true`

### Span attribute convention

Encode axis scores as span attributes with the `lambda.` prefix, in OTel snake_case
(camelCase keys such as `lambda.moralGrounding` are still read for back-compat):

```
lambda.moral_grounding = 0.96
lambda.measurability_honesty = 0.95
...
```

Missing axes default to `0.90`. The stub gate is a weighted arithmetic mean over nine
axes with threshold `0.85`, so **a span with no Λ attributes scores 0.90 and passes** —
this runtime does not fail closed. (The Python collector in `collector/` treats missing
evidence as 0 and vetoes.) Changing that default is an owner decision; it is disclosed
here rather than changed.

## HTTP endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/spans/verify` | Sign span(s) and return `{lambda, axes, pass}` |
| `POST` | `/spans/export` | Batch export; returns `{total, passed, failed}` |
| `GET`  | `/spans/:hash`  | Retrieve stored receipt for a span hash |

### Example `/spans/verify` response

```json
{
  "spanId":      "span-001",
  "lambda":      0.923,
  "axes":        { "moralGrounding": 0.96, ... },
  "pass":        true,
  "receiptHash": "a3f1..."
}
```

## Env vars

| Var | Default | Purpose |
|-----|---------|---------|
| `VSP_PORT` | `3004` | HTTP listen port |

## Gate dependency

`@szl/ouroboros-lambda-gate` — receipt storage and gate evaluation, provided in this
workspace by `stubs/ouroboros-lambda-gate` (in-memory receipt store, weighted-sum gate,
threshold 0.85). The upstream `ouroboros` repo is archived.

## Install & test

```bash
pnpm install          # from the repo root (pnpm workspace)
pnpm test             # runtime vitest (29 tests) + root gate suite (pnpm test:gates, 48 tests)
pnpm build            # tsc -> runtime/dist
# Start server
cd runtime && VSP_PORT=3004 node dist/server.js
```

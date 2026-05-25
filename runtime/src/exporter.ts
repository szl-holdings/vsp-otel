// SPDX-License-Identifier: Apache-2.0
// Author: Lutar, Stephen P. | ORCID 0009-0001-0110-4173 | SZL Holdings
// Module: vsp-otel  Thesis: VSP (Λ-signed OTel span exporter)
// Doctrine V6 preflight: ✓

import { createHash } from "node:crypto";
import {
  evaluateAxes,
  gateTransit,
  type EvalResult,
} from "@szl/ouroboros-lambda-gate";
import { type Axes, type Receipt, parseReceipt } from "@szl/ouroboros-types";

// ---------------------------------------------------------------------------
// OTel span interface (minimal, no @opentelemetry/api dependency in tests)
// ---------------------------------------------------------------------------

export interface OtelSpan {
  spanId:      string;
  traceId:     string;
  name:        string;
  startTime:   number;
  endTime:     number;
  attributes:  Record<string, string | number | boolean>;
  status:      "OK" | "ERROR" | "UNSET";
}

// ---------------------------------------------------------------------------
// Lambda-signed span: span + receipt
// ---------------------------------------------------------------------------

export interface LambdaSignedSpan {
  span:        OtelSpan;
  receiptHash: string;
  lambda:      number;
  axes:        Axes;
  pass:        boolean;
}

// ---------------------------------------------------------------------------
// Exporter: attaches a Λ-receipt to every span before export
// ---------------------------------------------------------------------------

/**
 * Derive axes from an OTel span's attributes.
 * Attributes may include pre-computed axis scores (e.g. from ML inference);
 * missing axes default to 0.90 (floor).
 */
export function axesFromSpan(span: OtelSpan): Axes {
  const get = (key: string, def = 0.90): number => {
    const v = span.attributes[`lambda.${key}`];
    return typeof v === "number" ? Math.min(1, Math.max(0, v)) : def;
  };
  return {
    moralGrounding:       get("moralGrounding"),
    measurabilityHonesty: get("measurabilityHonesty"),
    epistemicHumility:    get("epistemicHumility"),
    harmAvoidance:        get("harmAvoidance"),
    logicalCoherence:     get("logicalCoherence"),
    citationIntegrity:    get("citationIntegrity"),
    noveltyContribution:  get("noveltyContribution"),
    reproducibility:      get("reproducibility"),
    stakeholderAlignment: get("stakeholderAlignment"),
  };
}

/** Compute a deterministic receipt hash for a span. */
export function spanHash(span: OtelSpan): string {
  return createHash("sha256")
    .update(`${span.traceId}:${span.spanId}:${span.name}`)
    .digest("hex");
}

/**
 * Sign a span with a Λ-receipt and optionally push to the gate store.
 */
export function signSpan(span: OtelSpan): LambdaSignedSpan {
  const axes  = axesFromSpan(span);
  const ev    = evaluateAxes(axes);
  const hash  = spanHash(span);

  // Attempt gate transit (stores only if pass=true)
  try {
    gateTransit({
      hash,
      timestamp:   new Date(span.endTime).toISOString(),
      lambda:      ev.lambda,
      axes,
      payloadRef:  `otel:${span.traceId}/${span.spanId}`,
      doctrineVer: "6",
      meta:        { spanName: span.name, status: span.status },
    });
  } catch {
    // Gate rejection is recorded in eval; do not throw from exporter
  }

  return {
    span,
    receiptHash: hash,
    lambda:      ev.lambda,
    axes,
    pass:        ev.pass,
  };
}

// ---------------------------------------------------------------------------
// Batch export
// ---------------------------------------------------------------------------

export interface ExportResult {
  total:   number;
  passed:  number;
  failed:  number;
  signed:  LambdaSignedSpan[];
}

export function exportSpans(spans: OtelSpan[]): ExportResult {
  const signed = spans.map(signSpan);
  return {
    total:  signed.length,
    passed: signed.filter((s) => s.pass).length,
    failed: signed.filter((s) => !s.pass).length,
    signed,
  };
}

/**
 * SCITT Mask Entropy Redaction Gate
 *
 * @lean_theorem Lutar.DPI.SCITT.scitt_mask_entropy_bound
 * @lean_file    Lutar/DPI/SCITTMaskEntropy.lean
 * @lean_status  NOT-BOUND — the cited theorem does not back this gate. Its model keeps the
 *               probability vector unchanged under masking (`maskedDist.prob := d.prob`), so
 *               it holds by `simp` with equality, over a distribution of whole statements. It
 *               says nothing about the per-record value entropy computed here. That
 *               per-record bound is FALSE for field-wise masking: {id:"1", val:"1"} has
 *               entropy 0, {id:null, val:"1"} has 1 bit (pinned in
 *               test/scitt_mask_entropy.test.ts). Earlier revisions marked this GREEN and
 *               threw "THEOREM VIOLATION" on such valid redactions.
 * @lean_commit  see LEAN_COMMIT_SHA env var; pin at CI time from lutar-lean/lean-toolchain
 *
 * What this gate checks (not a Lean theorem):
 *   1. Redaction contract: `masked` has exactly the fields of `original`, and every masked
 *      value is null (redacted) or identical to the original value. Otherwise it throws.
 *   2. Revealed information never grows: with c_v the count of value v among n values,
 *      T(values) = Σ_v c_v · log2(n / c_v) bits (= n × empirical entropy). For any
 *      field-wise redaction, T(unredacted masked values) ≤ T(original values).
 *      Proof: T = n·log2(n) − Σ_v c_v·log2(c_v). Removing one occurrence of v lowers T
 *      by g(n) − g(c_v), where g(x) = x·log2(x) − (x−1)·log2(x−1) (with 0·log2(0) = 0)
 *      is increasing for x ≥ 1; since c_v ≤ n that decrease is ≥ 0, so T never
 *      increases; induct over the redacted fields.
 *   `originalEntropy` / `maskedEntropy` (nulls as one symbol) are reported as observations
 *   only: they MAY increase under field-wise masking and are not a guarantee.
 *
 * References:
 *   Cover & Thomas (2006) Elements of Information Theory, 2nd ed. §2.8.1
 *   IETF SCITT WG draft-ietf-scitt-architecture-07 §4.3
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import * as crypto from "crypto";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ScittMaskResult {
  /** Per-record Shannon entropy (bits) of the original field values (observation). */
  originalEntropy: number;
  /** Per-record Shannon entropy (bits) of the masked values, nulls as one symbol.
   *  Observation only: field-wise masking can make this exceed originalEntropy. */
  maskedEntropy: number;
  /** T(original values) = n × empirical entropy, in bits. */
  originalInformationBits: number;
  /** T(unredacted masked values); never exceeds originalInformationBits. */
  revealedInformationBits: number;
  /** True iff masked is a field-wise redaction of original and
   *  revealedInformationBits ≤ originalInformationBits + ε. */
  valid: boolean;
  /** DSSE receipt containing Lean theorem citation and I/O hash */
  receipt: DsseReceipt;
}

export interface DsseReceipt {
  formula: string;
  lean_theorem: string;
  lean_file: string;
  /** Binding status of lean_theorem for this gate (see @lean_status). */
  lean_status: string;
  lean_commit_sha: string;
  inputs_hash: string;
  output: {
    valid: boolean;
    originalEntropy: number;
    maskedEntropy: number;
    originalInformationBits: number;
    revealedInformationBits: number;
  };
  ts: string;
}

// ---------------------------------------------------------------------------
// Internal: Shannon entropy over value distribution
// ---------------------------------------------------------------------------

/**
 * Compute empirical Shannon entropy (bits) over values of a record.
 * Null values are treated as a single collapsed symbol "_REDACTED_".
 */
function shannonEntropy(values: Array<string | null>): number {
  if (values.length === 0) return 0;
  const freq = new Map<string, number>();
  for (const v of values) {
    const key = v === null ? "\0REDACTED" : v;
    freq.set(key, (freq.get(key) ?? 0) + 1);
  }
  let H = 0;
  const n = values.length;
  for (const count of freq.values()) {
    const p = count / n;
    if (p > 0) H -= p * Math.log2(p);
  }
  return H;
}

/**
 * Total empirical information T = Σ_v c_v · log2(n / c_v) bits (= n × entropy).
 * Non-increasing when values are removed (see the module docstring).
 */
function totalInformationBits(values: string[]): number {
  return shannonEntropy(values) * values.length;
}

function sha256Hex(obj: unknown): string {
  return crypto
    .createHash("sha256")
    .update(JSON.stringify(obj))
    .digest("hex");
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Check a SCITT field-wise redaction and measure what it reveals.
 *
 * @param original  Full PII record — field → plaintext value
 * @param masked    Redacted record — field → value | null (null = redacted)
 * @returns ScittMaskResult with entropy observations, revealed-information bound and receipt
 *
 * @throws Error if the field sets differ, or a masked value is neither null nor the
 *         original value (masked must be derived from original by nulling fields)
 */
export function scittMaskEntropyGate(
  original: Record<string, string>,
  masked: Record<string, string | null>
): ScittMaskResult {
  const origKeys = Object.keys(original).sort();
  const maskKeys = Object.keys(masked).sort();
  if (JSON.stringify(origKeys) !== JSON.stringify(maskKeys)) {
    throw new Error(
      `scittMaskEntropyGate: field mismatch — original has [${origKeys}], masked has [${maskKeys}]`
    );
  }

  const originalValues: string[] = origKeys.map((k) => original[k]);
  const maskedValues: Array<string | null> = origKeys.map((k) => masked[k]);
  for (const k of origKeys) {
    if (masked[k] !== null && masked[k] !== original[k]) {
      throw new Error(
        `scittMaskEntropyGate: field "${k}" is neither redacted (null) nor the original value — ` +
          `masked must be derived from original by setting fields to null`
      );
    }
  }

  // Observations: nulls are one collapsed symbol. NOT monotone under field-wise masking.
  const originalEntropy = shannonEntropy(originalValues);
  const maskedEntropy = shannonEntropy(maskedValues);

  // Guarantee: information carried by the unredacted values never exceeds the original's.
  const originalInformationBits = totalInformationBits(originalValues);
  const revealedInformationBits = totalInformationBits(
    maskedValues.filter((v): v is string => v !== null)
  );
  const EPS = 1e-9;
  const valid = revealedInformationBits <= originalInformationBits + EPS;

  const inputs_hash = sha256Hex({ original, masked });
  const lean_commit_sha = process.env["LEAN_COMMIT_SHA"] ?? "unknown";

  const receipt: DsseReceipt = {
    formula: "scitt_mask_entropy_bound",
    lean_theorem: "Lutar.DPI.SCITT.scitt_mask_entropy_bound",
    lean_file: "Lutar/DPI/SCITTMaskEntropy.lean",
    lean_status: "NOT-BOUND",
    lean_commit_sha,
    inputs_hash,
    output: {
      valid,
      originalEntropy,
      maskedEntropy,
      originalInformationBits,
      revealedInformationBits,
    },
    ts: new Date().toISOString(),
  };

  if (!valid) {
    // Unreachable for a field-wise redaction (proved in the module docstring).
    throw new Error(
      `scittMaskEntropyGate: revealed information ${revealedInformationBits} bits exceeds ` +
        `original ${originalInformationBits} bits — implementation error`
    );
  }

  return {
    originalEntropy,
    maskedEntropy,
    originalInformationBits,
    revealedInformationBits,
    valid,
    receipt,
  };
}

/**
 * Batch gate: apply scittMaskEntropyGate to an array of record pairs.
 * Returns the array of results; throws on the first invalid redaction.
 */
export function scittMaskEntropyBatch(
  pairs: Array<{
    original: Record<string, string>;
    masked: Record<string, string | null>;
  }>
): ScittMaskResult[] {
  return pairs.map(({ original, masked }) =>
    scittMaskEntropyGate(original, masked)
  );
}

import assert from 'node:assert/strict';
import { once } from 'node:events';
import test from 'node:test';
import { axesFromSpan, exportSpans, signSpan, spanHash } from '../runtime/dist/exporter.js';
import { createVspServer } from '../runtime/dist/server.js';
import { getReceipt } from '../stubs/ouroboros-lambda-gate/index.js';

// Fixed seed and bounded loops make every failing example reproducible in CI.
let seed = 0x51a7e;
function random() {
  seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return seed / 2 ** 32;
}
const names = [
  ['moral_grounding', 'moralGrounding'],
  ['measurability_honesty', 'measurabilityHonesty'],
  ['epistemic_humility', 'epistemicHumility'],
  ['harm_avoidance', 'harmAvoidance'],
  ['logical_coherence', 'logicalCoherence'],
  ['citation_integrity', 'citationIntegrity'],
  ['novelty_contribution', 'noveltyContribution'],
  ['reproducibility', 'reproducibility'],
  ['stakeholder_alignment', 'stakeholderAlignment'],
];
let serial = 0;
function span(attributes = {}) {
  return { spanId: `axis-property-${++serial}`, traceId: 'seed-51a7e', name: 'bounded-axis-test',
    startTime: 1700000000000, endTime: 1700000000001, status: 'OK', attributes };
}
function uniform(value) {
  return Object.fromEntries(names.map(([name]) => [`lambda.${name}`, value]));
}

test('finite scores stay bounded, deterministic and monotone across generated spans', () => {
  for (let i = 0; i < 256; i++) {
    const values = names.map(() => (random() - 0.5) * 8);
    const input = span(Object.fromEntries(names.map(([key], n) => [`lambda.${key}`, values[n]])));
    const before = structuredClone(input);
    const axes = axesFromSpan(input);
    assert.deepEqual(axes, axesFromSpan(input));
    assert.deepEqual(input, before);
    for (const value of Object.values(axes)) assert.ok(Number.isFinite(value) && value >= 0 && value <= 1);
    const higher = span(Object.fromEntries(names.map(([key], n) => [`lambda.${key}`, values[n] + random()])));
    assert.ok(signSpan(higher).lambda >= signSpan(input).lambda);
  }
});

test('absent axes retain defaults, finite values clamp and canonical names take precedence', () => {
  assert.deepEqual(Object.values(axesFromSpan(span())), Array(9).fill(0.9));
  assert.deepEqual(Object.values(axesFromSpan(span(uniform(-1)))), Array(9).fill(0));
  assert.deepEqual(Object.values(axesFromSpan(span(uniform(2)))), Array(9).fill(1));
  for (const [snake, camel] of names.filter(([a, b]) => a !== b)) {
    assert.equal(axesFromSpan(span({ [`lambda.${snake}`]: 0.6, [`lambda.${camel}`]: 0.8 }))[camel], 0.6);
  }
});

test('every explicit malformed axis rejects before receipt storage', () => {
  const bad = [NaN, Infinity, -Infinity, true, false, '0.9', null, undefined, [], {}];
  for (const key of new Set(names.flat().map(name => `lambda.${name}`))) {
    for (const value of bad) {
      const input = span({ [key]: value });
      assert.throws(() => signSpan(input), TypeError, `${key} accepted ${String(value)}`);
      assert.equal(getReceipt(spanHash(input)), null);
    }
  }
});

test('malformed canonical or legacy values cannot hide behind a valid alias', () => {
  for (const [snake, camel] of names.filter(([a, b]) => a !== b)) {
    for (const attributes of [
      { [`lambda.${snake}`]: null, [`lambda.${camel}`]: 0.99 },
      { [`lambda.${snake}`]: 0.99, [`lambda.${camel}`]: false },
    ]) assert.throws(() => axesFromSpan(span(attributes)), TypeError);
  }
});

test('passing finite spans are retrievable; rejected finite decisions do not emit receipts', () => {
  for (let i = 0; i < 64; i++) {
    const accepted = span(uniform(0.86 + random() * 0.14));
    const denied = span(uniform(random() * 0.8));
    const result = exportSpans([accepted, denied]);
    assert.deepEqual([result.total, result.passed, result.failed], [2, 1, 1]);
    assert.equal(getReceipt(spanHash(accepted)).hash, result.signed[0].receiptHash);
    assert.deepEqual(getReceipt(spanHash(accepted)).axes, result.signed[0].axes);
    assert.equal(getReceipt(spanHash(denied)), null);
  }
});

test('invalid axes reject whole batches before storing any valid prefix, in either order', () => {
  for (const reverse of [false, true]) {
    const valid = span(uniform(0.99));
    const invalid = span({ 'lambda.moral_grounding': true });
    const input = reverse ? [invalid, valid] : [valid, invalid];
    assert.throws(() => exportSpans(input), TypeError);
    assert.equal(getReceipt(spanHash(valid)), null);
    assert.equal(getReceipt(spanHash(invalid)), null);
  }
});

test('timestamp admission failure reports pass=false and stores no receipt', () => {
  for (const endTime of [NaN, Infinity, -Infinity, 8640000000000001, 'not-a-date']) {
    const input = { ...span(uniform(0.99)), endTime };
    const result = signSpan(input);
    assert.equal(result.pass, false);
    assert.ok(Number.isFinite(result.lambda) && result.lambda > 0.85);
    assert.equal(getReceipt(result.receiptHash), null);
    const batch = exportSpans([input]);
    assert.deepEqual([batch.total, batch.passed, batch.failed], [1, 0, 1]);
  }
});

test('compiled HTTP routes reject numeric overflow and mixed invalid batches without receipts', async () => {
  const server = createVspServer();
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const origin = `http://127.0.0.1:${server.address().port}`;
  try {
    for (const route of ['/spans/verify', '/spans/export']) {
      for (const reverse of [false, true]) {
        const valid = span(uniform(0.99));
        const invalid = span({ 'lambda.moral_grounding': true });
        const input = reverse ? [invalid, valid] : [valid, invalid];
        const response = await fetch(origin + route, { method: 'POST', body: JSON.stringify(input) });
        assert.equal(response.status, 400);
        assert.deepEqual(await response.json(), { error: 'bad request' });
        for (const inputSpan of input) {
          const receipt = await fetch(`${origin}/spans/${spanHash(inputSpan)}`);
          assert.equal(receipt.status, 404);
          await receipt.arrayBuffer();
        }
      }
      const overflow = span({ 'lambda.harm_avoidance': '__OVERFLOW__' });
      const overflowBody = JSON.stringify(overflow).replace('"__OVERFLOW__"', '1e999');
      const response = await fetch(origin + route, {
        method: 'POST', body: overflowBody,
      });
      assert.equal(response.status, 400);
      await response.arrayBuffer();
      const receipt = await fetch(`${origin}/spans/${spanHash(JSON.parse(overflowBody))}`);
      assert.equal(receipt.status, 404);
      await receipt.arrayBuffer();

      const badTime = { ...span(uniform(0.99)), endTime: 'not-a-date' };
      const timeResponse = await fetch(origin + route, { method: 'POST', body: JSON.stringify(badTime) });
      assert.equal(timeResponse.status, 200);
      const timeResult = await timeResponse.json();
      if (route === '/spans/verify') assert.equal(timeResult.pass, false);
      else assert.deepEqual(timeResult, { total: 1, passed: 0, failed: 1 });
      const timeReceipt = await fetch(`${origin}/spans/${spanHash(badTime)}`);
      assert.equal(timeReceipt.status, 404);
      await timeReceipt.arrayBuffer();
    }
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
});

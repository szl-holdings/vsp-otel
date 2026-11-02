// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 SZL Holdings
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { delimiter, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const runner = fileURLToPath(new URL('../.github/scripts/run-optional-fuzz.mjs', import.meta.url));

function fixture(t, { manifest, raw, installExit = 0, fuzzExit = 0, noPnpm = false, signal = false } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'vsp-optional-fuzz-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  if (raw !== undefined || manifest !== undefined) {
    writeFileSync(join(root, 'package.json'), raw ?? JSON.stringify(manifest));
  }
  const bin = join(root, 'bin');
  mkdirSync(bin);
  if (!noPnpm) {
    writeFileSync(join(bin, 'pnpm'), `#!${process.execPath}
const fs = require('node:fs');
const args = process.argv.slice(2);
fs.appendFileSync(process.env.FUZZ_CALLS, JSON.stringify(args) + '\\n');
if (args[0] === 'install') process.exit(Number(process.env.INSTALL_EXIT));
if (process.env.FUZZ_SIGNAL === '1') process.kill(process.pid, 'SIGTERM');
console.error('fixture fuzz output');
process.exit(Number(process.env.FUZZ_EXIT));
`, { mode: 0o755 });
  }
  const callsPath = join(root, 'calls.jsonl');
  const result = spawnSync(process.execPath, [runner], {
    cwd: root,
    encoding: 'utf8',
    env: {
      ...process.env,
      PATH: noPnpm ? bin : `${bin}${delimiter}${process.env.PATH}`,
      FUZZ_CALLS: callsPath,
      INSTALL_EXIT: String(installExit),
      FUZZ_EXIT: String(fuzzExit),
      FUZZ_SIGNAL: signal ? '1' : '0',
    },
  });
  let calls = [];
  try { calls = readFileSync(callsPath, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  return { ...result, calls };
}

const configured = { scripts: { 'test:fuzz': 'fixture fuzz' } };

test('an absent package reports that no fuzz tests ran without installing', t => {
  const result = fixture(t);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /no fuzz tests ran/);
  assert.deepEqual(result.calls, []);
});

test('an absent optional script reports no coverage without installing', t => {
  const result = fixture(t, { manifest: { scripts: { test: 'fixture unit tests' } } });
  assert.equal(result.status, 0);
  assert.match(result.stdout, /test:fuzz is absent; no fuzz tests ran/);
  assert.deepEqual(result.calls, []);
});

test('a configured script uses the frozen workspace install and runs successfully', t => {
  const result = fixture(t, { manifest: configured });
  assert.equal(result.status, 0);
  assert.deepEqual(result.calls, [['install', '--frozen-lockfile'], ['run', 'test:fuzz']]);
});

test('a failing fuzz script fails the job and retains its diagnostic output', t => {
  const result = fixture(t, { manifest: configured, fuzzExit: 23 });
  assert.equal(result.status, 23);
  assert.match(result.stderr, /fixture fuzz output/);
  assert.doesNotMatch(result.stdout, /not configured|No fuzz tests found/);
});

test('a failed install fails the job before any fuzz invocation', t => {
  const result = fixture(t, { manifest: configured, installExit: 17 });
  assert.equal(result.status, 17);
  assert.deepEqual(result.calls, [['install', '--frozen-lockfile']]);
});

test('invalid manifests and malformed configured scripts fail without installing', t => {
  for (const raw of ['{', 'null', '[]', '{"scripts":null}', '{"scripts":[]}',
    '{"scripts":{"test:fuzz":null}}', '{"scripts":{"test:fuzz":" "}}']) {
    const result = fixture(t, { raw });
    assert.notEqual(result.status, 0, raw);
    assert.deepEqual(result.calls, [], raw);
  }
});

test('an unavailable package manager is a failure, not an absent test', t => {
  const result = fixture(t, { manifest: configured, noPnpm: true });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /ENOENT/);
});

test('a fuzz process terminated by a signal fails the job', t => {
  const result = fixture(t, { manifest: configured, signal: true });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /SIGTERM/);
});

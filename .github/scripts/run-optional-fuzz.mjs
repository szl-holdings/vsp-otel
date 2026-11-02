// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 SZL Holdings
import { existsSync, readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

if (!existsSync('package.json')) {
  console.log('Fuzz not configured: package.json is absent; no fuzz tests ran.');
  process.exit(0);
}

const manifest = JSON.parse(readFileSync('package.json', 'utf8'));
if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) {
  throw new Error('package.json must contain an object');
}
const scripts = manifest.scripts;
if (scripts !== undefined && (!scripts || typeof scripts !== 'object' || Array.isArray(scripts))) {
  throw new Error('package.json scripts must contain an object');
}
const fuzz = scripts?.['test:fuzz'];
if (fuzz === undefined) {
  console.log('Fuzz not configured: test:fuzz is absent; no fuzz tests ran.');
  process.exit(0);
}
if (typeof fuzz !== 'string' || !fuzz.trim()) {
  throw new Error('test:fuzz must be a non-empty script');
}

for (const args of [['install', '--frozen-lockfile'], ['run', 'test:fuzz']]) {
  const result = spawnSync('pnpm', args, { stdio: 'inherit' });
  if (result.error) console.error(result.error.message);
  if (result.signal) console.error(`pnpm terminated by ${result.signal}`);
  if (result.status !== 0) process.exit(result.status ?? 1);
}

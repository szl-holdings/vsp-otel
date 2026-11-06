# Changelog

All notable changes to `vsp-otel` are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

> Published versions are `0.1.0`–`0.1.3` on PyPI (GitHub releases `v0.1.0`, `v0.1.2`,
> `v0.1.3`); they are not itemized here — see the GitHub releases. The `[0.2.0]` heading
> below records a May-2026 docs/CI batch and matches no published package version.

## [Unreleased]

### Fixed

- `vsp_otel`: exported spans now carry their Khipu receipt (`szl.mesh.receipt_hash`,
  `szl.mesh.khipu_index`, `szl.mesh.khipu_prev`, `szl.mesh.dsse_payload_type`, and
  `szl.mesh.rekor_log_index` when configured). Through 0.1.3 these stayed in process
  memory on every supported `opentelemetry-sdk` (1.25–1.45): `on_end` receives an
  immutable span. A failing signer no longer raises into the instrumented app;
  `bind_failures` / `stamp_failures` count unbound or unstamped spans.
- Root gate suite (`test/` over `src/{pipeline,redaction,sla}`) now runs in CI
  (`pnpm test:gates`, 49 tests); 3 of its tests had been failing unseen. The SCITT gate
  no longer throws "THEOREM VIOLATION" on valid field-wise redactions; it enforces the
  redaction contract and bounds revealed information instead, and its Lean citation is
  marked NOT-BOUND. The DPI theorem name/status is corrected
  (`Lutar.DPI.dpi_receipt_chain_entropy_bound`, CONDITIONAL).
- `Dockerfile.python-lib` copies the README and LICENSE to the paths `pyproject.toml` reads.

### Changed

- `/api/vsp/provenance` reports `slsa: "L1 (no SLSA L2 provenance workflow in vsp-otel)"`
  instead of "L1 honest + L2 attested", and adds `bind_failures` / `stamp_failures`.
- Packaging: PEP 639 `license = "Apache-2.0"` + `license-files`; Python 3.13 and 3.14
  classifiers and CI matrix entries.
- Docs: corrected test counts, collector quickstart, lutar-lean citation status,
  archived-repo labels, and disclosed the TypeScript runtime's fail-open default.

## [0.2.0] — 2026-05-28

### Changed

- docs(readme): Series-A polish — DOI badges + VSP-OTEL expansion
- docs: add Series-A compliance files (SECURITY.md, CoC, CONTRIBUTING)
- chore(actions): pin all action refs to commit SHA
- chore(deps): bump actions/setup-node, pnpm/action-setup, actions/checkout
- chore(security): enrich dependabot config — add npm ecosystem tracking

## [0.1.0] — 2026-05-25

### Changed

- feat(runtime): Vessels Spine Protocol over OTel + 10 tests
- chore(ci): add baseline CI workflow per Doctrine V6
- chore: add .github/CODEOWNERS
- docs: fix CITATION.cff given-names format (Stephen P.)
- chore: add .github/dependabot.yml
- feat(scaffold): initial README, CITATION.cff, scorecard workflow

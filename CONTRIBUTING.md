# Contributing to vsp-otel

Thank you for your interest in vsp-otel. This repository is part of the [SZL Holdings](https://github.com/szl-holdings) platform — governed AI decision infrastructure for regulated enterprises.

**Maintainer:** Lutar, Stephen P. · ORCID [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173) · SZL Holdings

## Contribution Model

vsp-otel is **Apache-2.0 licensed open-source software**. Contributions are welcome subject to the requirements below.

## Requirements for All Contributions

### DCO Sign-off (required)

Every commit must carry a Developer Certificate of Origin sign-off. Add it with:

```
git commit -s -m "your commit message"
```

This adds a `Signed-off-by: Your Name <your@email.com>` trailer. By signing off you certify that:

> You have the right to submit the contribution under the Apache-2.0 license, that you wrote it yourself or have permission from the author, and that it has not been contributed under a license incompatible with Apache-2.0.

### Signed Commits (required)

All commits must be GPG-signed:

```
git commit -S -s -m "your commit message"
```

Configure signing: `git config --global commit.gpgsign true`

### Doctrine-V6 Quality Gate (required for logic changes)

Any change touching Λ-gate evaluation, span emission, receipt hashing, or ρ-closure logic must satisfy the conjunctive doctrine-V6 alignment threshold:

**Λ ≥ 0.90** across all 9 axes simultaneously.

Include the Λ-vector in your PR description. PRs that do not meet this threshold will not be merged regardless of other quality signals.

### Permitted Licenses

Contributed code and incorporated dependencies must be licensed under one of:

- Apache-2.0
- MIT
- BSD-3-Clause
- CC-BY-4.0 (documentation only)

Do not introduce dependencies licensed under GPL, AGPL, SSPL, or any proprietary license without prior written approval from the maintainer.

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Write or update tests for your change.
3. Ensure all checks pass locally before opening a PR.
4. Open a pull request against `main` using this template:

```markdown
## Summary
<!-- What does this PR do? -->

## Motivation
<!-- Why is this change needed? -->

## Doctrine-V6 Λ-vector (required for logic changes)
<!-- Paste your 9-axis Λ-vector here. All axes must be ≥ 0.90. -->

## Checklist
- [ ] Commits are GPG-signed (`git commit -S`)
- [ ] Commits carry DCO sign-off (`git commit -s`)
- [ ] Tests added or updated
- [ ] Documentation updated if needed
- [ ] Permitted license check passed
```

5. Request review from **@stephenlutar2-hash**. All PRs require at least one approval from @stephenlutar2-hash before merge.

## How You Can Engage

We welcome the following:

- **Bug reports.** Open a [GitHub issue](../../issues/new) with reproduction steps, environment, and expected vs actual behavior.
- **Security disclosures.** Do **not** open a public issue. Follow [`SECURITY.md`](./SECURITY.md) — contact [stephen@szlholdings.com](mailto:stephen@szlholdings.com) or open a private GitHub security advisory.
- **Questions and feedback.** Email [stephen@szlholdings.com](mailto:stephen@szlholdings.com) for product questions, integration requests, or partnership inquiries.
- **Documentation corrections.** Small typo / link / factual fixes to public docs are welcome via PR. Please open an issue first describing the change.

## Reporting a Problem

| Channel | Use it for |
|---|---|
| [GitHub issues](../../issues) | Bugs, documentation gaps, reproducible defects |
| [stephen@szlholdings.com](mailto:stephen@szlholdings.com) | Security vulnerabilities (private), product, partnership, licensing |

---

(c) 2024–2026 SZL Holdings, LLC. Licensed under Apache-2.0.

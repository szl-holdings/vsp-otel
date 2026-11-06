// SPDX-License-Identifier: Apache-2.0
// Root gate suite: test/*.test.ts exercise src/{pipeline,redaction,sla}/*.ts.
// These sit outside the runtime/ package, so `pnpm -C runtime test` never ran
// them. Run with `pnpm test:gates` (uses the vitest installed for runtime/).
export default {
  test: {
    include: ["test/**/*.test.ts"],
    environment: "node",
  },
};

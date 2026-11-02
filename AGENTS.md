# Repository collaboration contract

Before changing files, read README.md and collaboration/STATUS.md, HANDOFFS.md, DATA_SYNC.md, CHANGELOG.md. Follow T1_统一实验说明_v1.md. Check git status and preserve unrelated work.

Complete the authorized task and update the relevant STATUS row plus a dated handoffs/ record. Update HANDOFFS when requirements change and CHANGELOG when protocol, interfaces, data versions or delivery requirements change. Submitted, awaiting review and accepted are distinct; only the receiving reviewer records their independent acceptance.

A's real cohort is not delivered. Do not invent clinical results or mark A/C/D complete based on synthetic validation. Do not change labels or splits to make a run succeed.

Track code, documents, small summaries and artifacts/registry.json in Git. Use this repository's GitHub Release bundles for large data and complete runs; verify SHA256. Preserve immutable runs and source/input bytes recorded in manifests. Do not rewrite historical manifests to force verification. Use project-relative paths in shared instructions/configurations, run relevant tests, and commit/push only within the user's authorized scope.

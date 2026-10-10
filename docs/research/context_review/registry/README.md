# Final registry reconciliation

Created 2026-10-09. This is a conservative metadata and verification-event view of the saved review, not new source verification. The authoritative originals remain in `C:\Users\adich\OneDrive\Documents\Repos\agent-civ-lab\docs\research\context_review\registry`; checks remain under that review's `verification` directory. Relative provenance paths in these tables resolve against the repo context_review directory.

- `sources_normalized.csv`: all 83 original lane records, retaining original `record_json` and labels. Work IDs use explicit arXiv/DOI identities when supplied; otherwise stable SHA-256-derived URL candidate IDs. URL artifact IDs identify locators, not downloaded bytes. Unknown authors, editions, retrieval dates, lineage and hashes remain explicit.
- `claims_status.csv`: all 91 original claim rows plus 19 targeted verification/correction events (3 additional Independent events, 12 executive checks, 4 Executive_B corrections). Event counts are not unique claim counts. Exact eight sampled registry row IDs map to their original checks; unsampled rows remain unpromoted. Original claim JSON preserves proposed wording, locators and scope.
- `normalize_registry.ps1`: offline reproducible transformation; writes only this Final Registry directory. It does not run source retrieval, experiments, inference or git operations.

Author labels such as `key_claim_verified` are reading-stage assertions. They never become independent checks by normalization. Most full-text labels are conservatively represented as selected passages; explicit complete-reading assertions are still author assertions. Independent checks certify only their specified passage/construct/code scope, not a whole work, executable reproduction, independence of empirical evidence, or every original claim.

The two tau-bench records R2:S7 and R9:R9-S07 share `arxiv:2406.12045` and `arxiv:2406.12045v1`; both review records survive. Ostrom R4:S4/R4:S8 remain separate URL candidates with potential adaptation lineage, pending exact edition/text collation. S8 remains unavailable; reading S4 does not verify the inaccessible lecture artifact.

Executive versions are separately pinned in check events; never silently substitute a lane's version. For example E10 checks Fish v1 while R5:S1 records v2. E12 appends successful Warwick full-text access with published pp384–385 after the original extra:R9-C02 access failure; that failure remains visible. Conditional-null calibration is still unresolved. E05 retains the requested Lakens2017 retrieval limitation.

E01–E12 allowed wording is bounded by both the table and each lane's `allowed_final_wording.md` and `checks.md`. Qualitative checks do not certify new numerical results. Prior descriptive audit values retain their original inferential caveats. Scientific novelty, deployed user value, psychological mechanisms, equal compute and universal laws remain unestablished where the checks say so.

Reviewer independence (prior exposure/shared ledger) and evidence lineage (authors/data/models/tasks) remain distinct unknown fields. Multiple lanes or cross-examination agreement do not establish independent empirical corroboration. There is no certified independent-study count.

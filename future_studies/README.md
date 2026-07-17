# Future-study execution boundary

No future study is currently authorized.

Any later study must keep its code under `future_studies/<study_id>/`, its data under
`data/future_studies/<study_id>/`, and use
`cross_review.future_study_loader.load_authorized_bytes` for every scientific input.
The loader revalidates the single canonical manifest before each read. Direct reads of
quarantined paths are outside the authorized research workflow.

Every read also rechecks the immutable source hashes, exclusion projections, content
fingerprints, and revoked authorizations. This is a repository-governance boundary,
not an operating-system ACL; programs running as the same user can still read preserved
historical bytes outside the authorized workflow.

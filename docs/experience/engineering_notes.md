# Engineering Notes

## 2026-07-19 Do not relabel classical complete testing as an LLM-agent coverage theory

- An obligation of the form `(information state, input, admissible outputs)` is
  structurally close to the elementary requirements used in deterministic FSM
  testing. Complete FSM/ioco and partial-observation testing are mandatory formal
  reduction targets under their finite/state-bounded, fairness and test-purpose
  assumptions; they do not automatically subsume a stochastic LLM policy. A new
  adequacy claim would first need a faithful compilation and an incremental theorem.
- A frozen finite fault domain, one witness per non-equivalent fault, and actual
  mutant killing are classical fault-based model testing. Keeping the obligation
  universe syntactically separate from mutants avoids one circularity but does not
  itself create novelty.
- Test whether a paired construction adds detection beyond the direct oracle. If
  `A_all(h)` is exact, membership of the agent's action already exposes the policy
  error. Two hidden-world executions may improve diagnosis while adding zero new
  kills; explanation is not adequacy.
- Lost acknowledgements, post-effect response timeouts, request identity, durable
  result replay, idempotency leases, readback, and compensation are established
  distributed-systems concepts. Their use in an LLM environment needs a distinct
  model-behavior question, not a renamed recovery mechanism.
- A cleaner training question uses identifiable visible interventions. Hold the
  task, tool identity/schema, state, and history fixed; change one visible contract
  atom; require an independent checker to flip the permission label of the same
  normalized witness action. This avoids falsely demanding disjoint full action sets
  when query, escalation, or no-op may remain legal in both contexts.
- Counterfactual pairs are data structure, not automatically a method. CounterComp
  and PairCFR already combine paired/counterfactual contrast with OOD objectives;
  compare against them as well as equal-token SFT, standard DPO, shuffled pairs,
  contract rereading, keyword/position rules, and a deterministic parser/planner.
  Require unseen-tool-family and unseen-contract-composition gains, plus retention
  of ordinary tool-calling ability.
- Treat training compute as capacity, not motivation. If a rule parser is near
  ceiling, the pair-aware objective does not beat equal-budget training, or gains
  disappear outside IID templates, stop the topic.

## 2026-07-19 A testing contribution needs incremental detection, not a new combination of familiar parts (historical; superseded above)

- Rainmaker already injects a response timeout after a remote request has taken
  effect and covers retry-induced duplicate effects, semantic violations, state
  divergence, and REST call sites. A post-effect/pre-reply injector is a baseline,
  not an LLM-agent testing novelty.
- The non-peer-reviewed AgentAssay technical report already proposes joining agent
  behavioral contracts, state/boundary coverage, mutation adequacy, and metamorphic
  relations, although its coupling claims still require replication. SGVEF-LOOP synthesizes
  metamorphic pairs while exploring MCP-agent topology. Combining contract, MR,
  mutation score, and agent traces no longer defines a contribution boundary.
- An exact `Safe(K)` oracle creates a stringent incremental-value test. If two
  independent single-case checks expose every failure attributed to an MR, the MR
  is redundant. Set inclusion between oracle outputs also does not constrain two
  single actions chosen by an agent without adding a separate preference oracle.
- The narrow object retained at that historical stage was an atomic semantic test obligation, not a fault or
  an MR: one visible history and concrete action, a pair of observation-equivalent
  worlds where that action is respectively safe and unsafe, available recovery
  capabilities, and a dependent prefix. Keep the obligation universe independent of
  defects; prove and execute defect-to-witness-to-kill only afterward. The later
  classical-baseline and direct-oracle audit above rejected it as the active method.
- Prefix and trajectory risks require different samples. Independent restarts at one
  visible prefix estimate that prefix's violation probability; only coherent complete
  rollouts estimate the probability of any violation along a trajectory.
- Compare coverage criteria at the same test-case budget. A new criterion is useful
  only if it kills defects missed by response-timeout/call-site, state-transition,
  final-state, Action-MR, and single-world baselines. More generated cases alone are
  not evidence of stronger adequacy.
- Keep safety, progress, and cost as separate oracles. World-uniform safety is an
  intersection over compatible worlds; choosing a preferred query, retry,
  compensation, or escalation requires additional liveness or cost assumptions.
- Pending-paper titles are a novelty gate, not evidence of contents. Record official
  authors, paper type, schedule, and missing full-text status; use a sibling paper
  such as NetAgentBench only to bound already occupied concepts, never as a proxy
  for an unavailable AITest paper.

## 2026-07-19 A safety wrapper can erase the LLM research question

- If an online guard receives the full transition model, task goal, exact belief,
  and winning region, it is not merely checking an LLM. It can synthesize the
  contingent controller itself. The LLM is then redundant when correct and harmful
  when wrong. This is a structural No-Go that does not require an experiment.
- Recent runtime-enforcement systems narrow the claim further. AgentSpec already
  supplies a DSL and lightweight runtime constraints; VIGIL compiles natural-language
  skill policies into SMT-checked finite-trace enforcement; ToolGate enforces tool
  contracts. “DSL plus training-free guard” is therefore not a novelty statement.
- Preserve a real LLM question through information separation. Let the LLM alone see
  the natural-language task goal; let the monitor see only a trusted safety projection,
  public trace, and proposed action; let the complete formal model remain in an
  offline evaluator. The monitor may allow or block, but must not select, repair, or
  reveal the safe action set.
- The defensible conditional contribution moves down one layer: define contracts for
  acknowledgement-versus-commit ambiguity, idempotency scope and expiry, query
  freshness, partial effects, and compensation preconditions, then compile them into
  a safety-only epistemic monitor. Belief planning and shielding remain cited
  foundations, not inventions.
- Separate safety from liveness in every claim. A goal-blind monitor can guarantee
  only contract-relative invariant preservation. Task completion, escalation, and
  cost remain empirical properties of the untrusted LLM policy.
- Synthetic formal environments need independent implementations. Cross-check the
  environment/oracle with an enumerator and a separately implemented symbolic
  checker; otherwise a shared DSL bug can make generation, labels, and enforcement
  agree while all three are wrong.
- Use goal-counterfactual pairs to prove non-redundancy: hold the public trace and
  safety projection fixed, vary only the natural-language goal, and require different
  choices among multiple safe actions. If a deterministic parser plus planner solves
  this under strict OOD, stop the topic instead of adding fine-tuning.

## 2026-07-19 Separate the LLM contribution from classical recovery machinery

- A recent benchmark can invalidate a contribution form without invalidating the
  underlying problem. FAILING TOOLS already covers runtime failures,
  postcondition checks, retry/fallback, and residual uncertainty, so a generic
  recovery benchmark is no longer enough. Atomix additionally covers
  post-effect/pre-return faults and ambiguous retries.
- Belief-space strong planning, contingent policies, and all-branch model
  checking are classical algorithms. Use them as a mechanical oracle and say so;
  do not present their application to tool agents as an algorithmic invention.
- The remaining LLM-specific question is at the semantic boundary: can the model
  interpret natural-language goals, contracts, and history well enough to propose
  a recovery action that a belief-safe guard can certify across indistinguishable
  applied/unapplied worlds?
- Keep the offline oracle and online guard epistemically separate. The oracle may
  enumerate the complete finite transition system; the guard may use only public
  contracts and visible history. If the guard sees hidden commit state or
  injector metadata, the evaluation merely reproduces its own labels.
- Test the shortest distributed-systems rule first. If “query when available,
  otherwise idempotent same-key retry, otherwise safe compensation, otherwise
  escalate” is sound and complete, stop the topic. A more elaborate benchmark
  would only disguise a deterministic lookup table.
- Training is not automatically the richer contribution. When a verifier can
  calculate hard safety exactly, ordinary SFT weakens the guarantee. Training is
  justified only later, inside the verified safe action set, if symbolic cost
  rules leave stable OOD decision residuals.

## 2026-07-19 Let the scientific oracle choose the domain, not the degree label

- A degree title is not evidence of domain competence and should not silently
  become an application constraint. Once the author clarified that Communication
  Engineering is administrative context rather than trained subject matter, the
  NIKA/ns-3 shortlist had to be retired instead of cosmetically reframed.
- A broad LLM-native search can still be mostly negative. Structured output,
  instruction self-correction, generic tool recovery, RAG reliability, code
  evolution, LoRA retention, quantization, and heterogeneous serving all have
  dense 2025--2026 direct neighbors. A clean experimental setup is not a novelty
  claim.
- Post-action outcome ambiguity is scientifically different from pre-action user
  ambiguity or an observed execution error. The same timeout can be compatible
  with both committed and uncommitted external state, so an extra retry can reduce
  safety. Labels must be defined over the whole belief set, not the hidden state
  known to the generator.
- A formal planner and model checker make an excellent oracle but can also destroy
  the LLM claim. The only possible model contribution is mapping natural-language
  goals and contracts to recovery decisions that generalize across held-out tool
  families. If a deterministic parser plus planner does that, stop the topic.
- Do not turn every reliability component into a thesis branch. Faithful final
  reporting can remain a reliable-termination metric; contract migration remains
  a fallback. The small paper and thesis should share one partial-observability
  spine.
- Metadata pages can auto-render research samples. When the AgentAbstain dataset
  card did so, stop access, do not reproduce or use the content, exclude the source
  from future data/design evidence, record the exposure, and keep the canonical
  future manifest empty. “No download” does not justify silently ignoring an
  unplanned display.

## 2026-07-18 Select a research direction without activating a study

- A publication-to-thesis plan needs one scientific spine, not two adjacent
  topics. Here the small paper selects static counterfactual evidence-consistency
  training, while the thesis adds uncertainty control and sequential evidence
  acquisition. Merely adding models or samples would not be a thesis extension.
- Degree label, publication floor, and compute constrain different layers. A
  Communication Engineering master's framing requires a real multi-source
  reliability and decision formulation; EI is a publication floor rather than a
  scientific claim; four A6000 and three 3090 GPUs justify controlled 7B--8B LoRA
  experiments but do not make model scale an innovation.
- Search the nearest methods before naming an algorithm. Generic contrastive APCA,
  GRPO patch classification, post-hoc code calibration, abstention, and noisy-RAG
  fusion already exist. The remaining candidate contribution is the controlled
  relation between evidence diagnosticity and fixed-coverage false-accept risk,
  not LoRA, contrastive learning, or reliability weighting by itself.
- Keep the first method minimal. One binary correctness loss plus one counterfactual
  ranking loss can be isolated against ordinary SFT and calibration. Adding active tools,
  test generation, multi-agent planning, and RL in the same paper would make the
  causal source of any gain unidentifiable.
- Do not choose a sample count from convenience or quarantined effects. Define the
  source-frame protocol first. Because a canonical manifest cannot name hashes for
  bytes that do not yet exist, use a separately audited and signed acquisition-only
  authority for deterministic staging and hashing; then authorize the nonempty
  hash-bound scientific-use manifest before establishing the frame. Estimate
  qualification and clustering only in a separate feasibility cohort, define a
  practically meaningful risk reduction, and run a cluster-aware power simulation
  before confirmatory training.
- Direction selection is not novelty confirmation or data authorization. A plan may
  select a scientific spine and define provisional RQs, non-goals, model-selection
  rules, metrics, and Gates while exact novelty awaits systematic review and the
  canonical input manifest remains empty. This prevents planning language from
  silently becoming permission to read data, tune a model, or produce a paper claim.
- Do not force heterogeneous GPUs into one synchronized job. Use homogeneous
  A6000 workers for training and 3090 workers for validation, containers, and
  baseline inference; this keeps reproducibility and failure diagnosis simpler.

## 2026-07-18 Isolate research roles, not historical files

- Deleting or moving old data does not remove researcher knowledge and damages
  provenance. Preserve historical bytes, then enforce what roles those artifacts
  may play: provenance, failure analysis, contamination audit, and exclusion only.
- A quarantine scoped to one analysis namespace is not a global lineage boundary.
  The old P1 snapshot passed before later DSA pilot scripts directly consumed
  EVP-7 metadata; recomputing it now fails. Never trust a stored audit status when
  the governed script set has changed.
- An `active` historical authorization remains executable unless a newer machine
  authority supersedes it at every entrypoint. Registry prose alone was
  insufficient: cursor configuration, stale cursor execution, pilot execution,
  and standing reactivation all needed guards before checkout, containers,
  credentials, or network access.
- Empty input is not evidence that a future dataset is clean. Report the current
  state as `armed_no_new_study` with data use explicitly false; require a nonempty,
  independently sourced, hash-bound manifest and pre-use author signoff before
  training or evaluation can become authorized.
- Use exact task and payload collisions as hard exclusions. Project overlap is a
  design decision with clustering and researcher-knowledge consequences, so the
  safe default is blocked; any future reuse must be decided in a new preregistration
  before data access rather than silently inherited from the old study.
- A repository-wide historical quality gate may itself execute obsolete audits or
  live network fetches. Here the aggregate gate exceeded 124 seconds after the
  legacy Springer-template fetch disconnected and left child audit processes
  running. Terminate only the processes started by the current run, record the
  diagnosis, and use the direct lineage/entrypoint/static Gates for the isolation
  claim; never relabel a timeout or stale prior output as a pass.
- Bind JSON policy and authorization metadata with canonical-JSON SHA-256 rather
  than worktree bytes. Windows CRLF and Git-index LF produced different byte
  hashes for unchanged JSON; canonical hashing removes that false drift. Continue
  to use raw-byte hashes for actual datasets, patches, responses, and signoffs.
- Derive exclusions from the complete source frame, not a convenient historical
  subset. The old 126-task projection missed touched records; the complete freeze
  contains 501 tasks and 17 projects. Compare task, project, source, and lineage
  identifiers case-insensitively after requiring trimmed, printable input, or a
  trailing space becomes an exclusion bypass.
- Keep exact patch payloads and conservative metadata identifiers distinct. Here
  522 hashes are exact patch payloads, while 3,420 hashes are the actual broader
  blocking set; reporting either count as the other overstates or understates the
  scientific exclusion boundary.
- A path denylist cannot stop a copied file, renamed file, or content restored
  from Git history. Bind cutoff HEAD blobs, all reachable-history blob IDs and raw
  SHA-256 values, plus cutoff-worktree raw SHA-256 values. The current freeze
  covers 1,515 HEAD paths, 3,232 history blobs, and 273,918 worktree files.
- Define the one-time fingerprint scope separately from runtime blocked paths.
  The former inventories old bytes wherever they existed at cutoff; the latter
  rejects known old locations in a future manifest. Conflating them can leave
  ignored outputs or root-level literal files outside one layer of the proof.
- A new-looking path is not independent data. Reject symlink, junction, and other
  reparse ancestors, reject hardlinks, resolve every file beneath the exact new
  namespace, and then compare both raw SHA-256 and Git blob identity.
- Lock execution coverage by an exact path count and projection hash. Broad globs
  initially missed `scripts/oracles/*.py` and the package CLI; the final boundary
  is 280/280 old research entrypoints guarded before any unsafe import or action.
- Validate only the canonical future manifest. Bind an exact study-specific
  signoff ID, signer identifier, UTC time not predating the manifest's
  Asia/Shanghai date or exceeding the current instant, registry hash, and pre-use
  manifest hash. Reject frozen study IDs and out-of-window manifest dates. These
  fields are auditable author attestations, not cryptographic identity or trusted
  timestamps.
- A sanctioned loader must recheck the entire isolation baseline on every read,
  not only validate file paths. Source hashes, task/project/payload projections,
  content registries, cutoff commit equality, and revoked authorizations all fail
  closed if changed. Hashing necessarily reads file bytes; the accurate claim is
  that credential values and research text were not interpreted or emitted.
- Repository governance is not an operating-system security boundary. Without a
  separate account or ACL, arbitrary programs running as the same user can read
  preserved historical bytes. State that limitation explicitly instead of
  claiming physical inaccessibility.

## 2026-07-13 Separate execution validation from favorable scientific outcome

- A pilot validates deployment only when every frozen route produces identity-
  valid, schema-valid, hash-bound records under the real transport path. A clean
  dry run or successful canary alone is insufficient; complete the frozen pilot
  unless an execution-integrity gate fails.
- Do not interpret an unfavorable direction as an execution failure. In this
  pilot, all 72 requests were operationally valid, while the hard-negative was
  still frequently accepted. Preserve that result and diagnose the research
  implication without rerunning, prompt editing, or route substitution.
- Keep two explicit conclusions: the end-to-end setting is executable; the
  one-pair development outcome does not establish effectiveness or generalize to
  a task population. This prevents engineering success from being promoted into
  a scientific claim.
- A tracked post-run audit should contain hashes, integrity counters, and
  aggregate decisions only. Provider payloads and rationales remain private raw
  evidence, while deterministic write/check preserves reproducibility locally.

## 2026-07-13 Bind standing authority to the scientific surface, not runner bytes

- Requiring a new author signature whenever implementation bytes change confuses
  scientific governance with engineering versioning. Freeze one immutable
  scientific-surface protocol and let each conforming runner aggregate derive a
  local execution record from the signed protocol.
- The surface lock must cover evidence selection/revalidation, model-visible
  packet bytes, prompt/schema, exact routes and parameters, normalized request
  schedule, repeats, exclusions, retry semantics, and no-outcome-rerun. Merely
  saying that a repair is "implementation only" is not a conformance proof.
- Preserve asymmetric resume semantics: pre-inference rejection with zero valid
  output can be reissued after a versioned repair; an HTTP 200 raw response is
  reparsed offline first; a valid model output is terminal and never requested
  again. Partial runs carry valid records forward and execute only unobserved work.
- Standing authority still stops on scientific-surface drift, hidden leakage,
  append-only/hash/raw-output failure, unclassified repairs, public release, and
  submission. Reducing signatures must not eliminate the author's scientific or
  publication decision points.

## 2026-07-13 Never serialize documentation sentinels into provider requests

- A frozen route can contain human-readable values such as `"omitted"` to document
  that a mutually exclusive parameter must not be sent. Treat these as manifest
  metadata, not executable values; strip them before request serialization and
  assert the final provider body contains only correctly typed token limits.
- Check concrete request bodies for every route. For Qwen, omit `max_tokens` and
  send integer `max_completion_tokens`; for DeepSeek/OpenRouter, send integer
  `max_tokens`. A valid manifest alone does not establish request-contract validity.
- Any HTTP error, parse error, schema failure, or identity mismatch is a non-valid
  terminal record and must hard-stop immediately after append-only recording.
  Transport retry policy must never turn an HTTP 400 into repeated canary traffic.
- Report endpoint requests separately from valid model outputs and scientific
  decisions. Eight pre-inference HTTP 400 responses mean eight API requests but
  zero model outputs; describing either count as the other corrupts the audit.
- A runner repair changes the execution surface. Preserve the failed ledger,
  archive its authorization, allocate a new request domain/output directory, and
  require a new aggregate-bound author signature before any repaired execution.

## 2026-07-13 Refreeze a provider change instead of treating it as a credential alias

- Moving Gemini from its native endpoint to OpenRouter changes provider, endpoint,
  request shape, credentials, identity semantics, and routing behavior. Revoke the
  old active authorization and create a new versioned freeze; never place an
  OpenRouter key in a native-provider credential slot.
- Preserve unchanged evidence, packets, prompt/schema, other model routes, and the
  request factorial. A route-only amendment should not trigger materialization or
  prompt redesign.
- OpenRouter defaults can select among providers and permit fallback. Freeze one
  exact provider tag, disable fallbacks, require parameter support, and opt into
  router metadata. Reject provider/model drift, multiple attempts, ambiguous
  selection, and pipeline transformations before accepting a response record.
- Bind the old authorization SHA and zero-call state in a revocation record, remove
  its active path so the old runner fails closed, and include that revocation in
  the new aggregate.

## 2026-07-13 Separate signed authorization from credential injection

- A valid hash-bound author signature does not imply that the runner process has
  credentials. Check exact frozen environment-variable names without printing
  values, and fail before creating outputs or making a request when one is absent.
- Historical aliases such as `QWEN_API_KEY` must not silently mutate a frozen
  credential contract. Inject the same real credential under the frozen name or
  stop; never alter the signed runner, invent a dummy key, or substitute a route.
- Treat a missing credential as an execution-boundary failure, not a prompt,
  evidence, schema, or model-quality result. Preserve zero-call state and resume
  from the same canary only after the missing external input exists.

## 2026-07-13 Freeze bytes and execution surfaces before an API pilot

- A prompt file, schema, and historical PASS audit do not mean a new experiment is
  deployed. Require real packets, an explicit request schedule, a guarded runner,
  exact route checks, append-only outputs, and a hash-bound author gate.
- Reuse old evidence only as development material. Select it mechanically before
  new model output, bind the selection preimage/hash, and permanently exclude it
  from confirmatory estimates and paper-facing effects.
- Historical summaries cannot be promoted into a stricter evidence contract.
  Re-run only the missing local checks in an isolated, network-disabled image and
  preserve command, exit code, output hashes, and image digest.
- On Windows, hashing an LF string before `write_text` can disagree with the CRLF
  bytes on disk. Write generated frozen artifacts as explicit UTF-8/LF bytes and
  make the execution runner verify byte hashes before reading credentials.
- A default check-only runner must fail closed when the author authorization file
  is absent. The negative execute test is part of the Gate; a successful dry run
  alone does not prove that credential or network boundaries work.
- Freeze all 72 requests before the eight-call canary. Canary verdict direction is
  never an execution criterion; only leakage, identity, schema, transport, hash,
  or append-only integrity failures may stop execution.

## 2026-07-12 Generalize only a hash-bound source-materialization exception

- A Windows-incompatible archive symlink is frozen source content, not an ordinary
  environment failure. Do not silently dereference, replace, or omit it.
- A reusable exception is safe only when every future task independently records
  path, target, kind, archive hashes and mechanically proves docs-only scope plus
  zero intersection with changed source, declared tests, project test roots, and
  package/build metadata.
- Bind the first observed manifest and the author's exact declaration before
  extraction. Any failed predicate remains a hard stop; this keeps the exception
  from becoming task-specific dependency or source repair.
- Keep the shared extractor fail-closed by default. Pass an exact omission set
  only from the V2-P2 cursor after the signed rule and task-local manifest pass;
  this avoids silently changing older P4/V2-P2 source semantics.
- A later Black task reproduced the same 13-link manifest under different
  archive hashes. Requiring a fresh per-archive manifest plus all predicates
  allowed automatic application without weakening the signed rule.

## 2026-07-12 Rebind every order-specific identity in a generic executor

- Repointing only file paths and `TASK_ID` is insufficient when reused modules
  also embed `ORDER`, record IDs, or replay assertions. A run can be scientifically
  valid while its ledger metadata still names order 1.
- When this is detected after a terminal oracle run, preserve container IDs and
  output hashes and repair only deterministic identity fields plus the dependent
  terminal digest. Do not rerun the observed tests.
- Finalize must take activity from the latest evidence layer (candidate results,
  then oracle, then environment); using environment unconditionally erases real
  container/test counts from oracle-terminal tasks.
- Cursor preflight assertions must bind `order == attempted_tasks + 1`, not a
  historical literal order. Otherwise a correct terminal ledger advancement
  makes the next task appear invalid.

## 2026-07-13 Terminalize only narrowly classified source failures

- A frozen task may have matching buggy/fixed commits and an empty reference
  patch. That is not hash drift when the immutable source record itself contains
  those values, but `git apply --check` cannot validate an oracle transform.
- Catch only reference-patch check/apply failures after archive and metadata
  verification, record archive/error hashes, and write a source terminal. Keep
  archive-root, metadata-hash, and dangling-predicate failures as hard stops.
- Derive changed-source paths lazily only when a dangling-link manifest exists.
  An empty reference patch on an archive without dangling links must reach the
  reference-validation terminal, not fail inside an unused omission rule.
- Two reference checks can both report `OK` yet fail the frozen dual-stability
  gate when their complete output hashes differ. Do not replace the registered
  fingerprint with the human-readable excerpt after observing this outcome;
  record a dual-disagreement terminal and continue.
- Pytest elapsed-time text is a concrete source of full-output hash instability.
  If the fingerprint was frozen before observation, normalizing that duration
  afterward is a protocol change, not an execution repair.

## 2026-07-12 Treat unavailable frozen prereleases as environment terminals

- If an exact frozen requirement names a prerelease that the configured index
  cannot supply, replacing it with the final release would be task-specific
  dependency repair and would change the materialized environment.
- Preserve the single build log/hash, record an environment-build terminal, and
  advance the source-order cursor without an oracle or candidate run.
- The same rule applies to development pins such as `ansible-base==2.10.0.dev0`;
  a nearby beta, release candidate, or final release is not an equivalent frozen
  dependency.
- A missing build executable discovered by editable-install hooks (for example
  `cython`) is also an environment terminal when it is absent from the frozen
  dependency recipe. Installing it after observation is task-specific repair.
- PEP517 can also request a build dependency whose current release line no
  longer supports the frozen Python (for example `cython>=3.1` on Python 3.7).
  Changing either side after observation is dependency repair.
- Platform-incompatible pins such as `pywin32` on Linux remain part of the frozen
  recipe. Removing them after a failed build is dependency repair, even when the
  incompatibility looks obvious.
- A successful editable install can still fail the frozen environment gate when
  package version provenance becomes `0+unknown` and violates another installed
  package's requirement. Do not patch version metadata or bypass `pip check`
  after observing the conflict.
- A Cython compiler crash inside an editable PEP517 hook is an environment
  materialization terminal under the frozen recipe. Changing Cython/setuptools
  after the observed crash is task-specific repair.

## 2026-07-12 Keep Windows archive staging paths deliberately short

- Large repositories can contain valid paths that exceed Windows `MAX_PATH`
  only after a long system-temporary prefix is added. That is an executor path
  bug, not a source-materialization outcome.
- Stage generic archive extraction under a fixed short drive-root directory and retry
  only when the failed attempt wrote no source registry or terminal evidence.
  Do not omit or rename archive members to work around the path length. The
  temporary directory must self-clean, while the final context remains in the
  ignored workspace runtime.
- Keep verbose versioned namespaces for tracked records, but map ignored task
  runtime directories to `tmp/dsa_r/oNNN`. Short staging alone is insufficient
  if the final context copy or Docker `COPY` target still reintroduces a long
  workspace path.
- Derive the official codeload archive root from the frozen repository URL
  basename, not the normalized catalog project key. Case-sensitive names such
  as `spaCy` are valid archive identity and must not be lowercased or treated as
  a source-content exception.

## 2026-07-12 Archive symlink fidelity is a frozen-content decision

- Normalize symlink targets before classifying them: Black's
  `docs/contributing.md -> ../CONTRIBUTING.md` resolves inside the archive,
  while thirteen generated-document links are genuinely dangling.
- On a host without symlink privilege, do not silently skip or replace dangling
  links. Freeze their path/target/kind and archive hashes, prove zero overlap
  with source/tests/build metadata, and require an author-signed extraction rule
  before materializing the tree.

## 2026-07-12 Advance cursor without mutating prior terminal evidence

- Each V2-P2 task needs a new result namespace and terminal draft. Treat the
  prior terminal ledger as a read-only cursor authority; append the new record
  only in the final audit after proving the prior record is byte-stable.
- Improving failure observability for a future task is allowed only before that
  task's outcome and must not alter dependency authority. Echoing the failing
  subcommand name and tail to the outer Docker log improves provenance without
  adding packages, changing tests, or reopening the previous terminal task.
- An absent setup file has no provenance hash. The shared source-copy helper's
  V2 alias expected `setup_provenance_only`, but FastAPI_11 has neither the file
  nor the field. Supply an unused empty adapter value only because the helper
  mechanically skips absent setup files; never synthesize or execute setup.
- FastAPI_11 demonstrates why both editable installation and `pip check` are
  environment Gates. Frozen pip20.1.1 cannot editable-install a pyproject-only
  tree without setup.py, while the frozen requirements simultaneously install
  Starlette0.12.8 against FastAPI0.55.1's exact0.13.2 constraint. Both are
  terminal evidence, not permission to upgrade tooling or change dependencies.

## 2026-07-12 Freeze the whole real runner before the first outcome

- A construction protocol is not protected from outcome-driven repair if only
  its prose is frozen. Before the first checkout, also freeze the source
  acquisition, image recipe, oracle collection/split, candidate materializer,
  dual-fresh executor, terminal writer, and every runtime authorization gate.
- Reusing a historical worker as a library is acceptable only when the active
  V2 entry point, image labels, source registries, and result namespaces are
  new and the generic worker semantics match the signed checks. Historical P4
  registries and cursors must never be active inputs.
- The V2 environment recipe deliberately differs from historical P4: official
  `setup.sh` is provenance only. Install the selected explicit Python lock,
  official requirements, the project via editable package metadata, and enforce
  `pip check`; any failure is terminal and cannot trigger a dependency edit.
- Candidate transform code needs behavioral-independent tests. A synthetic
  two-file/two-hunk patch can cover T1--T4 enumeration and prove every produced
  patch recreates its candidate tree before any real candidate outcome exists.
- A helper with a generic-looking name may still hide an old protocol cursor.
  The first V2 source-freeze attempt called P4 `build_context`, which internally
  required membership in the terminated P4 task list. Reuse only its pure
  archive/copy/apply primitives; construct V2 records directly from the signed
  V2 source order and never make a historical cursor an active dependency.
- Schema names can encode a scientific boundary. V2 renames the setup hash to
  `setup_provenance_only`; a pure copy/hash helper still expected `setup`.
  Adapt that name explicitly only at the helper boundary. Do not rename the V2
  record and do not let the alias make `setup.sh` executable authority.
- Failure provenance must escape the layer that can be discarded. The order-1
  Docker build redirected requirements/editable/pip-check logs into the image
  filesystem, so a failed `RUN` exposed only the aggregate exit and message.
  The outer build hash proves the terminal event but not its exact subcommand.
  Do not rerun the terminal task to improve logging; fix a future, pre-outcome
  runner version before another task if the signed protocol permits it.
- A task terminal is not automatically a cohort hard stop. Environment failure
  advances the frozen source cursor exactly once; only target completion or
  source exhaustion applies the V2-P2 global stop rule.

## 2026-07-12 Signed prose must match executable recipe fields

- A signed rule that refers to a value "declared by the project recipe" is not
  executable if the signed recipe records omit that field. A human-readable
  requirement does not substitute for the exact test root and collection
  adapter consumed by the runner.
- Detect this class of omission before checkout or test outcomes. Here the
  project-level roots can be derived without outcome data by splitting every
  frozen declared test path, normalizing it, and taking the longest common
  parent per project. The derived object still requires author sign-off because
  it completes an immutable signed protocol.
- Keep the amendment separate from the original manifest. Bind the proposed
  values by hash, preserve the original aggregate unchanged, and prohibit real
  activity until the author signs the exact amendment object.

## 2026-07-12 V2-P2 pure executor check-only

- A pre-materialization executor can be audited without giving it execution
  capability. Keep the state machine pure and inject synthetic observations;
  filesystem, process, network, container, test, prompt, and credential access
  belong only in a later explicitly authorized adapter.
- Do not trust a supplied candidate-order hash. Parse the exact canonical
  descriptor, reject field drift, and recompute the domain-separated SHA-256
  from the frozen seed and task id before accepting ordering or uniqueness.
- Positive path tests are insufficient for a frozen protocol. Also prove that
  out-of-order tasks, tampered hashes, noncontiguous ledgers, and execution after
  target/source terminal states are rejected.
- Selecting the first source-order identity is not starting a task. Record a
  pending cursor separately and keep checkout, environment, container, test,
  prompt, credential, and API activity counters explicitly at zero.

## 2026-07-12 Frozen-runtime collection compatibility

- A passing dual official F2P establishes the reference behavior but does not
  guarantee regression-pool capacity. The generic discovery worker can still
  fail inside an older frozen Python runtime before producing candidates.
- Treat a discovery parse failure with zero pool capacity as an ordinary
  pre-model materialization terminal when source, environment, and dual F2P
  evidence are already intact. Do not repair the shared adapter for one task or
  rerun the oracle after observing the outcome.

- Native-extension projects can pass source integrity yet fail before tests
  because the frozen generic image lacks a system development header. Record
  the compiler error as environment materialization evidence; adding an OS
  package after seeing it would be task-specific dependency repair.
- A top-level Cython requirement may appear satisfiable while a recursively
  built native dependency introduces a newer Python-incompatible Cython floor.
  Preserve the complete nested resolver trace and classify it as the frozen
  environment outcome; do not pin the transitive build dependency post hoc.
- Official catalogs may freeze an unambiguous abbreviated Git SHA while
  codeload names the archive root with the full SHA. Accept this only as a
  mechanical expansion: one canonical repository root, a 40-hex suffix, and a
  strict match to the frozen 7--39 hex prefix. Never accept a different root,
  non-hex suffix, or prefix mismatch.
- A task can pass source-time reference validation, environment build, dual
  F2P, and regression-pool stability yet fail the final oracle-positive replay
  because the official patch no longer applies inside the built image. Under a
  frozen no-rerun protocol, preserve both the earlier valid source evidence and
  the later built-image failure; do not post hoc repair the worker or patch.
- A transport-success exit is not archive integrity. Parse the complete gzip
  tar before source materialization; an unexpected EOF must leave the task
  unstarted and may only retry the identical official object. Never let a
  partial codeload file become a source record.
- An explicitly frozen `requirements_metadata.present=false` is not an error
  and must not be converted into a synthetic empty requirements file. The V2
  metadata copier should preserve absence, while the generic build records a
  deterministic no-install requirements step and continues to editable install
  and pip-check. Missing files remain errors whenever the frozen flag is true.

## 2026-07-12 V2-P1 metadata and base-lock freeze

- Source-frame eligibility does not imply that every official task directory
  contains a `requirements.txt`. Treat missing and empty files as an explicit
  absence of extra task requirements, record file presence, and continue to
  use project package metadata as the generic runtime-dependency authority.
  Do not synthesize a requirements file or infer task-specific packages.
- A textual phrase such as "frozen bootstrap" is not an executable freeze.
  Bind exact pip/setuptools/wheel/pytest/packaging versions and every Python
  explicit-lock path/hash before V2-P2 so environment resolution cannot drift.
- Transcribed hashes require a second authority. The first V2-P1 script draft
  copied the wrong Python 3.7.7 lock hash; cross-checking the existing P4
  preflight constant and the lock file itself identified the mismatch before
  any environment build or task outcome.
- A complete source order is safer than a small preselected reserve when
  pre-model materialization loss is unknown. Domain-separate the seed, order
  projects and tasks by hashes, then process project queues round-robin until
  30 pairs qualify or all eligible sources are exhausted.

## 2026-07-11 Confirmatory cohort must follow stimulus qualification

- An external improved-reproduction pass is provenance, not a clean task
  qualification when the external runner reuses environments by Python version
  and requirements hash. Freeze a construction rule first, but do not freeze
  the confirmatory cohort until every retained stimulus has been built and
  behavior-qualified under that rule.
- Structural transform applicability is insufficient for a reviewer-agent
  experiment. A negative stimulus must pass syntax/basic and every visible
  check before its hidden failure is scientifically interpretable; otherwise
  the model is being asked to detect a trivial broken artifact rather than
  respond to increasing evidence.
- Reserves drawn from the same project do not hedge project-level setup or
  dependency decay. Capacity planning must treat environment signatures as
  correlated and construct a qualified pool before freezing the final sample.
- Terminating a preregistered version before model output is not the same as
  claiming its capacity stop rule fired. Preserve the signed artifacts, record
  the deviation/termination explicitly, publish no confirmatory estimate from
  that version, and make the redesign a separate author-signed study version.
- For an evidence-conditioned response study, exact historical benchmark
  setup reproduction is one possible stimulus-construction method, not the
  research outcome. The necessary boundary is stable paired candidate behavior
  plus command/result/environment provenance; avoid turning environment
  archaeology into the main experiment.

## 2026-07-11 DSA P4 bootstrap and pre-transform audit

- Official GitHub codeload archives can contain symlinks that Windows cannot
  recreate in a Docker build context. Validate every link stays inside the
  archive root, then materialize its target content and record the count; keep
  the original archive SHA-256 as the source-provenance identity.
- BugsInPy `bug_patch.txt` may use CRLF while its codeload source uses LF. Keep
  and hash the raw metadata unchanged, but apply an explicitly hashed LF
  validation copy. Do not use whitespace-ignore patch matching because that
  weakens the reference-integrity gate.
- A frozen `unittest` task cannot be sent through a pytest-only oracle worker.
  Before any reference outcome, add a standard-library discovery adapter that
  emits dotted test IDs and execute each ID with `python -m unittest -q`; keep
  the source-token/tie-hash selection and dual-fresh-container rules unchanged.
- Do not silently treat standard-library modules named in benchmark setup
  metadata as no-op dependencies. Tornado bug 10's frozen `pip install
  unittest` has no installable distribution and made aggregate setup status 1.
  Even though later setup commands and `pip check` passed in the disposable
  diagnostic container, the task-specific image correctly failed to build and
  the task had to be discarded before F2P, pool discovery, or candidate work.
- The P3 phase generator is not the post-P3 immutable replay entry point: its
  derived Gate records every path changed since the P2 commit, so authorized P4
  files necessarily make that derived JSON differ. During P4, verify the frozen
  P2/P3 file hashes through `dsa2026_p4_preflight.py --check`; do not regenerate
  or edit any P3 artifact to silence the phase-scoped mismatch.
- A replacement cursor must join every terminal disposition registry, not only
  candidate task Gates. After Tornado failed its environment Gate before F2P,
  a task-Gate-only cursor still selected Tornado. Bind the pre-candidate discard
  registry by hash, require the terminal sets to be disjoint, and count both
  categories in reserve allocation and capacity before selecting the next task.
- Historical discard replay must bind the cursor that selected the task, not
  require the live cursor to remain on that task forever. Use the task-source
  record's frozen cursor SHA as the historical anchor; otherwise a legitimate
  cursor advance makes prior environment evidence falsely unreplayable.
- Improved BugsInPy's Conda environment name hashes only Python version plus
  `requirements.txt`; tasks with the same version and empty requirements can
  therefore reuse packages installed by earlier tasks' setup commands. Treat
  source-frame buggy/fixed logs as provenance, not proof that a fresh P4 image
  has those undeclared dependencies. A P4 task must use its isolated explicit
  lock and frozen metadata without importing the shared environment state.
- Dual-environment equality must compare stable environment evidence, not wall
  time. Keep command, exit/timeout/outcome, normalized output hashes, and every
  build-artifact hash in the fingerprint; retain durations as provenance but do
  not make two otherwise identical fresh runs disagree because they took
  different milliseconds.
- A successful task-image build with empty requirements is not an executable
  reference Gate. Matplotlib #21 built cleanly but both isolated F2P runs failed
  identically while importing NumPy. Do not reinterpret a shared historical
  Conda environment's installed packages as frozen metadata or add them after
  observing the failure; discard before pool/candidate activity.
- A hash-ordered transform is not reproducible until its edit identity and
  serialization are explicit. Before any candidate outcome, encode each T4
  source-diff line as canonical JSON over path, hunk index, line index, kind,
  and value; order by SHA-256 and freeze the chosen identity together with both
  candidate patch/tree hashes in a separate commit. Do not run syntax or tests
  until that commit exists.
- Read official patches as raw bytes for provenance hashes, but normalize CRLF
  to LF before passing text to `unidiff`. Feeding preserved CRLF lines directly
  caused duplicate paths with trailing `\r`; the structural assertion stopped
  materialization before any candidate registry or outcome was written.
- Candidate containers can retain the exact frozen task-image ID without a
  writable mount: create each stopped container with `network=none`, copy the
  committed worker and hash-bound patch into its private filesystem, inspect
  mounts/image/network, and only then start it. Use a distinct patch path per
  concurrent run so two fresh runs cannot race while writing one host file.
- A host-side `git apply` success does not prove a patch serialized with LF will
  apply inside a Linux container when the Docker context preserved CRLF source.
  The first candidate start failed at the integrity check before any test
  outcome. Preserve the official raw patch bytes for the positive, serialize
  the transformed patch with the official newline style, and restore a removed
  T4 line using the target file's newline style. Keep the same selected edit
  hash; this is an execution repair, not outcome-dependent candidate selection.
- Hidden failure is necessary but not sufficient for a hard negative. The first
  T4 candidate failed `py_compile`, the F2P, all three visible P2P checks, and
  all 20 held-out nodes consistently in both containers. Even though the hidden
  failure signal was maximal, the frozen visible-pass prerequisite requires a
  task discard. Never reinterpret a syntax-invalid partial patch as a stronger
  negative or switch to a different hash-ordered edit.
- A discarded task must contribute zero records to the admitted model-visible
  manifest. Keep its full 2-candidate x 2-container evidence only in the hidden
  tree, emit a task Gate and separation audit, decrement the nonstructural
  discard allowance, and defer reserve consumption to the next explicitly
  bounded P4 Goal.
- Primary and reserve order need an explicit execution cursor, not only two
  frozen arrays. The pre-outcome trajectory already skipped structurally
  inapplicable primary #1 and entered primary #2 before reserve #1, so preserve
  a primary-first scan: allocate realized discard slots to the reserve prefix,
  but execute that prefix only after the primary scan. Recomputing the cursor
  then skips structural primary #3 and uniquely selects primary #4
  `bugsinpy_tornado_10`; it does not use the direction of the FastAPI outcome.
- Capacity accounting must include future structural discards even before the
  cursor reaches them. Four structural primary discards plus one terminal
  candidate discard leave at most 35 complete pairs from 40 frozen sources,
  hence exactly five further discard allowances for a 30-pair target.
- A stopped reproduction container can contain fresh official Git objects even
  when its environment build failed. Export a Git bundle from committed refs
  only; never carry its dirty worktree, copied benchmark index, logs, or prior
  outcomes into a clean source snapshot.
- BugsInPy's improved runner copies its own historical `bugsinpy-index.csv` and
  CRLF shell scripts when the repository is mounted from Windows. A true run
  must remove the copied index/temp state and normalize executable scripts
  before invoking the framework; otherwise it can silently skip work or fail
  with `/bin/bash^M`.
- Container TLS EOF affected the official Anaconda, PyPI, and GitHub endpoints
  while HTTPS mirrors passed certificate verification. Keep `ssl_verify=true`,
  freeze a single mirror and explicit package URLs, and put network resolution
  in the image-build phase rather than disabling TLS or retrying during the
  experiment.
- Old Python alone is not a sufficient environment lock. Conda selected
  setuptools 75.1.0, then the 2020 requirements installed packaging 20.4;
  setuptools called an API absent from that packaging version and project
  installation failed before the F2P ran. Pin pip 20.1.1, setuptools 47.1.1,
  wheel 0.34.2, pytest 5.4.3, and packaging 20.4 together, then verify the
  actual target node. The repaired fresh sanic run produced buggy=fail and
  fixed=pass.
- BuildKit treats an unqualified local `image@digest` in `FROM` as a registry
  reference and may contact Docker Hub. Use the local frozen tag only after a
  mandatory RepoDigest assertion; record both the expected base digest and the
  resulting toolchain image ID.
- P2 froze transform priority, not a per-task candidate. P4 must compute shape
  over the official source-only `bug_patch.txt`, exclude test paths from all
  candidate edits, and record atomic patches as no-transform discards before
  any outcome. With 36 structurally eligible tasks for a 30-pair target, only
  six further exclusions can occur without `STOP_DSA`.
- Do not normalize an entire frozen metadata directory. Some BugsInPy source
  files and patch contexts both use CRLF; converting only `bug_patch.txt` to LF
  preserves neither the raw metadata hash nor patch applicability. Keep every
  metadata file byte-identical and strip `\r` only from a command string in
  memory when it is executed.
- `pip check` can report benchmark-snapshot conflicts even when the checked-out
  local source has the declared historical dependencies and the official F2P
  executes correctly. Preserve the conflict log and exact `pip freeze`; do not
  silently upgrade dependencies to make metadata green. Environment admission
  is based on the frozen image plus real dual-reference checks, not a rewritten
  dependency graph.
- Full-tree pytest collection can fail on optional tutorial modules while still
  yielding hundreds of valid nodeids. Collection is only discovery: freeze the
  pool before outcomes, then require each selected node to pass independently
  in two fresh reference containers. Never treat collection visibility as a
  passing oracle.
- Container output hashes need not match when pytest embeds elapsed time. Treat
  normalized scientific consistency as identical node identity, exit code,
  timeout state, and pass/fail outcome; retain both output hashes and excerpts
  for diagnosis instead of silently deleting timing-bearing evidence. For the
  first FastAPI pool, all 40 outcomes agreed although only 13 timing-bearing
  output hashes were byte-identical.

## 2026-07-11 DSA P3 candidate freeze and author gate

- Final closure should bind the exact author declaration, not just a copied
  checkbox state. Store the exact UTF-8 user message, define terminal-newline
  canonicalization, recompute its SHA-256, and include both declaration and
  sign-off record in the immutable manifest.
- An immutable P3 audit must prove the previous phase stayed frozen. Compare
  the P2 protocol, source order, transform registry, and development exclusion
  against their P2 SHA-256 values, and restrict every post-P2 tracked/untracked
  change to a P3 allowlist. A current hash alone cannot prove non-mutation.
- Cross-platform text manifests must define line-ending canonicalization.
  Windows `core.autocrlf=true` can convert newly generated LF files to CRLF on
  checkout; hash P3 UTF-8 text after CRLF/CR-to-LF normalization while keeping
  the already-frozen P2 raw-byte hashes as a separate invariant.

- Exact model ID is necessary but not sufficient. Freeze endpoint, reasoning
  control, JSON transport, output cap, response identity, price snapshot, run
  window, ordering, retries, and no-fallback behavior; any provider drift must
  stop rather than select a replacement.
- Provider-native controls are not symmetric. Qwen and DeepSeek can be frozen
  in non-thinking mode, whereas the current stable Gemini route exposes
  `minimal` as its lowest documented thinking level and recommends omitting
  sampling parameters. Record that asymmetry instead of pretending the same
  parameter has the same semantics across providers.
- A prompt leakage audit must separate prompt semantics from packet leakage.
  The prompt necessarily defines the output decision field, so recursive
  forbidden-key checks apply to the extracted serialized packet while prompt
  checks target condition cues, expected answers, and policy prescriptions.
- Synthetic rendered prompts can validate serialization and cumulative
  C0--C3 behavior without creating held-out candidates. Store only canonical
  packet/render hashes and errors, not rendered prompt text.
- A mechanical preregistration Gate cannot establish authorship responsibility.
  Keep the manifest mutable and P3 pending until the named author explicitly
  accepts the scientific design, AI-policy duty, and responsibility for every
  result and claim.
- Do not implement author sign-off as a single boolean. Require a real author
  name, timezone-qualified timestamp, the exact ordered set of preregistered
  item IDs, scientific-responsibility confirmation, and a hash tied to the
  actual user declaration. Negative tests must show that status-only, partial,
  or declaration-free records cannot pass.
- Conditional repeat-block intervals describe response stochasticity for
  frozen tasks/models. Pair C3 and C0 within repeat, keep task as the only
  scientific unit, and label project reweighting/deletion ranges as stability
  analyses rather than confidence intervals.

## 2026-07-11 DSA P2 source feasibility and protocol freeze

- A paper-result exclusion registry can still miss engineering probes. P2 must
  combine the P1 result quarantine with registered checkout/P2P development
  task IDs. The final source exclusion is 59 tasks, while the eight old paper
  projects remain excluded wholesale.
- Git object IDs in benchmark metadata may be abbreviated. Requiring exactly
  40 hex characters incorrectly rejected 168 pandas records; accept an
  unambiguous 7--40 character hex ID and verify reachability later.
- Environment failure is not automatically task failure. The BugsInPy
  reproduction study shows original virtualenv decay and improved Conda/Docker
  reproduction. Use buggy=fail/fixed=pass in the improved environment for P2
  source feasibility, record original decay as risk, and still require two
  fresh clean-environment candidate runs in P4.
- Protect one reserve per project before allocating primary tasks. Otherwise a
  small project can consume all eligible tasks as primary and make the project-
  count gate impossible to preserve when one task fails later.
- Transform validation should expose non-applicability. Sixteen atomic one-edit
  development patches do not support a principled partial-reference transform;
  marking them non-applicable is safer than inventing a task-specific mutation.
- Conditional repeat precision is not population precision. The P2 simulation
  conditions on fixed tasks/models and estimates only stateless repeat-window
  decision stochasticity; task/model/request counts must never be presented as
  independent external samples.
- Citation tooling can fail on valid arXiv-issued DOIs through Crossref. Recover
  bibliographic records from official arXiv pages, record the retrieval error,
  and keep one final RIS instead of treating missing Crossref metadata as a
  missing nearest neighbor.
- The nearest-neighbor boundary is substantive: LLM4PatchCorrect, PatchZero,
  SWE-PRBench, CodeJudgeBench, and requirement-conformance review overlap with
  parts of the design. The safe position is finite-cohort evidence-conditioned
  patch gating, not first/unique/SOTA or autonomous correctness verification.

## 2026-07-11 DSA P1 legacy-evidence quarantine

- Removing only named top-level verdict fields is not a no-verdict guarantee.
  The old E6 ablation left `visible_tests_rule_decision` nested under P2P
  evidence in 98/98 packets. Leakage checks must recurse over the complete
  model-visible object and reason about verdict-like semantics, not only a
  short forbidden-key list.
- A field name is not executable evidence. The old constructors emitted
  `not_run`, `not_recorded`, `not_separately_materialized`, and empty P2P
  collections while presenting a multi-level evidence ladder. Gate evidence
  on actual materialization before any API call.
- Failure reproduction does not require reopening sensitive payloads. Synthetic
  empty patch/test inputs can exercise the retired constructor and isolate its
  schema/control-flow defect without reading patch text, prompt text, raw model
  outputs, credentials, or making API calls.
- Preserve invalidated results as provenance instead of deleting them, but
  enforce their permitted uses mechanically. A denylist plus a namespace scan
  is stronger than prose saying that old numbers should not be reused.
- An exclusion registry is not a candidate source. The frozen union of 28 old
  tasks and 8 old projects can only prevent task/project reuse in P2; selecting
  from it would invert the independence rule.
- Venue policy/EI evidence and scientific validity are different gates. Missing
  external DSA confirmation blocks submission, while no-API venue-neutral
  scientific preparation can proceed. Model execution remains gated by P1--P5,
  and DSA submission remains gated by V0.

## 2026-07-11 DSA P0 official-template and policy gate

- Venue wording matters. The DSA track page explicitly says the 12/10-page
  limits include content and references, while the generic submission page only
  says maximum pages. Freeze the track-specific statement and do not preserve
  the earlier "unclear references" assumption.
- "Submitted for possible inclusion" is not an Ei guarantee. IEEE Xplore IDs,
  catalogs, and ISBNs for prior DSA proceedings are useful search keys, but D0
  requires actual Engineering Village/Compendex accession evidence.
- A general IEEE AI policy does not answer a missing venue-specific rule. This
  project has substantive AI help beyond grammar editing, so it needs a factual
  inventory and Secretariat disposition rather than relying on the grammar-only
  exception.
- Cloudflare-obfuscated conference email links can be decoded from the
  `email-protection#` hex token by XORing each subsequent byte with the first
  byte. The official DSA contact resolved to `zxc190007@utdallas.edu`; preserve
  the retrieval source and date.
- MiKTeX `latexmk` can exist while remaining unusable because it requires a Perl
  script engine. Diagnose this before changing TeX. For a simple deterministic
  skeleton, two direct `pdflatex` passes are the shortest valid repair and avoid
  installing an unrelated runtime.
- The official sample's optional `titlesec` and single-page `balance` call
  caused warnings/overfull output in the minimal skeleton. Removing only those
  nonessential skeleton uses, while leaving `IEEEconf.cls` byte-for-byte
  unchanged, produced a zero-warning second pass.
- A template PDF with placeholder author metadata is a technical build proof,
  not a passed authorship gate or submission-ready paper. Keep D0.6 partial
  until real author metadata and live rules are rechecked.
- Standing API authorization removes repeated budget questions but does not
  bypass scientific gates or hard caps. Record the authorization now and keep
  P0 strictly no-API until D0 and P1--P5 have passed.
- If private GitHub synchronization repeatedly fails, log the failure and keep
  the local scientific loop moving as the user instructed. Never reinterpret
  that instruction as permission to push the identity-linked public origin.

## 2026-07-10 DSA route lock and no-rerun design

- A venue pivot does not rehabilitate invalid evidence. The APSEC draft, old
  prompts, current-98/HARD/coverage/stress outputs, and candidate-level
  intervals remain exploratory after selecting DSA; they must be quarantined
  from the new title, abstract, results, confidence intervals, conclusion, and
  main figures.
- Lock the paper type before any model call. DSA Regular is the sole target;
  Short is an independently sized pre-API protocol, never a wrapper for weak
  Regular results. A null or unfavorable frozen result is reportable evidence,
  not a reason to change tasks, models, prompt, oracle, or repeats.
- One question is safer than two confounded interventions. Removing the old
  C4/C5 synthetic-advisory branch reduces request volume and leaves one
  auditable contrast: real cumulative executable evidence C0--C3 on paired
  positive and hidden-failing candidates.
- A balanced challenge cohort is not a prevalence sample. Task is the analysis
  unit; model/repeat/request counts do not increase its external n. Conditional
  intervals may estimate only stateless response variability for the frozen
  tasks/models/run window; project reweighting and leave-one-out show stability,
  not population confidence.
- Never test a candidate transform on would-be primary tasks before freezing it.
  Design and mechanically validate the transform registry only on permanently
  excluded development tasks; select sources without candidate outcomes, sign
  the registry, then apply it once to primary/reserve in fixed order.
- Run a nearest-neighbor literature gate before paying for model calls. A
  technically valid experiment can still be a poor submission if direct LLM
  patch-verifier/critic/ranker work removes the claimed gap. Novelty phrases
  require a search log, full-text verification, and claim-to-citation map.
- Treat AI policy as a scientific gate, not late boilerplate. Separately record
  LLMs as experimental subjects, AI help in design/code/statistics, and AI help
  in writing; author review does not erase substantive AI participation.
- A seven-page `IEEEtran` PDF is not a DSA submission template. Rebuild in a new
  namespace with official `IEEEconf.cls`, readable figure/table text, clean
  hashes, and distinct initial-submission, camera-ready, and presentation gates.
- The identity-linked public origin is not the private development remote.
  Prefer an independent private repository named `private`; until its URL and
  venue disposition are recorded, commit locally and do not push this route to
  the public origin.

## 2026-07-10 Legacy EVP-8 prompt retirement

- When a prompt family is invalid for confirmatory reuse, retaining it under
  the active prompt path makes accidental reruns and silent inheritance more
  likely. The user therefore authorized physical deletion of all four legacy
  EVP-8 templates after their SHA-256 values were recorded.
- Do not delete or rewrite historical protocol, manifest, packet, result, or
  audit references. Git history plus the retirement hashes preserve what was
  actually run; changing those paths would falsify provenance.
- A prompt change log is an audit record, not a prompt. Keep it in the active
  tree and record deletion, conflict checks, rationale, and the absence of a
  replacement.
- Historical configs and runners must never be silently repointed to a new
  prompt. A future EVP-v0.4 chain needs a new namespace and independent gates.
- Earlier notes that call v0.1/v0.2 the `main` or `frozen` EVP-8 prompt describe
  their historical experiment sequence only. They are superseded by this
  retirement and do not authorize execution.

## 2026-07-10 APSEC/CCF-C evidence-validity reset

- Removing only top-level verdict keys does not create a no-verdict condition.
  The old E6 ablation removed the E6 summary decision but retained the nested
  E4 visible_tests_rule_decision; a recursive packet and rendered-prompt
  denylist is required.
- A field named regression evidence is not evidence when test names/outcomes
  are empty, and not_run or not_recorded is not an evidence level. Paper
  terminology must follow materialized commands and outcomes.
- Prompt repair on a cohort converts that cohort into development data. The
  same task/candidate set cannot later be presented as independent
  confirmation, even when prompt and packet hashes are frozen.
- Candidate-level Wilson intervals are invalid for a cohort with multiple
  related variants per task and heavily unbalanced projects. Task is the main
  unit; project-to-task hierarchical resampling preserves the design.
- An all-negative stress set can measure false-accept handling but cannot
  estimate correct recall or demonstrate useful automation. Always-escalate
  must be shown as a strong risk baseline.
- Do not repair the old EVP-8 runner with another compatibility branch. Build a
  new fail-closed EVP-v0.4 chain in which real evidence bundles and the
  synthetic advisory cue are orthogonal.
- Freeze and hash each task's visible/hidden oracle split before constructing
  any mutant candidate. Changing an oracle after candidate materialization is
  label-design leakage and invalidates that task.
- Planned requests are not the authorization ceiling when retry exists. A
  global retry cap must turn 3240 unique full requests into an explicit 3402
  maximum attempts, with cost calculated at the hard maximum.
- Current fresh-project readiness is zero, so the 30-task cohort is not an
  available input. A no-API source-feasibility gate must pass before protocol
  freeze; a deadline is not evidence that tasks can be materialized.
- Venue policy is an experimental gate, not final formatting trivia. APSEC 2026
  permits only minor AI language assistance and forbids substantive AI-generated
  research content, claims, analysis, results, or manuscript text; provenance
  clearance must precede further venue-specific work.
- Git hygiene and double-blind policy can conflict. The current identity-linked
  public GitHub repository must not receive APSEC-facing updates during the
  anonymity period; project sync can resume only on a user-approved
  private/anonymized GitHub remote or after the APSEC route is stopped.
- The master route is recorded in
  docs/plans/apsec_ccfc_evidence_repair_plan_zh.md. Old current-98,
  EVP-8-HARD, coverage, and stress-31 results remain auditable history but are
  no longer confirmatory paper evidence.

## 2026-07-06 APSEC IEEEtran compile and layout audit

- Do not store LaTeX compile stdout in tracked JSON audits. MiKTeX logs include
  local absolute paths, which can leak the local user name and violate the
  double-blind boundary. Store command names and exit codes only.
- Markdown-to-LaTeX table conversion needs special handling for long
  identifier-like tokens. Wrapping underscore/slash tokens with breakable table
  formatting and reducing local `tabcolsep` lowered APSEC overfull warnings
  without changing paper claims.
- Page count alone is insufficient. The APSEC draft is within the 10-page
  boundary, but a render audit is still needed to catch blank pages, obvious
  layout failures, and stale non-anonymous/stale-claim wording.
- Compile-derived audits should be regenerated through the source generator,
  not by hand-editing `.tex`, because the Markdown-to-LaTeX package is
  generator-owned.

## 2026-07-06 hard-negative stress matrix manuscript synchronization

- When a late experiment changes the paper-facing boundary, update the
  manuscript generator, claim map, reviewer audit, and figures together. Editing
  only the Markdown can leave stale claims in generated artifacts.
- The 31-case hard-negative stress matrix improves the paper only as bounded
  triage evidence. It reduces repeated false accepts from 62/93 to 12/93 under
  coverage-contestation, but strict reject remains 0, so the result must not be
  described as semantic correction.
- Stress-cohort correct recall is undefined because all 31 cases are
  hidden-failing hard negatives. Any table or abstract that implies recall
  improvement on this cohort is logically invalid.
- Stale wording such as a failed three-project realistic gate can survive in
  figures and claim maps even after the main manuscript is fixed. Add forbidden
  wording checks to the reviewer audit whenever a claim boundary changes.

## 2026-07-06 EVP-8 prompt-setting audit

- A weak verifier result can be caused by the prompt/evidence setting without
  being a prompt bug. For EVP-8 repaired v0.3, the visible-only prompt and E6
  deterministic visible merge-gate summary are internally valid, but they make
  tool-following behavior expected.
- Do not silently repair the main evidence-visibility prompt by importing the
  tool-contestation prompt. The contestation prompt asks a different question:
  whether visible-test-only accepts should be challenged for coverage risk.
- E6 no-verdict is the right diagnostic for verdict anchoring, but its result
  must be read model by model. DeepSeek becomes much more conservative without
  verdict fields; Qwen remains close to the full E6 condition, so visible
  tests/tool evidence alone can still anchor decisions.
- A strong rule-only visible-tool baseline creates a headroom problem. On the
  frozen 98-candidate EVP-8 cohort, only 6/98 cases are tool opportunity cases,
  so large LLM gains should not be expected without a new hard-negative cohort
  or a different risk-triage condition.
- The safe paper phrasing is evidence-conditioned merge-gate policy behavior,
  not autonomous semantic correctness verification.

## 2026-07-03 final experiment-setting validity audit

- For a stable CCF-C paper route, the immediate risk is no longer whether a
  third realistic project can be repaired; it is whether existing results are
  artifacts of prompt setup, label leakage, parser loss, or post-hoc mixing.
- The final validity audit should pass only with bounded claims. A pass means
  the current results are usable as real bounded evidence for
  evidence-conditioned risk behavior, not that the system is a reliable
  autonomous correctness verifier.
- Paper-facing behavioral claims should come from accept-aware repaired
  analyses and their label-conditioned checks. Invalid earlier settings should
  not be kept in the manuscript as results or as a standalone explanatory
  storyline.
- Hidden evaluator labels may be used only after execution for analysis. The
  manuscript must state this separation rather than assuming readers infer it
  from artifact names.
- Luigi source acquisition is now optional future work for a higher-ambition
  route. It should not block the CCF-C manuscript unless the claim is upgraded
  beyond the bounded risk-behavior framing.

## 2026-07-02 third-project source selection

- The third-project gate should be repaired by source selection and
  materialization design, not by blind repeats of the same generation API
  interface.
- Projects with observed no-yield outcomes should not be reused as if they
  were promising by default: `httpie` produced hidden-failing candidates that
  failed visible tests, `thefuck` produced visible-pass/hidden-pass candidates,
  `tqdm` produced visible-fail/hidden-fail candidates, and the later
  `youtube-dl` full-file attempt produced visible-pass/hidden-pass candidates.
- Luigi remains a defensible next source only because the prior Luigi attempt
  failed before candidate construction. That makes the blocker a
  materialization/protocol problem, not evidence that Luigi has already failed
  the visible-pass/hidden-fail yield gate.
- Selecting Luigi does not authorize generation or verifier APIs. The next
  artifact must be a no-API Luigi source-acquisition/materialization protocol
  with dry-run, validation, and leakage gates. If that protocol cannot be made
  coherent, the paper should keep the fresh realistic branch as a two-project
  source-acquisition negative result.

## 2026-07-02 plan de-stacking audit

- Append-only plan logs can become logically unsafe even when every individual
  entry is true. Old branch names, sync hashes, and "next step" statements must
  be demoted to historical audit records once the active branch or research
  route changes.
- The short state file must name the active branch, remote branch, latest
  semantic commit, and unique next action at the top. Future agents should not
  infer current execution state from older `origin/main` entries in the long
  plan log.
- A boundary packet passing is not the same as an experiment gate passing. The
  current realistic hard-negative route remains blocked until the tracked gate
  reaches at least 30 visible-pass/hidden-fail cases across at least 3 projects.
- Do not solve plan clutter by deleting experiment history. Keep provenance,
  but add explicit hierarchy: current authority, active next action, historical
  audit records, and long-term alternatives.

## 2026-07-02 paper-uplift planning boundary

- The current paper should be positioned as an evidence visibility and risk
  behavior study, not as a reliable autonomous patch correctness verifier.
- The strongest current EVP-8-HARD improvement is escalation-driven safe
  handling, not semantic strict correction: strict reject remains zero on the
  known false-accept opportunity set. Keep `strict correction` and
  `safe handling` separate in all future tables.
- Do not improve the paper by adding more models under the same evidence
  boundary. The current bottleneck is external validity and opportunity-set
  size, especially the failed fresh realistic 30-case / 3-project
  verifier-readiness gate.
- A future realistic verifier experiment must first pass the source gate:
  patch applies, declared visible tests pass, hidden evaluator fails, at least
  30 cases, and at least 3 projects. Until then, Qwen/DeepSeek verifier API
  calls on that branch would only create unsupported results.
- If the gate passes, run the smallest useful model comparison: Qwen and
  DeepSeek only, with tool-only, with-verdict, evidence-only, and
  tool-contestation rows. The core question is whether LLMs reduce visible-tool
  false accepts or merely route them to escalation.
- A boundary packet can pass while the experimental gate fails. For the
  realistic hard-negative uplift packet, `passed=true` means the blocker is
  explicit and machine-readable; it does not mean the branch is verifier-ready.
  The current blocker is concrete: 26/30 visible-pass/hidden-fail cases and 2/3
  projects.

## 2026-06-30 SQJ availability boundary gate

- Data/code availability wording is a separate submission-package boundary,
  not a final artifact release decision.
- The SQJ draft should say that tracked artifacts use raw-output-free
  summaries and paper tables, while raw model responses, local API config,
  ignored execution logs, `.env`, `outputs/`, and `artifacts/` remain outside
  the tracked package boundary.
- Keep this check as an executable gate because otherwise availability wording
  can drift when final-freeze readiness, artifact dry-runs, and broad API
  authorization are edited independently.
- Passing `sqj_availability_boundary_ready` does not authorize submission,
  final artifact rebuild, model API calls, or final freeze.
- If the local gate commit succeeds but GitHub fetch/push cannot reach
  `github.com:443`, record the sync failure explicitly and leave the local
  commit intact for a later retry. Do not report GitHub sync as complete.
- A later direct tree-sync push can succeed even if an earlier fetch failed.
  After any such push, fetch again and compare local `HEAD^{tree}` with the
  remote branch tree before treating GitHub sync as complete.

## 2026-06-30 broad API authorization boundary

- A broad user statement authorizing all APIs should be treated as a human
  authorization condition, not as a concrete execute command.
- Real API execution still needs a named experiment, candidate set, model id,
  local config, strict preflight, output boundary, cost boundary, and stop
  condition recorded in `docs/plans/current_plan_zh.md`.
- Do not use broad API authorization to override SQJ final-freeze blockers,
  submission authorization, artifact release authorization, or claim-boundary
  gates.
- Before any new EVP-8-HARD call, first check whether the intended Qwen/DeepSeek
  results already exist. The current E6-evidence-only Qwen and DeepSeek parsed
  reviews already cover 47 candidates and should be analyzed rather than rerun
  unless a new, explicitly scoped ablation is planned.

## 2026-06-29 EVP-8-HARD evidence-only model-order gate

- DeepSeek authorization alone is not sufficient for the current
  `EVP-8-HARD E6-evidence-only` ablation because the execution packet requires
  Qwen evidence-only coverage first.
- The correct guard is to check for the tracked Qwen evidence-only parsed
  reviews and summary before any DeepSeek execute command. Existing E6-full
  Qwen/DeepSeek outputs cannot satisfy this precondition because the packet
  variant and visible evidence boundary differ.
- Do not flip ignored local config authorization or run DeepSeek directly to
  compensate for missing Qwen evidence-only results. Pause API execution,
  update the plan, run Qwen evidence-only first, audit coverage, then proceed
  to DeepSeek only if the audit allows it.
- The runner now enforces this for evidence-only DeepSeek execution before
  environment loading or client construction: it requires the Qwen evidence-only
  summary and parsed reviews to exist, pass run/parse gates, cover 47 unique
  candidates, and match the evidence-only packet variant.
- After the authorized evidence-only run, Qwen changed 2/9 repeated false
  accepts to `escalate` and DeepSeek changed 5/9 to `escalate`, but neither
  model changed any of the nine to `reject`. Treat this as risk triage evidence,
  not correctness-verification evidence.
- DeepSeek reduced false accepts more than Qwen, but did so by broad
  escalation, including six correct patches. Report this tradeoff explicitly
  instead of presenting lower false-accept rate as a free safety improvement.
- Add statistical intervals before making any paper claim from the hard-case
  evidence-only result. The nine-case opportunity set yields wide Wilson and
  bootstrap intervals; DeepSeek-minus-Qwen safe-handling delta is descriptive,
  not enough for a strong superiority claim.
- Keep a paper-facing synthesis separate from raw result tables. The supported
  claim is evidence-aware triage under a controlled hard-case ablation; the
  unsupported claim is any reliable automatic verifier or autonomous merge gate.

## 2026-06-05 AI execution handoff plan

- Added `docs/plans/ai_agent_experiment_execution_plan_zh.md` as the clean
  task book for another AI agent. It separates actionable experiment stages
  from historical notes and explicitly lists commands, gates, forbidden
  actions, paper-readiness rules, artifact rules, and human-required inputs.
- Expanded the handoff plan into an executable contract: every stage now has
  required evidence files, pass criteria, a run-record template, failure
  handling rules, and a minimum human-input checklist. This is meant to prevent
  a later AI agent from treating command logs, dry-runs, mock reviews, or
  incomplete API runs as experimental evidence.
- The handoff plan intentionally keeps real API execution blocked until `.env`,
  `configs/model_selection.local.json`, `configs/api_pilot.local.json`, strict
  preflight, and `--execute` are all present.
- The plan distinguishes no-API reproduction, prompt dry-run, mock smoke, and
  real API model results to prevent accidental overclaiming.

## 2026-06-05 no-API reproducibility manifest

- Added `scripts/write_reproducibility_manifest.py` to hash deterministic
  no-API outputs and compare reproduced runs with the original pilot.
- Current comparison:
  `outputs/reproducibility/pilot_compare.json` reports `matched = true` for
  seven deterministic files across `outputs/patch_verification_pilot_001` and
  `outputs/patch_verification_pilot_repro_001`.
- The script deliberately treats runtime workdirs, raw API responses, and
  environment-dependent files as out of scope for deterministic reproducibility
  evidence.

## 2026-06-05 AI plan progress audit

- Added `scripts/audit_ai_plan_progress.py` to turn the execution plan into a
  stage-by-stage status report.
- Latest report: `outputs/plan_progress/latest.md`.
- Current stage counts are 4 complete, 2 partial, and 8 blocked. The blocked
  stages are real-API dependent and require `.env`,
  `configs/model_selection.local.json`, and `configs/api_pilot.local.json`.

## 2026-06-05 human input packet

- Added `scripts/write_human_input_packet.py` to generate an ignored handoff
  packet before real API execution.
- Latest output: `outputs/handoff/human_input_packet.md`.
- The packet now prefers `scripts/bootstrap_api_prereqs.py --dry-run` followed
  by the write/preflight/check-only/execute sequence, and keeps the older
  separate model-selection/API-config commands only as a debugging fallback.
- The packet reports missing required inputs without printing secrets:
  OpenRouter API key presence, concrete model slug, model-selection rationale,
  and local API config.
- The script uses `<repo_root>` instead of local absolute paths so it can be
  safely included in the anonymous artifact.

## 2026-06-05 pre-API handoff

- Added `scripts/write_pre_api_handoff.py` as a one-command local handoff.
- It refreshes readiness, deterministic reproducibility, paper readiness, plan
  progress, goal completion, and human-input reports without calling model APIs.
- Latest report: `outputs/handoff/pre_api_handoff.md`.
- Command display is normalized to `python ...` so the ignored handoff report
  does not expose the local Python installation path.

## 2026-06-05 Git sync packet

- Added `scripts/write_git_sync_packet.py` to document Git sync state without
  initializing or pushing.
- Latest report: `outputs/handoff/git_sync_packet.md`.
- Current state: `research95` is not a Git repository; the old repo remote is
  `https://github.com/gaoming-a/review.git`; using that remote or a new remote
  requires explicit user confirmation before any Git mutation.
- The packet now includes a remote decision record template, staging allowlist,
  ignore checks, cached-diff checks, post-sync acceptance criteria, and an
  explicit ban on `git add .`. This keeps the Git handoff executable by a later
  AI agent while still requiring human confirmation before mutation.
- Added `scripts/audit_git_sync_packet.py` and wired it into
  `scripts/run_local_quality_gate.py`, so Git handoff safety is checked even
  while the workspace remains intentionally uninitialized.
- `scripts/write_pre_api_handoff.py` now refreshes the Git sync packet audit
  and includes it in the authoritative pre-API report list.

## 2026-06-05 model selection shortlist

- Added `docs/experiments/model_selection_shortlist.md` as a decision aid for
  Stage 3.
- The shortlist uses LMArena as the capability-band source and the OpenRouter
  public model catalog API as the availability source.
- It recommends `anthropic/claude-sonnet-4.6` as a conservative first
  single-model pilot candidate, but does not create local config or replace
  user confirmation.

## 2026-06-05 OpenRouter model catalog audit

- Added `scripts/audit_openrouter_model_catalog.py`.
- It checks public OpenRouter catalog visibility for candidate slugs without an
  API key and without creating local config.
- Latest report: `outputs/model_selection/openrouter_catalog_audit.md`.
- Current result: all six shortlist slugs are visible in the public catalog.
- Added `--require-openrouter-catalog` to
  `scripts/create_model_selection_local.py` and
  `scripts/create_api_pilot_local_config.py`. The option is explicit so offline
  dry-runs remain possible, but real local config creation should use it when
  network access is available.

## 2026-06-05 OpenRouter runtime failure handling

- `src/cross_review/openrouter.py` now supports configurable request timeout,
  retry count, and retry backoff through `OPENROUTER_TIMEOUT_SECONDS`,
  `OPENROUTER_MAX_RETRIES`, and `OPENROUTER_RETRY_BACKOFF_SECONDS`.
- OpenRouter HTTP/network errors are sanitized before surfacing so provider
  keys are not copied into tracked outputs or terminal summaries.
- `scripts/run_patch_verification_api_pilot.py` now writes a sanitized
  `run_error.json` when a real API call fails mid-run. That file records the
  candidate, condition, model, completed review count, and error type without
  storing prompts or secrets.
- `scripts/audit_api_run_completeness.py` now fails any run directory that
  contains `run_error.json`; such runs must be rerun and cannot be used as
  experiment results.
- Added `scripts/audit_api_failure_handling.py` and wired it into
  `scripts/run_local_quality_gate.py`. The audit uses a local refused
  connection rather than OpenRouter, checks the sanitized `run_error.json`
  shape, verifies stdout/stderr/error-file secret redaction, and confirms
  completeness rejects the failed run. `SystemExit` writes its message to
  stderr, so the audit intentionally accepts the failure notice from either
  stdout or stderr.
- Added `scripts/write_experiment_run_records.py` and wired it into the local
  quality gate. The script turns existing JSON evidence into the run-record
  format required by the execution plan, while explicitly marking no-API,
  smoke, missing full runs, and quality gates as not eligible for positive
  paper claims.
- `scripts/write_pre_api_handoff.py` now refreshes the run ledger and lists it
  as an authoritative report. `scripts/audit_goal_completion.py` now requires
  the ledger to contain no-API, smoke API, full API, and quality-gate records,
  so a final completion claim cannot omit the experiment record book.

## 2026-06-05 paper draft readiness expansion

- Updated `docs/paper/patch_verification_draft.md` with pre-API
  reproducibility controls and model-selection boundaries.
- Updated `scripts/audit_paper_readiness.py` so methods/negative draft
  readiness requires the paper outline, model-selection docs, reproducibility
  comparison, model catalog audit, and pre-API handoff in addition to the pilot
  report and paper draft.
- Positive paper claims still require real API reviews, metrics, failure
  examples, and a stop/continue gate.

## 2026-06-05 anonymous artifact audit

- Refreshed `artifacts/research95_anonymous_artifact.zip`; current package has
  95 project files plus embedded artifact metadata.
- Added `scripts/audit_anonymous_artifact.py` to inspect the ZIP directly and
  verify required files, manifest consistency, and exclusion rules.
- Updated `scripts/run_local_quality_gate.py` to run the artifact ZIP audit
  when the ZIP exists, while keeping artifact dry-run as the baseline check.

## 2026-06-05 generated paper tables

- Added `scripts/write_paper_tables.py` to generate pre-API Markdown and LaTeX
  tables from current JSON outputs.
- Generated `docs/paper/generated_tables.md` and
  `docs/paper/generated_tables.tex`.
- These tables include dataset composition, executable validation, no-API
  baselines, and deterministic reproducibility. They intentionally exclude real
  model-review results because those do not exist yet.

## 2026-06-05 IEEE pre-API LaTeX draft

- Added `scripts/write_ieee_latex_draft.py`.
- Generated `docs/paper/ieee_preapi_draft.tex` using IEEEtran structure and
  generated pre-API tables.
- The draft explicitly marks real API results as pending and states that
  current no-API baselines are not model-review results.

This file starts fresh for the patch-verification project.

## Rules

- Record only issues that affect the new AI-generated patch-verification
  workflow.
- Do not copy long historical bug logs from the old cross-review project.
- If old behavior matters, summarize it in one paragraph and link to
  `docs/background/previous_findings_summary.md`.

## Initial Notes

- The clean workspace intentionally excludes raw `data/`, `outputs/`, `tmp/`,
  local API keys, local model configs, and old artifact ZIPs.
- Compile checks may create `__pycache__` files with local absolute paths; delete
  them before packaging or scanning.
- Evaluator-facing `patch_id` may encode construction type, so it must not
  appear in model-visible evidence packets. Use anonymous `candidate_id` for
  prompts.
- Do not put words such as `reference_fix`, `buggy_noop`, `irrelevant_patch`,
  `No-op`, or expected outcome labels in any model-visible context.
- The first no-API pilot initially used neutral patch placeholders. The builder
  now materializes unified diffs from retained buggy/fixed checkouts and
  generates 30 validated candidates.
- Cross-task real diffs did not reliably apply across retained BugsInPy
  checkouts. For now, unrelated controls use applicable comment-only source
  diffs; these are low-difficulty controls and must not be presented as the main
  negative class.
- Candidate labels should be treated as usable only after
  `scripts/validate_patch_candidates.py` reports `all_validated = true`.
- API dry-runs only validate prompt rendering and prompt-boundary checks. They
  are not reviewer results and must not be reported as experimental evidence.
- API mock runs only validate the local output and metrics pipeline. They are
  not model results and must not be mixed with real API conditions.
- `scripts/summarize_api_pilot_results.py` can summarize mock runs, but those
  reports must stay under ignored `outputs/` and be treated as reporting-chain
  smoke tests only.
- `scripts/extract_api_failure_examples.py` can also run on mock outputs, but
  mock examples only validate bucket extraction. Qualitative paper examples
  require real API reviews and manual raw-response inspection.
- Run `scripts/preflight_api_pilot.py` before any real OpenRouter call; it
  catches missing `.env`, placeholder model slugs, missing validation summaries,
  and candidate/evidence count mismatches.
- `scripts/run_no_api_patch_pipeline.py` is the preferred fresh-environment
  check. It intentionally creates an ignored dry-run config under the output
  directory and never calls OpenRouter.
- `scripts/create_api_pilot_local_config.py` should be used after model
  selection to avoid hand-editing `configs/api_pilot.local.json`; it does not
  validate credentials, so `scripts/preflight_api_pilot.py` remains mandatory.
- `scripts/validate_model_selection.py` and
  `configs/model_selection.local.json` are now part of the real API gate.
  `preflight_api_pilot.py` fails if the model selection record is missing or
  does not match the API config model.
- `scripts/create_model_selection_local.py` can create the ignored model
  selection record from command-line arguments, preventing malformed manual JSON.
- `scripts/bootstrap_api_prereqs.py` now chains explicit model-selection inputs
  into both ignored local config files, validates the model match, and runs
  preflight. Use `--dry-run` first when handing the task to another agent; the
  script intentionally does not create `.env` or choose a model.
- The bootstrap script now checks `OPENROUTER_API_KEY` before writing local
  config files unless `--allow-missing-credentials` is explicitly set. This
  prevents a failed strict preflight from leaving half-created local config
  files when `.env` is missing.
- `.env.example` now contains only placeholder values and safety comments. It
  is safe for the anonymous artifact; concrete provider keys must stay in the
  ignored `.env` file and must not be copied into tracked docs or outputs.
- `scripts/audit_credential_boundary.py` now checks `.gitignore`,
  `.env.example`, and tracked secret-file state as structured evidence. The
  local quality gate runs this audit in addition to broad sensitive-string
  scanning, so a future real `.env` can exist locally while still remaining
  outside tracked files and anonymous artifacts.
- `scripts/audit_bootstrap_safety.py` now verifies the bootstrap guardrail:
  dry-run must not create local config files, and strict execution without
  `OPENROUTER_API_KEY` must fail before creating temporary local configs. This
  keeps credential-preflight changes testable without real API calls.
- `scripts/audit_workflow_guard.py` now verifies the guarded API workflow
  itself: `--check-only` must report `model_call_attempted = false`, and a
  strict missing-prerequisite run must stop before `reviews.jsonl` or raw
  response files are created.
- `scripts/audit_command_templates.py` now checks the human-input packet and
  key docs for command-template drift. It enforces the intended order:
  bootstrap dry-run with `--allow-missing-credentials`, strict bootstrap write,
  preflight, check-only, then `--execute`.
- Readiness and plan-progress next-action text now also points to the bootstrap
  path instead of the older two-helper workflow. The command-template audit
  checks these script-level prompts so future status reports do not drift away
  from the safer handoff procedure.
- `scripts/run_local_quality_gate.py` now refreshes plan-progress state as
  part of the local report. Blocked or partial stages are reported as project
  state rather than local quality failures, because real API and Git stages
  still require human inputs.
- `scripts/prepare_anonymous_artifact.py` now writes a richer embedded
  `ARTIFACT_README.md` with no-API reproduction, quality gates, credential
  checks, bootstrap checks, command-template checks, handoff, and guarded API
  command templates. `scripts/audit_anonymous_artifact.py` validates that these
  README snippets are present inside the ZIP.
- `scripts/evaluate_api_pilot_gate.py` is the required post-run guardrail
  before writing positive claims. A mock run must produce `not_evidence`, and a
  real run with weak or collapsed metrics must be treated as stop/redesign.
- `scripts/audit_execution_readiness.py` is the current-turn status entry
  point. It reports no-API readiness, missing `.env` or local config, and the
  fact that `research95` is not currently a Git repository.
- `scripts/audit_paper_readiness.py` should be run before expanding the paper
  beyond the pre-API methods draft. Current state should report missing real API
  reviews, API report, failure examples, and gate report.
- `scripts/prepare_anonymous_artifact.py` generated the current anonymous
  package successfully after tightening validation to allow `.env.example`
  placeholders while still rejecting concrete keys, local paths, local configs,
  raw outputs, and benchmark checkouts.
- `scripts/postprocess_api_pilot_run.py` is the preferred post-run entry point.
  On the mock smoke output it regenerated all reports and returned
  `gate_verdict = not_evidence` with `positive_claim_ready = false`, as
  expected.
- `scripts/run_api_pilot_workflow.py` is the guarded real API entry point. It
  supports `--check-only` without API calls and requires explicit `--execute`
  after strict preflight before any model call. It now records
  `model_selection_validation.json`; missing model-selection files are reported
  as structured failures rather than Python tracebacks.
- `scripts/create_api_pilot_local_config.py` and
  `scripts/bootstrap_api_prereqs.py` now emit guarded workflow next commands.
  Direct `run_patch_verification_api_pilot.py` use should stay limited to
  prompt dry-runs, mock checks, or workflow-internal execution.
- The low-level runner now rejects direct real API execution unless
  `run_api_pilot_workflow.py` supplies its internal `--allow-direct-api-run`
  flag. `scripts/audit_workflow_guard.py` verifies this path without making API
  calls.
- The workflow now forwards `--run-dir` and `--limit` to the API runner.
  Explicit `--limit 0` means a full 30-candidate run and is no longer replaced
  by config `smoke_limit=2`. The workflow refuses to overwrite an existing
  `reviews.jsonl` unless `--allow-existing-output` is passed intentionally.
- Added `scripts/audit_api_run_completeness.py` and wired it into
  `scripts/postprocess_api_pilot_run.py` and the guarded workflow. Smoke runs
  should pass `--expected-candidates 2`; full runs should pass
  `--expected-candidates 30`. Paper readiness now requires
  `run_completeness.json` with 60 non-mock review records.
- API review records now include `raw_response_sha256`. The completeness audit
  verifies that each raw response path exists under the run directory, parses as
  JSON, and matches the recorded hash, and that required review fields are
  present.
- Do not run `prepare_anonymous_artifact.py` and `audit_anonymous_artifact.py`
  in parallel against the same ZIP path. The audit can observe a partially
  written archive and raise `BadZipFile`. Generate the ZIP first, then audit it
  as a separate step.
- `scripts/write_human_input_packet.py` now includes both smoke and full
  postprocess commands. `scripts/audit_command_templates.py` checks that smoke
  uses `--expected-candidates 2` and full run uses `--expected-candidates 30`.
- `scripts/audit_ai_plan_progress.py` now also requires this 60-record
  non-mock run-completeness evidence before marking Stage 8 postprocess
  complete.
- `scripts/run_local_quality_gate.py` is the preferred end-of-turn local gate.
  It passed after dynamic construction of sensitive-scan patterns so the scanner
  no longer flags its own rule strings. Passing this gate does not mean real API
  readiness; it reports API readiness separately.
- `scripts/audit_goal_completion.py` is the whole-objective guardrail. It keeps
  `complete = false` until no-API readiness, reproducibility, real full API
  reviews, postprocess outputs, non-mock failure examples, a positive paper
  gate, artifact safety, local quality, and Git repository/remote evidence are
  all present.

## 2026-06-05 DeepSeek official API switch

- The current primary execution path is DeepSeek official API with
  `api_provider = deepseek_official` and `model = deepseek-v4-pro`; OpenRouter
  support remains only as an alternative provider path.
- `scripts/bootstrap_api_prereqs.py`, `scripts/preflight_api_pilot.py`,
  `scripts/run_patch_verification_api_pilot.py`, model-selection validation,
  readiness audits, and command-template audits are now provider-aware.
- A real-looking DeepSeek key was found in `.env.example` and removed. The
  quality gate and artifact packager now scan for concrete `DEEPSEEK_API_KEY`
  assignments in tracked/packageable text, not only OpenRouter keys.
- The strict bootstrap safety audit uses an intentionally missing env file
  under `outputs/bootstrap_safety/`, so it does not accidentally pass because
  the developer's real `.env` exists.
- Verified locally without model calls: compileall passed, credential boundary
  passed, bootstrap safety passed, command templates passed, readiness reports
  `overall_ready_for_real_api = true`, and guarded workflow check-only reported
  `model_call_attempted = false`.

## 2026-06-05 DeepSeek smoke result

- First real DeepSeek smoke at `outputs/patch_verification_api_pilot_001`
  generated 4 non-mock review records and passed run completeness, but 2/4
  outputs were invalid. The invalid records had `finish_reason = length`,
  empty final `content`, and all completion tokens spent in `reasoning_content`.
- Root cause: `max_tokens = 1200` was too low for DeepSeek V4 reasoning on the
  larger reference-fix candidate, so the final JSON never appeared.
- Fixed `scripts/run_patch_verification_api_pilot.py` so config values for
  `temperature` and `max_tokens` actually override runner defaults. Updated API
  pilot config to `max_tokens = 4096`.
- Second smoke at `outputs/patch_verification_api_pilot_001_tokens4096`
  generated 4 non-mock review records, passed completeness, and had invalid
  output rate 0. This validates the execution chain and schema stability.
- The smoke gate is still `indeterminate`; it is too small for research claims.
  It only justifies moving to the 30-candidate full run, not writing positive
  paper results.

## 2026-06-05 Git initialization boundary

- After initializing `research95` as a Git repository, the credential-boundary
  audit initially misclassified tracked `.env.example` as a secret file because
  it matched the `.env.*` tracked-file pattern.
- `.env.example` is the intentionally tracked template and must remain allowed;
  concrete `.env`, `.env.*` variants other than `.env.example`, key files, and
  `configs/*.local.json` must remain untracked.
- `scripts/audit_credential_boundary.py` now filters `.env.example` out of the
  tracked-secret-file list while still validating that the template contains
  only placeholders.

## 2026-06-05 DeepSeek full run result

- Full run directory: `outputs/patch_verification_api_pilot_002`.
- The run completed with 60 non-mock review records, 30 candidates, 2
  conditions, no `run_error.json`, raw response hashes present, and
  `run_completeness.json` passed.
- Gate verdict: `stop_or_redesign`.
- Evidence-first improved safety metrics: false accept rate 0.0000 versus
  0.0909 for llm-only, and accepted precision 1.0000 versus 0.7143.
- Evidence-first also reduced correct-patch recall: 0.7143 versus 1.0000 for
  llm-only. The drop is 0.2857, exceeding the configured `max_recall_drop=0.25`.
- This is a mixed/negative result. Do not write a positive claim that
  evidence-first is better. The honest claim is that it removed observed false
  accepts in this pilot but at too high a recall cost under the configured gate.
- Next research step should inspect `failure_examples.md` and decide whether to
  redesign the evidence packet/prompt or pivot the paper toward merge-gate
  safety/utility tradeoffs.

## 2026-06-05 DeepSeek failure-analysis lesson

- The full-run failure analysis is now tracked in
  `docs/experiments/deepseek_full_run_failure_analysis.md`.
- The important failure is not simply model capability. `llm_only` accepted two
  partial `httpie_1` patches because they looked behaviorally plausible, while
  `evidence_first` refused or rejected two correct reference fixes because the
  evidence packet did not include the test body, failing behavior, oracle
  output, or claim-level trace needed to justify acceptance.
- Do not scale `patch_verify_evidence_first_v1` as-is. It would mostly scale a
  known evidence-poverty failure mode.
- The next experiment should be a failure-case-only redesign smoke with a
  clearly named tool/evidence-augmented condition. If that smoke cannot recover
  recall on the known reference-fix failures, the honest paper direction is a
  negative/methods claim about prompt-only merge-gate limits.

## 2026-06-05 redesign smoke config override bug

- While preparing `tool_augmented_evidence`, dry-run unexpectedly rendered 10
  prompts for `llm_only` and `evidence_first` instead of 5 prompts for the new
  condition.
- Root cause: `scripts/run_patch_verification_api_pilot.py` gave argparse a
  non-`None` default for `--conditions`, so `apply_config()` treated conditions
  as already set and did not load the config value.
- Fix: `--conditions` now defaults to `None`, and `apply_defaults()` fills the
  old two-condition default only after config values have been applied.
- Rule: if a new condition is driven by config, dry-run must prove the rendered
  manifest contains only that condition before any real API call.

## 2026-06-05 tool-augmented redesign smoke

- After fixing the config override bug, dry-run rendered exactly five
  `tool_augmented_evidence` prompts for the five known failure cases.
- The actual rendered prompt boundary scan found no evaluator labels, old
  evaluator patch ids, or local paths.
- Real DeepSeek smoke at `outputs/patch_verification_redesign_smoke_001`
  completed with 5 non-mock records, completeness passed, and invalid output
  count 0.
- Decisions matched the smoke gate: reference fixes `candidate_0001` and
  `candidate_0023` were accepted; partial fixes `candidate_0005`,
  `candidate_0006`, and `candidate_0020` were rejected.
- Treat this as evidence that tool-visible execution summaries can repair the
  known failure cases. It is not evidence that the original prompt-only
  `evidence_first` condition succeeded.

## 2026-06-05 tool-augmented full run

- After the user confirmed the route, the paper framing was revised before the
  full run: tool-augmented verification is a separate condition, not a rescue
  of prompt-only evidence-first.
- Built 30-candidate full-run inputs under
  `outputs/patch_verification_tool_augmented_full_001/inputs` with
  `--all-candidates`.
- Dry-run produced exactly 30 `tool_augmented_evidence` prompts, and direct
  rendered-prompt scanning found no evaluator labels, old evaluator patch ids,
  or local paths.
- Real DeepSeek full run completed with 30 non-mock records, completeness
  passed, and `tool_augmented_full_gate.json` passed.
- Metrics: false accept rate 0.0, accepted precision 1.0, correct-patch recall
  1.0, false reject rate 0.0, escalation rate 0.0, invalid-output rate 0.0.
- Interpret this as conditional tool-assisted verifier evidence. The result
  depends on visible executable behavior summaries and must not be described as
  prompt-only model-review ability.

## 2026-06-05 dual-claim audit repair

- After the tool-augmented full run passed, the old readiness scripts still
  treated the original prompt-only `stop_or_redesign` gate as the only path to
  a positive claim.
- Root risk: future execution would either keep reporting the new direction as
  blocked, or incorrectly rewrite the prompt-only negative result into a
  success.
- Fix: `scripts/audit_paper_readiness.py`, `scripts/audit_ai_plan_progress.py`,
  and `scripts/audit_goal_completion.py` now report prompt-only readiness and
  tool-augmented conditional readiness as separate checks.
- Rule: never change the old `positive_claim_ready=false` into true unless the
  prompt-only gate itself changes. The supported positive result is
  `tool_augmented_claim_ready=true`, bounded to tool-assisted verification.

## 2026-06-05 IEEE submission draft generation

- The Markdown paper draft already contained the real API and tool-augmented
  full-run results, but `docs/paper/ieee_preapi_draft.tex` still described a
  pending API pilot.
- Fix at that time: `scripts/write_ieee_latex_draft.py` generated
  `docs/paper/ieee_submission_draft.tex` as the then-current IEEEtran
  submission draft and left the old pre-API file as historical context.
- Initial generation bug: the prompt-only evidence-first result row was empty
  because `metrics.json` stores condition groups with provider-qualified keys
  such as `evidence_first::evidence_first__deepseek-v4-pro`.
- Repair: the script now resolves condition groups by prefix and reads the
  tool-augmented row from `tool_augmented_full_gate.json`.
- Verification: direct `pdflatex` compilation succeeded and produced a 4-page
  PDF under ignored `outputs/latex_build`. `latexmk` is unavailable because the
  local MiKTeX installation lacks Perl.

## 2026-06-06 publication figure generation

- Generated a reproducible figure set with `scripts/generate_paper_figures.py`
  instead of using non-reproducible bitmap generation.
- Outputs are written under `docs/figures/` in PDF, SVG, and PNG formats.
- Initial visual QA found overlap in `fig1_framework`: the execution-evidence
  note collided with the decision boxes. The script was repaired by reducing
  title size and moving the note below the verifier path.
- The IEEE draft now imports `graphicx` and references five PDF figures:
  framework, evidence visibility, dataset composition, result tradeoff, and
  claim boundary.
- Direct `pdflatex` compilation succeeded after figure insertion and produced a
  5-page PDF under ignored `outputs/latex_build`.

## 2026-06-06 imagegen visual candidates

- Generated four raster PNG candidates with the built-in `$imagegen` workflow:
  framework, evidence-boundary, tradeoff, and claim-boundary panels.
- Stored project copies under `docs/figures/imagegen/` and recorded exact
  prompts in `docs/figures/imagegen/prompts.md`.
- Rule: these imagegen outputs are conceptual visual assets for graphical
  abstracts, presentations, or visual drafts. They must not replace exact
  Matplotlib-generated vector figures when the figure is used as experimental
  evidence.

## 2026-06-08 final paper roadmap

- Saved the evaluated 90+ final-paper route as
  `docs/plans/final_paper_roadmap_zh.md`.
- The roadmap deliberately remains separate from `current_plan_zh.md`: it is a
  long-term route for an evidence-visibility empirical study, not the next
  mandatory execution baseline.
- Rule: do not jump directly to 80 bugs / 240 patches. First strengthen the
  current pilot with tool-only baselines and qualitative cases, then expand to
  15-20 bugs, and only enter larger data expansion after the pipeline remains
  stable.

## 2026-06-08 six-step prerequisite execution

- Added the long-term PatchEvidenceBench schema and leakage policy before
  expanding data. This prevents hidden evaluator results from being mixed into
  model-visible evidence.
- Implemented `scripts/run_tool_only_baseline.py` with two conditions:
  `tool_only_apply_only` and `tool_only_validation_summary`.
- Current metrics show why the boundary matters: apply-only is safe but
  unusable because it escalates all 30 candidates; validation-summary is perfect
  on the pilot but uses retained executable validation and must be treated as a
  tool-summary/oracle-style comparison.
- Generated a qualitative case report covering LLM-only false accepts,
  evidence-first recall loss, tool-only contrast, and tool-augmented repair.
- Screened the retained BugsInPy workspace: 22 tasks were eligible at checkout
  level and 15 were selected for the next registry. This is not yet an expanded
  validated dataset; each new task still needs an oracle wrapper and candidate
  validation.

## 2026-06-08 subsequent target designation

- `docs/plans/final_paper_roadmap_zh.md` is now the canonical subsequent
  research target for this project.
- Future work should use that roadmap as the source of next tasks, while still
  updating `docs/plans/current_plan_zh.md` before each concrete execution
  round.
- Boundary: this designation does not start the full 90+ route automatically;
  execution should proceed through Stage A/B and the existing 15-task expansion
  registry first.

## 2026-06-08 documentation cleanup

- Problem: README, current plans, and early experiment-plan files still mixed
  old API/pre-API "next step" wording with the newer final-paper roadmap. This
  could cause a future agent to restart completed prompt-only or
  tool-augmented runs instead of following the final roadmap.
- Fix: make `docs/plans/final_paper_roadmap_zh.md` the only final-paper route,
  keep `docs/plans/current_plan_zh.md` as the per-turn execution log, and mark
  older execution plans as historical/reference material.
- Rule: when a document describes a completed experiment, keep the result and
  command context, but rewrite any active "next step" language into completed
  status plus a pointer to the current roadmap.

## 2026-06-08 httpie Stage A/B slice

- The five selected `httpie` expansion tasks already had task-specific oracle
  files under `scripts/oracles/`. The missing piece was not oracle authoring but
  producing a separately bounded Stage A/B run instead of reusing the old
  seven-task pilot as if it were a new expansion result.
- Added filtered build support to `scripts/build_patch_verification_dataset.py`
  with `--task-id` and `--run-id`. Default behavior remains the original full
  built-in pilot, so existing quality gates and reports are not disturbed.
- `httpie_stage_ab_001` produced 22 candidates from five tasks, validated
  22/22 with apply + oracle checks, rendered 44 dry-run prompts, and generated
  tool-only baseline metrics.
- Rule: when a screened task group is promoted from registry to dataset slice,
  create a new run id and tracked result document; do not silently reinterpret
  an older pilot as expansion evidence.

## 2026-06-08 AI patch generation attempt

- Added `scripts/generate_ai_patch_candidates.py` for DeepSeek official API
  patch generation and `scripts/relabel_ai_patch_candidates.py` for
  post-validation outcome relabeling.
- Initial generator behavior was too brittle: it wrote candidate files only
  after the whole 10-patch run completed. When one response exhausted all
  output tokens in reasoning and returned empty final content, previously
  saved raw responses were not converted into candidates.
- Repair: generator now writes prompt manifest and pending candidates
  incrementally, reuses parseable raw responses, and stores retry attempts as
  separate raw files.
- Result: 10 AI patches were generated, but only 4 applied cleanly and 6 failed
  `git apply`. This is diagnostic generator-pipeline evidence, not a usable
  verifier experiment slice.
- Rule: for AI-generated patch datasets, generation success must be measured by
  apply + oracle validation, not by receiving a model response. If apply
  failure is high, stop and redesign the generation protocol before verifier
  API calls.

## 2026-06-08 strict agent generation with Qwen

- Added Qwen official API support through the OpenAI-compatible client using
  `QWEN_API_KEY` and optional `QWEN_BASE_URL`.
- Qwen solved the DeepSeek empty-final-content failure mode for
  `bugsinpy_httpie_5`: it returned structured JSON and a plausible edit plan.
- Under strict mode, the edit plan still failed because its `find` snippet did
  not match the buggy source exactly. The user explicitly rejected fuzzy apply,
  so the attempt was recorded as a strict generation failure.
- Rule: exact edit-plan mode is clean but brittle. If it blocks too many
  candidates, the project must either accept lower yield, allow controlled
  fuzzy apply with explicit paper wording, or switch to a true tool-using agent
  that can inspect and revise its edits before emitting the final diff.

## 2026-06-09 Qwen 3.7 Plus strict agent retry

- `qwen3.7-plus` generated one strict exact-match edit plan for
  `bugsinpy_httpie_5`; the script applied it in a copied checkout and exported a
  real `git diff`.
- The candidate applied cleanly and the retained oracle ran, but the oracle did
  not pass. This makes it a validated generated negative candidate, not a
  repair.
- The second candidate timed out after 3 provider attempts. Treat this as
  provider/run instability and do not infer semantic failure from the missing
  candidate.
- Fixed generator metadata so the candidate `source` field records the selected
  API provider instead of always using `deepseek_official_agent_edit`.
- Rule: successful materialization and semantic correctness must remain separate
  gates. A generated patch can be valuable for the verifier dataset even when it
  is incorrect, as long as apply + oracle validation is reproducible.

## 2026-06-09 DeepSeek agent-style patch validation

- Validated the 8 existing DeepSeek agent-style candidates from
  `httpie_agent_patch_stage_ab_001`; no new API calls were made.
- All 8 patches applied cleanly and all 8 retained oracles ran. This confirms
  that agent-style edit plans plus local `git diff` are much more reproducible
  than direct model-written unified diffs for this slice.
- All 8 retained oracles failed, so every candidate relabeled as `incorrect`.
  The protocol produced good generated negative samples, not correct repairs.
- Decision rule: do not expand AI-generated patches as the main balanced dataset
  source until the generator can produce both oracle-passing and oracle-failing
  patches. Use them as an extension for generated-negative or partial-fix
  verifier stress tests.

## 2026-06-09 final roadmap task-set reconstruction

- Do not change the research line from patch verification to patch generation.
  The central question remains whether verifiers accept, reject, or escalate
  candidate patches under different evidence visibility conditions.
- A task can be valuable even if no generator solves it. If validation is stable,
  keep it as a hard-generation or stress case and report generator success rate.
- Exclude a task only when reproducible validation fails: unstable environment,
  flaky tests, invalid reference patch, unreliable labels, or uncontrolled
  runtime.
- `httpie_5` should not be a main success case or a prompt-tuning target. If its
  oracle and reference validation remain stable, keep it with capped weight:
  one reference correct patch, a few generated incorrect patches, and at most
  one constructed partial/control patch.
- Rule: dataset balance is required at the dataset level, not per bug. Each bug
  does not need an AI-generated correct repair.

## 2026-06-09 httpie5 task accounting audit

- Rebuilt a single-task `httpie_5` slice and validated it twice. Both runs
  produced 6/6 validated labels: one reference patch passed the retained oracle,
  and five negative/control candidates failed as expected.
- Added `scripts/build_task_generation_accounting.py` to merge validation
  records, relabeled generated candidates, and prompt manifests into task-level
  accounting metadata.
- Current `httpie_5` accounting: 7 generation attempts, 3 admitted generated
  patches, 1 applicable incorrect patch, 2 environment-invalid patches, and 0
  correct generated patches.
- Decision: keep `httpie_5` as `hard_generation_case` with capped candidate
  weight. Do not use it as a main generation success case.
- Boundary: broad pass-to-pass regression stability is not separately measured
  by the current retained-oracle audit. Do not describe `httpie_5` as fully
  regression-stability audited until a pass-to-pass suite is defined.

## 2026-06-09 httpie5 P2P-broad scope

- Implemented `scripts/build_pass_to_pass_scope.py` to define P2P scope before
  using it for candidate labels. The script creates a compatibility shim for
  legacy `requests.compat.is_py26` imports and records that shim in the output.
- Direct per-test execution was initially too slow because each pytest process
  has high startup overhead and the suite contains external-network tests.
  Static exclusion of test methods containing `httpbin`, `http://`, or
  `https://` made the scope construction tractable and auditable.
- For `httpie_5`, 17 tests were collected, 1 retained fail-to-pass oracle was
  excluded, 13 external-network tests were excluded, and 3 stable local
  P2P-broad tests remained.
- `scripts/validate_candidates_with_p2p.py` labeled the 6 current candidates:
  one `correct_under_f2p_and_p2p_broad` reference patch and five
  `incorrect_issue_not_fixed` candidates.
- Rule: P2P-broad is an environment-specific stable runnable subset. Always
  report collection counts and exclusion reasons; do not describe it as the
  original project's full test suite.

## 2026-06-09 Luigi replacement tasks

- Built retained-oracle candidate slices for `bugsinpy_luigi_3` and
  `bugsinpy_luigi_4`; both repeated validations were stable.
- Extended P2P compatibility handling for old Luigi tests: Python 3.11
  `collections`/`inspect` compatibility, `mock` mapped to `unittest.mock`, and
  a lightweight `psutil` shim for import-time compatibility.
- Per-test P2P execution was too slow for Luigi 3. Added batch-first P2P scope
  construction and chunked candidate P2P validation.
- Luigi 3 result: 137 tests collected from `test/parameter_test.py`, 1 retained
  fail-to-pass oracle excluded, 1 static external dependency excluded, 135
  P2P-broad tests retained.
- Luigi 4 result: 14 tests collected from `test/contrib/redshift_test.py`, 1
  retained fail-to-pass oracle excluded, 13 P2P-broad tests retained.
- Boundary: current Luigi P2P-broad scopes are task-file stable subsets, not a
  project-wide Luigi regression suite. This needs a final design decision
  before claiming project-wide P2P coverage.

## 2026-06-10 project-level P2P-broad rebuild

- Final main labels should use `project_level_p2p_broad`, not task-file P2P
  scopes. Task-file scopes remain useful for smoke checks and appendix
  discussion only.
- `scripts/build_pass_to_pass_scope.py` now supports project-level test-file
  discovery, checkout-independent nodeid normalization, manifest output,
  Windows-safe batch chunking, and file-grouped batch validation.
- Legacy projects may not collect tests with `pytest .`. For `httpie_5`, the
  script must explicitly discover `tests.py`; otherwise project-level collection
  returns zero tests even though `tests/tests.py` is valid.
- `httpie_5` project-level P2P-broad completed with 17 collected tests, 1
  fail-to-pass oracle exclusion, 13 external-dependency exclusions, and 3
  included P2P-broad tests over 3 stability runs per version.
- `validate_candidates_with_p2p.py` now emits
  `correct_under_f2p_and_p2p_broad` for the positive final label.
- Luigi project-level P2P is not just a matter of using the task-file command on
  a larger path. Luigi 3 discovers 113 test files and 904 nodeids, with 44
  collection errors in external-service/contrib areas. Two construction attempts
  exceeded local execution limits even after file-grouped batching.
- Do not silently downgrade Luigi to task-file P2P for final labels. Either
  build collection-error manifests plus stability caches for strict
  project-level P2P, or mark Luigi as `project_level_p2p_pending` and use
  smaller replacement tasks for final project-level main labels.

## 2026-06-10 Luigi freeze and cohort gating

- Final decision: do not continue brute-force Luigi project-level P2P in the
  current phase. Mark Luigi as `pending_blocked`, retain task-file P2P only as
  appendix/smoke evidence, and prioritize smaller replacement tasks with
  completed project-level P2P-broad manifests.
- Added `data/cohorts/task_cohort_registry.json` as the tracked source of truth
  for main-cohort inclusion. Current state: `bugsinpy_httpie_5` is
  `p2p_broad_main`; `bugsinpy_luigi_3` and `bugsinpy_luigi_4` are
  `blocked_or_pending` plus `p2p_local_smoke`.
- Main metrics should include only tasks where
  `project_level_p2p_status == completed` and `p2p_broad_main_included is
  true`.
- `scripts/analyze_patch_verification.py` now applies this filter by default
  when the cohort registry exists. Use `--no-cohort-filter` only for appendix or
  diagnostic runs.
- `scripts/build_task_generation_accounting.py` now reads the same cohort
  registry and overrides `main_experiment_included` for blocked tasks, so Luigi
  task-file labels do not leak into final main accounting.

## 2026-06-10 bounded replacement sweep

- Tried `bugsinpy_httpie_1` through `bugsinpy_httpie_4` as quick replacement
  candidates because they already existed in the Stage A/B validated `httpie`
  slice.
- Updated test discovery to ignore bundled virtual environments (`env`, `venv`,
  `.venv`) after `httpie_1` initially exposed hundreds of dependency package
  tests from `env/Lib/site-packages`.
- Updated project-level collection to run per test file. A single collection
  error should not erase all otherwise collectable nodeids for a project.
- `httpie_1` remains blocked because its tests require the real
  `pytest_httpbin` plugin from `tests/conftest.py`. Do not fake this fixture for
  main labels; it changes the test environment semantics.
- `httpie_4` needed additional old `requests.compat` fields such as
  `is_windows`, `is_py3`, and `bytes`. This compatibility shim is acceptable
  because it restores removed compatibility constants, but the project-level
  scope still exceeded the bounded sweep runtime.
- `httpie_2` and `httpie_3` also exceeded the bounded project-level P2P runtime.
  They are recorded as `pending_blocked`, not silently removed.
- Current lesson: replacement-task screening should happen before candidate
  expansion. Prefer projects with no required service fixtures, no bundled
  virtualenv inside the checkout, and project-level collection that finishes
  within the predefined budget.

## 2026-06-10 tqdm feasibility sweep

- `bugsinpy_tqdm_1` and `bugsinpy_tqdm_2` have much smaller test-file counts
  than Luigi, but most test files require the legacy `nose` dependency.
- Both tasks completed bounded project-level scope construction, but each
  retained only one stable P2P-broad test:
  `tqdm/tests/tests_version.py::test_version`.
- Because the main threshold is `p2p_broad_size >= 3`, both tasks are recorded
  as `completed_insufficient_p2p_broad` and excluded from `p2p_broad_main`.
- Do not silently install or emulate `nose` for main labels. Treat dependency
  installation as a separate environment decision because it changes the
  reproducibility contract.

## 2026-06-10 unittest adapter and black sweep

- Added a bounded `unittest` adapter to `scripts/build_pass_to_pass_scope.py`.
  The adapter uses standard-library discovery and runner execution and emits
  the same P2P manifest shape as pytest scopes.
- `_FailedTest` entries from unittest discovery must be recorded as collection
  errors, not as runnable tests. Otherwise a failed module import can be
  mistaken for one collected test.
- When `--manifest-out` is used and collection errors exist, the script now
  writes a tracked sibling collection-error manifest under `data/p2p_scopes/`.
- `bugsinpy_black_1` and `bugsinpy_black_3` both failed project-level unittest
  collection because importing `black` requires `typed_ast`. The dependency is
  listed in the BugsInPy requirements, but it was not installed silently during
  this sweep.
- Result: both black tasks are `pending_blocked`, not unsupported-framework
  failures. The framework adapter works enough to expose the real environment
  dependency blocker.
- A confirmed attempt to install `typed-ast==1.4.0` in an isolated Python 3.11
  venv failed because pip had to build the extension from source and the machine
  lacks Microsoft Visual C++ 14.0+ Build Tools. The failed venv was removed.
  Do not retry the same Python 3.11 installation path without changing one of:
  system build tools, Python version, or the allowed dependency version.

## 2026-06-10 cookiecutter feasibility sweep

- `bugsinpy_cookiecutter_1` reached project-level pytest discovery but collected
  zero nodeids because collection failed before executable test selection.
- First blocker: the retained checkout's `setup.cfg` supplied pytest-cov
  arguments. The repair was not to install pytest-cov, but to implement an
  audited sanitizer that removes only coverage options and preserves the rest
  of `addopts`.
- The sanitizer correctly transformed
  `-vvv --cov-report term-missing --cov=cookiecutter` into `-vvv`, but the
  retry then exposed real missing dependencies: `poyo`, `binaryornot`, and
  `freezegun`.
- After explicit approval, an isolated Python 3.11 venv under ignored
  `outputs/envs/` installed the Cookiecutter runtime/test dependencies needed
  for P2P while still excluding pytest-cov. Passing the venv Python explicitly
  as both the script runner and `--python` test interpreter mattered; a prior
  relative-path run left mixed system/venv Python processes and had to be
  terminated manually.
- Pytest 9 plus retained `-vvv` addopts emits tree-form `--collect-only` output
  instead of nodeid lines. The scope builder now parses tree output and maps
  parametrized nodeids back to their source segments for static exclusions.
- Result at this stage: `cookiecutter_1` had 296 common nodeids and 290
  P2P-broad tests over 3 stability runs per version. It still needed
  fail-to-pass oracle and candidate validation before main inclusion; that
  follow-up is recorded in the next note.

## 2026-06-10 cookiecutter candidate validation

- The `cookiecutter_1` retained buggy checkout lacks the original
  `non_ascii.json` test fixture while the fixed checkout contains it. The
  migrated oracle should create its own temporary UTF-8 JSON file and assert
  behavior directly; otherwise the label can conflate source behavior with test
  fixture presence.
- On this Windows environment, the Cookiecutter checkout contains `docs/*.md`
  reparse point/junction entries. `shutil.copytree` fails on them when building
  candidate workdirs. Candidate validation now skips symlink/reparse-point
  entries during checkout copying; these documentation links are not inputs to
  the retained oracle, patch diff, or P2P scope.
- Candidate-level P2P validation must reuse the P2P scope manifest's audited
  pytest addopts override. Without `-o addopts=-vvv`, pytest reads the original
  coverage options from `setup.cfg`, fails because `pytest-cov` is intentionally
  absent, and can falsely mark the reference patch as a regression.
- `cookiecutter_1` now has one reference candidate labeled
  `correct_under_f2p_and_p2p_broad` and three negative/control candidates
  labeled `incorrect_issue_not_fixed` over 290 P2P-broad tests. It is admitted
  to `p2p_broad_main`, but this does not make the final dataset large enough.

## 2026-06-10 cookiecutter_2 candidate validation

- The retained workspace for `cookiecutter_2` lacks BugsInPy metadata files
  such as `bugsinpy_bug.info` and `bugsinpy_run_test.sh`; derive the behavior
  from buggy/fixed source diff and tests, and document that inference rather
  than pretending original metadata exists.
- `tests/test_hooks.py::TestFindHooks::test_find_hook` is not a stable retained
  oracle in the retained checkout because `tests/test-hooks` already exists and
  setup fails with `FileExistsError`. Use direct behavior validation instead.
- The stable F2P node is
  `tests/test_hooks.py::TestExternalHooks::test_run_hook`: buggy fails because
  only one matching hook runs; fixed passes because all matching hooks run.
- A standalone oracle should create its own temporary template repository with
  two matching `pre_gen_project` hooks and assert that both marker files are
  produced. This avoids relying on mutable in-repo test fixture directories.
- `cookiecutter_2` now contributes 11 validated candidates: one reference
  correct patch, one no-op, one irrelevant patch, and eight partial fixes. Its
  project-level P2P-broad scope retains 278 tests, so it is admitted to
  `p2p_broad_main`.

## 2026-06-11 cookiecutter_3 candidate validation

- `cookiecutter_3` has complete BugsInPy metadata, and its original F2P command
  targets `tests/test_read_user_choice.py::test_click_invocation`.
- The first direct F2P run exposed a missing declared dependency:
  `future>=0.15.2`, required for `past.builtins`. Installing pinned
  `future==0.18.3` in the ignored Cookiecutter venv restored this import.
- The first project-level P2P scope still had 18 collection-error files due to
  missing `whichcraft`, also declared in `setup.py`. Installing pinned
  `whichcraft==0.6.1` in the same ignored venv reduced collection errors to
  zero.
- Parameterized F2P tests should be passed as explicit parameterized nodeids to
  the P2P scope builder. Passing only the parent nodeid excluded them as buggy
  baseline failures, which was semantically safe but produced unclear
  accounting.
- A task-specific negative for this single-line prompt bug can set
  `show_choices=True`: it edits the relevant argument but preserves the
  duplicated-choice behavior.
- `cookiecutter_3` now contributes four validated candidates over 255 stable
  P2P-broad tests and is admitted to `p2p_broad_main`.

## 2026-06-11 tqdm_9 candidate validation

- `bugsinpy_tqdm_9` avoided the `tqdm_1/2` `nose` blocker because its retained
  checkout has a compact `tqdm/tests/tests_tqdm.py` suite that collected 14
  pytest nodeids without collection errors.
- Its retained oracle must cover both visible failures:
  `test_si_format` and `test_update`. A single SI-format check would miss the
  `__len__` behavior fixed in the same reference patch.
- Generic partial-diff generation is unsafe when the reference patch mixes bug
  fixes and style-only edits. The first `tqdm_9` candidate pass produced six
  `partial_fix` records that still passed the retained oracle. These records
  were filtered out with a task-level partial allowlist before final validation.
- Rule: every generated partial negative must be validated under the retained
  oracle before it can enter the dataset. Do not assume that omitting any
  reference diff hunk creates a behaviorally incorrect patch.
- `bugsinpy_tqdm_9` now contributes seven validated candidates over 12 stable
  P2P-broad tests and is admitted to `p2p_broad_main`.

## 2026-06-11 sixth-task screening boundary

- After `tqdm_9`, the remaining retained selected candidates were
  `black_2` and `tqdm_3` through `tqdm_8`.
- `black_2` has a clear `fmtonoff4` behavior test in `tests/test_black.py`, but
  importing `black` fails before test execution because `typed_ast` is absent.
  This is the same dependency class as `black_1/3`; do not silently install or
  emulate it.
- `tqdm_3` through `tqdm_8` collect only
  `tqdm/tests/tests_version.py::test_version` without new dependencies. The
  behavior-relevant test files still fail through the legacy `nose` path.
- Rule: do not downgrade these tasks to main cohort entries with a one-test
  P2P-broad scope. The next expansion needs an explicit environment decision
  for legacy dependencies or a broader BugsInPy project import.

## 2026-06-11 broader BugsInPy candidate pool

- The user confirmed the broader-project route: do not spend the next phase on
  legacy `nose` or Black `typed_ast` / MSVC repair.
- The local BugsInPy source archive is available at
  `D:/mgao/code/research/tmp/bugsinpy_archive/BugsInPy-master`; no network
  download is needed for metadata screening.
- `scripts/screen_bugsinpy_candidate_pool.py` performs metadata-only screening
  before checkout. The first run found 501 BugsInPy tasks, 479 new tasks not in
  the current registry, and 195 promising metadata-level candidates.
- Top low-friction candidates are `PySnooper_1-3`, followed by several
  `fastapi` and `sanic` pytest tasks. Heavy/native projects such as
  `keras`, `pandas`, and `spacy` are deprioritized by metadata blockers.

## 2026-06-11 PySnooper_1 candidate validation

- PySnooper's retained checkout needs the existing Python 3.11
  `collections.abc` compatibility shim before either buggy or fixed F2P can run.
  This is a runtime-compatibility shim, not a behavior patch.
- After the shim, the test suite requires `python-toolbox`, which is declared in
  `setup.py` under `extras_require['tests']`. Install such dependencies only in
  ignored isolated venvs and track a dependency audit; do not install them
  globally.
- The stable F2P behavior is `tests/test_chinese.py::test_chinese`: buggy fails
  with a UTF-8 log read error, fixed passes. A standalone oracle should create
  its own temporary snoop log and assert non-ASCII text preservation directly.
- Project-level P2P-broad for PySnooper retains 24 stable tests out of 29
  collected/common nodeids. Four tests fail on both buggy and reference
  checkouts under the retained Python 3.11 environment and must be excluded as
  buggy-baseline failures.
- The reference patch touches both `pysnooper/tracer.py` and
  `pysnooper/pycompat.py`. Candidate construction must support multi-file
  reference diffs; otherwise the reference patch can be incomplete.
- Label-leakage guards should match full tokens, not arbitrary substrings:
  `noop` is a substring of `PySnooper` and `pysnooper`, so substring matching
  falsely blocks legitimate candidates.
- `missing_change_1` is not a valid negative under the current Python 3.11
  oracle because it keeps the UTF-8 decode and UTF-8 log write behavior while
  omitting only Python 2 compatibility. Partial negative allowlists must be
  validated against the retained oracle before final dataset admission.
- `bugsinpy_PySnooper_1` now contributes six validated candidates over 24 stable
  P2P-broad tests and is admitted to `p2p_broad_main` as the sixth completed
  project-level main task.

## 2026-06-12 PySnooper_2 boundary decision

- `bugsinpy_PySnooper_2` checks out, but its original F2P path does not reach
  the target `custom_repr` assertion under the retained pipeline.
- The buggy checkout's copied `tests/test_pysnooper.py` imports
  `.mini_toolbox`, but `tests/mini_toolbox.py` is absent from the retained
  checkout.
- The reference checkout imports `pycompat.PY2` from `pysnooper/tracer.py`, but
  `pysnooper/pycompat.py` does not define `PY2` in the retained checkout.
- This is an unclear experimental-boundary problem, not a simple declared
  dependency or coverage-instrumentation blocker. A fixture shim could change
  test preconditions or output-capture behavior.
- User-confirmed rule: do not introduce task-specific
  compatibility/test-fixture shims for main-cohort admission at this stage.
- `bugsinpy_PySnooper_2` is therefore recorded as a blocked feasibility case
  with `p2p_broad_main_included = false`; next try `bugsinpy_PySnooper_3`, and
  if it needs the same class of shim, block it and move to `bugsinpy_fastapi_1`.

## 2026-06-12 PySnooper_3 candidate validation

- `bugsinpy_PySnooper_3` targets the older `pysnooper/pysnooper.py` file-output
  bug: the buggy code opens `output_path`, which is undefined, instead of the
  user-provided `output` path.
- Initial collection failed on missing `future`, then `python_toolbox`. Both are
  declared in the retained checkout through `requirements.txt` and
  `test_requirements.txt`, so installing them into a separate ignored venv is
  acceptable and should be audited.
- Do not reuse and mutate the `PySnooper_1` venv for this older checkout. Use a
  separate ignored environment, `outputs/envs/pysnooper3_p2p_py311`, so each
  task's dependency audit remains accurate.
- Unlike `PySnooper_2`, this task does not require a fixture shim or source-tree
  compatibility injection. Declared dependency installation is not the same as
  changing test fixtures.
- The reference patch is a single-line fix, so generic partial construction
  produces too few difficult negatives. A task-specific negative that changes
  the file mode but keeps the undefined `output_path` gives a relevant
  issue-not-fixed candidate.
- `bugsinpy_PySnooper_3` contributes four validated candidates over four stable
  P2P-broad tests and is admitted to `p2p_broad_main` as the seventh completed
  project-level main task.

## 2026-06-12 FastAPI_1 scope timeout boundary

- `bugsinpy_fastapi_1` has a clear F2P oracle:
  `tests/test_jsonable_encoder.py::test_encode_model_with_default` fails on the
  buggy checkout with an unexpected `exclude_defaults` keyword argument and
  passes on the fixed checkout.
- Its isolated environment uses only declared project/runtime test dependencies
  installed under ignored `outputs/envs/fastapi1_p2p_py311`.
- Full-repo project-level P2P-broad construction timed out twice and produced no
  `data/p2p_scopes/bugsinpy_fastapi_1_p2p_broad.json` manifest, even after an
  expanded execution window.
- This is a scope-policy boundary, not a candidate-label result. Do not mark the
  task as `p2p_broad_main` without an explicit decision on whether FastAPI's
  project-level P2P scope may be defined as the main `tests/` directory.
- User confirmed a general official-test-root policy: project-level P2P-broad
  may use a project's official test roots after repeated full-repo discovery
  timeouts, but not task-local test files.
- The scope builder needed a small execution-chain repair for directory roots:
  `static_source_segments` must read source files from collected nodeids when
  `--test-path` is a directory. Reading the directory path itself raises
  `PermissionError`.
- After that repair, the FastAPI `tests/` official-root attempt still exceeded
  the 60 minute construction budget and produced no P2P manifest. Record
  `bugsinpy_fastapi_1` as `pending_blocked_official_test_root_timeout`; do not
  keep retrying or downgrade to a task-file scope.

## 2026-06-12 FastAPI_2 and Sanic_1 feasibility

- `bugsinpy_fastapi_2` has a clear F2P oracle under the existing FastAPI venv:
  buggy receives `Socket Dependency`, fixed receives `Override`. It should not
  trigger another long FastAPI official-root P2P attempt because `fastapi_1`
  already exhausted that project-level scope path.
- `bugsinpy_sanic_1` requires a separate ignored dependency environment. Do not
  install the full requirements file: it contains broad unrelated dependencies
  and platform-hostile packages. Install only the declared runtime/test subset
  needed for the F2P and P2P probe.
- `multidict==4.7.6` can be installed with `MULTIDICT_NO_EXTENSIONS=1` to avoid
  the local MSVC build-tool blocker while preserving the package API needed by
  this probe.
- Old Sanic/aiofiles under Python 3.11 needs external runtime compatibility for
  `asyncio.coroutine` and legacy `loop=` keyword arguments on asyncio
  primitives. Keep this in the shared compat shim and record it as a runtime
  compatibility boundary, not a source or test-fixture edit.
- `bugsinpy_sanic_1` has a clear F2P oracle after that compatibility layer:
  buggy middleware order is `[1, 2, 3, 6, 5, 4]`, fixed passes with
  `[1, 2, 3, 4, 5, 6]`.
- Sanic project-level P2P-broad construction reached the 60 minute budget while
  running timeout-related tests and produced no manifest. Record it as
  `pending_blocked_project_level_scope_timeout`; do not downgrade to task-file
  P2P for main evidence.

## 2026-06-12 Scrapy_1 dependency blocker

- `bugsinpy_scrapy_1` checkouts succeed, but the target unittest F2P commands
  require Twisted before any oracle behavior can be observed.
- Installing the declared Scrapy dependency `Twisted==20.3.0` in the isolated
  probe venv fails on Windows/Python 3.11 because the package builds a native
  extension and local Microsoft Visual C++ 14.0+ build tools are unavailable.
- Do not silently replace Twisted with a newer wheel-bearing version, stub the
  dependency, or edit Scrapy fixtures for main-cohort admission. Record the task
  as `blocked_dependency_native_build` and skip Scrapy-family candidates unless
  the dependency/toolchain boundary is explicitly revisited.

## 2026-06-12 youtube-dl_1 project-level discovery timeout

- `bugsinpy_youtube-dl_1` has a clean retained F2P oracle: the buggy checkout
  treats `is_live=False` as a match, while the fixed checkout passes.
- Full project-level unittest scope construction can still be infeasible even
  for a low-dependency utility bug. The `test/` discovery/P2P run reached 30
  minutes and produced only the compat shim directory, with no manifest.
- Do not convert this clear F2P result into main evidence by downgrading to
  `test_utils.py` task-file P2P. Record the project-level discovery timeout and
  move to the next candidate.

## 2026-06-12 Tornado local-server tests on Windows

- Tornado websocket/http tests that use local sockets fail under Python 3.11 on
  Windows with the default Proactor event loop because `add_reader` is not
  implemented.
- Setting `asyncio.WindowsSelectorEventLoopPolicy()` before importing/running
  Tornado tests restores the local test-server execution path and exposes the
  actual `bugsinpy_tornado_1` oracle: buggy `set_nodelay` asserts on
  `self.stream`, fixed passes.
- Keep this as a shared runtime compatibility shim for Windows local-server
  tests. It is not a Tornado source edit, test fixture edit, or external network
  dependency.
- `bugsinpy_tornado_1` still did not complete project-level unittest
  P2P-broad construction after the selector policy fix. The run reached 40
  minutes with only the compat shim written, and cleanup observed an SSL
  iostream test active. Record the task as a project-level scope timeout rather
  than downgrading websocket_test.py to main evidence.

## 2026-06-12 BugsInPy checkout parallelism boundary

- Do not run buggy and fixed checkout for the same BugsInPy task in parallel.
  The `bugsinpy-checkout` script uses the shared
  `projects/<project>/bugs/<id>/` directory as temporary storage for copied
  test and changed files, then removes those temporary directories.
- Parallel same-task checkout can race and leave one checkout with incomplete
  injected tests, as observed for `bugsinpy_tornado_9` fixed checkout missing
  `test_url_concat_none_params`.
- Safe parallelism is across different task ids, or after checkout has already
  completed. Same-task buggy/fixed checkout should stay serial.
- `bugsinpy_tornado_9` confirms that a pure-function F2P target does not by
  itself make Tornado project-level P2P feasible. The F2P oracle is clear after
  serial checkout repair, but project-level `tornado/test` scope construction
  still failed to produce a manifest. Treat this as shared Tornado
  project-level scope risk and avoid repeated long Tornado sweeps.

## 2026-06-12 Ansible checkout cost

- `bugsinpy_ansible_2` looked attractive at metadata level because its target is
  pure version-comparison logic, but the large Ansible checkout did not complete
  inside the bounded feasibility window.
- If a BugsInPy checkout does not write the metadata marker files such as
  `bugsinpy_run_test.sh`, do not run F2P against that partial checkout. Stop the
  checkout process, remove the incomplete retained workspace, and record a
  checkout feasibility blocker.

## 2026-06-12 Matplotlib native extension boundary

- Matplotlib checkout is expensive, and target tests can require compiled
  extensions such as `ft2font` even for apparently narrow rendering/tight-bbox
  behavior.
- Running from `PYTHONPATH=checkout/lib` is not enough for these tasks. Do not
  treat an unrelated installed Matplotlib package as checkout evidence, and do
  not silently run editable/native builds for main-cohort admission.
- `bugsinpy_matplotlib_1` should be recorded as a native/import blocker unless
  the build boundary is explicitly revisited.

## 2026-06-12 final-roadmap advice extraction

- The external advice was broadly aligned with the existing final roadmap, so
  the safe update was to add only deltas: Evidence Visibility Curve framing,
  FACR/Evidence Gain as secondary calibrated metrics, staged E0/E2/E4/E6-first
  ablation, realistic tool-only boundaries, and stale paper/cohort wording
  cleanup.
- Do not duplicate the already established E0-E7 ladder, visible/hidden
  separation, tool-only baseline list, Candidate Patches title, or scale
  tiers. Repetition makes later agents think these are competing plans.
- Treat “30-50 bugs / 100-180 patches” as the robust-thesis target, not an
  unconditional next-step gate. The latest BugsInPy sweep found real candidate
  pool and build-boundary blockers, so changing the scaling route requires a
  user decision.
- Any current result based on retained validation summaries or oracle-style
  summaries must stay labeled diagnostic, upper-bound-style, or non-realistic
  for hidden-evaluator-free merge-gate claims.

## 2026-06-12 EVP-7 protocol freeze

- User decision: choose Option A now. Freeze the current 7 completed
  project-level P2P tasks as `EVP-7 Protocol Pilot`; do not keep chasing an
  eighth BugsInPy task under the same low-friction screening boundary.
- The first protocol artifact should be task-level only:
  `data/tasks/evp7_tasks.jsonl` and
  `data/exclusions/blocked_bugsinpy_projects.jsonl`. Candidate-level EVP-7
  records must be generated in a separate step because current candidate JSONL
  files are referenced under ignored `outputs/` paths.
- When building protocol manifests, read only tracked registry and P2P scope
  files. Do not copy local retained checkout paths or infer commits from
  untracked workdirs; record missing commit/issue/touched-file fields as
  `metadata_backfill_required`.
- Blocked tasks are evidence of the sampling boundary, not noise. Preserve them
  in the blocker registry to avoid hidden cherry-picking.

## 2026-06-12 EVP-7 candidate manifest count boundary

- The task-level registry reported 36 known candidates because
  `bugsinpy_httpie_5` lacked `collection_summary.candidate_count` and label
  counts. Treat this number as a registry-known lower bound, not the final
  EVP-7 candidate count.
- The validated candidate JSONL plus P2P validation files promote to 42 tracked
  candidates: 7 correct reference patches and 35 issue-not-fixed negatives.
- Candidate manifests may carry evaluator-only fields for metrics, but evidence
  packet builders must strip labels, retained-oracle status, provenance, and
  failure taxonomy from model-visible prompts.
- When summary counts disagree, first diagnose source-of-truth granularity
  before changing inclusion policy. Here the task registry was incomplete for
  one admitted task; the candidate output files were the correct source for
  candidate-level cardinality.

## 2026-06-12 EVP-7 evidence packet leakage boundary

- Evidence packet records can be generated before every evidence level is
  complete, but they must explicitly mark missing visible evidence. Do not fill
  E4/E6 by copying retained-oracle or hidden P2P validation outcomes from the
  evaluator-side candidate manifest.
- E0/E2 are currently complete for all 42 EVP-7 candidates. E2 only exposes
  patch-apply evidence from validation; syntax/import/static analysis remains
  `not_run` until a visible static runner is added.
- E4/E6 records are useful for schema and leakage auditing, but G1 is still not
  passed because independent visible test outcomes and realistic visible tool
  summaries do not exist yet.
- The leakage audit should scan both keys and values for evaluator-only terms.
  It is a gate for accidental label/provenance leakage, not proof that G1/G5
  signal exists.

## 2026-06-12 EVP-7 visible-test runner boundary

- Visible E4 outcomes must be regenerated as a separate model-visible evidence
  source. Do not reuse retained-oracle or hidden P2P validation outcomes from
  evaluator validation JSONL.
- Empty-string `pytest_addopts_override` is meaningful: it clears project
  default addopts. Treating it as false caused cookiecutter_3 visible tests to
  fail with pytest exit code 4 until the runner switched to
  `addopts_override is not None`.
- PySnooper_1 and httpie_5 visible-test attempts currently hit environment or
  dependency import errors under Python 3.11. These are runner/environment
  boundaries, not candidate-patch failures. Do not classify pytest exit codes
  other than 0 and 1 as visible test failed; record them as `error`.
- Reusing tracked P2P manifest compat shims in the visible runner is an
  environment-consistency repair, not a new task-specific shim. The runner must
  not create or modify shims; it may only use `compat_shim.enabled=true` paths
  already recorded in tracked P2P manifests.
- After adding tracked compat-shim reuse, current visible outcome source
  completes 42/42 candidates. Three outcomes remain `error`, but they are
  candidate-induced import failures after the runner environment is aligned,
  so they count as complete visible runtime evidence. Deterministic E6 visible
  tool summaries also complete 42/42 by summarizing already model-visible
  patch-apply/static/test evidence.

## 2026-06-13 EVP-7 tool-only baseline boundary

- Tool-only decision records must be generated from model-visible evidence
  packets only. Evaluator labels may be joined only after decisions exist, and
  only for aggregate metrics.
- Apply-only is a safe but unusable baseline for EVP-7: it escalates all 42
  candidates, yielding false accept rate 0.0 and correct recall 0.0.
- Visible-tests and visible-tool-summary baselines currently have false accept
  rate 0.0, accepted precision 1.0, and correct recall 0.857143. They reject
  one correct patch, so they are strong safety baselines but not an oracle.

## 2026-06-13 EVP-7 merge-gate schema dry-run boundary

- G4 schema stability should be checked before any real verifier API call. The
  dry-run runner renders deterministic accept/reject/escalate JSON objects from
  model-visible EVP-7 packets and then parses them through the fixed schema.
- The dry-run records are not model outputs. They can prove parser/schema
  stability, evidence-level coverage, and leakage-boundary hygiene, but they
  cannot support claims about LLM merge-gate behavior.
- Keep `raw_response_text` and `parsed_output` in the dry-run records aligned:
  future API runners should be able to replace the deterministic raw response
  with a provider response while preserving the same parsed schema fields.
- Leakage scans for schema dry-run outputs should include evaluator markers
  such as final labels, construction taxonomy, hidden oracle terms, and
  candidate provenance. A parse-valid record is still invalid if it carries one
  of those markers.

## 2026-06-13 EVP-7 G5 metric scaffold boundary

- G5 needs two separate claims: metric-path readiness and real signal
  existence. Deterministic dry-run records can establish the former, but not
  the latter.
- FACR and Evidence Gain should be computed from the same aggregate confusion
  counts as FAR, accepted precision, recall, rejection, and escalation. This
  keeps the added paper-friendly metrics auditable rather than ornamental.
- Utility weights are currently a scaffold:
  `accept_correct - 5*accept_wrong - 0.25*escalate - reject_correct`.
  Before paper claims, run sensitivity analysis or document why these weights
  match the merge-gate risk model.
- The dry-run metric scaffold intentionally sets
  `g5_signal_claim_status = requires_real_llm_verifier_outputs`. Do not change
  that to passed unless genuine LLM verifier outputs have been produced under
  an approved API/model/cost boundary and analyzed through the same path.

## 2026-06-13 EVP-7 G5 prompt manifest boundary

- The G5 prompt manifest should store hashes and lengths, not full prompt text,
  so tracked artifacts can prove prompt coverage and leakage checks without
  duplicating all prompt payloads.
- `patch_verify_evidence_visibility_merge_gate_v1` is a new EVP-7 protocol
  prompt. It is not a scale-up of the stopped
  `patch_verify_evidence_first_v1` condition and does not reuse the
  retained-oracle/tool-summary boundary of
  `patch_verify_tool_augmented_evidence_v1`.
- Generic schema enum values such as `partial_fix` can appear in the prompt as
  possible verifier output categories. They are not leakage unless attached to
  a specific candidate as evaluator-side truth.
- Real G5 runs should stop on prompt-boundary failure, high smoke
  invalid-output rate, API/preflight failure, cost growth beyond the
  user-confirmed budget, or `run_error.json`.

## 2026-06-13 EVP-7 G5 preflight boundary

- Keep `configs/evp7_g5_llm.example.json` as a template only. Placeholder
  provider/model/cost/smoke/full-run fields must keep `api_ready = false`.
- `scripts/preflight_evp7_g5_llm_run.py` intentionally separates
  `structural_ready` from `api_ready`. Structural readiness can pass with the
  example config; strict API readiness must fail until the user supplies an
  ignored local config with concrete confirmations.
- The G5 preflight does not read `.env`, does not create local configs, and
  does not call any API. Credential checks belong to the final guarded runner
  after user confirmation.
- If a future agent changes the example config to concrete values, treat that
  as a scope violation unless the user explicitly asked to record those values
  in tracked files. Real provider/model/cost decisions should be local or
  documented as non-secret policy, not mixed with credentials.

## 2026-06-13 EVP-7 G5 guarded workflow boundary

- A guarded workflow should offer check-only and mock modes before real API
  execution. The check-only mode must report `model_call_attempted = false` and
  `api_call_attempted = false`.
- Mock G5 workflow records are useful only for validating parser, schema, and
  metrics plumbing. Keep `g5_signal_claim_status =
  requires_real_llm_verifier_outputs`; do not relabel mock variation as
  evidence-visibility signal.
- The initial workflow implementation exposed a relative-path bug: passing a
  relative `reviews_out` into `analyze_evp7_schema_dry_run_metrics.py` caused
  `Path.relative_to(REPO_ROOT)` to fail. Fix both caller and analyzer by
  resolving paths against `REPO_ROOT` before reading or reporting paths.
- The real execute path must reject the tracked example config and stop before
  API calls unless strict preflight passes on an ignored local config and the
  user has explicitly confirmed provider, model, cost ceiling, smoke scope, and
  full-run permission.

## 2026-06-13 EVP-7 G5 local config helper boundary

- The helper for `configs/evp7_g5_llm.local.json` must default to dry-run and
  must not choose provider, model, budget, smoke scope, or full-run permission.
- Dry-run artifacts are allowed in tracked docs/data because they contain only
  placeholders and the required confirmation checklist. They must record
  `local_config_write_attempted = false` and `api_call_attempted = false`.
- Non-dry-run config creation must fail if any confirmation is missing. A
  failed write must leave `configs/evp7_g5_llm.local.json` absent.
- The safe order after user confirmation is: create ignored local config, run
  strict preflight, run check-only workflow, execute smoke, inspect smoke
  invalid-output/cost, then decide whether full run is allowed.

## 2026-06-13 GitHub sync retry after transient network failure

- A failed `git push` with `Failed to connect to github.com port 443` or
  `Recv failure: Connection was reset` should be treated as a transport issue,
  not as a repository-state issue, after `git status --short --branch` shows a
  clean tree ahead of origin.
- Re-run a connection check or retry `git push origin main` before changing
  repository state. In this case the retry succeeded and synchronized
  `37e1b7f` to `origin/main`.
- Do not create extra commits only to compensate for a failed push; first
  verify whether the local commit is already clean and simply awaiting network
  recovery.
- `audit_execution_readiness.py` must use `git status --short --branch`, not
  plain `git status --short`, so a clean working tree that is still ahead of
  upstream remains visible in readiness reports.

## 2026-06-13 EVP-7 G5 DeepSeek max-token smoke repair

- DeepSeek V4 can return an empty final `content` when the completion budget is
  too low, even when the prompt is valid. In EVP-7 G5, `max_tokens = 1024`
  produced valid E0/E2 outputs but empty E4/E6 outputs in the first 4-packet
  smoke.
- Treat this as an execution-chain output-format failure, not as model signal.
  Do not continue to full run until a repaired smoke has invalid-output rate 0.
- Raising G5 `max_tokens` to 4096 matched the earlier DeepSeek smoke lesson and
  repaired the same 4-packet smoke to 4/4 parse-valid outputs.

## 2026-06-13 EVP-7 G5 parallel full-run efficiency boundary

- If a long sequential G5 run is interrupted but the Python process continues in
  the background, inspect `Win32_Process.CommandLine` before starting another
  run. Stop only the obsolete non-concurrent process to avoid duplicate API
  spend.
- Use bounded concurrency for real G5 full runs after smoke passes. The first
  successful full run used `--concurrency 4`, completed 168 records, preserved
  original packet order, and wrote outputs once after all workers completed.
- Do not silently repair schema-invalid LLM outputs after a full run. The
  single invalid E0 record is a real output-quality boundary and should be
  reported in summaries instead of overwritten by a targeted retry.

## 2026-06-13 EVP-7 G5 bounded concurrency boundary

- Keep G5 execution sequential by default. `--concurrency` should be an explicit
  full-run speed knob, not an implicit behavior change.
- Validate all prompt boundaries before submitting parallel model calls. This
  keeps leakage or prompt-shape failures from becoming partially executed API
  runs.
- Parallel workers should return in any order, but the runner must write review
  JSONL in the original packet order. Do not let multiple workers append to the
  same JSONL file.
- Start bounded full runs at concurrency 4 or 6. If rate limits, timeouts, or
  invalid outputs rise, stop and diagnose instead of raising concurrency.

## 2026-06-13 EVP-7 controlled expansion probe status boundary

- Expansion readiness should distinguish metadata candidates from attempted
  probes. Keep attempted probe outcomes in
  `data/tasks/evp7_controlled_probe_results.json` and let the readiness
  summarizer overlay those statuses, rather than editing generated Markdown by
  hand.
- `bugsinpy_fastapi_4` checkouts completed, but both buggy and fixed versions
  failed during pytest collection under the current Pydantic v2 environment.
  Treat this as a dependency-environment blocker, not as F2P evidence.
- `bugsinpy_sanic_2` checkouts completed quickly, but both versions failed
  before the target test because `aiofiles` is absent. Treat missing declared
  runtime dependencies the same way: record the blocker and do not install
  silently inside a F2P-only probe.
- Do not silently install or substitute dependencies after a collection-level
  environment blocker. Move to another independent lane unless a later plan
  explicitly authorizes dependency isolation.
- In parallel F2P-only triage, keep each task's buggy/fixed checkout serial,
  but run independent project lanes concurrently. This saved time while still
  keeping each F2P result interpretable.
- `bugsinpy_youtube-dl_2` established clean F2P under the no-install boundary.

## 2026-06-16 Sanic 2 dependency recheck and P2P gate

- `bugsinpy_sanic_2` should no longer be treated as only
  `missing_aiofiles_dependency`. An explicit isolated env
  `outputs/envs/sanic2_f2p_py311` with `httpx==0.9.3`,
  `aiofiles==0.5.0`, `websockets==8.1`, `multidict==4.7.6`, and the existing
  Python 3.11 asyncio shim reaches the actual F2P behavior: buggy fails on
  missing `AsyncioServer.start_serving`, fixed passes.
- Reusing the older `sanic1_p2p_py311` env is not equivalent for Sanic 2,
  because it carries `httpx==0.11.1` and fails during Sanic import before the
  target behavior.
- The Sanic official tests-root P2P construction for `bugsinpy_sanic_2`
  exceeded a 15 minute outer budget and produced no manifest. Do not admit this
  task, do not construct candidates, and do not fall back to task-file-only P2P
  without an explicit policy decision.

## 2026-06-16 Tornado 2 F2P without repeated long P2P

- `bugsinpy_tornado_2` can be reconstructed from the retained local Tornado Git
  clone without a GitHub checkout. Follow the BugsInPy flow: reset to fixed,
  copy the fixed test file and fixed source file, reset to buggy, then copy the
  fixed test into both checkouts and the fixed source only into the fixed
  checkout.
- Use the same Windows selector event loop policy documented for Tornado 1:
  `asyncio.WindowsSelectorEventLoopPolicy()`. Without changing Tornado source or
  tests, this reaches the real F2P behavior for local HTTP server tests.
- Tornado 2 F2P is clear: buggy fails with `HTTPStreamClosedError` and a
  5-second `TimeoutError`, fixed passes.
- Do not launch another long Tornado project-level unittest P2P sweep by
  default. Tornado 1 and Tornado 9 already show repeated timeout risk. A dry-run
  is enough to record the boundary unless a new explicit bounded P2P policy is
  approved.
  It is not admission evidence until project-level P2P-broad and candidate
  revalidation are explicitly run.
- In F2P-only screening, distinguish path setup from dependency installation:
  `ansible_1` needed `PYTHONPATH=lib` to reach the package, but then hit the
  Windows `fcntl` blocker. That final blocker should be recorded rather than
  hidden behind the first path error.
- Existing runtime compatibility shims can be reused when already documented
  for the project family, as with Luigi `inspect.ArgSpec/getargspec`; once the
  next missing dependency appears, stop rather than silently installing it.
- When one project family establishes clean F2P under the no-install boundary,
  additional same-family F2P-only probes can be efficient as long as they do
  not bypass the project-level P2P-broad admission gate. The youtube-dl 3-5
  continuation added three F2P candidates without changing main-cohort status.
- Prefer the pure utility tests inside youtube-dl for additional F2P-only
  screening before attempting expensive project-level P2P. They run quickly and
  make the later P2P decision more evidence-based.
- After seven clean `youtube-dl` F2P probes, additional F2P-only screening has
  diminishing value. The next efficient gate is a single bounded representative
  project-level P2P attempt; do not run multiple long youtube-dl P2P attempts in
  parallel unless the first representative manifest succeeds.
- Static no-run preflight is useful before an expensive P2P decision. For
  `youtube-dl_6`, buggy/fixed both expose 154 static unittest methods under
  `test/`, 111 remain after current static exclusions, and the remaining method
  sets are identical. This supports one bounded representative attempt but does
  not prove dynamic P2P feasibility.
- Keep this preflight reproducible with `scripts/static_unittest_p2p_preflight.py`
  rather than one-off inline snippets. The script is intentionally static-only:
  it must not be used as admission evidence or as a substitute for
  project-level P2P-broad validation.
- When static preflight evidence changes the cheapest representative task,
  update the decision packet before running P2P. For the current youtube-dl
  family, `youtube-dl_7` has the smallest remaining method set under the current
  exclusions, so it should be the first bounded representative attempt if P2P is
  approved.
- Use `scripts/audit_youtubedl_p2p_decision.py` before any future youtube-dl
  P2P attempt. It catches drift between the controlled probe data, the static
  preflight sweep, the decision packet recommendation, and the command template.
- The decision audit should also compare `--fail-to-pass-nodeid` against the
  controlled probe's retained unittest target; a correct representative task is
  not enough if the oracle nodeid in the P2P command drifts.
- Keep the proposed youtube-dl P2P command in the no-run decision audit output
  with `approval_required = true`. This makes the next action copyable after
  confirmation while still preventing accidental P2P execution during
  unattended preparation.
- The youtube-dl decision audit should parse the documented PowerShell command
  and compare all expected flags against the generated approval-gated command
  packet. Partial checks on task id and oracle nodeid are not enough once the
  command becomes the handoff artifact.
- `build_pass_to_pass_scope.py --dry-run` must remain side-effect free: it
  validates inputs and prints a JSON plan, but does not create output
  directories, compat shims, or manifests. Use it before any approval-gated P2P
  execution.
- The youtube-dl decision audit should call the builder dry-run directly. This
  closes the handoff gap between a correct command packet and the actual scope
  builder accepting the command without side effects.
- API pilot preflight should be recorded as an ignored JSON/Markdown artifact,
  not only terminal output. `scripts/preflight_api_pilot.py --out-json --out-md`
  preserves no-API readiness evidence without changing local configs or calling
  the provider.
- `audit_execution_readiness.py` should consume the latest ignored API preflight
  report so it does not repeatedly ask for a preflight that already passed for
  the current local config.
- Goal completion audits must track the current research frontier, not only the
  older API/paper/artifact workflow. If `youtube-dl_7` P2P remains approval
  gated and no manifest exists, `audit_goal_completion.py` should report the
  goal incomplete.
- Human-input handoff packets must track the same frontier as goal completion.
  When the only missing required check is `youtube_dl_p2p_decision_resolved`,
  `write_human_input_packet.py` should surface a required
  `youtube_dl_p2p_decision` input and include the approval-gated command packet
  plus dry-run checks, so execution does not proceed without explicit approval
  or an explicit reject/stop decision.
- Readiness Markdown must render the same next-action state as the JSON audit.
  Do not hard-code stale fallback commands when `next_actions` is empty; report
  `None.` so the human handoff does not waste time rerunning completed API
  smoke/preflight steps.
- Experiment run ledgers must include the positive-claim run, not only the
  negative prompt-only full run. For the current project, the ledger should
  contain a separate `tool_augmented_full_api` record for
  `outputs/patch_verification_tool_augmented_full_001` and mark it as supporting
  only the conditional tool-assisted claim.
- Handoff summaries must not collapse prompt-only and tool-augmented claim
  readiness into one "positive paper claim" line. Keep the legacy prompt-only
  field for compatibility, but display prompt-only readiness and
  tool-augmented conditional readiness separately.
- Human-input packets need the same claim-boundary split as the pre-API
  handoff. A single "positive paper claim ready" line is ambiguous after the
  tool-augmented full run passed while prompt-only evidence-first remains a
  negative/redesign result.
- youtube-dl unittest discovery can produce dynamic `test.test_download`
  nodeids that are not visible to AST source-token filtering. Static
  `--static-exclude-token` rules do not catch those generated tests, so a real
  P2P run can enter long network/download batches even when static preflight
  looks cheap. Treat this as a scope-policy decision: add an explicit
  nodeid-level exclusion only after recording the policy boundary.
- For that case, use `build_pass_to_pass_scope.py --exclude-nodeid-prefix`
  rather than adding misleading static source tokens. The policy should name the
  generated prefix, keep the retained F2P oracle untouched, and be verified by
  dry-run before any real P2P rerun.
- For unittest project-level scopes, static source filtering must map dotted
  nodeids like `test.test_age_restriction.TestAgeRestriction.test_youtube` back
  to `test/test_age_restriction.py`. Method-only source scanning is also too
  shallow for local helper wrappers such as `_assert_restricted()` calling
  `_download_restricted()`. Expand only same-file helper calls so external
  dependency tokens catch indirect downloads without inventing a broad
  cross-file analysis.
- After that fix, `bugsinpy_youtube-dl_7` completed project-level P2P-broad
  with the explicit `youtube_dl_dynamic_download_nodeid_exclusion_v1` policy:
  1472 common unittest nodeids, 1297 generated download nodeids excluded by
  prefix, 64 external-dependency tests excluded statically, one retained oracle
  excluded, and 108 P2P-broad tests retained.
- Once a previously approval-gated P2P path has produced a tracked manifest,
  handoff packets should stop rendering the old approval command. Otherwise a
  later continuation can accidentally rerun stale parameters that predate the
  final scope policy.
- Candidate-level P2P validation must dispatch by the P2P manifest's
  `test_framework`. `bugsinpy_youtube-dl_7` stores unittest dotted nodeids; when
  the validator reused pytest, the correct reference patch was mislabeled as a
  regression even though the patch and P2P scope were sound. The fix is to run
  unittest scopes as `python -m unittest -q <nodeids...>` and keep pytest only
  for pytest scopes.
- Visible-test reproduction has the same runner-boundary requirement. After
  admitting a unittest task, `run_evp7_visible_tests.py` must use the task's P2P
  manifest framework instead of assuming pytest, otherwise E4 evidence can drift
  from P2P validation behavior.
- When the EVP-7 cohort grows, hardcoded gate constants must be updated in the
  builders before trusting check output. The `youtube-dl_7` admission changed
  the current structural counts from 7 tasks / 42 candidates / 168 packets to
  8 tasks / 46 candidates / 184 packets. Old real LLM summaries should remain
  scoped to the cohort they actually ran on.
- The fresh 184-packet DeepSeek V4 G5 run produced one schema-invalid record:
  `evp7_candidate_0004__E2` had an empty raw response, so parsing failed with
  `invalid_json:No JSON object found in model response`. Treat this as an
  API/model-output quality issue, not a prompt-boundary or evidence-leakage
  failure. The tracked summary should report the invalid rate and keep raw
  responses only in ignored `outputs/evp7_g5_llm_002/`.
- The 184-run quality audit should be `passed_with_limitations`, not an
  unconditional pass. The key boundary is that DeepSeek E4/E6 reached zero
  observed false accepts and 0.375 correct recall, while deterministic
  visible-test tool-only recall is 0.875. Therefore the paper can claim
  evidence visibility changes LLM merge decisions in the EVP-7 pilot, but
  cannot claim the LLM outperforms the tool-only baseline.
- `bugsinpy_youtube-dl_6` hit the same generated-download P2P hazard as
  `youtube-dl_7`: a broad unittest run can spend the full batch budget inside
  `test.test_download.TestDownload.*`. Reuse the explicit
  `youtube_dl_dynamic_download_nodeid_exclusion_v1` boundary for this family,
  verify it with `--dry-run`, and confirm the final manifest has zero retained
  nodeids with that prefix.
- The `youtube-dl_6` admission changed the current structural cohort from
  8 tasks / 46 candidates / 184 packets to 9 tasks / 50 candidates / 200
  packets. Update no-API builders and preflight gates to the new counts, but do
  not rewrite the old real DeepSeek G5 full-run claim: that run remains scoped
  to the earlier 184-packet cohort even after the separate 200-packet run is
  executed and audited.
- The fresh 200-packet DeepSeek V4 G5 run for the 9-task cohort produced one
  schema-invalid record: `evp7_candidate_0021__E4` failed with
  `invalid_suspected_failure_type:test_overfitting`. Treat this as model-output
  quality, not a prompt-boundary, leakage, or execution-chain failure. Keep raw
  responses only in ignored `outputs/evp7_g5_llm_003/`.
- The 200-run quality audit is `passed_with_limitations`: E4/E6 reached zero
  observed false accepts and accepted precision 1.0, with positive recall and
  positive evidence gain over E0. The limitation is that E4 recall is 0.111111
  and E6 recall is 0.222222, still below deterministic visible-test tool-only
  recall 0.888889. The supportable claim is a pilot evidence-visibility signal,
  not LLM superiority over the tool-only baseline or scale generalization.
- `bugsinpy_youtube-dl_5` can reuse the approved
  `youtube_dl_dynamic_download_nodeid_exclusion_v1` policy. The canonical
  static tokens are `YoutubeDL(`, `download(`, `urlopen`, `http://`, and
  `https://`; using a partial token set changes the static preflight count and
  must be treated as a command-reproduction bug before running P2P.
- The `youtube-dl_5` admission changed the structural cohort to
  10 tasks / 54 candidates / 216 packets. The fresh DeepSeek V4 G5 run for this
  cohort produced one schema-invalid record: `evp7_candidate_0034__E4` failed
  with `invalid_json:No JSON object found in model response`. Treat this as
  model-output quality, not prompt-boundary, leakage, or execution-chain
  failure. Keep raw responses only in ignored `outputs/evp7_g5_llm_004/`.
- Do not hardcode G5 quality-audit cohort sizes. The 216-run initially failed
  `audit_evp7_g5_full_run_quality.py` because the script still expected
  200 reviews, 50 candidates per level, and 9-task wording. Quality audits
  should derive review count, level counts, and invalid-output rate from the
  tracked summary so controlled expansion does not create false gate failures.
- `bugsinpy_youtube-dl_2` can reuse
  `youtube_dl_dynamic_download_nodeid_exclusion_v1`. Its canonical static
  preflight leaves 151 unittest methods after excluding `YoutubeDL(`,
  `download(`, `urlopen`, `http://`, and `https://`, with no buggy/fixed set
  diff. The final P2P-broad manifest retains 147 tests after excluding 1997
  generated download nodeids, 86 static external-dependency tests, the F2P
  oracle, and 4 buggy-baseline failures.
- `build_evp7_visible_tool_summaries.py` depends on the latest
  `evp7_evidence_packets.jsonl`; it should not be run in parallel with
  `build_evp7_evidence_packets.py` after a cohort-size change. In the
  `youtube-dl_2` admission, running them concurrently made tool summaries read
  the old 54-candidate packet file. Sequentially rerunning tool summaries and
  then evidence packets fixed E6 completeness for the 58-candidate cohort.
- The 232-packet DeepSeek V4 G5 run initially produced two empty model
  responses: `evp7_candidate_0055__E4` and `evp7_candidate_0057__E0`. When raw
  response length is zero and prompt-boundary checks already passed, classify
  this as API/model output quality rather than prompt leakage or evidence data
  failure.
- For empty model responses, the shortest repair is a targeted retry of only
  those packets with the same config, prompt, model, temperature, and max token
  setting. Write the merged result to a new ignored repaired output directory
  and keep the original full-run output for audit.
- G5 metric scaffold checks must derive expected record counts from the current
  candidate manifest. The invariant is
  `total_reviews == candidate_count * len(EVIDENCE_LEVELS)` and each evidence
  level has exactly `candidate_count` records. Do not hardcode 200/50,
  216/54, or any historical cohort size into current gates.
- After a task is formally admitted, update both the cohort registry and the
  controlled-probe ledger. `youtube-dl_5` and `youtube-dl_6` were already in
  `p2p_broad_main`, but stale `f2p_established_p2p_not_attempted` probe records
  kept them in expansion readiness as P2P candidates. Refresh readiness only
  after the ledger and registry agree.

## 2026-06-13 youtube-dl_4 controlled admission boundary

- `bugsinpy_youtube-dl_4` reuses the same
  `youtube_dl_dynamic_download_nodeid_exclusion_v1` policy, but it still needs
  its own static preflight, builder dry-run, real P2P manifest, oracle
  validation, and candidate P2P validation before admission. Family-level
  policy reuse is not sample admission.
- The ydl4 static preflight left 141 unittest methods after excluding
  `YoutubeDL(`, `download(`, `urlopen`, `http://`, and `https://`, with no
  buggy/fixed remaining-set diff. The final manifest retained 137 P2P-broad
  tests after excluding 1772 generated download nodeids, 81 static
  external-dependency tests, the F2P oracle, and 3 buggy-baseline failures.
- Candidate patch hunks need direct apply validation before trusting labels.
  The first ydl4 irrelevant patch contained a corrupt context hunk and failed
  before oracle execution; fixing the minimal hunk header restored the intended
  negative candidate without changing the experimental design.
- The ydl4 admission changes the structural cohort to 12 tasks / 62 candidates
  / 248 packets. Update builder constants, preflight checks, readiness
  documents, and metric scaffolds to 248, but keep the repaired 232-packet
  DeepSeek G5 result scoped to the previous 11-task cohort until a fresh
  248-packet run is executed and audited.
- After any cohort-size change, run evidence packets, then visible tool
  summaries, then evidence packets again if E6 initially reads stale tool
  summaries. This dependency order is sequential and should not be parallelized.

## 2026-06-13 EVP-7 G5 248-packet full-run boundary

- The fresh 248-packet DeepSeek V4 G5 run for the 12-task cohort produced one
  schema-invalid record: `evp7_candidate_0030__E2` failed with
  `invalid_json:No JSON object found in model response`.
- This invalid response was not empty: raw response length was 444 chars and
  showed a truncated JSON object. Treat it as model-output quality, not
  prompt-boundary failure, evidence leakage, or an execution-chain bug.
- Do not silently repair non-empty schema-invalid full-run responses. Targeted
  retry is appropriate for empty model responses under the same prompt/config,
  but truncated JSON should remain in the tracked raw-output-free summary as an
  invalid-output limitation.
- The 248-run quality audit is `passed_with_limitations`: E4/E6 keep zero
  observed false accepts and accepted precision 1.0, with E4 recall 0.166667,
  E6 recall 0.25, and Evidence Gain 7.25 / 7.5. The result still does not
  support scale generalization, LLM superiority over deterministic visible-test
  tool-only baseline, or a known-cost claim.

## 2026-06-14 paper readiness frontier drift

- `scripts/audit_paper_readiness.py` originally tracked the older
  30-candidate prompt-only/tool-augmented paper route only. After EVP-7 reached
  a 12-task / 62-candidate / 248-record real DeepSeek G5 run, that audit still
  reported only the old prompt-only `stop_or_redesign` blocker and the old
  tool-augmented conditional claim.
- The fix is to keep those legacy fields for compatibility but add a separate
  `evp7_g5` readiness block. It reads only the raw-output-free tracked summary
  and quality audit, requires 248 reviews, four evidence levels with 62 records
  each, `real_llm_verifier_signal_observed_on_evp7`, no tracked raw outputs,
  positive E4/E6 recall and Evidence Gain, and the tracked EVP-7 protocol/result
  documents.
- Do not collapse these three paper-result boundaries. Prompt-only remains a
  negative/redesign result, the old tool-augmented run remains a conditional
  tool-assisted result, and EVP-7 G5 supports only bounded pilot observations
  about evidence-level variation.

## 2026-06-14 youtube-dl_11 controlled admission

- `bugsinpy_youtube-dl_3` still times out under corrected
  `youtube_dl_dynamic_download_nodeid_exclusion_v1` policy. The timeout moved
  past dynamic download tests and then stalled in `test_xpath_attr` /
  `test_xpath_element`. Treat this as a corrected-policy project-level P2P
  timeout blocker, not as permission to downgrade to task-file P2P.
- `bugsinpy_youtube-dl_11` can reuse the same youtube-dl family policy. Its
  manifest retains 160 P2P-broad tests after excluding
  `test.test_download.TestDownload*`, static external-dependency tests, the F2P
  oracle, and buggy-baseline failures.
- Candidate hunk headers must be validated before trusting oracle labels. The
  first ydl11 candidate script emitted corrupt patch hunks; fixing only the hunk
  ranges restored 4/4 patch apply and preserved the intended candidate set.
- Preserve `evp7_candidate_id` stability when adding tasks. Lexicographic sort
  places `youtube-dl_11` before `youtube-dl_2` and shifts historical IDs. Use a
  task sort key that treats the trailing bug id numerically so new youtube-dl
  tasks append after existing lower-numbered admissions.
- Registry-known candidate count is a lower bound while `httpie_5` lacks
  candidate count fields in the registry. Do not use it as a hard floor for the
  true candidate manifest; validate the generated candidate manifest directly.
- After ydl11 admission, the structural cohort is 13 tasks / 66 candidates /
  264 packets, but the latest real DeepSeek G5 run remains the previous
  12-task / 62-candidate / 248-packet run. Keep claim boundaries separate until
  a fresh 264-packet real run is explicitly authorized and audited.

## 2026-06-14 youtube-dl_13 checkout timeout boundary

- A BugsInPy checkout can fail before any F2P evidence exists. For
  `bugsinpy_youtube-dl_13`, the local checkout tool was available only through
  the retained archive and WSL bash path, but the buggy checkout exceeded the
  10 minute probe window and produced only an incomplete `.git` directory.
- Do not treat an incomplete checkout directory as a reusable workspace. If
  expected BugsInPy markers such as `bugsinpy_run_test.sh` are missing after
  timeout, stop residual processes, verify the resolved path is inside the
  intended workspace root, remove the partial directory, and record a checkout
  blocker.
- A checkout timeout is distinct from F2P failure and P2P failure. For ydl13,
  no fixed checkout, target unittest, P2P dry-run, dependency install, or
  checkout edit was performed, so the controlled-probe ledger status is
  `f2p_blocked_checkout_timeout`.
- On Windows, quality-gate subprocess output must not rely on the process
  locale. `run_local_quality_gate.py` previously used `subprocess.run(text=True)`
  without an explicit encoding, so `rg` output containing non-GBK bytes could
  raise `UnicodeDecodeError` before the gate summary was written. Use explicit
  UTF-8 decoding with replacement and make tail rendering tolerant of missing
  captured streams; this preserves the gate rules while fixing the execution
  chain.
- Tracked plans and reports should avoid local absolute workspace paths. The
  artifact dry-run treats them as package-safety violations, so checkout
  diagnostics should name the retained archive or workspace role and the task
  directory, not the developer-specific root path.

## 2026-06-14 youtube-dl_10 local clone and P2P timeout

- `bugsinpy-checkout` can return exit code 0 even when `git clone` fails. For
  ydl10, GitHub clone failed with a TLS termination, then the script continued
  and printed missing-directory errors. Always verify BugsInPy marker files
  such as `bugsinpy_run_test.sh`; do not trust checkout exit code alone.
- If the exact buggy/fixed commits already exist in a local checkout, a local
  clone can avoid a transient GitHub clone failure. The replacement must follow
  the BugsInPy checkout logic: copy the fixed test file, reset to the buggy
  commit, restore the fixed test file for buggy, and additionally restore fixed
  changed files for fixed. Verify the resulting diffs before running F2P.
- ydl10 established F2P after local clone repair, but corrected-policy
  project-level P2P-broad still exceeded the 40 minute budget with no manifest.
  Treat it like ydl3: a P2P timeout blocker, not an admission and not
  permission to downgrade to task-file P2P.

## 2026-06-14 youtube-dl_16 admission and validator ceiling

- ydl16 used the local clone checkout path after GitHub clone instability was
  observed. The admission still requires the same gates as a normal checkout:
  marker files, HEAD/diff verification, F2P fail/pass, project-level P2P-broad,
  retained-oracle validation, and P2P validation.
- Candidate patch text should be sourced from the fixed workspace `git diff`
  whenever possible. The first ydl16 candidate builder used hand-written hunks
  and produced patch-apply failures; replacing them with source-only diffs from
  the validated workspace fixed the issue without changing the candidate set.
- Validation workdirs under `outputs/` are inside the research95 Git repository
  but intentionally lack their own `.git`. Plain `git apply` can discover the
  parent research95 repository and report success without modifying the copied
  checkout. Set `GIT_CEILING_DIRECTORIES` to the validation workdir parent
  before applying candidate patches so Git treats the copied checkout as the
  working directory root.
- ydl16 admission raises the structural cohort to 14 tasks / 70 candidates /
  280 packets. The latest real DeepSeek G5 result remains the earlier
  12-task / 62-candidate / 248-packet run until a fresh 280-packet run is
  explicitly authorized and audited.

## 2026-06-14 youtube-dl_17 admission and oracle import path

- ydl17 is a pure `test/test_utils.py` unittest lane for
  `cli_bool_option`. The BugsInPy patch only changes `youtube_dl/utils.py`:
  missing optional bool params should return `[]`, while explicit `False`
  still emits the false option.
- The same local clone checkout strategy worked: both buggy and fixed
  workspaces stay on the buggy commit, with fixed test files copied into both
  sides and the fixed source file copied only into the fixed side.
- Corrected-policy project-level P2P-broad succeeded with the canonical
  youtube-dl generated-download nodeid exclusion: 2203 common nodeids,
  1967 generated downloader tests excluded, 85 static external-dependency
  tests excluded, 1 F2P oracle excluded, 4 buggy-baseline failures excluded,
  and 146 retained P2P tests.
- New oracle scripts that import the target project must add `Path.cwd()` to
  `sys.path` inside `main()` before importing project modules. The validator
  executes oracle scripts by absolute path from research95, so without this
  insertion Python resolves imports from `scripts/oracles` and misses the
  candidate checkout.
- ydl17 admission raises the structural cohort to 15 tasks / 74 candidates /
  296 packets, meeting the lower bound of the 15-20 bug expansion target. The
  latest real DeepSeek G5 result remains the earlier 12-task / 62-candidate /
  248-packet run until a fresh 296-packet run is explicitly authorized and
  audited.

## 2026-06-14 youtube-dl_43 admission and small-suite P2P

- ydl43 is a pure `test/test_utils.py` unittest lane for `url_basename`. The
  reference source patch is a one-line regex fix in `youtube_dl/utils.py` that
  allows multiple path segments before the basename.
- The old youtube-dl version around ydl43 has a much smaller collected unittest
  surface than ydl16/ydl17: 324 common nodeids instead of roughly 2200. After
  dynamic-download and static external-dependency exclusion, 32 buggy-baseline
  failures also had to be excluded, leaving 18 retained P2P-broad tests.
- This is still a valid project-level P2P-broad admission because the retained
  tests come from project-level discovery, exclude the F2P oracle, and pass the
  same repeated stability gate. It should be documented as a small-suite
  youtube-dl vintage rather than compared directly with later 140+ retained
  scopes.
- ydl43 admission raises the structural cohort to 16 tasks / 78 candidates /
  312 packets. The latest real DeepSeek G5 result remains the earlier
  12-task / 62-candidate / 248-packet run until a fresh 312-packet run is
  explicitly authorized and audited.

## 2026-06-14 youtube-dl_20 admission and HTML attribute oracle

- ydl20 is a pure `test/test_utils.py` unittest lane for
  `get_element_by_attribute`. The reference source patch broadens
  `get_elements_by_attribute` so HTML elements still match a target attribute
  when valueless attributes such as `itemscope` appear before or after it.
- The retained oracle must check both attribute orders. A partial patch that
  accepts only prefix valueless attributes or only suffix valueless attributes
  can satisfy one order and still miss the other, so the oracle needs paired
  before/after cases rather than a single copied F2P assertion.
- Corrected-policy project-level P2P-broad succeeded with the canonical
  youtube-dl generated-download nodeid exclusion: 2181 common nodeids,
  1948 generated downloader tests excluded, 84 static external-dependency
  tests excluded, 1 F2P oracle excluded, 6 buggy-baseline failures excluded,
  and 142 retained P2P tests.
- ydl20 admission raises the structural cohort to 17 tasks / 82 candidates /
  328 packets. The latest real DeepSeek G5 result remains the earlier
  12-task / 62-candidate / 248-packet run until a fresh 328-packet run is
  explicitly authorized and audited.

## 2026-06-14 youtube-dl_21 admission and urljoin bytes oracle

- ydl21 is a pure `test/test_utils.py` unittest lane for `urljoin`. The
  reference source patch decodes UTF-8 bytes for both `base` and `path` before
  validating and joining URLs.
- The retained oracle must check bytes in both positions independently and
  together. Path-only and base-only fixes are plausible partial patches: each
  fixes one new assertion but still misses the full behavior.
- Candidate builders that handwrite unified diffs must keep hunk line counts in
  sync with the normalized patch text. The local `normalize_patch_blank_context`
  helper strips trailing blank lines, so a hunk copied from `git diff` with a
  final blank context line may need reduced `-old,+new` counts after
  normalization. Otherwise `git apply` reports `corrupt patch` even when the
  code intent is right.
- Corrected-policy project-level P2P-broad succeeded with the canonical
  youtube-dl generated-download nodeid exclusion: 2107 common nodeids,
  1879 generated downloader tests excluded, 81 static external-dependency
  tests excluded, 1 F2P oracle excluded, 3 buggy-baseline failures excluded,
  and 143 retained P2P tests.
- ydl21 admission raises the structural cohort to 18 tasks / 86 candidates /
  344 packets. The latest real DeepSeek G5 result remains the earlier
  12-task / 62-candidate / 248-packet run until a fresh 344-packet run is
  explicitly authorized and audited.

## 2026-06-14 youtube-dl_23 admission and js_to_json line-comment oracle

- ydl23 is a pure `test/test_utils.py` unittest lane for `js_to_json`. The
  reference source patch requires two coordinated changes: tokenize
  `//[^\n]*` comments and make `fix_kv` drop tokens starting with `//`.
- Good partial negatives are therefore `regex_only_line_comment` and
  `replacer_only_line_comment`; each applies cleanly but still fails the
  retained oracle because the behavior needs both tokenizer and replacer logic.
- When reusing a local checkout as a clone source, copied BugsInPy marker files
  may describe the previous lane. Before F2P/P2P, verify and correct
  `bugsinpy_bug.info`, `bugsinpy_patchfile.info`, and
  `bugsinpy_run_test.sh`; otherwise audit records can silently point to the
  wrong commit pair even if the checkout diffs are correct.
- Corrected-policy project-level P2P-broad succeeded with the canonical
  youtube-dl generated-download nodeid exclusion: 2059 common nodeids,
  1836 generated downloader tests excluded, 82 static external-dependency
  tests excluded, 1 F2P oracle excluded, 3 buggy-baseline failures excluded,
  and 137 retained P2P tests.
- As with ydl21, adding candidates first left E6 complete counts stale until
  `build_evp7_visible_tool_summaries.py --check` refreshed summaries. The
  correct rebuild order after new visible outcomes is visible tests -> tool
  summaries -> evidence packets.
- ydl23 admission raises the structural cohort to 19 tasks / 90 candidates /
  360 packets. The latest real DeepSeek G5 result remains the earlier
  12-task / 62-candidate / 248-packet run until a fresh 360-packet run is
  explicitly authorized and audited.

## 2026-06-14 youtube-dl_37 admission and uppercase_escape oracle

- ydl37 is a pure `test/test_utils.py` unittest lane for `uppercase_escape`.
  The Python 3 failure is an `AttributeError` from calling
  `str.decode('unicode-escape')`; the reference patch uses
  `codecs.getdecoder('unicode_escape')` and returns the decoded string.
- Useful negatives are simple and local: importing `codecs` without replacing
  the failing call still raises the same error, while returning the raw escape
  string avoids the exception but fails the semantic decode oracle.
- Writing ydl37 marker files during checkout construction avoided the ydl23
  marker-copy issue. For future local clone reuse, marker creation should be
  treated as part of checkout construction, not as a blind file copy.
- Corrected-policy project-level P2P-broad succeeded with the canonical
  youtube-dl generated-download nodeid exclusion: 528 common nodeids,
  380 generated downloader tests excluded, 73 static external-dependency tests
  excluded, 1 F2P oracle excluded, 44 buggy-baseline failures excluded, and
  30 retained P2P tests.
- Tool summaries depend on the current evidence-packet candidate universe.
  After adding ydl37, running summaries before the first evidence-packet rebuild
  left the summary count at 90. The reliable order is visible tests -> evidence
  packets -> tool summaries -> evidence packets.
- ydl37 admission raises the structural cohort to 20 tasks / 94 candidates /
  376 packets. The latest real DeepSeek G5 result remains the earlier
  12-task / 62-candidate / 248-packet run until a fresh 376-packet run is
  explicitly authorized and audited.

## 2026-06-14 20-task cohort freeze and G5 smoke gate

- After ydl37, EVP-7 reached the planned upper bound: 20 tasks / 94 candidates /
  376 evidence packets. Continuing admissions would increase youtube-dl
  concentration and should not be the next default step.
- The correct next boundary is a frozen structural cohort plus guarded G5 smoke
  preparation. The current package is structurally ready, but it is not new LLM
  evidence because no API call has been made for the 376-packet cohort.
- `create_evp7_g5_llm_local_config.py --dry-run` is the safe way to refresh the
  confirmation packet. It does not write `configs/evp7_g5_llm.local.json` and
  records missing provider/model/cost/smoke/full-run confirmations.
- Strict preflight with the tracked example config should fail API readiness
  while passing structural readiness. That failure is the expected guard, not an
  execution bug.
- Do not execute real smoke until provider, model, max total cost, smoke packet
  count, and post-smoke full-run permission are explicitly confirmed.

## 2026-06-14 G5 376-packet cohort smoke execution

- Confirmed smoke config used `deepseek_official`, `deepseek-v4-pro`,
  `max_total_cost_usd=10`, `smoke_scope=4`, and full-run permission after
  smoke.
- Strict local preflight and check-only passed before execution. The smoke then
  produced 4 real non-mock API records, one per E0/E2/E4/E6 for
  `evp7_candidate_0001`.
- Parser/schema gate passed: 4/4 valid JSON outputs, invalid output rate 0.0.
  The model chose `escalate` for all four smoke packets.
- The recorded `cost_usd` was 0.0 for every record. Treat this as provider
  cost telemetry missing or not mapped by the client, not as proof of zero cost.
  Because the configured $10 cost ceiling cannot be reliably enforced from the
  recorded response, do not proceed to the 376-record full run without fixing
  cost observability or getting explicit user approval for this limitation.

## 2026-06-14 G5 cost observability repair

- Root cause: the G5 runner only read `response["usage"]["cost"]`. DeepSeek
  official OpenAI-compatible responses can expose token usage without a direct
  `cost` field, so the runner collapsed missing billing metadata into
  `cost_usd=0.0`.
- The fix keeps `cost_usd` for downstream compatibility but adds `usage`,
  `cost_source`, `cost_observability`, and `cost_pricing` to each review.
  Provider-reported cost wins; otherwise `deepseek_official` /
  `deepseek-v4-pro` is estimated from DeepSeek's per-1M-token pricing.
- Missing usage or unsupported pricing now produces unknown cost and stops the
  executed workflow after writing outputs. Unknown cost must never be treated as
  zero-cost budget compliance.
- Historical smoke output cannot be backfilled because it did not persist
  provider `usage`. Re-run a bounded smoke after this repair before considering
  the 376-record full run.

## 2026-06-14 post-repair G5 smoke cost check

- The repaired smoke must use a new output directory, not overwrite the
  pre-repair smoke. `outputs/evp7_g5_llm_376_smoke_002` preserves a clean
  before/after boundary.
- DeepSeek official returned token usage with prompt cache hit/miss splits.
  The runner estimated 4/4 costs from tokens with
  `unknown_cost_record_count=0` and total estimated cost USD `0.003392942`.
- The smoke also showed decision variability versus the pre-repair smoke:
  E4 was `accept`, while E0/E2/E6 were `escalate`. This is smoke-level evidence
  only and should not be analyzed as a cohort-level signal.
- After cost observability passes on a real smoke, the next decision point is
  whether to execute the full 376-packet G5 run under the confirmed cost budget.

## 2026-06-15 post-repair 376-packet G5 full run

- Run full G5 executions in a fresh directory. The post-repair 376-packet run
  used `outputs/evp7_g5_llm_376_full_001` and did not overwrite either smoke.
- `--concurrency 4` completed the 376-record run successfully while preserving
  ordered JSONL output. The runner still writes reviews only after all futures
  complete, so long runs have weak progress observability; avoid starting a
  duplicate run while waiting.
- The full run produced 376/376 valid records, E0/E2/E4/E6 each 94, no mock
  records, API attempted for all records, token-usage cost estimates for all
  records, and `unknown_cost_record_count=0`. Estimated total cost was
  0.327352058 USD.
- G5 signal status is now observed on the frozen 20-task/94-candidate/376-packet
  cohort, but the claim boundary remains pilot-scale. The quality audit still
  rejects scale-generalized claims, deterministic-baseline superiority, E6
  strict superiority over E4, and treating runner-estimated cost as an external
  billing statement.
- `audit_api_run_completeness.py` is not a valid audit for G5 review records:
  it expects the old API-pilot schema with raw response path/hash and patch
  fields. Use `summarize_evp7_g5_llm_full_run.py` plus
  `audit_evp7_g5_full_run_quality.py` for G5.

## 2026-06-15 paper-facing 376-run readiness drift

- After the 376-record G5 run, paper-facing scripts still pointed at the older
  248-record summary/audit and generated tables still described themselves as
  pre-API only. This would make the paper draft look current while the
  readiness gate was auditing stale evidence.
- Fix the drift by moving `audit_paper_readiness.py` defaults and cardinality
  checks to the current 376-record summary/audit, then regenerate paper tables
  from tracked raw-output-free summaries only.
- Keep old 248-record documents indexed as historical artifacts. The current
  claim boundary belongs to `evp7_g5_llm_376_full_summary.json` plus
  `evp7_g5_376_full_quality_audit.json`.
- The generated tables may report runner-estimated cost from provider token
  usage, but should not label it as an external DeepSeek bill. Keep unsupported
  claims explicit: scale generality, deterministic-baseline superiority, E6
  strict superiority over E4, and billing equivalence.

## 2026-06-15 IEEE draft body/table drift

- Updating `generated_tables.tex` is not enough for the IEEE submission draft:
  `write_ieee_latex_draft.py` also owns the abstract, research questions,
  result narrative, model boundary, threats, and conclusion.
- After adding EVP-7 G5 376-run tables, refresh the generator body from the
  same raw-output-free summary and quality audit. Otherwise the compiled
  submission can contain current tables but an obsolete 30-candidate-only
  narrative.
- Keep the IEEE draft claim boundary aligned with the audit: bounded EVP-7
  evidence-visibility signal is allowed; scale generality, deterministic
  baseline superiority, E6 strict superiority, and billing equivalence remain
  unsupported.

## 2026-06-15 canonical roadmap current-state drift

- `final_paper_roadmap_zh.md` is the canonical planning entry. If it still says
  the current cohort is 12 tasks / 248 packets or that the next step is
  expanding to 15-20 bugs, later execution can incorrectly restart expansion
  work that has already reached the frozen 20-task boundary.
- After a fresh cohort freeze or full G5 run, update the canonical roadmap, not
  only `current_plan_zh.md`, README, and generated paper artifacts.
- Keep 248-run text as a historical checkpoint and make the current state
  explicit: 20 tasks / 5 projects / 94 candidates / 376 evidence packets,
  376/376 parse-valid G5 records, and bounded pilot-only claims.

## 2026-06-15 evidence-visibility figure drift

- After freezing the 20-task EVP-7 cohort, the existing publication figure set
  still only contained first-pilot review-condition figures. The roadmap asks
  for an Evidence Visibility Curve, so a current paper draft needs a separate
  figure derived from the 376-run summary rather than reusing the older
  30-candidate tradeoff chart.
- Generate `fig6_evp7_visibility_curve` from
  `evp7_g5_llm_376_full_summary.json`; do not hand-copy plotted values. Keep
  `fig4_result_tradeoff` scoped to the first pilot and use fig6 for E0/E2/E4/E6
  evidence-level claims.

## 2026-06-15 EVP-7 statistical artifact boundary

- The roadmap asks for Wilson intervals, bootstrap intervals, paired
  comparisons, and per-project/per-source breakdowns. Point estimates in
  `generated_tables.md` are not enough for paper-facing statistical analysis.
- A statistics script may read ignored G5 review records, but tracked outputs
  must remain raw-output-free. Normalize records down to candidate id, evidence
  level, parse status, decision, project, patch source, label, and cost before
  computing aggregates.
- Use candidate-level bootstrap for EVP-7 because E0/E2/E4/E6 are paired by
  candidate. Report effect sizes as point-estimate deltas versus E0, and keep
  bootstrap probability/delta language bounded to the 20-task pilot.

## 2026-06-15 claim-boundary traceability

- A passing quality audit is not enough for paper readiness if the paper body
  does not visibly carry the same supported and unsupported claim boundary.
- Keep a separate claim traceability artifact that maps supported/unsupported
  claims to the tracked summary, quality audit, statistical analysis, generated
  tables, Markdown draft, and IEEE draft.
- When the traceability audit fails, prefer fixing the paper claim wording if
  the evidence already supports the claim. Only relax audit matching when the
  paper is already explicit and the matcher is too narrow.

## 2026-06-15 utility sensitivity boundary

- Utility formulas in paper tables are policy assumptions, not empirical facts.
  Report the default penalty choice and at least one bounded sensitivity grid
  before leaning on utility rankings.
- In the current EVP-7 run every evidence level has zero observed false accepts,
  so changing the false-accept penalty does not change rankings. The useful
  sensitivity axis is escalation and false-reject penalty.
- Keep sensitivity conclusions scoped to the frozen 20-task pilot. Stable
  rankings across the grid strengthen the local interpretation but do not prove
  scale generality or LLM superiority over a deterministic baseline.

## 2026-06-15 paper framing drift

- Paper tables, readiness summaries, and result sections can be current while
  high-level framing files still carry an older title or contribution claim.
  In this project the outline and research definition still centered
  AI-generated patches and a tool-augmented verifier after the roadmap had
  moved to evidence visibility for candidate patch verification.
- Treat title, one-sentence contribution, research questions, and non-claims as
  readiness-critical artifacts, not just prose. Add explicit paper-framing
  checks to `audit_paper_readiness.py` so stale framing fails the gate instead
  of silently passing because the file exists.
- Keep tool-augmented results in the paper, but describe them as a conditional
  evidence-assisted workflow. The current main title should remain
  `Candidate Patches` until AI-generated patches become a dominant validated
  candidate source.
- Do not run artifact packaging and artifact audit in parallel against the same
  ZIP path. The audit can observe a partially written archive and raise
  `BadZipFile`. Run `prepare_anonymous_artifact.py` to completion before
  `audit_anonymous_artifact.py`.

## 2026-06-15 active protocol current-state drift

- `docs/protocol/evidence_visibility_protocol.md` is an execution entry, not a
  historical note. If it still describes 86 candidates, 70 tool-only decisions
  per condition, 280 schema dry-run records, or the 248-packet run as current,
  later work can restart from an obsolete protocol state even when paper tables
  and readiness summaries are current.
- Use tracked summaries as the source of truth for protocol refreshes:
  `evp7_manifest_summary.json`, `evp7_candidate_summary.json`,
  `evp7_evidence_packet_summary.json`, `evp7_tool_only_metrics.json`,
  `evp7_merge_gate_schema_dry_run_summary.json`, and the current G5 summary.
- `audit_paper_readiness.py` should check protocol current-state text, not only
  protocol file existence. Required phrases should cover the current
  20-task / 94-candidate / 376-packet state and explicitly demote the 248-run
  to a historical checkpoint.
- Apply the same rule to `docs/experiments/evp7_protocol_pilot.md`. It began as
  the protocol-pilot launch report, but later became a high-traffic handoff
  entry. If its "current next step" still asks for a fresh 376-record G5 run
  after that run has completed, downstream agents can repeat or misprioritize
  expensive work.
- Figure drift can also happen inside reusable figure IDs. In this project,
  `fig2_evidence_visibility` originally encoded the older LLM-only /
  prompt-only evidence-first / tool-augmented condition split. For current
  EVP-7 paper-facing material, fig2 must encode the E0/E2/E4/E6 evidence-level
  boundary and keep evaluator truth labels hidden across all levels.
- The compact fig2 layout can omit the long bottom explanatory sentence for
  slide/PDF fit, but it must keep the evaluator truth labels row in the matrix
  and show that row as hidden for E0/E2/E4/E6. Removing both the sentence and
  the row would erase the hidden-evaluator boundary.
- Figure captions can drift separately from figure assets. After compacting
  fig2, the IEEE generator still described the old review-condition /
  tool-augmented boundary. Fix the generator-owned caption and add a readiness
  guard; editing only the generated `.tex` would be overwritten on the next
  paper refresh.
- Readiness checks that inspect generated LaTeX captions should normalize
  whitespace before matching prose. TeX line wrapping can split a semantically
  correct caption across physical lines and otherwise produce false blockers.
- Figure-specific typography should not change global matplotlib font settings.
  A Chinese-label draft of `fig7_decision_metric_flow` switched the global
  figure font to `Microsoft YaHei` when available, which regenerated fig1-fig6
  with unrelated visual diffs. Keep the global font stable for existing figures,
  or isolate typography to the new figure.
- A claim-bounded draft can still have the wrong narrative center. After the
  376-record EVP-7 run became the paper-facing result, the IEEE abstract and
  research questions still foregrounded the older 30-candidate three-condition
  pilot. Fix this in the generator so the current result is the main argument
  and the first pilot is diagnostic design evidence.
- Canonical roadmap drift can recur even after protocol and paper files are
  fixed. `final_paper_roadmap_zh.md` had a current-state update to 20 tasks /
  94 candidates / 376 packets, but its Phase A numbered list still described
  older 46-candidate, 200-packet, 150-tool-decision, and 248-prompt states as
  current. Paper readiness should check the roadmap itself, not only protocol
  reports.

## 2026-06-15 Nature-style reviewer audit

- A reviewer-style paper audit should be treated as a manuscript-quality
  artifact, not as new experimental evidence. It can identify technical and
  framing risks, but must not introduce new results, citations, line-specific
  claims, reviewer identities, or an editorial decision.
- The current Nature-style pre-submission audit found four next paper-writing
  risks: the EVP-7 LLM-plus-evidence result still needs clearer attribution
  against deterministic tool-only baselines; the paper needs qualitative EVP-7
  decision cases; related-work positioning must explain why evidence visibility
  is distinct from generic prompt engineering or test-only validation; and the
  reader path should foreground the evidence-packet-to-metric flow before
  first-pilot chronology.

## 2026-06-15 EVP-7 tool-only attribution boundary

- Aggregate LLM metrics are not enough to answer the reviewer question "is the
  LLM doing more than restating tool evidence?" Add candidate-level
  tool-only-vs-LLM overlap analysis before strengthening any LLM contribution
  claim.
- For the current EVP-7 result, matched E6 LLM decisions agree with the
  visible-tool-summary baseline on 76/94 candidates, accept no candidate outside
  the tool-only accept set, and recover 4/4 observed tool-only false accepts.
  The same comparison also downgrades 12/19 tool-only true accepts. The
  defensible wording is therefore a bounded safety/recall attribution boundary,
  not LLM superiority over deterministic visible evidence.

## 2026-06-15 EVP-7 qualitative case boundary

- Qualitative cases should be reproducible selections from structured review
  records, not hand-picked prose copied from raw responses. Keep `raw_response`
  and prompt text out of tracked artifacts, and validate the selected cases
  against expected decision sequences.
- Separate model-visible sequence from evaluator-only interpretation. The
  model-visible side may contain E0/E2/E4/E6 decisions, confidence, risk flags,
  and evidence categories. Hidden labels, patch source, and validation outcomes
  belong only in an explicitly marked evaluator-only section.
- Use qualitative cases to explain decision mechanics and reader flow. They do
  not increase sample size and must not be used to make scale-generalized claims
  beyond the frozen EVP-7 pilot.

## 2026-06-15 related-work positioning boundary

- Nature/CNS-only citation scope can be wrong for a software-engineering claim.
  When the paper needs to position against benchmarks, automated program repair,
  or agentic software engineering, use field-specific primary sources and record
  the scope decision rather than forcing irrelevant Nature/CNS citations.
- Related work should be grouped by mechanism: real-bug benchmarks, patch
  plausibility/test-suite validation, and LLM/agent repair. End the section by
  stating the gap this paper fills: evidence visible to the verifier at
  accept/reject/escalate decision time.
- Evidence Gain must remain a descriptive pilot metric for the frozen EVP-7
  protocol. Do not frame it as a standardized community benchmark score unless
  a later paper explicitly validates it as such.

## 2026-06-15 reader-flow simplification

- Put the experiment's unit of analysis before historical runs. The reader
  should see candidate patch -> model-visible evidence packet ->
  accept/reject/escalate decision -> hidden-label join -> aggregate metric
  before first-pilot chronology.
- Existing figures can carry this structure. When `fig7_decision_metric_flow`
  exists, reference it in the IEEE draft rather than leaving it as an unused
  asset.
- Keep first-pilot API and tool-augmented results as diagnostic design evidence.
  The current paper-facing result remains the frozen EVP-7 evidence-visibility
  run.

## 2026-06-15 manuscript consistency polish

- A draft can pass claim-boundary checks while still sounding too strong.
  Words such as "establishes" are risky in the conclusion when the evidence is a
  bounded single-model pilot. Prefer "reports", "shows bounded variation", or
  "supports bounded observations".
- Keep paper-facing metric names canonical. `Evidence Gain` should stay
  title-cased in tables, prose, captions, and generated drafts; do not let source
  generators reintroduce lowercase variants.
- Unsupported claims should be readable claims, not a long audit string pasted
  into prose. Format them as explicit rejected interpretations so reviewers can
  see the boundary without parsing JSON-like text.

## 2026-06-15 final artifact packaging checklist

- When the paper starts referencing a new figure, update the artifact audit's
  required-file list in the same pass. Otherwise the manuscript can compile while
  the anonymous package silently omits a required reviewer-facing asset.
- Keep a tracked submission checklist separate from ignored `artifacts/`
  outputs. The checklist is the stable reviewer/maintainer entry point; the ZIP,
  manifest, and audit reports are generated delivery artifacts.
- Do not run artifact packaging and artifact audit in parallel. The audit reads
  the ZIP and can observe a partially written archive if both commands overlap.

## 2026-06-15 Git sync ahead-state handoff

- A configured remote is not the same as GitHub sync. The sync packet must parse
  `git status --short --branch` and require `ahead=0`, `behind=0`, a clean
  working tree, and an upstream before reporting `sync_ready=true`.
- When the branch is locally ahead, the handoff should require a push/defer
  decision. Do not report sync complete just because `git remote -v` is present.
- The safe command template for an already initialized repo should inspect
  ignored paths and `origin/main..HEAD` before the final `git push origin main`.

## 2026-06-16 plan and file-map organization

- When the active execution log becomes large, do not split, delete, or reorder
  historical plan sections without an explicit archival decision. Add a short
  current-state entry instead and point README/INDEX to it.
- Keep `current_plan_zh.md` as the strict append-only execution log, and keep
  `final_paper_roadmap_zh.md` as the canonical research route. A short state map
  may summarize them, but must not override them.
- For broad "整理项目文件" requests, use a non-destructive pass first: audit
  current status, add/update indexes, and list future cleanup candidates rather
  than moving or deleting files silently.

## 2026-06-16 EVP-7 expansion gate metadata repair

- Expansion readiness depends on registry metadata as well as the candidate
  manifest. `bugsinpy_httpie_5` had six tracked candidates in
  `data/patches/evp7_candidates.jsonl`, but its cohort-registry entry lacked
  `collection_summary.candidate_count`, causing registry-derived candidate
  totals to read as 88 instead of the paper-facing 94.
- Repair the registry metadata from tracked candidate and P2P evidence before
  making any expansion decision. After repair, protocol summary, expansion
  readiness, candidate manifest, and evidence-packet counts align at 20 tasks /
  94 candidates / 376 E0/E2/E4/E6 packets.
- A refreshed expansion gate that reports zero
  `f2p_established_p2p_not_attempted` tasks is not a cohort expansion. Treat it
  as a boundary result requiring an explicit next probe/data-source decision
  before admission.

## 2026-06-16 self editable Git requirements in BugsInPy screening

- Do not treat every URL in `requirements.txt` as an external network-service
  blocker. `thefuck` tasks use a self editable Git requirement such as
  `-e git+https://github.com/nvbn/thefuck@...#egg=thefuck`; the target
  `bug.info` and `run_test.sh` do not contain network references.
- Classify that pattern as a metadata note (`self_editable_git_requirement`)
  and keep it out of `network_reference_in_metadata`. This surfaces fresh
  project-diverse probe lanes without silently admitting them.
- The next valid expansion step is still bounded checkout/F2P probing. Metadata
  eligibility for `bugsinpy_thefuck_1` does not satisfy project-level
  P2P-broad, candidate construction, or candidate revalidation.

## 2026-06-16 BugsInPy checkout can mask clone failure

- The BugsInPy checkout script can continue after `git clone` fails and still
  return success, leaving no checkout directory and producing downstream
  `cd`/`cp`/`git reset` errors. Do not treat checkout process exit code alone
  as evidence of a valid checkout.
- For `bugsinpy_thefuck_1`, both buggy and fixed checkout attempts failed while
  cloning `https://github.com/nvbn/thefuck` over port 443. Record this as
  `f2p_blocked_checkout_network`, not as F2P evidence and not as an admission
  candidate.
- Future checkout probes must verify the expected checkout directory and marker
  files (`bugsinpy_bug.info`, `bugsinpy_run_test.sh`, and target test file)
  before running tests or summarizing F2P status.

## 2026-06-16 thefuck_1 F2P retry after checkout recovery

- Once GitHub checkout became reachable, `bugsinpy_thefuck_1` checkout completed
  for both buggy and fixed versions. The fixed checkout produced the BugsInPy
  patched-file form on the buggy HEAD, so verify both git status and modified
  files instead of expecting the fixed commit as HEAD.
- The first no-install target pytest run failed during collection because
  `psutil` was missing. An ignored isolated Python 3.11 venv with only target
  test dependencies (`pytest`, `psutil`, `six`, `decorator`, `colorama`,
  `pyte`, `win-unicode-console`) established the oracle: buggy = one failed
  parameterized case plus one pass; fixed = two passes.
- Record this as `f2p_established_p2p_not_attempted`, not as cohort expansion.
  The next gate is project-level P2P-broad, then candidate construction and
  candidate revalidation before any `p2p_broad_main` admission.

## 2026-06-16 P2P builder psutil shim and thefuck timeout

- `build_pass_to_pass_scope.py` previously injected a fallback `psutil` module
  whenever `sitecustomize` started before real `psutil` was imported. In a venv
  where `psutil` is installed, that shadowed the real package and broke
  `thefuck.shells.Process(os.getpid())` with `_Process() takes no arguments`.
- The builder shim now first attempts to import real `psutil` and only falls
  back when import fails; the fallback `Process` accepts constructor arguments
  and exposes minimal `name`, `parent`, and `children` methods.
- After this repair, `bugsinpy_thefuck_1` project-level P2P-broad execution
  started real pytest batches but exceeded the 30 minute outer budget and
  produced no manifest. Residual pytest processes were stopped. Record the
  task as `f2p_established_project_p2p_timeout`, not as admission evidence.

## 2026-06-16 rules-root P2P policy admission boundary

- A static include token is not a collection filter. For `thefuck`, the
  collection-wide `--static-include-token pip` attempt still had to collect
  shell and functional tests first, so it could not avoid collection-time
  blockers or runtime budget pressure.
- If a full project P2P attempt times out, an admissible redesign must change
  the collection root or scope type explicitly and record the policy name. For
  `bugsinpy_thefuck_1`, the successful boundary is
  `thefuck_rules_root_pip_p2p_v1`: collect `tests/rules`, then retain
  `pip`-related source segments. This supports a rules-root pip-family claim,
  not full project coverage.
- Registry, controlled-probe results, admission reports, and README/INDEX text
  must all carry the same boundary. Otherwise readiness summaries can continue
  to report a task as timed out after it has been admitted under a later policy.

## 2026-06-16 thefuck_5 legacy pytest and P2P boundary

- Later `thefuck` bugs may sit on older commits than `thefuck_1`. For
  `bugsinpy_thefuck_5`, `tests/conftest.py` still uses
  `request.node.get_marker`, so the pytest 9 env from `thefuck_1` is the wrong
  toolchain and fails before F2P.
- A task-specific ignored env with `pytest==3.10.1` reaches the target test, but
  Python 3.11 needs `py==1.11.0` and `--assert=plain` to avoid legacy
  assertion-rewrite AST failures.
- `bugsinpy_thefuck_5` F2P is clear, but P2P does not pass admission: the
  rules-root `git push` filter yields only 2 P2P tests, while the broader `git`
  filter times out around `tests/rules/test_git_merge.py::test_match`.
- Do not construct candidates for `thefuck_5` unless a new bounded P2P policy
  produces at least 3 stable pass-to-pass tests.

## 2026-06-16 visible-test runner and wrapper oracles

- `run_evp7_visible_tests.py` originally inferred the test Python executable
  from the first retained-oracle command. That works when the oracle command is
  `python -m pytest` or `python -m unittest`, but fails when the retained oracle
  is a wrapper script that internally launches an isolated venv Python.
- The failure mode is misleading: pytest can return `exit_code=4` for every
  visible test even though the candidate workdirs and tests are valid. Re-run a
  sample command with the P2P manifest's batch Python before classifying it as
  evidence failure.
- The runner now uses direct oracle Python only for `-m` test commands. For
  wrapper oracles, it reads the tracked P2P manifest batch command and resolves
  relative Python paths against the repo root.

## 2026-06-17 EVP-7 four-anchor boundary

- Do not treat the current E0/E2/E4/E6 artifacts as a partially filled
  adjacent-difference E0-E6 ladder. The current E0 already exposes
  `patch_diff` and `touched_files`, while E2 mainly adds patch-apply evidence
  and keeps syntax/import/static analysis as `not_run`.
- Because of that implementation, adding E1/E3/E5 to the current EVP-7 would
  duplicate or overlap evidence variables rather than create clean one-variable
  increments. It would also require rerunning packets, prompts, baselines, LLM
  reviews, statistics, and figures.
- The current paper route should frame EVP-7 as a four-anchor evidence
  visibility pilot. A complete adjacent-difference ladder belongs in a future
  EVP-8 or EVP-7-v2 protocol with redesigned levels from E0 onward.

## 2026-06-18 non-conflicting paper reinforcement

- If workload is questioned, first make the existing pipeline visible:
  admission, candidates, F2P/P2P, evidence packets, LLM review, tool-only
  baselines, qualitative cases, claim traceability, and artifact audit. This is
  a writing/figure/table task, not a new evidence-level experiment.
- A second-model replication can strengthen robustness only when the user
  confirms provider, model, budget, scope, and stop conditions. Keep it to
  E0/E4/E6 key anchors unless a new plan explicitly says otherwise.
- Do not let either reinforcement path reopen E1/E3/E5, full-ladder claims,
  blind bug expansion, or a claim that LLMs beat deterministic tool-only
  baselines.

## 2026-06-18 EVP-7 workload ledger in paper generators

- Workload presentation should be generated from tracked summaries, not typed
  independently into only one draft. The current ledger pulls task, candidate,
  packet, tool-only baseline, G5 quality, and qualitative-case counts through
  `scripts/write_paper_tables.py`.
- Keep the two scopes explicit: structural/no-API pipeline work is 21 tasks,
  98 candidates, and 392 E0/E2/E4/E6 packets; the paper-facing real DeepSeek G5
  run remains 20 tasks, 94 candidates, and 376 records.
- Avoid wording that reverses the hidden-evaluator design. The pipeline is a
  hidden-evaluator verification setup with labels joined after review, not a
  hidden-evaluator-free setup.

## 2026-06-18 Cookiecutter 4 P2P blocked by runtime command boundary

- Do not promote `bugsinpy_cookiecutter_4` from a partial project-level P2P
  builder output. The observed P2P attempt was dominated by environment and
  command failures: missing `yaml`, `ruamel`, and `past`; unavailable
  `cookiecutter` console command invocation; and external template tests that
  failed or timed out.
- Track only the decision-level blocker policy in
  `data/p2p_scopes/bugsinpy_cookiecutter_4_p2p_blocked_environment_policy.json`.
  The full builder outputs contain local paths and verbose failure tails, so
  they are local diagnostics, not admission artifacts.
- This task is not a `p2p_broad_main` admission and should not trigger
  candidate construction unless a future plan explicitly changes the dependency
  and command boundary first.

## 2026-06-18 submission handoff audit boundary

- Adding a handoff file is weaker than auditing the handoff contract. The
  anonymous artifact audit can prove the file is packaged, but it cannot prove
  the file still says no-API default continuation, no second-model API without
  confirmation, no cohort expansion, and no E1/E3/E5 insertion.
- Use `scripts/audit_submission_handoff.py` for that semantic boundary. It
  checks the tracked handoff text, the next-decision packet pointer, the
  four-anchor counts, and forbidden-action wording without calling APIs or
  touching experiment data.
- Keep this audit inside `scripts/run_local_quality_gate.py` so routine
  end-of-turn checks catch handoff drift before artifact packaging.

## 2026-06-18 paper readiness submission package boundary

- `audit_paper_readiness.py` should keep result-claim readiness and submission
  package readiness separate. A bounded EVP-7 claim can be ready while a
  packaging or handoff boundary is broken; the audit now reports
  `submission_package_ready` for the conjunction.
- Reuse `audit_submission_handoff.py` instead of duplicating handoff phrases in
  paper readiness. This keeps the no-API default and forbidden-action contract
  in one semantic audit while still surfacing it in paper readiness output.

## 2026-06-18 Windows JSON audit read encoding

- Inline Python checks on Windows must pass `encoding="utf-8"` when reading
  tracked or generated JSON/Markdown outputs with `Path.read_text()`. The
  default Windows locale can be GBK, which can raise `UnicodeDecodeError` on
  UTF-8 audit files even when the audit itself passed.
- Treat this as a local inspection-command issue, not an experiment or artifact
  failure. Re-run the read with an explicit UTF-8 encoding before diagnosing
  downstream readiness fields.

## 2026-06-18 advisor packet artifact gate

- If a document becomes part of the submission-facing explanation contract, do
  not rely only on broad `docs/` packaging. Add it to
  `audit_anonymous_artifact.py` required files and to the generated
  `ARTIFACT_README.md` snippets so future package drift fails loudly.
- The advisor workload response is not experimental evidence, but it is a
  paper-package explanation artifact. It should travel with the anonymous
  package because it records the bounded workload and overclaim boundary.
- Keep the same boundary visible in `audit_paper_readiness.py` required docs.
  Otherwise the artifact gate can fail while paper readiness still appears
  ready, which splits the submission-package contract.

## 2026-06-18 non-conflicting reinforcement wording

- Workload presentation and second-model key-anchor replication can coexist in
  the plan only as separate branches: workload presentation is the default
  no-API route, while second-model replication requires explicit provider,
  model, budget, scope, and stop-condition confirmation before any API call.
- If the user says "second-model key-level replication", normalize that phrase
  to the current `E0`/`E4`/`E6` key anchors. Do not interpret it as permission
  to insert `E1`/`E3`/`E5` or to build a full adjacent-difference ladder.
- Do not describe the current pipeline as `hidden-evaluator-free`. The current
  paper relies on hidden-evaluator separation: model-visible evidence is
  reviewed before labels are joined for aggregate metrics and audits.
- Do not keep README Git sync text that claims local `main` matches
  `origin/main` when the branch is known to be ahead after push failures. Use
  `git status --short --branch` as the sync source of truth.

## 2026-06-18 submission freeze-candidate boundary

- A freeze-candidate packet is not a final freeze decision. It should record the
  current paper/artifact candidate state and the remaining user confirmations,
  especially venue/format constraints and whether the current PDF should be
  frozen.
- If the freeze-candidate packet becomes part of the submission-facing package,
  add it to both artifact audit required files/snippets and paper readiness
  required docs. Otherwise the handoff can mention it while the package gates do
  not enforce it.
- Do not include artifact ZIP hashes in tracked freeze-candidate docs if the
  doc is packaged into the artifact; that creates a circular package state.

## 2026-06-18 freeze-candidate semantic audit gate

- Required-file checks are not enough for submission freeze candidates. Add a
  semantic audit that requires the packet to remain a candidate, not a final
  freeze decision, and to keep API, expansion, and E1/E3/E5 actions forbidden.
- Keep the artifact file count in the freeze-candidate packet aligned with the
  packaged tracked file count. After adding the packet and its semantic audit
  script, the current anonymous artifact manifest count is 303.
- Paper readiness should require both the handoff semantic audit and the
  freeze-candidate semantic audit before reporting `submission_package_ready`.

## 2026-06-18 submission checklist latest verification drift

- A submission checklist can be structurally correct while its latest local
  verification paragraph still describes an older gate. After rebuilding the
  paper package, refresh that paragraph in the same pass as current plan notes.
- The checklist should say which maintenance action was last verified, not just
  that some prior artifact gate passed. For the current package, the relevant
  latest state is the no-API paper package rebuild with a 7-page PDF, 303-file
  anonymous artifact, and handoff/freeze-candidate semantic gates.
- Keep INDEX wording generic enough to survive future rebuilds: describe the
  checklist as carrying the latest local PDF/artifact verification status,
  rather than tying it to an older workload-ledger-only refresh.

## 2026-06-18 submission handoff latest-run drift

- The handoff semantic audit protects no-API, no-expansion, and no-E1/E3/E5
  boundaries, but it does not prove that the latest-run command list includes
  every maintenance action just performed.
- After a paper package rebuild, update the handoff's latest maintenance run
  alongside the checklist. In this package, that means listing figure
  regeneration, 7-page PDF compilation, 303-file artifact rebuild, and the
  refreshed submission checklist status.
- Keep this as documentation maintenance only: do not reinterpret it as a final
  freeze decision, second-model authorization, or new experimental result.

## 2026-06-18 submission rebuild-command drift

- If paper figures are part of the required submission package, the submission
  checklist rebuild command block must include `scripts/generate_paper_figures.py`
  alongside table and IEEE draft generation.
- The anonymous artifact `Current Audit` paragraph should follow the latest
  package-maintenance boundary. If it remains tied to an older gate, future
  handoffs can underestimate which paper/artifact checks were actually rerun.
- This is still documentation synchronization: updating rebuild commands and
  current-audit wording does not authorize API calls, dataset expansion, or a
  final freeze.

## 2026-06-18 short project-state drift

- The short project state page is the first handoff entry for future sessions,
  so it must not preserve an old dirty-worktree description after later commits
  make the branch clean.
- Keep exact ahead counts tied to the inspection time and still tell readers to
  use `git status --short --branch` as source of truth; committing the refresh
  itself can increase the local ahead count.
- If repeated local documentation commits make the exact ahead count stale,
  prefer non-cyclic wording such as "local main is clean and ahead; use
  `git status --short --branch` for the exact count" instead of committing a new
  ahead number every turn.
- The short project-state page should also keep recent semantic anchor commits
  current enough for handoff. Prefer anchors such as package rebuild, local
  completion audit, and GitHub sync retry over an old exact ahead snapshot.
- Treat GitHub push failures as sync-state context only. They do not authorize
  API calls, cohort expansion, E1/E3/E5 insertion, or a final freeze.
- A `git push origin main` failure with `Recv failure: Connection was reset`
  is still a network-level GitHub sync failure. Record it, keep `git status
  --short --branch` as the source of truth, and continue local no-API work when
  the user has authorized skipping repeated sync failures.

## 2026-06-18 Markdown and IEEE RQ drift

- The Markdown paper draft and the IEEE submission draft can drift because the
  IEEE draft is generated from `scripts/write_ieee_latex_draft.py`, while the
  Markdown draft is manually maintained.
- When the paper-facing RQs move from first-pilot LLM-only/prompt-only framing
  to EVP-7 evidence-visibility framing, update both drafts in the same pass.
- The paper outline is a third paper-facing RQ source. Keep it aligned with the
  Markdown and IEEE drafts, and use `E0/E2/E4/E6` rather than `E0 through E6`
  when describing the current four-anchor pilot.
- This is wording synchronization only: do not use RQ alignment to add new
  scale, second-model, or LLM-over-tool-only claims.

## 2026-06-20 EVP-8 journal-scale planning boundary

- Upgrading to a journal version changes the research design. Do not treat it
  as a continuation of EVP-7 by inserting `E1`/`E3`/`E5` into existing
  artifacts. Create a new EVP-8 protocol, freeze the full E0-E6 evidence ladder
  from E0 onward, and rerun packets/prompts/baselines/models/statistics under
  that version.
- The first execution batch may use DeepSeek V4 Pro and Qwen3.7 Max, but only
  after no-API protocol freeze, leakage checks, prompt-boundary dry-run,
  cost-observability readiness, and smoke gates pass. Once either model has
  started, do not change evidence levels, prompt schema, candidate set, or
  evaluator joins without bumping the protocol version and rerunning affected
  models.
- Later Kimi K2.6, Devstral 2, and Gemini 2.5 Flash runs are allowed only as
  completion of the same frozen EVP-8 input set. If they are routed through
  OpenRouter, pin exact model IDs and record actual returned model/provider per
  review record; do not rely on unrecorded fallback or automatic substitution.
- Do not justify model selection primarily by leaderboard rank. Public
  leaderboards are at most a secondary sanity check. The defensible selection
  criteria are fixed model IDs, context-window fit, structured-output support,
  comparable practical cost/capability, provider-family diversity, and
  software-engineering task suitability.
- DeepSeek and Qwen can be excluded from external OpenRouter cost planning when
  the user treats them as already available. The later three-model OpenRouter
  planning estimate is only a budget estimate, not a billing statement.

## 2026-06-20 EVP-8 protocol-spec audit boundary

- A written EVP-8 plan is not enough for later API execution. Create a tracked
  machine-readable protocol spec first, then audit adjacent evidence deltas,
  visible/hidden field boundaries, model batches, routing policy, cost
  observability, and stop gates before building packets or prompts.
- The first EVP-8 spec audit may pass while API readiness remains blocked. That
  is the intended state when the candidate set, prompt text, packet dry-run,
  schema dry-run, prompt-boundary audit, cost-observability dry-run, and
  deterministic baseline have not all been generated.
- Keep the audit strict on synonymous hidden fields. If the script requires
  both `hidden_oracle_results` and `hidden_oracle_result`, update the protocol
  spec to cover both rather than weakening the leakage boundary.

## 2026-06-20 EVP-8 candidate-set freeze boundary

- If historical model summaries no longer preserve every candidate id for an
  older run, do not reconstruct a candidate set by guesswork. Freeze the
  current tracked structural candidate manifest for Phase 0 smoke/protocol
  validation, and explicitly state that it is not the journal-scale full-run
  cohort.
- Candidate-set manifests can contain anonymous candidate ids, task/project
  identity, touched files, and patch hashes. Keep evaluator labels, hidden
  oracle paths, expected outcomes, and per-candidate validation summaries out
  of model-visible candidate records.
- Aggregate label counts are acceptable for candidate-balance audit only when
  the summary clearly marks them as evaluator-side aggregate counts that never
  enter prompts.

## 2026-06-20 EVP-8 prompt-template freeze boundary

- Freezing a prompt template is not the same as freezing rendered per-packet
  prompts. Track the template and hashes, but keep rendered prompt text out of
  tracked artifacts until a packet manifest policy explicitly allows it.
- Prompt audits should check both the template and a minimal visible sample
  render. If the template uses exact evaluator-only field names, treat that as
  a prompt-boundary problem rather than weakening the scanner.
- A prompt-change log is required when adding or changing experiment prompts.
  Record whether the new prompt replaces an older one or is a new protocol
  prompt, and note the schema differences.

## 2026-06-20 EVP-8 packet/schema dry-run boundary

- A packet dry-run summary can validate level counts, cumulative field groups,
  and leakage boundaries without generating full evidence packets. Name it as a
  skeleton dry-run and keep `full_evidence_packets_generated=false`.
- Schema dry-runs can validate parser/output shape with deterministic placeholder
  decisions, but they are not LLM verifier results and should not be used for
  evidence-level claims.
- If full packet JSONL records are later generated, treat that as a separate
  Phase 0 artifact with its own leakage audit and protocol-version boundary.

## 2026-06-20 long-plan patch anchor boundary

- `docs/plans/current_plan_zh.md` is long and contains repeated verification
  command blocks. When appending a new section, do not anchor on generic lines
  such as local quality gate results; they can insert the new section into an
  older historical block.
- Use a unique nearby heading or the latest section-specific verification block
  as the patch anchor, then confirm with `rg -n` and a tail read that the new
  section appears exactly once at the intended end of the file.

## 2026-06-20 EVP-8 cost/baseline dry-run boundary

- Cost-observability dry-run is an accounting-surface check, not a cost result.
  It can validate planned call counts and required usage/cost fields without
  reading credentials, local configs, provider catalogues, or bills.
- Deterministic-baseline dry-run can validate output schema using planned
  model-visible evidence slots only. If actual evidence values or evaluator
  labels are needed, that is a later artifact, not this Phase 0 summary.
- `phase0_api_readiness=ready_for_api_preflight` means all tracked no-API Phase
  0 blockers are cleared. It does not authorize API execution; local preflight
  and an explicit execution command are still required before model calls.

## 2026-06-20 EVP-8 DeepSeek/Qwen local preflight boundary

- Local preflight may read the ignored local config and `.env` only to validate
  path, model, output, and credential-presence boundaries. It must never print
  API key values or store local config contents in tracked artifacts.
- A passed local preflight means the smoke run can be executed after an explicit
  user command. It is not itself execution authorization and must not be used to
  start model calls automatically.
- Keep the ignored local config under `configs/*.local.json` and raw outputs
  under `outputs/`; tracked preflight summaries should contain only model ids,
  env var names, planned call counts, check names, and boolean/state results.

## 2026-06-20 EVP-8 guarded smoke runner boundary

- The smoke runner check-only path may construct visible smoke packets and
  prompt hashes in memory, but it must not store rendered prompt text, call
  model APIs, or write raw responses.
- The EVP-8 smoke subset should be deterministic and project-frequency
  stratified, not simply the first five candidate records or the first five
  distinct projects. The manifest begins with repeated PySnooper candidates and
  youtube-dl is the dominant project, so frequency-stratified selection keeps
  the smoke small while still covering the highest-risk project family.
- Real smoke execution must reject tracked example configs and require an
  ignored local config plus explicit `--execute` and `--model-id`.
- Do not invent USD cost for Qwen official responses. If the provider response
  exposes tokens but no cost and no controlled pricing source is wired in,
  record token usage and mark the USD cost gate as blocked rather than treating
  an unsupported estimate as observed cost.

## 2026-06-20 EVP-8 smoke execution packet boundary

- A smoke execution packet is a handoff artifact, not execution authorization.
  It may contain exact future `--execute` commands only when it also records
  `execution_authorized_by_packet=false` and `requires_explicit_user_command=true`.
- Keep guard commands in the packet so a future executor reruns no-API checks
  immediately before any real model call instead of relying on older summaries.
- Record expected raw response paths under ignored `outputs/` and tracked
  summary paths separately. The packet should never copy rendered prompts, raw
  responses, local config contents, or API key values into tracked files.

## 2026-06-20 EVP-8 post-smoke audit boundary

- A post-smoke audit may report `waiting_for_execution` before real summaries
  exist. That is an expected pre-API state, not a failed model result.
- The audit should validate tracked raw-output-free summaries and raw-output
  path boundaries without opening raw response JSONL files under `outputs/`.
- Qwen summary presence is invalid unless the DeepSeek summary has already
  passed. This preserves the predeclared DeepSeek-first smoke sequence.
- Cover future post-smoke branches with a synthetic no-API self-test before
  real execution. The self-test should use temporary packet/summary files,
  create no raw outputs, and verify waiting, DeepSeek-only partial, both-model
  passed, Qwen-before-DeepSeek failed, and parse/cost failed states.
- The audit must also check that an executed summary keeps the same
  `protocol_id`, `candidate_set_id`, expected raw-response path, and
  no-rendered-prompt/no-raw-text tracked-summary boundary as the handoff
  packet. Otherwise a future run could silently drift inputs while still
  satisfying parse/count gates.
- Because post-smoke audit must not read raw responses, the runner's tracked
  executed summary needs aggregate request/actual model-id and provider-route
  counts. Without those raw-output-free aggregates, actual provider/model drift
  would only be visible in ignored raw outputs.
- Keep a one-command G0 guard for future API execution. It should run the same
  no-API commands listed in the handoff packet and execution plan, then write a
  raw-output-free summary. This avoids drift between documented guard steps and
  what a future executor actually runs before `--execute`.
- G0 should also fail if expected smoke raw-response or tracked-summary output
  paths already exist. This catches stale outputs before the runner reaches its
  overwrite-refusal branch at real execution time.

## 2026-06-20 EVP-8 short-state handoff drift

- When `docs/plans/current_plan_zh.md` is updated with a new execution boundary,
  refresh `docs/plans/current_project_state_zh.md` in the same turn if the
  short-state page is the expected next-session entry point. Otherwise a future
  handoff can see stale local-ahead commits or miss the latest G0 guard.
- For EVP-8 Phase 1, the short-state page should explicitly name the latest
  local semantic commit, the remote anchor, the G0 expected-output absence
  guard, and the exact manual authorization phrase for real smoke execution.
  Generic continuation still must not be treated as API authorization.

## 2026-06-20 EVP-8 per-level smoke summary contract

- If a later synthesis needs evidence-level behavior, the executed tracked
  summary must store per-level aggregates before any real API run starts.
  Otherwise the synthesis step would have to read ignored raw responses, which
  breaks the raw-output-free audit boundary.
- For EVP-8 DeepSeek/Qwen smoke, keep `review_count_by_evidence_level`,
  `parse_valid_count_by_evidence_level`, `invalid_parse_count_by_evidence_level`,
  and `decision_counts_by_evidence_level` in the tracked summary. The
  post-smoke audit should require every `E0-E6` level to have five records in
  the 5-candidate smoke subset and should self-test per-level drift without
  calling APIs or creating raw outputs.

## 2026-06-20 EVP-8 G4 synthesis scaffold boundary

- Keep post-smoke audit and G4 synthesis separate. The audit answers whether
  tracked smoke summaries are structurally valid; the synthesis turns those
  already-audited summaries into a bounded two-model smoke readout.
- The synthesis scaffold should report `waiting_for_execution` before real
  summaries exist, `partial_waiting_for_qwen` after DeepSeek-only pass, and
  `passed` only after both tracked summaries pass audit. It must not read raw
  response JSONL files.
- The allowed G4 claim is descriptive per-level decision patterns on the frozen
  5-candidate EVP-8 v0.1 smoke subset. It is not evidence for a full cohort,
  a five-model journal result, or final evidence-level effectiveness.

## 2026-06-20 EVP-8 execution-packet guard drift

- Whenever a new pre-execution guard is added to G0 or the execution plan,
  update `scripts/write_evp8_smoke_execution_packet.py` and regenerate the
  tracked packet. Otherwise a future executor following only the handoff packet
  can skip a newer guard while still appearing to follow the plan.
- The smoke execution packet should include both the one-command G0 guard and
  the expanded guard commands. Duplication is acceptable here because the
  packet is a human handoff artifact and must make missing checks visible.

## 2026-06-20 EVP-8 staged execution boundary

- Do not collapse smoke, first-batch full run, later-model completion, and
  paper writing into one authorization. Each transition needs its own gate
  because the allowed claims and failure handling differ.
- After DeepSeek/Qwen smoke passes, the next artifact should be a no-API
  first-batch full-run packet, not an immediate 686-call execution. This keeps
  cost, expected outputs, audit commands, and claim boundaries reviewable before
  any larger API spend.
- Later Kimi/Devstral/Gemini runs are completion of the same frozen EVP-8
  packet set, not a chance to repair prompts, change evidence fields, or swap
  candidate joins after seeing DeepSeek/Qwen behavior.

## 2026-06-20 EVP-8 DeepSeek smoke output-budget repair

- The first authorized EVP-8 DeepSeek smoke used `max_output_tokens = 1024`.
  DeepSeek returned 35 responses with valid model/provider/cost observability,
  but 15/35 were parse-invalid because the responses hit `finish_reason =
  length`; most invalid records spent the completion budget in
  `reasoning_content` and produced empty final content.
- This is the same failure mode seen in earlier DeepSeek smoke work. Treat it
  as an execution-budget bug, not a protocol, prompt, schema, candidate-set, or
  evaluator-join bug.
- Preserve the failed 1024-token outputs under ignored diagnostic paths, raise
  the EVP-8 DeepSeek/Qwen smoke `max_output_tokens` to 4096, rerun no-API
  preflight/check-only/execution-packet guards, and only then rerun DeepSeek.
  Qwen remains gated until the repaired DeepSeek audit passes.

## 2026-06-20 EVP-8 Qwen CNY cost-observability repair

- Qwen3.7 Max smoke can return complete token usage without a provider USD
  cost field. Treating that as an observed USD bill is wrong, but treating it
  as unknown forever blocks a valid smoke run even when an official pricing
  source exists.
- Keep two separate concepts in summaries:
  - `cost_usd` for provider-reported USD cost or controlled USD token-pricing
    estimates such as DeepSeek;
  - `cost_cny` plus `cost_currency = CNY` for Qwen official token-pricing
    estimates from Alibaba Cloud Model Studio pricing.
- Do not do exchange-rate conversion inside the smoke runner. The gate only
  needs auditable usage/cost observability, not a normalized financial report.
  If a future paper table needs all costs in USD, add a separate dated exchange
  rate source and label it as reporting conversion, not provider billing.
- When repairing a cost-only summary failure, do not rerun the model if raw
  usage already exists under ignored outputs. Recompute only the aggregate
  cost fields from existing ignored raw `response.usage`, then rerun the
  raw-output-free smoke audit and synthesis.

## 2026-06-20 EVP-8 G0 guard after smoke execution

- `check_evp8_deepseek_qwen_g0.py` is a pre-execution guard. It intentionally
  requires the expected raw-response and tracked-summary output paths to be
  absent before real API calls.
- After smoke execution succeeds, running G0 again will fail the
  expected-output absence check. That is not a smoke-result failure; it means
  the workflow has moved past G0.
- Post-smoke validation should use `audit_evp8_smoke_results.py --check` and
  `summarize_evp8_smoke_synthesis.py --check`. Do not overwrite the tracked
  pre-execution G0 summary with a post-execution failure unless documenting a
  stale-output blocker before a new run.

## 2026-06-20 EVP-8 first-batch full-run packet boundary

- Do not treat a successful two-model smoke as authorization for a 686-call
  first-batch full run. Insert a separate no-API packet gate that proves exact
  commands, expected output paths, cost fields, audit commands, and stop gates
  before any larger API spend.
- Reuse the same guarded runner for smoke and full scopes, but make the scope
  explicit with `--run-scope smoke|full`. Keep `smoke` as the default so older
  smoke commands remain stable; require `--run-scope full` in the G5 packet so
  a full run is never started accidentally by a smoke command.
- The first-batch full check-only path should prove the packet matrix before
  execution: 98 frozen candidates x 7 evidence levels = 686 prompts per model,
  686 unique prompt hashes, no stored rendered prompts, no raw outputs, and no
  API calls.
- The first-batch audit and synthesis scaffolds should report
  `waiting_for_execution` before full summaries exist. That is the expected
  G5 state, not a failure.

## 2026-06-20 Post-push state-entry drift

- After a push succeeds on retry, update the short state entry immediately.
  Otherwise the next agent may treat an already-synced commit as an unresolved
  GitHub blocker and waste a turn retrying sync.
- Use `git status --short --branch` and `git log -1 --oneline` as the
  authority. Plan text that says "ahead" or "un pushed" is stale once those
  commands show `main...origin/main`.
- This kind of drift is a documentation-state repair only. It must not be
  interpreted as authorization to move from a no-API packet gate into a large
  API run.

## 2026-06-20 EVP-8 long API run checkpointing

- A 686-call full run must checkpoint raw responses incrementally under
  ignored `outputs/`. Holding all raw records in memory and writing only at
  the end creates an unobservable cost risk when an outer command timeout or
  host interruption occurs.
- Keep the default overwrite policy strict: a normal execute command must
  refuse existing raw or summary outputs. Use `--resume` only when there is an
  interrupted raw JSONL prefix and no tracked summary.
- Resume must validate that existing raw records are exactly a prefix of the
  planned packet order, with matching candidate id, evidence level, configured
  model, and provider route. Do not silently skip unordered or mismatched raw
  records.
- If a long run becomes unobservable and has not written any raw prefix, stop
  the orphan process before restarting after the checkpointing repair. Do not
  run the next model while the first model's full audit is absent.

## 2026-06-20 EVP-8 tracked summaries under ignored data paths

- The repository ignores broad `data/*` paths, so a newly generated
  raw-output-free summary under `data/reviews/` may be invisible in normal
  `git status`.
- Before force-adding such a summary, run the corresponding audit and confirm
  the tracked summary does not contain rendered prompt text or raw response
  text. Raw JSONL responses and runner logs must remain only under ignored
  `outputs/`.
- For EVP-8 first-batch full runs, `data/reviews/*_full_summary.json` is the
  commit-worthy audit surface; `outputs/evp8_phase1_deepseek_qwen_full/**`
  remains local evidence and must not be staged.

## 2026-06-21 EVP-8 G5 packet after partial full execution

- `write_evp8_first_batch_full_run_packet.py --check` is a pre-full-run handoff
  gate. It intentionally checks that expected DeepSeek and Qwen full outputs do
  not yet exist.
- After DeepSeek full execution has passed and Qwen is still waiting, rerunning
  the G5 packet check will mark the packet `blocked` because the DeepSeek raw
  and summary outputs now exist. That is a gate-order misuse, not a model or
  protocol failure.
- For the pre-Qwen gate, use strict preflight, full-scope runner check-only,
  first-batch full-result audit, and first-batch synthesis. Do not regenerate
  the G5 packet snapshot after partial full execution.

## 2026-06-21 EVP-8 G7 later-model packet boundary

- A later-model completion packet can be ready while actual execution remains
  blocked. For G7, `write_evp8_later_model_completion_packet.py --check`
  validates protocol/audit/synthesis/catalog/expected-output absence, but it
  also records that the later-model runner and preflight are still required.
- Treat OpenRouter catalog audit as a public model-availability check only. It
  does not prove API credentials, provider routing, returned model IDs, cost
  fields, parse validity, or raw-output boundaries for real calls.
- Do not run Kimi/Devstral/Gemini from command templates until the real runner
  exists, the ignored local config and `OPENROUTER_API_KEY` pass preflight, and
  each model has explicit execution authorization.

## 2026-06-21 EVP-8 G7.1 OpenRouter runner/preflight boundary

- Keep structural readiness and strict API readiness separate. The later-model
  preflight can pass structurally with `--allow-missing-credentials`, but
  `ready_for_user_execute_command` must remain false until `OPENROUTER_API_KEY`
  is set in ignored local environment.
- The later-model runner should use exact model IDs and OpenRouter provider
  preferences with fallbacks disabled, and request metadata with
  `X-OpenRouter-Metadata: enabled`. The tracked summary must record aggregate
  actual-model/provider/cost observability, while raw responses stay only under
  ignored `outputs/`.
- Do not treat OpenRouter `usage` token counts as cost. If provider-reported
  USD cost is absent, the executed summary must block on unknown cost rather
  than silently estimating from an unrelated price sheet.

## 2026-06-21 EVP-8 G7.2 OpenRouter env-name repair

- The strict later-model preflight matches `OPENROUTER_API_KEY` case
  sensitively inside the ignored `.env` file. A lowercase
  `openrouter_api_key` line can look present in a case-insensitive PowerShell
  probe but still fail the Python preflight as missing.
- Diagnose credential blockers by printing only key-name metadata and value
  length/presence, never the secret value. If the key value is valid but the
  name case is wrong, repair only the variable name in `.env`, rerun strict
  preflight, and refresh the no-secret packet/check-only summaries.

## 2026-06-21 EVP-8 G7.3 later-model post-run scaffold

- Add result-audit scaffolds before spending later-model API budget. The
  later-model audit should pass as `waiting_for_execution` when tracked
  Kimi/Devstral/Gemini summaries are absent, then become the gate that checks
  686 records/model, per-level counts, parse validity, model/provider metadata,
  cost observability, and tracked-summary raw-output boundaries after each run.
- Five-model synthesis should read only tracked first-batch synthesis and
  later-model audit fields. While later models are missing, it must stay in a
  waiting or partial state and explicitly forbid final five-model journal
  claims.

## 2026-06-21 EVP-8 G8 later-model concurrency repair

- A serial OpenRouter later-model full run is too slow for the 686-record
  packet set. If it has written a valid raw JSONL prefix but no tracked summary,
  stop the live process, keep the ignored raw prefix, and resume with explicit
  bounded concurrency.
- Preserve ordered raw JSONL writes even when requests complete out of order.
  Resume validation depends on the raw file being an exact prefix of the frozen
  packet order.
- Keep concurrency explicit and conservative. Start at `--concurrency 4`; if
  provider rate limits, parse failures, unknown cost, or provider metadata
  gaps appear, stop and diagnose before running the next model.
- Treat non-JSON OpenRouter response bodies as retryable transport/provider
  failures. They can be transient gateway pages rather than model outputs; the
  final error may include only a sanitized short body snippet and must never
  print API keys.

## 2026-06-22 EVP-8 Kimi reasoning gate blocker

- A full Kimi K2.6 later-model run can finish transport-wise and still be an
  invalid experimental result. The runner must block if parse validity,
  provider metadata, or cost observability is incomplete after writing ignored
  raw outputs.
- In the observed Kimi run, 686 raw records were written but only 607 parsed
  against the EVP-8 JSON schema. The invalid records were spread across E0-E6
  and were not tied to a single task or evidence level.
- The dominant failure mode was OpenRouter returning nonempty
  `message.reasoning` with empty or unusable `message.content`, often with
  `finish_reason=length`. Treat this as a routing/inference-setting problem,
  not a prompt, schema, candidate-set, or evidence-packet problem.
- Do not repair this by retrying only invalid packets. Selective retry would
  mix inference settings inside one model's 686-record result. Preserve the
  blocked attempt as ignored output and run a full clean Kimi pass under one
  explicit reasoning-control policy.
- For Kimi K2.6, OpenRouter catalog reports reasoning is default-enabled but
  not mandatory. Record `reasoning.enabled=false` and
  `include_reasoning=false` in the protocol/config/preflight/summary path
  before the clean rerun, then require the normal later-model audit gate before
  starting the next model.

## 2026-06-22 EVP-8 Kimi OpenRouter 429 resume boundary

- A reasoning-disabled clean rerun can still be interrupted by provider-side
  OpenRouter 429 after writing an ordered raw prefix. Treat this as an
  execution/provider-rate-limit problem, not as a protocol, prompt, candidate,
  evidence, or parser failure.
- If the raw JSONL is an exact ordered prefix and no tracked summary exists,
  preserve the ignored prefix and resume the same model with lower explicit
  concurrency. Do not delete the prefix, do not switch to the next model, and
  do not write a partial-result claim.
- OpenRouter 429 stderr can include provider metadata and a platform user id.
  Keep those logs in ignored `outputs/`, redact them in any human-facing
  summary, and do not stage runner stderr logs.
- If 429 repeats, lower concurrency further or wait before resuming. Only
  consider runner-level retry/backoff changes after documenting the rate-limit
  diagnosis and keeping request payload, frozen packets, prompt, and schema
  unchanged.

## 2026-06-22 EVP-8 OpenRouter top-level error repair

- OpenRouter can return an HTTP 200 JSON body with a top-level `error` object
  whose `code` is 429. That is still a rate-limit/provider failure, not a
  model completion. The chat client must retry it like an HTTP 429 rather than
  returning it to the runner as a successful response.
- If such a top-level error is written into raw JSONL, the run is polluted even
  if the remaining records are valid. Keep that file as an ignored blocked
  attempt and rerun the model from a clean canonical path after the client
  repair; do not surgically edit the raw JSONL into a passed result.
- Keep retry boundaries auditable. For EVP-8 later-model runs, instantiate the
  OpenRouter client with the local config/protocol `max_retries_per_record`
  and write the retry policy into the raw-output-free summary.
- Sanitize provider error details before surfacing them. OpenRouter error
  payloads can include a platform `user_id`; redact it alongside API keys in
  human-facing errors and summaries.

## 2026-06-22 EVP-8 Kimi clean run closure

- After disabling Kimi reasoning output and repairing top-level OpenRouter
  error retry classification, rerun Kimi from an empty canonical raw path
  rather than reusing a polluted raw JSONL. The passed Kimi result had
  686/686 parse-valid records, zero unknown-cost records, zero provider/model
  metadata gaps, and provider-reported cost for every record.
- Keep the passed Kimi result as one later-model completion only. At Kimi
  closure time, the later-model audit should move to
  `partial_waiting_for_remaining_later_models`; five-model synthesis remains a
  partial scaffold until all later models pass.
- Record actual provider concentration. The passed Kimi clean run routed all
  686 records to `Chutes`; this is acceptable only because the exact requested
  model and actual returned model were recorded for every record.

## 2026-06-22 EVP-8 Devstral clean run closure

- Devstral 2 completed the same frozen EVP-8 later-model packet set without
  needing a model-specific prompt or routing repair. The passed summary had
  686/686 parse-valid records, zero unknown-cost records, zero provider/model
  metadata gaps, and provider-reported cost for every record.
- Treat Devstral's all-escalate output as an observed model behavior, not a
  final conclusion. At Devstral closure time, this supported only a partial
  later-model audit with Kimi and Devstral passed; Gemini and the final
  synthesis gate still had to be run separately.
- Keep per-provider metadata in the tracked summary. The Devstral run routed
  all 686 records to `Mistral`, and the actual model id matched
  `mistralai/devstral-2512` for every record.

## 2026-06-22 EVP-8 Gemini and five-model synthesis closure

- Run the final later model only after strict preflight, single-model
  check-only, expected-output absence, and no-runner inspection all pass. This
  avoids mixing a completion run with stale partial outputs or a hidden process.
- Gemini 2.5 Flash completed the same frozen 686-record packet set with
  686/686 parse-valid records, zero unknown-cost records, zero provider/model
  metadata gaps, and provider-reported cost for every record.
- Once Kimi, Devstral, and Gemini all pass the later-model audit, the
  five-model synthesis may become `passed`. Keep the claim narrow: it supports
  descriptive per-level decision-pattern reporting for the frozen EVP-8 v0.1
  packet set, not LLM superiority over deterministic baselines or final
  evidence-level effectiveness.
- Keep raw response files, stdout/stderr logs, `.env`, and local OpenRouter
  config ignored. Only the raw-output-free Gemini summary and regenerated
  audit/synthesis artifacts belong in Git.

## 2026-06-22 EVP-8 cost overrun and API freeze

- Separate valid-result cost from actual consumed cost. The five passed EVP-8
  summaries cost USD `2.892118056` excluding Qwen, with Qwen tracked separately
  as CNY `41.119548`; the two ignored Kimi blocked attempts added USD
  `7.27612053` but are not valid model-result records.
- The main overrun cause was not the final five-model result. It was the Kimi
  blocked-attempt sequence: first a default-reasoning full run with 79 invalid
  JSON outputs, then a reasoning-disabled run polluted by top-level OpenRouter
  429 error records before the client retry repair.
- Future expensive models need a stricter staged rule: model-specific routing
  controls and provider-error classification must be smoke-tested before a
  686-record full run, especially when a provider reports default reasoning or
  nonstandard response metadata.
- After the cost accounting summary is generated, freeze all model API calls
  for EVP-8. Continue only no-API paper tables, figures, claim-boundary audit,
  and artifact packaging until the user explicitly approves a new budgeted
  experiment.

## 2026-06-22 SQJ low-cost submission planning

- Venue choice has two different costs: paper-rewrite cost and cash cost.
  Conferences such as EASE may be semantically convenient but usually require
  author registration and travel; for a low-cash-cost route, prefer a
  subscription journal path when the school recognition target is D class or
  above.
- SQJ is a plausible low-cost first target because it is a CCF C software
  engineering journal and can support a software quality / reliability framing.
  Do not present that as guaranteed school recognition. Before submission,
  confirm the current CCF classification, the school's publication-year rule,
  the high-risk/warning-list status, and the user's author/affiliation
  eligibility with the department or research office.
- Avoid accidentally choosing Open Access. The current plan is non-OA /
  subscription publication unless the user explicitly approves APC.
- The next main manuscript format for SQJ is Springer Nature `sn-jnl` LaTeX.
  Keep the IEEEtran draft only as a content source or historical draft; do not
  continue polishing it as the target submission format.
- Keep the claim bounded for SQJ: evidence visibility affects LLM merge-gate
  decisions across five models, but the response is model-dependent and
  non-monotonic. Do not turn this into an LLM superiority or evidence-level
  effectiveness ranking claim.
- Before generating the Springer `sn-jnl` draft, write a venue-specific framing
  packet. This prevents the old IEEE submission package and artifact checklist
  from silently becoming the SQJ route, and it gives later agents one place to
  read the allowed claims, forbidden claims, result mapping, and school
  recognition gate.
- The local MiKTeX environment does not currently provide `sn-jnl.cls`.
  Generate and validate the SQJ source draft with a source-structure gate first;
  add the official Springer class/template before making PDF compilation a
  required gate.

## 2026-06-22 SQJ checklist gate

- Do not reuse the old IEEE submission checklist as the SQJ freeze packet. It
  carries four-anchor EVP-7 and IEEE PDF assumptions that are now historical for
  the SQJ route.
- Keep SQJ submission readiness as a separate source-package gate:
  `docs/artifact/sqj_submission_checklist.md` plus
  `scripts/audit_sqj_submission_checklist.py`.
- Checklist audits must allow the document to list forbidden claims. Avoid
  naive forbidden-phrase scans that fail just because the checklist says a claim
  is forbidden. The audit should catch positive overclaim assertions, not the
  forbidden-claims section itself.
- The EVP-8 cost accounting summary stores `api_freeze` under `decision` and
  money totals under `totals`. Future audits should read those nested fields
  instead of assuming top-level cost fields.

## 2026-06-22 SQJ EVP-8 figure pass

- Keep the SQJ/EVP-8 figure set separate from the historical IEEE/EVP-7 figure
  set. The current SQJ manuscript-facing figures live under `docs/figures/sqj/`
  and are generated by `scripts/generate_sqj_figures.py`.
- For the SQJ paper, the figure logic is: protocol boundary, five-model
  evidence-level decision patterns, and cost-validity boundary. This supports
  the descriptive, model-dependent, non-monotonic evidence-visibility claim
  without implying model superiority or final evidence-level ranking.
- Visual QA matters even for generated matplotlib figures. The first protocol
  figure had overlapping explanatory text, and the decision heatmap had excess
  horizontal whitespace because `imshow` used the default equal aspect ratio.
  Fix these in the generator, then regenerate figures rather than editing image
  outputs by hand.
- Do not run figure generation and figure audits in parallel. A parallel run
  can let the audit inspect a file while matplotlib is still writing it, causing
  a transient zero-byte PDF observation. Dependent gates should run in order:
  generate figures, confirm nonzero file sizes, then audit source/checklist.

## 2026-06-22 SQJ final-freeze readiness gate

- Keep SQJ source-package readiness, final-freeze readiness, and actual final
  submission freeze as separate states. A source/checklist gate can pass while
  school recognition, `sn-jnl.cls`/PDF compilation, author/funding/competing
  interest text, artifact rebuild, and final user authorization are still
  blockers.
- The SQJ final-freeze readiness packet should be auditable and passing without
  claiming final freeze. Its job is to prevent later agents from treating a
  source draft plus figures as submission authorization.
- Include the readiness audit in both paper readiness and local quality gates
  so the route remains visible from normal verification commands.

## 2026-06-26 EVP-8 accept-aware retest closure

- A `0 accept` result can be caused by evidence construction, not only model
  conservatism. The original EVP-8 v0.1 full run exposed visible test/static/
  tool slots mostly as not-run placeholders, and its E6 deterministic visible
  merge gate had no accept branch. For an accept-aware retest, derive E3-E6
  from already model-visible sanitized artifacts and keep hidden evaluator
  labels out of the packet.
- Treat prompt/schema repairs as versioned experiments. The first v0.2
  DeepSeek diagnostic run was blocked by an invented risk flag; prompt v0.2
  tightened the risk-flag enum without changing the decision policy. A later
  DeepSeek diagnostic run was blocked because several responses spent tokens in
  `reasoning_content` while `message.content` was empty. Do not parse
  reasoning content as the result.
- Provider request controls belong in protocol/config/preflight, not in an
  ad hoc command. The passed retest used JSON mode for DeepSeek and Qwen, and
  disabled DeepSeek thinking. The preflight now checks these direct-provider
  controls against the protocol before API execution.
- Smoke-test provider controls before another 686-call run. DeepSeek and Qwen
  json-mode smoke runs both passed before the full reruns. The final full
  retest had 686/686 parse-valid records for both models, with raw responses
  retained only under ignored `outputs/` and tracked summaries kept
  raw-output-free.

## 2026-06-26 EVP-8 v0.3 Qwen-first main-experiment batch

- A confirmatory batch should not reuse a post-hoc diagnostic branch name or
  claim boundary. Create a new branch and a new protocol/config/packet version
  when turning the v0.2 diagnosis into a Qwen-first main-experiment batch.
- Qwen-first means the local config should be allowed to list only
  `qwen/qwen3.7-max`; preflight should validate configured models as a subset
  of the protocol model plan and should verify only the configured API-key env
  names. Do not require unrelated DeepSeek credentials for a Qwen-only run.
- Keep Qwen-first ordering explicit in the packet. Result audit and synthesis
  should default to the old DeepSeek-before-Qwen dependency unless the packet
  declares `execution_order_policy = qwen_first_no_deepseek_dependency`.
- Long model runs can outlive the shell tool timeout. If the command times out
  but the Python process still exists and raw JSONL rows keep increasing, do
  not launch a concurrent resume. Inspect the process command line, wait for
  the original process to finish, and only use `--resume` after confirming the
  process has stopped without a tracked summary.
- Do not run dependent post-run audit and synthesis in parallel. In this run,
  synthesis briefly read the previous waiting audit before the passed audit was
  rewritten. The fix is ordering, not experiment repair: run audit first, then
  synthesis.

## 2026-06-27 EVP-8 v0.3 Qwen label-conditioned analysis

- Label-conditioned claims require a post-execution join between model
  decisions and evaluator-only labels. Aggregate accept counts alone cannot
  establish correct-patch recall or accepted precision.
- For Qwen v0.3, the accepted count rise is mostly useful but not risk-free:
  E6 accepts 20/21 correct patches and 4/77 non-correct patches. Report this
  as a safety/recall tradeoff, not as a pure monotonic improvement.
- The label analysis script must parse only the final JSON decision stored in
  `raw_response_text`; do not parse provider `reasoning_content` as the
  result.
- When writing audit-style booleans, distinguish a check result from the
  observed value. A field such as `api_call_attempted=false` should usually be
  recorded as `passed=true, detail=false`; otherwise a correct no-API boundary
  is accidentally reported as a failed check.

## 2026-06-29 EVP-8 LLM-vs-tool headroom planning

- If LLM decisions match a tool baseline, do not assume the experiment failed.
  First measure headroom: how many tool false accepts, false rejects, and
  unnecessary escalations exist for the LLM to fix.
- A cohort where the deterministic tool baseline is nearly perfect cannot
  answer whether an LLM adds value. In that case, stop before API calls and add
  harder cases instead of forcing a positive result.
- If the tool baseline has mistakes and the LLM repeats them, that is a valid
  negative result: the LLM is not correcting the visible-tool failure modes.
- E6 ablation should separate evidence from verdict. Keep visible tests,
  counts, contradictions, patch application, and diagnostics; remove
  `rule_based_visible_merge_gate_decision`, rule-based reasons, and
  `source_decision` before claiming any LLM-added-value result.

## 2026-06-29 EVP-8 E6-no-verdict execution

- Long API runs can outlive the shell timeout. During the Qwen
  `E6-no-verdict` full run, the shell timed out at 93/98 raw records while the
  Python process continued writing. The correct handling is to inspect the
  process command line and raw JSONL count, wait for the process to finish,
  and avoid launching `--resume` concurrently.
- The Phase 0 headroom audit is a real gate, not bureaucracy. Here it found
  6 tool opportunity cases: 5 false accepts and 1 false reject. That justified
  the ablation; if the count had been near zero, API execution should have
  stopped.
- Removing the verdict field has model-dependent effects. Qwen stayed close to
  `E6-full`, but DeepSeek became much more conservative: false accepts fell to
  zero while correct recall dropped sharply and escalations rose. Report this
  as risk-control behavior, not as a better automatic accept gate.
- Opportunity-set metrics reveal what aggregate metrics hide. DeepSeek
  `E6-no-verdict` did not correct tool false accepts to reject; it escalated
  all five. That is safer than accepting them, but it is triage rather than
  independent correctness verification.

## 2026-06-29 EVP-8 Phase A paper-ready analysis

- Add uncertainty before strengthening claims. Wilson intervals make clear
  that the current 6-case opportunity set has wide uncertainty; report this
  openly instead of treating point estimates as stable.
- Keep strict correction and safe handling separate. DeepSeek
  `E6-no-verdict` has zero strict false-accept corrections to reject, but it
  safely handles all five tool false accepts by escalation. Those support
  different claims.
- Utility tables should be framed as policy weights, not measured money.
  They are useful for explaining why a conservative model may be preferable
  under safety-critical assumptions even when its correct recall is lower.

## 2026-06-29 EVP-8 hard-case source inventory

- Source inventory is not candidate construction. Counting local files is only
  useful if already-promoted controlled-cohort candidates, duplicate pilot
  outputs, pending/relabeled pairs, and fresh non-promoted sources are separated.
- Reuse the passed headroom audit for old-cohort opportunity counts. Recomputing
  the same count from a different label shortcut can silently drift from 6
  opportunity cases to 5.
- Report both raw record counts and unique counts. Pending and relabeled agent
  files can double-count the same patch; paper-facing readiness should use the
  unique count.
- Do not scan or summarize raw response files in source inventory. Aggregate
  candidate and validation metadata are enough for Phase B planning.

## 2026-06-29 EVP-8-HARD candidate draft gate

- A candidate draft can pass structural gates while still being API-blocked.
  Here the draft has 35 applied candidates and no model-visible label leakage,
  but it has only 17 non-trivial hard negatives and no visible test outcomes.
- Do not convert hidden oracle validation into visible tool evidence. If the
  source only lists visible test hints, the deterministic baseline must
  escalate rather than pretend tests passed.
- Separate "opportunity including escalations" from actionable false-accept or
  false-reject headroom. An all-escalate baseline may create triage workload,
  but it does not test whether tools are fooled by plausible wrong patches.
- Pending and relabeled generated-patch files should not both enter the draft.
  Prefer relabeled files and exclude patch-apply failures and missing-validation
  records from the API-facing candidate draft.

## 2026-06-29 EVP-8-HARD visible-test execution

- Missing workdirs are a data-availability blocker, not a test result. Record
  them as `blocked` and do not convert them into pass/fail evidence.
- Environment or collection errors are model-visible tool evidence, but they do
  not create useful LLM-added-value headroom by themselves. In the hard-case
  draft, 9 visible tests errored and 26 were blocked, so the tool baseline has
  no false accepts or false rejects to correct.
- Keep visible-test outcome records free of source patch IDs, evaluator labels,
  hidden oracle outcomes, prompt text, and raw model responses. Even execution
  metadata should use neutral source names rather than labels such as
  `patch_id`.
- Do not run Qwen/DeepSeek merely because visible-test records now exist. The
  gate still requires enough non-trivial hard negatives and actionable
  false-accept/false-reject headroom.

## 2026-06-29 EVP-8-HARD HTTPie visible-test environment repair

- Old HTTPie tests need a controlled Python 3.11 compatibility runner. The
  local ignored venv must provide pytest, `pytest-httpbin`, requests, Pygments,
  mock, and docutils; the tracked wrapper only patches runtime incompatibilities
  and duplicate fixture decoration before calling pytest.
- Fixing execution coverage can change the tool-only baseline qualitatively.
  The hard-case draft moved from `error=9` to `completed=9`, producing 4 tool
  false accepts instead of zero actionable headroom.
- Sanitize before truncating stdout/stderr tails. Truncating first can leave a
  partial path fragment such as an agent workdir suffix that no longer matches
  the full replacement string and fails the forbidden-marker leakage gate.
- This is still not an API-ready cohort. The current draft has only 17
  nontrivial hard negatives and 4 actionable false-accept/false-reject cases,
  both below the planned gates of 20 and 10.

## 2026-06-29 EVP-8-HARD Luigi hard-case ingestion

- Existing validation outputs can be usable even when their filenames differ
  from the initial builder assumptions. `validation_run1.jsonl` promoted Luigi
  stability-audit candidates into the hard-case draft.
- Visible-test execution must locate the actual candidate workdir, not just the
  oracle patch command parent. Luigi used tracked local P2P workdirs under
  `data/patch_verification/workdirs/*_p2p_validation`.
- Do not reuse `already_promoted_to_evp7_controlled` sources for the hard-case
  extension. When Cookiecutter3 was found to be old-cohort material, replace it
  with a tracked extra Luigi4 partial candidate instead of keeping the easier
  source.
- Passing the hard-negative count gate is not enough. After adding Luigi and
  the extra Luigi4 partial, the hard-case draft reached 44 candidates, 20
  nontrivial hard negatives, and 18 completed visible-test records, but
  actionable tool headroom remained 7/10 after the latest visible-test rerun.
- Therefore the next repair is cohort composition, not API execution: replace
  low-information escalated/control candidates with validated hard cases that
  actually pass visible tests while failing hidden correctness, or otherwise
  create tool false rejects.

## 2026-06-29 EVP-8-HARD headroom gate repair

- Workdir lookup must prefer the validation record's `.candidate.patch`
  parent before generic task-level P2P workdirs. Otherwise a local candidate id
  collision such as `candidate_0001` can silently run visible tests against the
  wrong patched checkout and inflate false accepts.
- Rebuilding ignored HTTPie workdirs changed the baseline again: broader
  visible execution can reduce headroom when previously escalated wrong
  patches become true rejects. Treat execution coverage and actionable
  headroom as separate gates.
- HTTPie1 exposes a useful visible-test blind spot: the visible
  `test_unique_filename` test mocks `get_filename_max_length`, while the
  hidden `httpie_1_errno_fallback` oracle checks the `EINVAL` pathconf
  fallback. Distinct partials that implement visible trimming but break the
  fallback are valid hard negatives.
- Latest no-API gate now reaches 47 candidates, 23 nontrivial hard negatives,
  all 47 visible outcomes completed or timed out, and actionable tool
  headroom 11/10. This makes the cohort API-ready, but model execution still
  requires explicit user authorization.

## 2026-06-29 EVP-8-HARD API preflight boundary

- Do not reuse the old 98-candidate EVP-8 runner for EVP-8-HARD. It is bound
  to the frozen controlled candidate set and seven-level packet construction.
  The hard-case cohort needs a separate E6-only packet path over
  `evp8_hard_model_visible_seed_v0_1.jsonl`.
- The hard-case runner must default to check-only. Passing check-only means
  packets render cleanly, schema-rule outputs validate, and required key names
  are present; it does not authorize or perform model calls.
- The tracked example config is safe to commit and must refuse execution.
  Execution requires the ignored local config plus explicit user authorization,
  `--execute`, and a model id.

## 2026-06-29 EVP-8-HARD parsed-review audit boundary

- Do not wait until after API execution to design the analysis artifact. If the
  runner only writes aggregate summaries and ignored raw responses, later
  label-conditioned analysis is forced to read raw outputs.
- The execution path should write a separate parsed review JSONL containing
  only schema fields and usage/cost metadata. Keep `raw_response_text`,
  provider response objects, rendered prompts, hidden labels, and hidden oracle
  outcomes out of this tracked file.
- A result audit can be useful before model execution. It should report
  `waiting_for_model_results` and still verify the tool baseline, evaluator
  labels, and no-raw-output boundary instead of treating absent model results
  as an execution failure.
- CLI option names with hyphens become underscore attributes in `argparse`.
  Use `args.parsed_reviews_out`, not `args.parsed-reviews-out`.

## 2026-06-29 EVP-8-HARD execution packet and coverage gate

- Add the execution packet before API authorization, not after. It freezes the
  exact Qwen-first command sequence, expected outputs, post-run audit command,
  and stop gates while there is still no model-result pressure.
- A parsed review file is not complete merely because it exists. The audit
  must require exactly one parsed decision for each of the 47 hard-case
  candidate ids per executed model; missing, duplicate, or extra ids should
  block the result.
- Negative execution guards should include the new parsed-review output path.
  A tracked example config must refuse `--execute` before either summary or
  parsed-review sentinel files can be created.
- The execution packet remains a handoff artifact, not permission. Keep
  `execution_authorized_by_packet=false` and require a separate explicit user
  command before model API calls.

## 2026-06-29 EVP-8-HARD Qwen hard-case result

- A hard-case cohort can expose lack of LLM-added value. Here the tool baseline
  had 11 actionable opportunity cases, but Qwen repeated all 9 tool false
  accepts and both tool false rejects.
- Matching the tool baseline is not a failed execution; it is a negative
  experimental result. Report it as evidence that Qwen did not act as an
  independent verifier under the current E6 tool-summary construction.
- Keep "run gate passed" separate from "research claim supported." The Qwen
  run was complete and parse-valid, but it does not support a claim that LLM
  verification improves hard-case patch acceptance.
- After one model exactly mirrors the tool boundary, the next scientific
  question is model dependence: run DeepSeek only with explicit authorization
  and compare whether it escalates/corrects tool opportunity cases.
- `data/reviews` is ignored by the broad `data/*` rule. Force-add only
  raw-output-free summaries and parsed review JSONL files after scanning for
  raw fields; keep ignored raw responses and runner logs under `outputs/`.

## 2026-06-29 EVP-8-HARD post-Qwen packet boundary

- After Qwen outputs exist, the original combined Qwen/DeepSeek execution
  packet is no longer the right current gate because its expected-output
  absence checks included Qwen paths. Create a post-Qwen packet that treats
  Qwen passed results as preconditions and checks only DeepSeek output absence.
- This avoids two bad shortcuts: deleting valid Qwen results to make an old
  packet pass, or running DeepSeek without a fresh authorization-specific gate.
- The post-Qwen packet should still keep `execution_authorized_by_packet=false`;
  readiness is not permission.

## 2026-06-29 EVP-8-HARD DeepSeek hard-case result

- DeepSeek repeated the exact Qwen/tool decision boundary on all 47 hard-case
  candidates: 17 accepts, 30 rejects, zero escalations, nine repeated tool
  false accepts, and two repeated tool false rejects.
- When two different models exactly match the deterministic baseline candidate
  by candidate, treat it as a design signal, not as random model behavior. The
  current E6 evidence likely contains enough verdict-like structure to dominate
  model decisions.
- This negative result is useful only if reported honestly: the hard-case
  cohort has tool headroom, but neither model used it. Do not claim LLM-added
  verification value from these runs.
- The next repair should target evidence/verdict separation and qualitative
  false-accept analysis, not another same-prompt model run.

## 2026-06-29 EVP-8-HARD false-accept case analysis

- Post-execution false-accept analysis may join evaluator-only labels with
  parsed model decisions, but the generated artifact must say it is not
  model-visible input and must not store patch diffs or raw responses.
- The repeated false accepts form a useful failure pattern: visible tests pass,
  hidden oracles fail, the deterministic tool accepts, and both LLMs accept
  without risk flags. That is stronger evidence for merge-gate risk than an
  aggregate false-accept count alone.
- Case concentration matters. Here all repeated false accepts are `httpie`,
  with four partial fixes and five agent-plausible wrong patches. Report this
  concentration as an external-validity limit instead of implying the pattern
  is already broad across projects.
- If the next experiment removes verdict-like fields, keep the same nine cases
  as the primary opportunity set. Otherwise a new cohort could hide whether the
  evidence-boundary repair actually affects the known failure cases.

## 2026-06-29 EVP-8-HARD evidence-only ablation boundary

- Do not add ablation metadata into the model-visible packet unless it is part
  of the intended evidence. An initial implementation added `packet_variant`
  to all packets, which would have changed the frozen E6-full prompt boundary.
  Keep variant metadata in config/check summaries, not inside the prompt.
- Future evidence-only outputs must use separate summary and parsed-review
  filenames. Otherwise a correctly guarded execute path would collide with the
  existing Qwen/DeepSeek E6-full results and either fail late or tempt an
  unsafe overwrite.
- A schema dry-run that escalates all evidence-only packets is not a result.
  It only proves that the output schema and prompt boundary remain parseable
  after verdict fields are removed.
- The primary opportunity set for this ablation is the nine repeated false
  accepts, not overall accuracy. Broad escalation may be useful risk control,
  but it is not independent correctness verification.

## 2026-06-29 EVP-8-HARD evidence-only execution packet

- Add the execution packet before API authorization. It freezes expected
  output paths and stop gates while there is no result pressure.
- The evidence-only audit should have a valid waiting state. Absence of parsed
  reviews before authorization is not a failure; it is the correct pre-run
  state.
- Keep Qwen-first ordering explicit. The next authorized step is Qwen only;
  DeepSeek should wait for Qwen evidence-only audit unless the user explicitly
  authorizes both in one command.
- The primary analysis target must stay the nine repeated false accepts. A
  whole-cohort table is secondary and can hide whether the known failure mode
  was actually affected.

## 2026-06-29 EVP-8-HARD evidence-only opportunity analysis

- Add opportunity-set analysis before executing the ablation. Waiting state is
  useful because it fixes the exact post-run question before model outputs can
  influence the analysis design.
- The key quantities are repeated accept, corrected reject, escalation, and
  non-empty risk flags on the nine known false accepts. Overall accepted
  precision is secondary for this ablation.
- Treat reject and escalate separately. Reject is a strict correction; escalate
  is safe handling or triage. Combining them is useful only when explicitly
  labeled as risk handling.
- Do not parse ignored raw responses for this analysis. Parsed review schema
  fields are enough to evaluate the opportunity-set decision transitions.

## 2026-06-29 EVP-8-HARD evidence-only local config readiness

- An execution packet that names a local config should check that the ignored
  local config actually exists. Checking only the path boundary can produce a
  misleading `ready` packet that fails immediately after authorization.
- Creating a local config by copying the tracked example is acceptable as a
  no-API readiness action only when it remains ignored, contains no secrets,
  and keeps `api_execution_authorized=false`.
- After creating or refreshing a local config, rerun check-only using that
  local path so the tracked summary reflects the actual execute command path.
- Do not submit `configs/*.local.json`; verify it appears as ignored before
  committing readiness artifacts.

## 2026-06-29 Realistic agent-patch cohort planning

- Broad API authorization is not a reason to keep running same-prompt models.
  After the EVP-8-HARD evidence-only result, the bottleneck is external
  validity and opportunity-set size, not API access.
- A stronger paper needs more realistic tool-failure cases. If the visible
  tool baseline has few mistakes, LLM-added value cannot be measured no matter
  how many models are run.
- Treat the next cohort as a separate no-API construction problem first:
  inventory sources, curate candidates, run visible-tool baseline gates, and
  scan leakage before model execution.
- Hidden evaluator separation must be designed before candidate curation
  pressure appears. If a candidate can only be judged by exposing hidden oracle
  results to the model-visible packet, it is not valid evidence for a
  realistic merge-gate claim.

## 2026-06-29 Realistic agent-patch source inventory

- Do not count historical EVP-8 or EVP-8-HARD candidates as fresh realistic
  cohort material. They remain useful for motivation and failure-mode analysis,
  but reusing them as "new" data would overstate external validity.
- A large raw source count can hide zero fresh readiness. The first realistic
  inventory scanned 409 candidate records and 51 agent-like records, but the
  strict fresh-cohort count was still 0 because all usable material was already
  promoted, curated into EVP-8-HARD, legacy duplicate, or pending.
- Pending agent-like records are not enough for model execution. They can guide
  the next no-API validation/generation step, but the visible-tool headroom
  baseline cannot be built until a separate curated manifest exists.
- Inventory artifacts should store source paths and aggregate counts only.
  Keeping patch diffs and raw responses out of source-readiness reports avoids
  accidental leakage before the model-visible/evaluator-only split is designed.

## 2026-06-29 Realistic agent-patch target matrix

- When the current generation runner supports only a subset of stable tasks,
  the target matrix must distinguish "stable in registry" from "executable by
  this runner." Otherwise the plan can silently depend on unsupported tasks.
- Avoid letting `httpie` dominate the next realistic cohort again. The first
  target matrix uses six non-httpie runner-supported tasks across PySnooper,
  cookiecutter, and tqdm for 54 planned slots, and keeps httpie at zero slots.
- Raising the bounded variant budget on existing runner-supported tasks is the
  shortest no-API path to a 50-slot generation plan. Extending the runner to
  thefuck/youtube-dl is a separate task and should only be done if dry-run or
  generation diversity is inadequate.
- A target matrix is not generation authorization. It must be followed by a
  dry-run prompt-boundary check, then explicit generation API authorization,
  then validation/relabeling before any verifier experiment.

## 2026-06-29 Realistic agent generation dry-run

- A generation dry-run should prove prompt coverage and leakage boundaries, not
  candidate quality. The dry-run produced 54 prompt hashes and zero candidates,
  which is the correct no-API behavior.
- Keep dry-run outputs under ignored `outputs/` and commit only a tracked audit
  summary. The audit should verify prompt count, task coverage, absent raw
  response directory, absent candidate files, and absence of prompt/payload
  fields in the prompt manifest.
- Generation API and verifier API are separate gates. Passing generation
  dry-run only authorizes the next discussion about patch generation, not Qwen
  or DeepSeek verifier execution.

## 2026-06-29 Realistic agent generation execution packet

- An execution packet can be `ready` while still not authorizing execution.
  Keep `execution_authorized_by_packet=false` even when credentials are present
  and the output directory is absent.
- Use a separate execution output directory from the dry-run directory. This
  prevents a dry-run prompt manifest from being mistaken for real generated
  candidates and keeps raw responses contained under a single ignored path.
- Generation output is not verifier input yet. After API generation, the next
  mandatory steps are validation, relabeling, source inventory rerun, and only
  then separated cohort construction and visible-tool baseline gating.

## 2026-06-29 Realistic agent generation and validation on Windows

- Copying whole historical checkouts can fail on Windows even when the target
  patch only touches one source file. The cookiecutter checkout contains docs
  and templated test paths that triggered invalid-argument and long-path
  errors during generation.
- For generation, the shortest safe repair is to copy only `.git` plus
  `touched_files`, then use `git diff -- <touched_files>` to materialize the
  candidate patch. This preserves the patch baseline without copying unrelated
  long paths.
- Failed generation attempts can leave read-only `.git/objects/pack` files in
  ignored workdirs. Any resume-capable runner that deletes workdirs on Windows
  should chmod failed paths writable before retrying `shutil.rmtree`.
- Validation has a different boundary from generation: oracles need importable
  project packages, so do not reduce validation workdirs to touched files only.
  For this cohort, ignoring `docs` and the known cookiecutter
  `test-generate-binaries` long-path fixture preserved oracle execution while
  avoiding Windows copy failure.
- A completed generation run is still not a verifier-ready cohort. The Qwen
  run produced 54 pending candidates, but validation/relabel yielded 9 correct
  and 45 incorrect; source inventory then counted only 46 fresh usable
  candidates after duplicate/existing-cohort filtering. Keep the Phase 1 gate
  separate from the generation count.

## 2026-06-30 Realistic agent supplement generation

- Supplement runs need globally unique `patch_id` and `model_candidate_id`
  values. Reusing a new output directory is not enough, because the inventory
  duplicate guard checks `model_candidate_id` against historical hard-cohort
  IDs as well as patch IDs.
- `--variant-start-index` prevents patch-id collisions, while
  `--model-candidate-start-index` prevents model-candidate-id collisions.
  On resume, the model-candidate start must be offset by the number of already
  persisted candidates; otherwise the resumed candidate can reuse the first
  ID in the supplement run.
- API timeouts can occur after some candidates have already been persisted.
  Before retrying, inspect `prompt_manifest.jsonl`, `candidates.pending.jsonl`,
  `evidence_packets.pending.jsonl`, and raw-file counts. Resume the same run
  only after confirming the script will skip existing patch IDs and continue
  with non-colliding candidate IDs.
- A supplement generation count is not the same as fresh-source count.
  supplement_001 generated and validated 10 candidates, but only 2 counted as
  fresh because 8 model-candidate IDs duplicated historical IDs. supplement_002
  used separated IDs and added 5/5 fresh usable hard negatives, raising the
  source gate to 53.

## 2026-06-30 Realistic cohort manifest boundary

- Keep evaluator and model-visible artifacts separate from the first manifest
  step. The evaluator manifest may contain labels, oracle summaries, source
  IDs, and patch hashes; the model-visible seed must not contain those fields.
- A model-visible seed can contain `patch_text` because the verifier must see
  the candidate diff, but tracked audits and summaries should not duplicate
  patch text.
- A rule-only baseline over patch-apply status plus visible test names is not a
  real headroom baseline. If visible tests have not been executed, the honest
  deterministic decision is escalation. Do not treat `escalate=53` as evidence
  that the tool baseline is good or bad; it only says the headroom gate still
  needs visible-test execution.

## 2026-06-30 Realistic visible-test/headroom gate

- Run visible tests from model-visible packets, not from evaluator rows. The
  runner only needs `candidate_id`, `task_id`, `project`, `patch_text`, and
  declared visible tests; labels and oracle fields belong only in the later
  headroom analysis.
- Leakage checks should match evaluator-only field names, not substrings that
  collide with public IDs. `evp8_realistic_agent_candidate_0001` legitimately
  contains `agent_candidate_`, so that substring is too broad as a forbidden
  marker.
- PySnooper visible tests on Python 3.11 need the existing
  `run_pytest_legacy_py311.py` wrapper. Without it, `bugsinpy_PySnooper_1`
  fails during collection on `collections.Mapping`, which is an environment
  compatibility error rather than candidate behavior.
- The realistic visible-tool baseline is now a meaningful headroom check:
  visible tests alone accept 30 candidates, but 29 of those accepts are
  evaluator-labeled test-passing wrong patches. This cohort is therefore useful
  for false-accept reduction experiments. It is not useful for strong
  correct-recall claims because it currently has only one correct patch.

## 2026-06-30 Realistic Qwen verifier result

- Do not interpret the first realistic Qwen run as LLM added value. With the
  deterministic visible merge-gate summary present, Qwen matched the visible
  tool baseline exactly: `accept->accept=30`, `reject->reject=23`, and no
  baseline disagreements.
- The accepted precision and false-accept rate are therefore identical to the
  visible-tool baseline: accepted precision `1/30`, false accept rate among
  wrong patches `29/52`.
- This is still useful as a negative result. It shows that an E6 packet with an
  explicit rule-based decision can dominate model behavior on realistic
  agent-generated patches, just as earlier hard-cohort experiments suggested.
- The next diagnostic should be an E6-no-verdict ablation for the realistic
  cohort. Remove the visible merge-gate decision fields, keep raw visible test
  outcomes, and rerun Qwen before claiming whether LLMs add semantic judgment
  beyond tools.
- The no-verdict ablation produced the same decisions as the full packet:
  `accept=30`, `reject=23`, with 0/53 full-vs-no-verdict decision changes.
  This means Qwen is not merely copying the explicit verdict field; it is still
  following visible test pass/fail outcomes and failing to identify
  test-passing wrong semantic errors.
- The next useful work is not another same-evidence Qwen run. Either inspect
  the 29 false accepts to learn what evidence is missing, add realistic visible
  evidence that could expose those faults, or use DeepSeek only as cross-model
  replication of this negative result.

## 2026-06-30 Realistic label validity repair

- False-accept inspection exposed a label-validity bug, not a model behavior
  insight. Original hidden-oracle failures for PySnooper and cookiecutter were
  caused by running oracles under the wrong Python environment
  (`future`, `slugify`, and `past` missing), so many candidates were falsely
  labeled `test_passing_wrong`.
- Revalidating hidden oracles under the task/project venvs changed the label
  distribution from `correct=1, test_passing_wrong=52` to hidden-oracle-only
  `correct=40, test_passing_wrong=13`, with 0 dependency errors.
- Hidden-oracle-only correctness is still not a merge-gate label. If a patch
  fails declared visible fail-to-pass tests, it should not be considered
  merge-correct even when the hidden oracle passes. The final v0.3 merge label
  therefore requires patch apply, visible-test pass, and hidden-oracle pass.
- Under v0.3 merge labels, the realistic cohort is fully separated by visible
  tests: `correct=30`, `visible_test_failing_wrong=23`; visible-tool and Qwen
  both achieve accepted precision `30/30` and false accept rate `0/23`.
- This supersedes the earlier 29-false-accept interpretation. The usable
  lesson is methodological: dependency-correct oracle execution and merge-label
  definition are first-order threats. Do not build paper claims on hidden-oracle
  labels until the oracle environment and visible-test consistency have been
  audited.

## 2026-06-30 Realistic hard-negative opportunity gate

- Broad API authorization is not an experiment-design gate. After corrected
  v0.3 merge labels, the realistic 53-candidate cohort has 0
  visible-pass/hidden-fail candidates and 0 visible-tool accepted wrong
  candidates, so more verifier API calls on the same packets would mostly
  retest a dataset already separated by visible tests.
- Keep historical EVP-8-HARD opportunity cases in their proper role. They are
  useful calibration cases because the visible-tool baseline false-accepts 9
  candidates, but all 9 are `httpie`, so they cannot carry the external
  validity burden for a stronger realistic-agent paper.
- A future verifier run should require a fresh opportunity-set gate: patches
  must apply, declared visible tests must pass, hidden oracle must fail, and
  the cases should span at least 3 projects before Qwen/DeepSeek verifier API
  calls are scientifically useful.
- When a source inventory was created before label repair, treat its
  hard-negative counts as locator metadata only. Recompute visible-pass/
  hidden-fail counts after corrected oracle execution before making any
  headroom or API-readiness claim.

## 2026-06-30 Fresh hard-negative generation packet

- A new hard-negative generation attempt must not reuse old primary/supplement
  identifiers. The next packet uses run id
  `evp8_realistic_hardneg_generation_qwen_001`, variant start index 13, and
  model-candidate start index 3001 because earlier realistic generation runs
  already used variants through 12 and model-candidate ids through 2005.
- Dry-run evidence is only prompt-boundary evidence. The new hard-negative
  dry-run has 54 prompt hashes and 0 candidates; it proves task coverage and
  leakage boundaries, not candidate quality.
- Keep generation API readiness separate from verifier API readiness. The
  packet can be ready for future Qwen patch generation while verifier API
  remains blocked until the generated candidates pass apply, visible tests,
  and hidden-oracle filtering.
- The next validated hard-negative gate should be expressed as a property,
  not as a stale label name: `patch applies`, declared visible tests pass, and
  hidden oracle fails. Only that property creates tool-headroom cases for the
  paper's realistic-agent claim.

## 2026-06-30 Fresh hard-negative generation outcome

- Generated labels are not enough. The fresh Qwen run produced 45
  hidden-oracle failures, but only 26 also passed declared visible tests. The
  paper-facing hard-negative unit must be the joined property
  visible-pass/hidden-fail, not `incorrect` from relabel alone.
- Keep schema adapters explicit. Relabeled agent evidence packets expose
  visible tests as top-level `visible_tests`, while the later realistic
  verifier seed uses `visible_test_evidence.listed_tests`. The visible-test
  runner now accepts both model-visible shapes; otherwise it silently reports
  blocked records.
- Project-specific visible-test environments matter. `httpie` visible tests
  need `outputs/envs/httpie_hard_visible_py311` plus the legacy pytest wrapper;
  using the current Python misses `pytest_httpbin`, and using plain pytest in
  the venv hits duplicate fixture registration.
- Supplement generation can fail to improve the actual gate even when it
  validates cleanly. Qwen and DeepSeek httpie supplements each generated 12
  applicable candidates, but all hidden-failing httpie candidates failed the
  visible tests, so they contributed 0 visible-pass/hidden-fail cases.
- Do not run verifier API after a failed source gate. The combined fresh set
  has 78 generated candidates but only 26 visible-pass/hidden-fail candidates
  across 2 projects. The next work is source redesign or claim reduction, not
  another verifier run.
- A weak visible test is not sufficient by itself to create hard negatives.
  The Qwen `thefuck_1` supplement used a model-visible smoke/P2P test and a
  hidden F2P oracle, but all 12 generated candidates passed both. For simple
  single-file regex repairs, a clear issue summary can push the generator to
  correct-like patches even when visible evidence is weak.
- Exact search/replace edit-plan generation is fragile on more complex source
  files. The Qwen `youtube-dl_7` supplement passed dry-run boundaries but
  failed before candidate construction because the generated `find` snippet
  was not present in `youtube_dl/utils.py`. Luigi had exposed the same failure
  class earlier. Do not keep spending API on blind retries under the same edit
  interface; redesign the source strategy or generation interface first.
- When changing a generation interface, declare a new protocol before any API
  run. The full-file replacement route is now separated as
  `agent_full_file_v1`; its dry-run only proves prompt construction and
  leakage boundaries. Do not merge future full-file results silently with the
  exact edit-plan supplement series.
- A generation interface can be technically successful while still failing the
  source gate. `agent_full_file_v1` produced 4 applicable `youtube-dl_7`
  patches and all passed both visible test and hidden oracle. This is not a
  verifier opportunity set; it is evidence that the current third-project task
  is too easy or too clearly specified for Qwen under this prompt.
- When a source gate fails after multiple protocol-compliant attempts, freeze
  the claim boundary instead of continuing to spend API. The fresh realistic
  branch now supports a two-project supplement/source-acquisition negative
  result, not a three-project verifier-ready main experiment.

## 2026-06-30 SQJ package claim-boundary audit

- Keep manuscript generators aligned with paper-facing framing. After the
  fresh realistic branch was downgraded, the SQJ framing was correct but the
  generated LaTeX draft still omitted the gate-readiness/source-acquisition
  negative-result subsection. Treat generator output as the authoritative
  manuscript surface; otherwise regenerated drafts can silently drop claim
  boundaries.
- Required-snippet checks are exact string checks. The first SQJ draft
  regeneration failed because `two-project source-acquisition negative result`
  was split by a line break in the generated LaTeX source. When adding a
  boundary phrase to a snippet gate, keep that exact phrase contiguous in the
  generated artifact or make the audit explicitly token-aware.
- Checklist/readiness audits should verify both allowed and forbidden fresh
  realistic claims. It is not enough for `sqj_submission_framing.md` to forbid
  three-project verifier-ready claims; the source-package checklist and
  final-freeze readiness audit must also require the two-project negative
  result boundary and forbid practical-autonomous-verifier wording.

## 2026-06-30 SQJ PDF compile gate preflight

- Do not conflate audit pass with PDF compile pass. The SQJ PDF compile gate can
  pass as an audit while reporting `gate_status=blocked_missing_sn_jnl_cls` and
  `pdf_compile_passed=false`; that means the blocker is explicit and
  machine-readable, not that final-freeze compilation succeeded.
- Keep `sn-jnl.cls` acquisition outside automated repair unless explicitly
  approved. The current local MiKTeX environment has `pdflatex`, but
  `kpsewhich sn-jnl.cls` fails and reports that MiKTeX updates have not been
  checked. The safe project action is to record the blocker and require the
  official Springer Nature class before PDF compilation.
- The same gate should become the real compile gate once the class is available:
  run two `pdflatex` passes into ignored `outputs/sqj_pdf_compile/` and require
  a non-empty PDF before any final-freeze claim.

## 2026-06-30 SQJ official template cache and PDF compile

- Keep third-party template assets out of Git. The official Springer Nature
  journal article template can be downloaded and extracted into ignored
  `outputs/sqj_springer_template/`; the tracked artifact should record only the
  source URLs, ZIP sha256, file counts, and `sn-jnl.cls` cache path.
- PDF compilation needs both the template path and the manuscript directory in
  `TEXINPUTS`. The first local-cache compile path found `sn-jnl.cls` but would
  not be robust for `\input{generated_tables.tex}` unless `docs/paper/` was
  also included.
- Treat LaTeX command failures as source-generation issues, not template
  issues, after the class is found. The local compile exposed three draft
  problems: obsolete `\jyear{2026}` for the current template, missing
  `amsmath` for `\allowdisplaybreaks`, and bare paths with underscores in prose.
  Fix these in `write_sqj_latex_draft.py` so regeneration preserves the fix.
- A successful PDF compile is not a final-freeze signal. The compile gate should
  run `pdflatex -> bibtex -> pdflatex -> pdflatex`, require a non-empty PDF and
  BBL, and still keep final freeze blocked by school recognition, human
  metadata, artifact rebuild, and final submission authorization.
- Do not run compile-dependent SQJ gates in parallel. `audit_sqj_pdf_compile_gate`,
  `audit_sqj_pdf_layout_review`, `audit_sqj_figure_layout_gate`, and
  `audit_sqj_final_freeze_readiness` can write or inspect the same ignored
  `outputs/sqj_pdf_compile/` directory, so running them concurrently can create
  transient false failures.
- Fix layout defects at the generator source. The post-compile layout review
  exposed clipped wide tables and unresolved citations; the durable fix was to
  resize wide generated `table*` tabulars in `write_paper_tables.py` and make
  the compile gate run BibTeX, not to edit generated `.tex` output by hand.

## 2026-06-30 GitHub sync retry after local SQJ compile commit

- Treat GitHub 443 connection failures as external sync blockers, not as local
  validation failures. The SQJ local compile commit can be valid and the working
  tree can be clean while `git fetch origin evp8-v03-qwen-main-exp` still fails
  with `Could not connect to server`.
- Preserve the local commit hash and branch divergence state in the plan before
  retrying later. For this branch, the next sync must still use the established
  tree-sync flow because local and remote histories intentionally diverge.
- Do not create workaround remotes, force-push, or rewrite local history to
  "fix" a transient GitHub connection failure. The safe recovery is to retry
  fetch, verify the expected parent tree, create a commit-tree commit on the
  remote parent, push that commit to the branch, and verify remote tree equality.

## 2026-06-30 SQJ human-input gate preflight

- Do not fill submission metadata from inference. Author names, affiliations,
  email, funding, acknowledgements, competing-interest confirmation, and author
  contributions are human inputs. The safe automated action is to detect
  placeholders and keep final freeze blocked.
- Placeholder detection in LaTeX sources must normalize whitespace. The first
  human-input gate missed the competing-interest confirmation sentence because
  LaTeX wrapped `confirmed` and `before submission` across a newline. Normalize
  whitespace before matching blocker snippets.
- A passing human-input gate audit does not mean human inputs are complete. In
  the current SQJ draft the audit passes while reporting
  `gate_status=blocked_missing_human_inputs`; that means the blocker is
  explicit and machine-readable.

## 2026-06-30 SQJ artifact candidate gate

- Separate candidate artifact safety from final artifact rebuild. The SQJ
  artifact gate can pass with `gate_status=candidate_artifact_dry_run_ready`
  while still reporting `dry_run_only=true` and
  `final_artifact_rebuild_complete=false`.
- Reuse the canonical anonymous-artifact file enumeration and validation
  instead of maintaining a second allow/exclude implementation. This keeps the
  SQJ gate aligned with the package builder and prevents drift in credential,
  raw-output, local-config, and benchmark-checkout exclusions.
- Required-file gates should include the gate script itself. Otherwise the
  candidate package may look complete while lacking the script needed to
  reproduce the audit.
- Passing this gate does not authorize API calls, PDF compilation, submission,
  or final freeze. It only proves that the current tracked SQJ source package
  can be safely enumerated and scanned as a dry-run artifact candidate.

## 2026-06-30 SQJ school-recognition gate

- Do not infer journal recognition from venue name, indexing, or prior
  experience. School/department recognition is an external human/policy input,
  so the automated gate should report
  `blocked_missing_school_recognition` until a confirmed decision is supplied.
- Forbidden wording checks must distinguish pending questions from completed
  claims. The first gate version treated `Confirm whether SQJ is recognized...`
  as if recognition had been confirmed. Match only explicit completed-state
  phrases such as `recognition is confirmed` or `recognition is complete`.
- Keep the gate no-web and no-API unless the task is explicitly to verify a
  current public school policy. The current gate checks local claim boundaries,
  not the truth of an external recognition list.
- Include new audit gates in the artifact candidate required-file set. A source
  package is not reproducible if it depends on a gate script that the candidate
  artifact omits.

## 2026-06-30 SQJ final-authorization gate

- Keep final submission authorization separate from API authorization. The user
  has broadly authorized API usage in the thread, but that does not authorize
  SQJ final submission, final artifact rebuild, or access to a submission
  system.
- A final-authorization gate should fail only on explicit completion wording,
  such as `authorized to submit`, `ready-to-submit`, or `final freeze complete`.
  It should pass while reporting `blocked_missing_final_authorization` when the
  documents clearly say the package is not final.
- Do not use local quality success as a proxy for submit readiness. Local gates
  can prove the blocker is explicit and machine-readable, not that the external
  human decision has been made.
- Add authorization gates to the artifact candidate required-file set so the
  future package can reproduce why it was not final-submission-ready.

## 2026-06-30 SQJ figure-layout gate

- Split source-level figure readiness from post-compile layout review. The gate
  can pass while reporting `blocked_pending_pdf_compile`; that means the three
  SQJ figures, captions, labels, and `includegraphics` references are present,
  not that visual placement in a compiled PDF has been approved.
- Keep PDF layout judgment downstream of the PDF compile gate. When
  `sn-jnl.cls` is missing, the only defensible automated check is source and
  asset completeness; final layout review requires a compiled manuscript.
- Add new SQJ blocker gates to both local quality and artifact required-file
  lists. Otherwise the package can silently lose the script that explains why
  final freeze is still blocked.

## 2026-06-30 SQJ human-decision packet

- Keep human-decision collection separate from human-input placeholder
  detection. The human-input gate detects unresolved text in the manuscript;
  the human-decision packet lists every external decision needed before final
  freeze.
- Do not let broad API authorization satisfy submission authorization, school
  recognition, author metadata, PDF compilation, artifact release, or final
  freeze. These are distinct human/external decisions.
- Forbidden-state audits should match explicit positive completion states, not
  negated instructions such as "Do not claim...". Broad substring matching can
  make the packet fail precisely because it documents the forbidden claim.

## 2026-06-30 SQJ claim traceability

- SQJ needs its own claim traceability gate because the current submission route
  is EVP-8/five-model centered, while the older claim-boundary audit is EVP-7
  centered. Reusing the old audit alone leaves the SQJ manuscript claims only
  indirectly checked.
- Forbidden-claim checks must distinguish positive assertions from forbidden
  lists and negated explanatory text. Strip the `Forbidden Claims` section from
  framing before positive-assertion matching and treat markers such as
  `does not`, `must not`, and `instead of` as negation context.
- Keep the traceability output raw-output-free: report source paths, aggregate
  checks, keyword coverage, and claim ids, but never raw model responses,
  prompts, or patch text.

## 2026-06-30 SQJ citation consistency

- A source-structure check that only looks for `\bibliography{sqj_references}`
  is too weak for submission maintenance. Add a separate citation/BibTeX key
  audit so missing citation keys are caught before PDF compilation.
- Keep citation consistency local and mechanical. Do not use this gate to add
  or validate external references; it only checks that current `\cite{...}`
  keys and current BibTeX entries agree.
- Treat repeated citations as informational, not a failure. Missing cite keys,
  duplicate BibTeX keys, and uncited BibTeX entries are failures for the current
  compact SQJ bibliography.

## 2026-06-30 EVP-8-HARD tool-contestation API execution

- Long Qwen runs can outlive the shell tool timeout. In the tool-contestation
  run, the shell command timed out at 15 minutes while the Python child process
  continued writing `outputs/evp8_hard_tool_contestation_full/.../raw_responses.jsonl`.
  Do not immediately rerun in this state; first inspect the child process and
  raw-response line count.
- If raw responses are still increasing and no tracked summary exists, treat
  the state as in-progress, not failed. Wait for the process to finish, then
  run the raw-output-free audit on the generated parsed reviews and summary.
- Never duplicate API calls against a partially written raw prefix unless a
  resume/recovery path has been implemented and verified. The safe sequence is
  process check, raw count check, tracked summary/review existence check, then
  audit.
- Tool-contestation outputs must be interpreted separately from correctness
  verification. `would_challenge_visible_test_only_accept=true` and
  `insufficient_for_accept` are risk-triage signals; only `reject` would be a
  strict correction of a known false accept.

## 2026-06-30 PowerShell tree-sync refspec safety

- Quote Git revision expressions with braces in PowerShell, for example
  `git rev-parse "HEAD^{tree}"`. Unquoted `HEAD^{tree}` can be mangled by the
  shell and produce an invalid tree value.
- Never push a variable refspec unless the variable has been checked as
  non-empty. An empty left side in `$newCommit:refs/heads/branch` can become a
  delete refspec. Use `"$($newCommit):refs/heads/branch"` and explicitly throw
  if `$newCommit` is empty.
- If a tree-sync push accidentally deletes a remote branch, recover by using
  the already fetched remote parent commit and the local `HEAD` tree:
  create `git commit-tree "<local-tree>" -p "<remote-parent>" -m "<message>"`,
  push `"$($newCommit):refs/heads/<branch>"`, fetch, and verify
  `origin/<branch>^{tree}` equals `HEAD^{tree}`.

## 2026-06-30 EVP-8-HARD policy utility interpretation

- Keep policy-utility analysis separate from correctness-verification claims.
  A system can win a utility scenario by escalating risky cases when false
  accepts are expensive; that does not mean it semantically identified the
  patch as wrong.
- Report the cost assumptions beside every utility rank. Without the false
  accept penalty and escalation cost, a policy table is easy to misread as an
  unconditional model ranking.
- For tool-contestation, the key distinction is strict correction versus safe
  handling. `reject` is a strict correction of a known tool false accept;
  `escalate` is risk triage. The current EVP-8-HARD result improves safe
  handling but has 0/9 strict rejects on the opportunity set.
- Preserve the automation-recall tradeoff in summaries. Tool-contestation
  lowers unsafe accepts, but it also drives correct recall to zero in this
  cohort, so it cannot be presented as a high-recall automatic merge gate.

## 2026-06-30 EVP-8-HARD claim traceability scaffold

- Build paper-facing claims from tracked aggregate audits, not from memory or
  raw outputs. The claim audit should map every allowed claim to named files
  and should list forbidden claims explicitly enough that later writing cannot
  drift into them.
- Keep `strict correction` and `safe handling` as separate table columns.
  Escalating a known tool false accept is useful risk triage, but it is not
  evidence that the model semantically rejected the wrong patch.
- Raw-boundary checks should not fail just because an aggregate audit records
  `prompt_text_read=false`, `raw_response_text_allowed=false`, or
  `patch_diff_saved=false`. Treat false boundary booleans as safety evidence;
  fail only on actual raw-like content or true raw-read/save indicators.
- The final results table scaffold is a writing scaffold, not a new
  experiment. It should preserve source variants (`tool-only`, `with-verdict`,
  `evidence-only`, `tool-contestation`) so readers can see which result
  supports which claim.

## 2026-07-03 Final manuscript claim map and body rewrite

- Do not let a completed writing step remain the documented "unique next
  action." After the claim map and threats-to-validity boundary are generated,
  the current next action must move to the actual remaining blocker: figure
  generation after an explicit Python/R backend choice.
- Generate manuscript prose from a claim map, not directly from scattered
  experiment summaries. The claim map should bind every supported result to its
  evidence source and list forbidden claims before the body draft is written.
- Keep "strict correction" and "safe handling" separated in the manuscript.
  Escalation can support risk triage and human-review routing, but it must not
  be described as semantic rejection of a wrong patch.
- Figure generation has a backend gate. If no backend is explicitly selected,
  do not write plotting scripts, generate mock figures, or default to Python/R;
  record the figure plan and ask for the backend instead.

## 2026-07-03 CCF-C figure generation

- When the user asks which backend is better, that is a valid backend-selection
  request. Use the backend-selection rules, state the reason, then proceed with
  the chosen backend as exclusive for drawing, previews, exports, and QA.
- For this repository, Python is the lower-risk figure backend because the
  source data are tracked aggregate JSON files and the existing manuscript
  figure pipeline is matplotlib-based. R would add a second plotting stack
  without improving the required workflow schematic, heatmap/bar grid, or
  claim-boundary map.
- Visual QA must inspect the generated PNGs, not just file existence. The first
  CCF-C figure pass had text collisions in Fig. 1--3; fixing layout before
  committing prevented a technically passing but manuscript-weak figure set.
- Keep generated manuscript status synchronized with figure status. After
  Fig. 1--3 are generated, `planned_requires_backend` must become
  `generated_python` in the claim map and manuscript figure section.

## 2026-07-03 CCF-C inline figure placement

- A generated figure set is not the same as figures being placed in the paper.
  The manuscript should carry each figure at the paragraph where it supports the
  argument: protocol figure in Methods/Protocol, decision-pattern figure in
  Results, and claim-boundary figure before Threats to Validity.
- Update the manuscript generator, not only the rendered Markdown. Otherwise a
  later regeneration will silently move figures back to a terminal asset list.
- Add a placement audit when figure position matters. File-existence checks
  prove assets exist; they do not prove figures are in the right section, in the
  right order, or paired with captions.

## 2026-07-03 Critique-driven CCF-C manuscript rewrite

- When a reviewer says the draft reads like an audit report, do not merely add
  stronger wording. Rebuild the paper around contribution, RQs, main evidence,
  baselines, and boundaries. The audit artifacts should support the argument,
  not be the argument.
- Promote repaired evidence only when the tracked metrics justify it. In this
  revision, Qwen v0.3 label-conditioned metrics became main evidence because
  they contain accept, correct accept, false accept, accepted precision, correct
  recall, false accept rate, and escalation rate over the frozen 98-candidate
  matrix.
- Do not launder missing baselines into prose. If always-escalate, random,
  majority, or full E0/no-tool baselines are not tracked completed artifacts,
  list them as submission risks or future work, not as results.
- Keep failed source-acquisition gates out of the main verifier claim. The
  realistic hard-negative branch is useful boundary evidence, but a failed
  three-project gate cannot support a main verifier-ready experiment.

## 2026-07-03 Excluding invalid experiment settings from main results

- If an earlier setting is diagnosed as an experimental artifact, executing it
  at larger scale does not make it paper evidence. It should not appear as an
  RQ, main figure, explanatory subsection, or positive/negative
  empirical finding.
- For this manuscript, the main chain starts from the repaired evidence:
  Qwen v0.3 label-conditioned metrics, E6 rule-only/no-verdict ablation, and
  tool-contestation.
- Figures must follow the same exclusion rule as prose. A figure can
  reintroduce an invalid experiment even if the text avoids it; Fig. 2
  therefore had to be redrawn from Qwen v0.3 and E6 ablation metrics.
- Future writing passes should fail review if they describe invalid earlier
  settings as paper-facing experimental evidence.

## 2026-07-03 PaperSpine-style paper planning boundary

- A PaperSpine-style pass is useful for contribution/result/reviewer alignment,
  but it must not be treated as evidence generation. It should reorganize
  tracked aggregate results, not invent claims or backfill missing baselines.
- For the current CCF-C route, the strongest stable spine is a bounded
  evidence-visibility and risk-behavior measurement paper. Pushing it toward
  autonomous correctness verification would create unsupported claims.
- The next high-leverage work is citation support, deterministic baseline
  feasibility, and uncertainty presentation. Expanding API experiments should
  be a later, explicit decision because it can reopen execution and validity
  risks.

## 2026-07-04 Citation and baseline support boundary

- A citation support bank should map claims to sources before editing the
  manuscript. Dropping references directly into prose can hide whether the
  cited work supports motivation, method framing, or an actual result claim.
- For this CCF-C route, the citation workflow can borrow claim segmentation
  from `nature-citation`, but the source pool must be CS/SE/ML primary sources.
  Nature/CNS-only filtering is not appropriate for a software-engineering CCF-C
  manuscript.
- A baseline that is calculable from label totals is not the same as a completed
  verifier experiment. Always-escalate, always-reject, and always-accept are
  valid reference policies; only the tracked rule-only visible-tool result is
  the current completed deterministic baseline.
- Majority vote needs candidate-level aligned model decisions and hidden-label
  joins under a raw-output-free audit. Aggregate summaries alone are not enough
  to report it as a completed baseline.
- Check fields must distinguish "the bad event did not happen" from "the check
  failed." In `ccfc_baseline_feasibility_audit_v0_1`, no API/raw/prompt reads
  are recorded as `passed=true` with `detail=false`.

## 2026-07-04 Manuscript v0.3 integration audit

- Paper-support artifacts are not enough until the manuscript generator consumes
  them. For this project, citation support, baseline feasibility, and Phase A
  uncertainty had to be wired into `scripts/write_final_manuscript_claim_map.py`
  so regenerated Markdown preserves them.
- A reference policy must be phrased as a policy boundary, not as an experiment
  result. The manuscript now says always-escalate, always-reject, and
  always-accept orient the decision space but are not successful verifier
  results.
- Reviewer-style audits should allow negated overclaim phrases. The manuscript
  correctly says it does not support LLM superiority over deterministic
  baselines; the audit therefore checks for the negated context rather than
  banning the phrase mechanically.
- Wide Wilson intervals are a writing constraint, not a formatting footnote.
  They must sit near the E6 baseline/no-verdict table so readers see that
  point-estimate differences are bounded and should not be overclaimed.

## 2026-07-04 Five-step CCF-C completion boundary

- A random-policy baseline can be useful without becoming a new experiment. In
  this project, `uniform_random_three_way_expected` is only an expected
  reference over aggregate label totals; do not describe it as a stochastic run,
  a completed verifier, or evidence that the model beats randomness.
- Tool-contestation opportunity counts are small. Reporting Wilson intervals
  for safe handling, strict correction, and repeated accept makes the
  uncertainty visible and prevents escalation-heavy behavior from being
  over-read as semantic correction.
- Structure compression should happen in the generator, not just the rendered
  Markdown. Otherwise Methods/Results/Discussion/Threats headings can drift on
  the next regeneration.
- The five-step paper pass is complete only under the current bounded route:
  citation support, aggregate-feasible baselines, uncertainty presentation,
  structure compression, and reviewer-aware audit. It still does not complete
  majority-vote or a separate E0/no-tool deterministic verifier.

## 2026-07-04 Majority and E0/no-tool feasibility boundary

- Majority-vote is a data-shape problem before it is an experiment problem. It
  does not require a new model call if candidate-level aligned decisions already
  exist, but aggregate per-level summaries are insufficient.
- Do not compute majority-vote by reading raw responses under a no-raw-output
  audit boundary. First create a tracked raw-output-free candidate decision
  export/audit, then compute majority from that artifact.
- Qwen E0 is an observed model condition, not a deterministic no-tool baseline.
  It can show what the model did with minimal evidence, but it must not be used
  as a non-LLM verifier result.
- Always-escalate/always-reject/always-accept can serve as no-evidence
  reference policies from label totals. They remain policy references, not
  implemented deterministic verifiers.

## 2026-07-05 APSEC manuscript rewrite boundary

- A target-venue rewrite should be generated from the same claim map as the
  stable manuscript. Hand-editing only the rendered Markdown risks drifting
  from the audited evidence chain.
- APSEC-style framing changes emphasis, not evidence scope. The rewrite can
  foreground novelty, technical soundness, and software-engineering relevance,
  but it must not turn evidence-conditioned risk behavior into autonomous
  patch-correctness verification.
- Audit rules should catch forbidden overclaims, but the manuscript should also
  avoid phrases that create mechanical or reviewer ambiguity. Rephrase negated
  superiority claims as positive boundary statements when possible.
- A Markdown rewrite is not a submission artifact. The next gate is anonymous
  IEEEtran/BibTeX/page-budget conversion, including figure/table layout and
  double-blind wording checks.

## 2026-07-05 APSEC reviewer-risk repair

- When a reviewer identifies a single-model main-result risk, text can only
  narrow the claim; it cannot create multi-model evidence. The paper should say
  controlled LLM patch-verifier study until repaired E0-E6 results exist for
  additional models.
- Dataset composition belongs in Methods, not only in internal audits. For this
  cohort, the defensible paper-facing numbers are 98 candidates, 6 projects,
  21 tasks, 21 correct patches, and 77 non-correct patches with candidate-type
  counts from the frozen candidate-set summary.
- Strong deterministic baselines should be treated as results, not hidden
  embarrassments. If rule-only visible-tool nearly matches Qwen E6, the paper's
  claim must shift from LLM superiority to risk-policy behavior under evidence
  removal and contestation.
- False-accept analysis must match available evidence granularity. Aggregate
  tracked summaries support saying Qwen E6 accepted three partial fixes and one
  regression patch; per-case project/rationale claims require a separate
  raw-output-free case-analysis artifact.

## 2026-07-05 False-accept case-analysis feasibility boundary

- Aggregate false-accept anatomy is not a case table. If tracked summaries do
  not carry candidate IDs for the false accepts, do not infer the cases from
  candidate-type counts.
- A raw-output-free case table needs a sanitized decision export with candidate
  ID, project, task, candidate type, hidden label, E6 decision, no-verdict
  decision, tool-contestation linkage, and a categorical rationale summary.
- The sanitized export must exclude raw response text, rendered prompts, patch
  diffs, full rationale text, and credentials. If producing it requires reading
  an ignored raw decision source, that needs an explicit plan and boundary.

## 2026-07-05 DeepSeek repaired v0.3 run boundary

- API authorization must still pass through local readiness gates. The
  DeepSeek repaired v0.3 run only proceeded after strict preflight, smoke
  check-only, and full check-only passed; this prevented the authorized API
  call from bypassing the project execution loop.
- A second repaired model changes the paper claim boundary, but not all the way
  to broad generality. Qwen + DeepSeek supports a two-model controlled
  evidence-visibility result; a third repaired model is still needed before
  writing a stronger APSEC main table.
- When multiple experiment packages share labels such as `E6-full`, the
  manuscript must identify which package each row comes from. In this run,
  repaired v0.3 DeepSeek E6 and the earlier E6 verdict-field ablation package
  have different numbers; the fix was to state that the ablation table is
  separate evidence, not the repaired v0.3 main E0-E6 table.
- DeepSeek's E4-E5 conservatism is a result, not an error to smooth over.
  More visible evidence changed policy behavior, but did not produce monotonic
  correctness or a correctness oracle. The manuscript should preserve that
  nonmonotonic pattern.
- Raw-output-free tracked summaries are enough for aggregate label-conditioned
  metrics and run packets, but not enough for concrete false-accept case
  analysis unless candidate-level decision exports are explicitly produced.

## 2026-07-06 Gemini repaired v0.3 and APSEC packaging boundary

- OpenRouter models may return valid JSON inside fences or other wrapper text
  even when the runner successfully parses the final decision. Downstream
  analyzers should use the shared JSON-object extractor rather than
  `json.loads(raw_response_text)` directly; otherwise a parse-valid API run can
  fail during label-conditioned postprocessing.
- Adding a third repaired model changes the APSEC claim from two-model to
  three-model evidence, but still not to broad generality. The manuscript must
  say Qwen/DeepSeek/Gemini support a controlled descriptive result and preserve
  the deterministic rule-only baseline boundary.
- A sanitized false-accept case analysis may read ignored raw decisions as an
  input only when the tracked output excludes raw response text, rendered
  prompts, patch diffs, full rationale text, and credentials. The output should
  retain only candidate identifiers, hidden-label categories, decisions, and
  compressed rationale categories.
- IEEEtran/BibTeX conversion needs a separate audit from the manuscript audit.
  Passing the APSEC manuscript audit means the research argument is internally
  consistent; it does not mean the LaTeX source compiles, fits the venue page
  limit after floats, or satisfies double-blind visual requirements.
- Citation conversion must preserve BibTeX keys exactly inside `\cite{...}`.
  Escaping underscores is correct in prose and tables, but wrong inside
  citation keys.
- BibTeX support records are not submission-grade entries by default. If a
  reference string contains characters such as `$`, the generator must emit
  structured BibTeX fields and escape special characters; otherwise the PDF may
  compile with distorted reference text.
- A successful IEEEtran compile can still leave submission-blocking layout
  debt. The current APSEC draft compiles to 6 pages with resolved references,
  but table-width overfull/underfull warnings remain and should be treated as
  a formatting task before submission.

## 2026-07-06 Coverage-contestation prompt boundary

- A prompt-sensitivity condition should not replace the main prompt after main
  results are known. Keep `evp8_visible_evidence_merge_gate_v0_2` as the main
  protocol prompt and report coverage-contestation as a separate ablation.
- Coverage-contestation prompts intentionally measure a different behavior:
  whether the model challenges visible-test-only accept premises and routes
  high-risk visible-pass cases to strict reject or safe escalation. Their
  results cannot be merged into the main E0-E6 table without a condition label.
- Removing `rule_based_visible_merge_gate_decision` and
  `rule_based_visible_merge_gate_reasons` is necessary for this ablation;
  otherwise the prompt still tests verdict following rather than coverage
  challenge.
- Hard-negative stress tests need a real opportunity set. The current
  realistic branch remains below gate at 26/30 cases and 2/3 projects, so
  verifier APIs must stay blocked until source-acquisition and validation add
  at least one project and four visible-pass/hidden-fail cases.

## 2026-07-06 Coverage-contestation execution repairs

- If a new runner reuses `run_evp8_deepseek_qwen_smoke.fetch_raw_record`
  without setting `max_output_tokens`, the default is 1024. DeepSeek V4 Pro can
  spend that entire budget on reasoning tokens or truncate the JSON body,
  producing many `invalid_json:No JSON object found` records even though the
  API calls succeeded. For EVP-8 verifier runs, set `max_output_tokens=4096`
  in the config before execution and treat parse invalids as an execution-chain
  blocker, not as a model result.
- When a provider run fails after writing a valid raw JSONL prefix, do not
  restart from scratch. Check the raw line count, confirm no process is still
  writing the file, then resume only if the existing packet IDs are a prefix of
  the planned packet order.
- OpenRouter-compatible calls can fail with `http.client.RemoteDisconnected`.
  This is a retryable transport failure like a transient URL error, not an
  experimental result. The shared client now retries it; if it appears again,
  inspect whether the raw prefix is complete before resuming.
- Tracked coverage-contestation reviews should remain normalized and raw-free.
  Keep raw responses in ignored `outputs/**`; do not copy full model rationale,
  rendered prompts, patch diffs, or credentials into `data/reviews/**` or
  paper-facing Markdown.
- The completed current-98 coverage-contestation result is conservative triage:
  zero repeated false accepts, but severe correct-recall loss. Future writing
  must not present it as improved autonomous semantic verification.

## 2026-07-06 Mainline B hard-negative source repair

- A third project is only useful for visible-pass/hidden-fail acquisition if the
  visible test is weaker than the hidden oracle. Luigi was rejected because
  `luigi_3` uses the same tuple round-trip behavior in visible and hidden
  checks, and `luigi_4` has a visible test that is stronger than the hidden
  oracle.
- Environment failures must be separated from candidate behavior. Luigi needed
  the existing legacy pytest wrapper for Python 3.11 compatibility; Scrapy
  needed a legacy unittest wrapper for `inspect.ArgSpec` plus missing ignored
  env dependencies before visible tests became meaningful.
- Do not reuse the same full-file generation directory for dry-run and execute.
  `generate_agent_full_file_candidates.py` appends to `prompt_manifest.jsonl`;
  using the same directory causes prompt counts to include both dry-run and
  execute manifests. Use a separate dry-run directory or a clean execute
  directory before result audit.
- If model-generated candidates all pass the hidden oracle, that is a result,
  not a failure to hide. Qwen generated correct Scrapy_1 full-file fixes, so
  those candidates were not counted as hard negatives.
- Curated no-API partial variants can repair a stress-test opportunity set, but
  they must be labeled as curated stress-source evidence. They cannot be
  described as a pure agent-generated realistic cohort.
- Keep patch-bearing stress-cohort packets in ignored `outputs/**`. Tracked
  files should carry only hashes, source IDs, labels, visible outcomes, and
  aggregate baseline decisions. This preserves the raw-free/prompt-free
  boundary while still giving future verifier runners a concrete local input.
- A useful stress cohort should make the visible-tool baseline fail clearly.
  The separated 31-case cohort does this: visible-tool accepts every case, and
  every case is hidden-failing, so verifier prompts have direct false-accept
  reduction headroom.

## 2026-07-06 Hard-negative stress verifier preflight

- Do not assume an `E6-no-verdict` condition exists just because it was useful
  on the current-98 EVP-8 packets. The separated hard-negative stress packets
  do not contain `rule_based_visible_merge_gate_decision`,
  `rule_based_visible_merge_gate_reasons`, or `source_decision`; removing those
  fields changes nothing. Treating that as an independent ablation would be an
  experimental-design error.
- The stress verifier matrix should run only the conditions that actually
  change the prompt/packet contract. Current ready conditions are
  `current_merge_gate` and `coverage_contestation`; across 31 cases and three
  models, this is 186 calls, not the originally sketched 279 calls.
- Patch-bearing verifier packets can still be model-visible, but preflight and
  tracked summaries must store only packet/prompt hashes, counts, condition
  gates, and metadata. The call manifest belongs under ignored `outputs/**`.
- Remove nonessential hidden/provenance metadata such as `has_hidden_oracle`,
  `label_leakage_guard`, and `stress_source_boundary` before rendering verifier
  prompts. These fields are not hidden outcomes, but they are unnecessary for a
  clean visible-evidence decision contract.

## 2026-07-06 Hard-negative stress matrix execution

- OpenRouter/Gemini can return an empty response with zero token usage for a
  single record even when the surrounding run is healthy. Treat this as a
  provider/execution-chain issue, not a model decision. The runner now supports
  `--resume --retry-invalid`, backs up the ignored raw JSONL, and retries only
  records that fail parsing.
- On an all-negative hard-negative cohort, do not report correct recall. The
  valid metrics are repeated false accept, strict reject, safe escalation, and
  safe handling.
- The stress result is strong for prompt-sensitivity and triage: coverage
  contestation reduced repeated false accepts from 62/93 to 12/93. It is not
  strict semantic correction evidence because strict reject stayed at 0 for
  both conditions.
- Model behavior remains heterogeneous. Qwen and Gemini accepted all stress
  cases under the current prompt; DeepSeek escalated all. Under coverage
  contestation, DeepSeek and Gemini escalated all cases, while Qwen still
  accepted 12/31.

## 2026-07-06 APSEC stress-matrix manuscript integration

- When a previously blocked branch later receives a bounded stress-test repair,
  update the manuscript generator, not only the Markdown output. Otherwise the
  next regeneration will restore stale gate-failed prose.
- The correct APSEC framing is now: the hard-negative branch supplies a
  31-case stress-test supplement across three projects, but it is not a pure
  agent-generated realistic cohort because the scrapy cases are curated no-API
  stress-source partial variants.
- The stress-matrix result should sit after current-98 coverage-contestation:
  current-98 shows prompt sensitivity with severe recall cost, while the
  all-negative stress matrix shows false-accept reduction without defining
  correct recall.
- Keep the key boundary sentence near the result table: repeated false accepts
  fell from 62/93 to 12/93, but strict rejects stayed at 0, so this is
  conservative triage evidence, not strict correction.

## 2026-07-07 APSEC camera-facing PDF cleanup

- A compiled PDF is not automatically submission-facing just because LaTeX
  compiles. Mechanical captions such as `Converted APSEC draft table X`,
  duplicated `Figure N` captions, internal package notes, raw floating-point
  values, and too many converted tables should be audit blockers.
- Main-body table count must be curated at the generator level. If the Markdown
  generator emits every analysis table, the IEEEtran converter will create an
  appendix-like PDF even when each individual table compiles.
- Keep detailed per-level, CI, and per-model stress breakdowns in analysis
  artifacts unless they carry the main paper's evidence chain. For the APSEC
  draft, the camera-facing main PDF uses six tables: evidence levels, dataset
  composition, selected three-model main results, E6 ablation, hard-negative
  stress aggregate, and false-accept case groups.
- Treat strong deterministic baselines as a result boundary, not as a threat to
  hide. The APSEC text should say that EVP-8 exposes tool-following,
  abstention, and prompt-induced conservatism rather than claiming large LLM
  gains over rule-only visible-tool summaries.
- Single-case regression failures can be severe signals, but not statistical
  conclusions. The manuscript should explicitly say that the one regression
  negative accepted by all three models is a severe failure signal, not a broad
  regression-safety failure rate.
- After changing table labels, recompile and inspect the log. The
  `Coverage-contestation` condition label caused the only overfull hbox; shorter
  paper labels removed it without changing the underlying experimental result.

## 2026-07-07 APSEC references and method-detail pass

- Reference expansion should be connected to claims, not appended as uncited
  bibliography. The APSEC rewrite now cites APR/test-overfitting, LLM code
  review, LLM code generation/repair, software-agent benchmarks,
  LLM-as-judge reliability, and reject-option/selective-classification work in
  the paragraphs that need those supports.
- Do not use DOI fields unless they are verified. A SANER DOI initially pointed
  to a different paper; the safer repair was to remove that DOI and keep the
  entry as an arXiv-backed conference reference.
- Temporary support-record strings should not become submission references.
  APSEC now uses structured BibTeX entries and the page-budget audit blocks
  sparse references and all-`@misc` temporary bibliographies.
- A method-detail paragraph can be added without reading raw outputs if it is
  built from tracked configs, run packets, and summaries. The paper can report
  frozen prompt/template identity, temperature, output-token cap, parse-valid
  counts, cost telemetry boundaries, and raw-free artifact policy from tracked
  files only.
- Cost telemetry needs careful wording. Qwen's tracked provider cost field is
  0.0, so it must not be described as a billing statement; DeepSeek/Gemini
  tracked summaries can be reported as runner/provider-token cost summaries.
- If a figure is readable only as an internal claim map, remove it from the
  APSEC main paper rather than forcing reviewers to decode it. Figure 3 remains
  available as a CCF-C/claim-boundary artifact, while APSEC keeps Figure 1 and a
  larger double-column Figure 2.

## 2026-07-08 APSEC figure and citation consistency pass

- Figure text must match the paper-facing result scope. A protocol schematic
  that says `5 model verifiers` conflicts with a three-model APSEC main result;
  use generic verifier wording unless the figure is specifically about the
  earlier descriptive five-model synthesis.
- Result figures should carry the main evidence chain. APSEC Fig. 2 now uses
  Qwen, DeepSeek, and Gemini E0/E3/E6 metrics instead of the older Qwen-only
  ladder plus ablation panel.
- Benchmark citations are not optional. If the dataset paragraph names
  BugsInPy tasks, the manuscript and BibTeX must cite BugsInPy directly.
- Cost telemetry is an artifact boundary, not a paper-facing result here. Do
  not report provider-specific dollar values in the main paper unless cost is a
  designed comparison.
- If the main table only shows E0/E3/E6, keep E4/E5 behavior as an artifact
  boundary rather than a prominent main-text claim.

## 2026-07-19 Direction selection must remain revocable until novelty and identifiability pass

- A document labeled `DIRECTION_SELECTED / NOVELTY_PENDING` can become a stale
  execution hazard when later literature and label audits reject the direction.
  Preserve the old design as provenance, but add an explicit superseding status
  at every authority entry instead of silently rewriting its historical logic.
- GPU availability and an easy LoRA path do not establish a scientific problem.
  Training is allowed only after a no-model audit shows that deterministic
  canonicalization, lookup, decision trees, information gain, or ordinary hidden
  tests do not already solve the task.
- A benchmark's public row count is not evidence of an admissible train/test
  split. Provenance IDs, source-run grouping, derived-sample closure, target-field
  isolation, and a mechanically checkable label contract are separate Gates.
- Closely related 2026 work can invalidate a broad candidate while leaving a
  narrower intersection open. Record both the prohibited broad claim and the
  exact conditional remainder; do not turn a narrow remainder into a locked
  topic before the author resolves discipline and training requirements.
- Correcting project status is not the same as writing a locked implementation
  plan. During Act 1, `current_plan_zh.md` may record a withdrawal and conditional
  candidates, while `PLAN.md` must wait until the one-question-at-a-time decision
  tree is resolved with the author.

## 2026-07-19 Candidate labels must follow the decision answer, not hidden state uniqueness

- In fault diagnosis, multiple physical hypotheses can imply the same actionable
  diagnosis. Commit labels must therefore use the remaining answer-equivalence
  set, not require a singleton physical-fault set.
- A failed or timed-out diagnostic tool is zero information. It must preserve the
  candidate set; treating failure as negative evidence creates artificial
  identifiability and rewards brittle agents.
- For generated simulators, re-generating code from two transformed prompts mixes
  semantic fidelity with sampling variance. The smaller mechanically testable
  question is one generated parameterized program evaluated over hidden values
  already declared in the prompt.
- Relational tests are useful only if they beat ordinary hidden tests at equal
  execution budget. Otherwise an ns-3-specific metamorphic labeler adds domain
  terminology without adding a scientific problem.

## 2026-07-19 Possible worlds are an oracle; visible transformations make a metamorphic test

- A formal concept is not novel merely because it is moved into an LLM-agent
  setting. Lifting a safety monitor over every trace compatible with partial
  observations, or computing safe actions over a belief support, must first be
  reduced against runtime verification, supervisory control, shielding, and
  distributed-recovery literature.
- Two hidden applied/unapplied worlds with exactly the same agent-visible input
  define a set-valued world-uniform oracle. They are not by themselves a useful
  metamorphic pair: a deterministic system already returns the same output for
  the same input.
- A valid metamorphic relation changes a visible contract, observation, goal, or
  semantics-preserving representation and specifies a nontrivial output-set
  equality or inclusion. Its testing value should be measured by additional
  mutant kills over single-instance oracles, random pairs, and ordinary trace
  checks.
- For a testing-method paper, oracle soundness mainly establishes implementation
  correctness. The more defensible contribution is a mechanically generated MR
  suite with mutation adequacy or completeness for a declared defect class.
- An official accepted-paper list can reveal a serious collision before the full
  papers are public. Record this as a temporary novelty blocker: do not infer
  content from titles, but do not declare the boundary complete until the texts
  can be audited. A direct full-text collision is a switch-topic condition, not a
  reason to preserve a weakened claim.
- Auxiliary manifest probes must read the committed schema instead of guessing
  field names. Here the canonical fields are top-level `status`,
  `selection_inputs`, and `records`, with authorization nested under
  `authorization.data_use_authorized`; the deterministic isolation audit remains
  the authoritative Gate.
- A remote named `origin` is not necessarily the branch's authorized destination.
  Before every research-plan push, inspect the branch's configured remote,
  pushRemote, repository visibility, and exact target ref. If a new commit is sent
  to the wrong remote, first preserve the intended private synchronization, then
  restore only the mistaken ref with an expected-hash lease; verify both remotes
  independently. Rewriting the ref does not prove immediate backend object
  erasure, so report the exposure boundary explicitly.

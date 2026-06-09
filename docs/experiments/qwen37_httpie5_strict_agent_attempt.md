# Qwen 3.7 Plus Httpie 5 Strict Agent Attempt

## Scope

Run id: `httpie_agent_patch_qwen37_httpie5_strict_001`.

This attempt used Qwen official OpenAI-compatible API with `qwen3.7-plus` to
retry `bugsinpy_httpie_5` under the strict coding-agent-style edit-plan
protocol.

The execution boundary stayed unchanged:

- no fuzzy apply;
- no manual patch repair;
- exact `find` snippets only;
- no verifier/reviewer API calls.

## Result

The dry-run passed for 2 prompts.

The first real candidate was generated successfully:

- candidate: `bugsinpy_httpie_5__agent_patch_01`;
- model: `qwen3.7-plus`;
- patch materialization: strict edit-plan exact replace, then local `git diff`;
- patch apply: passed;
- oracle ran: yes;
- oracle passed: no;
- relabeled outcome: `incorrect`.

The second real candidate did not complete. The Qwen request timed out after 3
attempts during the provider call, so no `patch_02` candidate was admitted.

## Candidate Behavior

The generated patch changed the separator regex from a preceding-character
pattern to a negative lookbehind:

```diff
-            regex = '[^\\\\]' + sep
+            regex = '(?<!\\\\)' + sep
             match = re.search(regex, string)
             if match:
-                found[match.start() + 1] = sep
+                found[match.start()] = sep
```

This patch is syntactically applicable and locally reproducible, but the
retained `httpie_5` oracle still fails. Therefore it is a useful generated
negative candidate rather than a correct repair.

## Interpretation

Compared with `qwen3-coder-plus`, `qwen3.7-plus` improved the strict generation
yield for this task: it produced an exact-match edit plan that could be
materialized into a real patch.

However, the patch did not fix the target behavior. The result supports a more
limited claim:

- stronger generator models can improve patch materialization under strict
  edit-plan rules;
- materialization success is not equivalent to semantic correctness;
- executable oracle validation remains necessary before a generated patch enters
  the verifier experiment.

## Boundary

This run produced 1 validated generated negative candidate. It does not prove
that `qwen3.7-plus` can reliably repair `httpie_5`, and the timeout on the
second candidate should be treated as provider/run instability rather than a
semantic model judgment.

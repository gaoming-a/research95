# EVP-7 Protocol Pilot

Date: 2026-06-12

## Decision

The project now follows Option A:

```text
Freeze the current BugsInPy low-friction cohort at 7 bugs / 4 projects.
Stop blind BugsInPy expansion under project-level P2P-broad.
Move immediately to an evidence-visibility protocol pilot on the frozen cohort.
```

Option B is not approved as the current main path. Option C is deferred until
the protocol interface is stable.

## Generated Artifacts

This round added a reproducible manifest builder:

```text
scripts/build_evp7_protocol_manifests.py
```

Command:

```powershell
python scripts\build_evp7_protocol_manifests.py --check
```

Tracked outputs:

```text
data/tasks/evp7_tasks.jsonl
data/tasks/evp7_manifest_summary.json
data/exclusions/blocked_bugsinpy_projects.jsonl
```

## Frozen Cohort Summary

The manifest contains exactly 7 completed project-level P2P-broad tasks:

| task | project |
| --- | --- |
| `bugsinpy_httpie_5` | `httpie` |
| `bugsinpy_cookiecutter_1` | `cookiecutter` |
| `bugsinpy_cookiecutter_2` | `cookiecutter` |
| `bugsinpy_cookiecutter_3` | `cookiecutter` |
| `bugsinpy_tqdm_9` | `tqdm` |
| `bugsinpy_PySnooper_1` | `PySnooper` |
| `bugsinpy_PySnooper_3` | `PySnooper` |

Known candidate count from the registry: 36.

Project coverage:

```text
PySnooper
cookiecutter
httpie
tqdm
```

## Blocker Registry

The blocker registry currently contains 27 excluded, pending, insufficient, or
appendix-only tasks. It preserves failed expansion attempts and prevents hidden
cherry-picking.

Blocked project families include:

```text
PySnooper
ansible
black
fastapi
httpie
luigi
matplotlib
sanic
scrapy
tornado
tqdm
youtube-dl
```

Common blocker classes:

- project-level scope timeout;
- official test root timeout;
- native dependency or compiled extension blocker;
- checkout timeout;
- insufficient P2P-broad size;
- legacy dependency blocker;
- unclear fixture or compatibility boundary.

## Current Limitation

This round freezes task-level protocol state only. It does not yet generate
candidate-level EVP-7 patch records or evidence packets.

Reason:

- candidate JSONL files for several admitted tasks are currently referenced in
  experiment reports under ignored `outputs/`;
- promoting them into `data/patches/evp7_candidates.jsonl` needs a separate
  schema-preserving step;
- E0/E2/E4/E6 evidence packets should be generated only after candidate records
  are tracked and audited.

The task manifest marks missing task metadata such as commits, issue summaries,
and touched files as `metadata_backfill_required` instead of fabricating values
from local checkouts.

## Next Step

The next executable step is:

```text
Build tracked EVP-7 candidate records from the existing validated candidate
outputs and experiment reports, then audit whether every task has enough
fields to construct E0/E2/E4/E6 packets without label leakage.
```

No new BugsInPy expansion, native build work, external benchmark migration, or
real API calls should occur before that candidate-schema step.

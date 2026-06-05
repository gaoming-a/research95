from __future__ import annotations

import json


GENERATION_V1 = """Given the following programming task, write a correct Python solution.
Return only the code.

Task:
{task_prompt}
"""

REVIEW_V1 = """Given the task specification and submitted solution, determine whether the solution correctly satisfies the task.

Return JSON only:
{{
  "bug_found": true or false,
  "bug_type": "syntax_runtime|logic|boundary|api_data_structure|performance|specification|other|none",
  "location": "line number, code fragment, or none",
  "explanation": "brief explanation",
  "suggested_fix": "minimal fix or empty string",
  "confidence": 1-5
}}

Task:
{task_prompt}

Submitted solution:
{code}
"""

SAME_SESSION_REVIEW_V1 = """Now review the Python solution you just provided for the same task.
Use the task specification and the submitted solution below as the only correctness criteria.

Return JSON only:
{{
  "bug_found": true or false,
  "bug_type": "syntax_runtime|logic|boundary|api_data_structure|performance|specification|other|none",
  "location": "line number, code fragment, or none",
  "explanation": "brief explanation",
  "suggested_fix": "minimal fix or empty string",
  "confidence": 1-5
}}

Task:
{task_prompt}

Submitted solution:
{code}
"""

REPAIR_V1 = """Given the task specification, submitted solution, and review finding, produce a minimal repaired Python solution.
Return only the complete repaired code.

Task:
{task_prompt}

Submitted solution:
{code}

Review finding:
{review_json}
"""


def generation_prompt(task_prompt: str) -> str:
    return GENERATION_V1.format(task_prompt=task_prompt)


def review_prompt(task_prompt: str, code: str) -> str:
    return REVIEW_V1.format(task_prompt=task_prompt, code=code)


def same_session_review_prompt(task_prompt: str, code: str) -> str:
    return SAME_SESSION_REVIEW_V1.format(task_prompt=task_prompt, code=code)


def repair_prompt(task_prompt: str, code: str, review: dict[str, object]) -> str:
    review_json = json.dumps(review, ensure_ascii=False, sort_keys=True)
    return REPAIR_V1.format(task_prompt=task_prompt, code=code, review_json=review_json)

# Qualitative Case Report

## Boundary

Cases are selected from existing audited pilot outputs. The tool-only validation-summary condition uses retained executable validation and is not a hidden-evaluator-free final baseline.

These cases are for middle-report explanation and paper diagnosis. They should not be quoted as final expanded-study evidence before raw responses, visible/hidden evidence separation, and oracle labels are manually checked.

## `candidate_0005` / `bugsinpy_httpie_1__missing_change_1`

- task: `bugsinpy_httpie_1` / `httpie`
- candidate type: `partial_fix`
- evaluator outcome: `partial`
- issue: download filename collision handling should create a unique filename
- visible tests: `['tests/test_downloads.py::TestDownloadUtils::test_unique_filename']`

| condition | decision |
| --- | --- |
| LLM-only | accept (confidence=0.88, verifier=llm_only__deepseek-v4-pro) |
| Evidence-first | escalate (confidence=0.0, verifier=evidence_first__deepseek-v4-pro) |
| Tool-only apply-only | escalate (confidence=1.0, verifier=tool_only_apply_only) |
| Tool-only validation-summary | reject (confidence=1.0, verifier=tool_only_validation_summary) |
| Tool-augmented evidence | reject (confidence=0.0, verifier=tool_augmented_evidence__deepseek-v4-pro) |

Patch excerpt:

```diff
--- a/httpie/downloads.py
+++ b/httpie/downloads.py
@@ -135,12 +135,43 @@
     return fn


+def trim_filename(filename, max_len):
+    if len(filename) > max_len:
+        trim_by = len(filename) - max_len
+        name, ext = os.path.splitext(filename)
+        if trim_by >= len(name):
+            filename = filename[:-trim_by]
+        else:
+            filename = name[:-trim_by] + ext
+    return filename
+
+
+def get_filename_max_length(directory):
+    try:
+        max_len = os.pathconf(directory, 'PC_NAME_MAX')
+    except OSError as e:
+        if e.errno == errno.EINVAL:
+            max_len = 255
+        else:
+            raise
+    return max_len
+
+
+def trim_filename_if_needed(filename, directory='.', extra=0):
+    max_len = get_filename_max_length(directory) - extra
+    if len(filename) > max_len:
+        filename = trim_filename(filename, max_len)
+    return filename
+
+
 def get_unique_filename(filename, exists=os.path.exists):
     attempt = 0
     while True:
         suffix = '-' + str(attempt) if attempt > 0 else ''
-        if not exists(filename + suffix):
-            return filename + suffix
+        try_filename = trim_filename_i
...[truncated]
```

## `candidate_0001` / `bugsinpy_httpie_1__reference_fix`

- task: `bugsinpy_httpie_1` / `httpie`
- candidate type: `correct_reference`
- evaluator outcome: `correct`
- issue: download filename collision handling should create a unique filename
- visible tests: `['tests/test_downloads.py::TestDownloadUtils::test_unique_filename']`

| condition | decision |
| --- | --- |
| LLM-only | invalid_output (confidence=0.0, verifier=llm_only__deepseek-v4-pro) |
| Evidence-first | escalate (confidence=0.0, verifier=evidence_first__deepseek-v4-pro) |
| Tool-only apply-only | escalate (confidence=1.0, verifier=tool_only_apply_only) |
| Tool-only validation-summary | accept (confidence=1.0, verifier=tool_only_validation_summary) |
| Tool-augmented evidence | accept (confidence=0.95, verifier=tool_augmented_evidence__deepseek-v4-pro) |

Patch excerpt:

```diff
--- a/httpie/downloads.py
+++ b/httpie/downloads.py
@@ -7,6 +7,7 @@
 import os
 import re
 import sys
+import errno
 import mimetypes
 import threading
 from time import sleep, time
@@ -135,12 +136,43 @@
     return fn


+def trim_filename(filename, max_len):
+    if len(filename) > max_len:
+        trim_by = len(filename) - max_len
+        name, ext = os.path.splitext(filename)
+        if trim_by >= len(name):
+            filename = filename[:-trim_by]
+        else:
+            filename = name[:-trim_by] + ext
+    return filename
+
+
+def get_filename_max_length(directory):
+    try:
+        max_len = os.pathconf(directory, 'PC_NAME_MAX')
+    except OSError as e:
+        if e.errno == errno.EINVAL:
+            max_len = 255
+        else:
+            raise
+    return max_len
+
+
+def trim_filename_if_needed(filename, directory='.', extra=0):
+    max_len = get_filename_max_length(directory) - extra
+    if len(filename) > max_len:
+        filename = trim_filename(filename, max_len)
+    return filename
+
+
 def get_unique_filename(filename, exists=os.path.exists):
     attempt = 0
     while True:
         suffix = '-' + str(attempt) if attempt >
...[truncated]
```

## `candidate_0023` / `bugsinpy_luigi_3__reference_fix`

- task: `bugsinpy_luigi_3` / `luigi`
- candidate type: `correct_reference`
- evaluator outcome: `correct`
- issue: TupleParameter should round-trip JSON serialized scalar tuples as tuples
- visible tests: `['test/parameter_test.py::TestSerializeTupleParameter::testSerialize']`

| condition | decision |
| --- | --- |
| LLM-only | accept (confidence=0.95, verifier=llm_only__deepseek-v4-pro) |
| Evidence-first | reject (confidence=0.0, verifier=evidence_first__deepseek-v4-pro) |
| Tool-only apply-only | escalate (confidence=1.0, verifier=tool_only_apply_only) |
| Tool-only validation-summary | accept (confidence=1.0, verifier=tool_only_validation_summary) |
| Tool-augmented evidence | accept (confidence=0.0, verifier=tool_augmented_evidence__deepseek-v4-pro) |

Patch excerpt:

```diff
--- a/luigi/parameter.py
+++ b/luigi/parameter.py
@@ -1114,8 +1114,8 @@
         try:
             # loop required to parse tuple of tuples
             return tuple(tuple(x) for x in json.loads(x, object_pairs_hook=_FrozenOrderedDict))
-        except ValueError:
-            return literal_eval(x)  # if this causes an error, let that error be raised.
+        except (ValueError, TypeError):
+            return tuple(literal_eval(x))  # if this causes an error, let that error be raised.


 class NumericalParameter(Parameter):
```

## `candidate_0006` / `bugsinpy_httpie_1__missing_change_2`

- task: `bugsinpy_httpie_1` / `httpie`
- candidate type: `partial_fix`
- evaluator outcome: `partial`
- issue: download filename collision handling should create a unique filename
- visible tests: `['tests/test_downloads.py::TestDownloadUtils::test_unique_filename']`

| condition | decision |
| --- | --- |
| LLM-only | accept (confidence=0.8, verifier=llm_only__deepseek-v4-pro) |
| Evidence-first | escalate (confidence=0.9, verifier=evidence_first__deepseek-v4-pro) |
| Tool-only apply-only | escalate (confidence=1.0, verifier=tool_only_apply_only) |
| Tool-only validation-summary | reject (confidence=1.0, verifier=tool_only_validation_summary) |
| Tool-augmented evidence | reject (confidence=0.95, verifier=tool_augmented_evidence__deepseek-v4-pro) |

Patch excerpt:

```diff
--- a/httpie/downloads.py
+++ b/httpie/downloads.py
@@ -7,6 +7,7 @@
 import os
 import re
 import sys
+import errno
 import mimetypes
 import threading
 from time import sleep, time
@@ -139,8 +140,10 @@
     attempt = 0
     while True:
         suffix = '-' + str(attempt) if attempt > 0 else ''
-        if not exists(filename + suffix):
-            return filename + suffix
+        try_filename = trim_filename_if_needed(filename, extra=len(suffix))
+        try_filename += suffix
+        if not exists(try_filename):
+            return try_filename
         attempt += 1
```

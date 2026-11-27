---
description: Print the work order for contributing to an org repository before touching it
argument-hint: "<repo> [task description]"
allowed-tools: Bash(python3 scripts/brain/brain.py:*), Read
---

Get the brief for an org repository, following the **`org-contribute`** skill.

**Input:** `$ARGUMENTS`: the first word is the repository (registry name, `owner/name`, or hub name); the rest, if any, is the task.

1. Run `python3 scripts/brain/brain.py brief <repo> --task "<task>"`. If the repository is not registered, run `python3 scripts/brain/brain.py repos` and say which names exist.
2. Read the brief in full and summarize for the user: where the change belongs, the gates to run, the readiness gaps that matter for this task, and the two or three notes most worth reading first.
3. Do not start the change until the user confirms, unless they already asked for it.

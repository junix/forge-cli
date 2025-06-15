---
trigger: always_on
description: About the codebase setup
globs:**/*.py
---

## **MUST** set PYTHONPATH before you run any python/uv commands.

```bash
PYTHONPATH=/Users/junix/knowledge-forge-office/knowledge_forge,
```

then run the commands

## where to fetch server log
the server already running, and will auto reload when code changes. if you want to see the erver log, run:

```bash
tail -200 /tmp/knowledge-forge.log
```
to seen last 200 lines of serverlog

## how to run smoking tests

```bash
PYTHONPATH=/Users/junix/knowledge-forge-office/knowledge_forge  uv run commands/hello.py
```


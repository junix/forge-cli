---
trigger: always_on
description: manager project in uv
globs: **/*.py
---

1.  **Primary Tool:** Use the `uv` tool for all package management and script execution tasks.
2.  **Adding Dependencies:** When asked to add or install a Python package, use the command:
    ```bash
    uv add <package-name>
    ```
3.  **Running Scripts:** When asked to run a script defined in `pyproject.toml`, use the command:
    ```bash
    cd /Users/junix/knowledge-forge-office/knowledge_forge/ && PYTHONPATH=/Users/junix/knowledge-forge-office/knowledge_forge uv run  <script-name>
    ```
4.  **Avoid Alternatives:** Refrain from using `pip install`, `poetry add`, `pipenv install`, or similar commands from other package managers unless explicitly told otherwise for a specific, exceptional reason. Always default to `uv`.

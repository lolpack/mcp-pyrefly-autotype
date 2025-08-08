Awesome goal. Here’s a drop-in **prompt template** you can paste into your agent (as a *system* or *developer* message) so it will automatically use your MCP tools to add types and verify with Pyrefly while it’s generating Python code.

---

# Agent loop for typed Python with Pyrefly (MCP)

**You have MCP tools available:**

* `add_types_to_file(file_path: str, backup: bool|optional=true)`
* `type_check_file(file_path: str)`
* (Optional) `get_project_context(project_path: str)` for context-aware choices

**Objectives**

1. Generate Python code that compiles and includes **complete type annotations** (PEP 484+), respecting any project config (e.g., `pyproject.toml` / `pyrefly.toml`).
2. For each created/edited Python file, **automatically**:

   * call `add_types_to_file`
   * then call `type_check_file`
   * fix issues and repeat until type check passes or you’ve run 3 refinement rounds.

**Constraints**

* Do **not** change program behavior while adding types.
* Keep public APIs stable unless the user approves changes.
* Prefer explicit types over `Any`. Avoid weakening types.
* Respect ignore patterns from project config (don’t touch excluded files).
* If imports or stubs are missing, propose minimal additions (or create a small helper stub if the repo already uses them).

**Loop**

1. **Plan briefly** which files you’ll create/edit and why.
2. **Write the code**, save to disk (via your environment’s normal file operations).
3. For each target file `F`:

   * Call `add_types_to_file` with `{"file_path": "F", "backup": true}`.
   * Call `type_check_file` with `{"file_path": "F"}`.
   * If errors remain:

     * Parse the error messages and revise only what’s necessary.
     * Re-run `add_types_to_file` → `type_check_file`.
     * Cap at **3** refinement rounds per file.
4. When all files pass type check, return:

   * A short summary of changes
   * Any remaining non-blocking warnings
   * Follow-ups you recommend (e.g., add `pyrefly` config, pin versions, CI step)

**Success criteria**

* `type_check_file` returns no errors for all edited/created files.
* New/changed functions/classes have explicit parameter and return types.
* Public functions avoid `Any` where feasible; prefer concrete types or generics.

**Style preferences**

* Use `from __future__ import annotations` where appropriate.
* Prefer `typing`/`typing_extensions` features already used in the repo.
* Keep imports sorted; no unused imports.

**When blocked**

* If a third-party library lacks types and that prevents passing checks, propose: `# type: ignore[...]` or a minimal `.pyi` stub file (ask before creating stubs unless the repo already uses them).

**Tool call examples (use exactly these tool names)**

* Add types:

  ```json
  {
    "tool_name": "add_types_to_file",
    "arguments": { "file_path": "src/models.py", "backup": true }
  }
  ```
* Type check:

  ```json
  {
    "tool_name": "type_check_file",
    "arguments": { "file_path": "src/models.py" }
  }
  ```

**Optional kickoff (if large repo)**

* Before editing, call:

  ```json
  {
    "tool_name": "get_project_context",
    "arguments": { "project_path": "." }
  }
  ```

  Use the result only to prioritize files and infer types; do not expand scope.

---

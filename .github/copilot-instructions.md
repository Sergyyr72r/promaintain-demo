## copilot-instructions for promaintain-demo

This file gives concise, actionable guidance for an AI coding agent working on this repository.

Key facts (read before editing):

- This is a small Streamlit app (`app.py`) backed by a local SQLite DB file `construction_log.db`.
- The DB schema (created at runtime and in `seed_db.py`) contains tables: `projects`, `workers`, `scaffolds` and `work_logs`.
- `seed_db.py` inserts example data (including `volume_m3` and `total_cost` for scaffolds). Use it to populate the DB for manual testing.
- `fix_theme.py` creates `.streamlit/config.toml` to force the light theme used by the app.
- Dependencies are minimal; see `requirements.txt` (streamlit, pandas, plotly, openpyxl).

Run / dev commands (how humans run the app):

- Create or seed the DB (optional for dev):
  - `python3 seed_db.py`  # populates `construction_log.db` with projects, workers, scaffolds and work_logs
- Ensure theme file exists (optional):
  - `python3 fix_theme.py`  # writes `.streamlit/config.toml` with the light theme
- Run the app locally:
  - `streamlit run app.py`

Important code patterns and where to edit safely

- Database access uses two helpers in `app.py`:
  - `get_data(query, params=())` returns a pandas DataFrame (uses `pd.read_sql_query`).
  - `run_query(query, params=())` executes a write and returns True/False.
  - When changing schema or column names, update both `init_db()` in `app.py` and `seed_db.py` to keep them in sync.

- Table schema examples (SQL used in code):
  - scaffold insert/update: `INSERT INTO scaffolds (project_id, number, description, volume_m3, total_cost) ...`
  - update scaffolds: `UPDATE scaffolds SET volume_m3=?, total_cost=? WHERE project_id=? AND number=?`
  - work_logs insert: `INSERT INTO work_logs (user_name, project_name, scaffold_number, work_date, hours) VALUES (?, ?, ?, ?, ?)`

- UI conventions (important for automated edits):
  - Many select boxes show scaffold entries as `"{number} ({description})"` in the `disp` column. When you parse or construct scaffold selection values, extract the scaffold number by splitting on `" ("` and taking the left part.
  - Session keys used in `st.session_state`: `logged_in`, `user_role`, `current_user_name`, `admin_warning_shown`. Preserve these names when adding session behavior.
  - The code relies on `st.form` + `st.form_submit_button` patterns; prefer to keep operations inside the same form block to preserve Streamlit state behavior.

Localization / comments

- The UI and many comments are in German; some developer comments are in Russian. When adding or modifying user-facing text, keep the German phrasing or provide clear translations where appropriate.

Styling / theme

- `local_css()` in `app.py` injects inline CSS for branding (logo colors, button styles, footer). Small UI changes to colors or fonts are done here.
- `fix_theme.py` sets `.streamlit/config.toml` to force a light theme. Keep coordinated changes between `local_css()` and the theme file.

Safety notes / migration cautions

- Do not change the uniqueness constraint on `scaffolds` (`UNIQUE(project_id, number)`) without migrating existing DB rows (both `seed_db.py` and `init_db()` must be adjusted together).
- The app uses raw `sqlite3` connections without a connection pool. For edits that introduce long-running DB operations, ensure connections are closed promptly.

Where to look for examples

- `app.py` — the main app: session handling, DB access wrappers, UI patterns (forms, tabs, selectboxes), `local_css()`.
- `seed_db.py` — canonical example of how rows are created, including random generation of `volume_m3` and `total_cost` for scaffolds.
- `fix_theme.py` — how the project enforces a Streamlit theme file.

If you need clarification

- Ask which text should remain in German vs English for UI changes.
- Ask whether you should run `seed_db.py` automatically when adding columns or during schema migrations.

When editing, prefer small, reversible changes and run the app locally (`streamlit run app.py`) to validate UI/state interactions.

---
Please review this draft and tell me if you'd like more or less detail in any section, or if there are other files or workflows to include.

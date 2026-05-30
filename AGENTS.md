# SkillCI Agent Notes

## Project Shape

- Python 3.10+ Typer CLI for linting, trigger-testing, snapshotting, and reporting Agent Skill directories that contain `SKILL.md` plus `skillci.yaml`.
- Console entrypoint is `skillci.cli:app`; the installed command is `skillci` from `pyproject.toml`.
- Core flow is `parse_skill` + `parse_config` -> static health checks -> local or LLM trigger evaluation -> terminal/JSON/Markdown report.

## Commands

```bash
pip install -e .[dev]          # pytest + ruff
pip install -e .[llm]          # OpenAI-compatible provider support
python -m pytest -v            # full test suite
python -m pytest tests/test_cli.py -v
python -m pytest tests/test_cli.py::test_test_command_runs_local_mode_for_example_skill -v
ruff check .
ruff check --fix .
```

- There is no separate typecheck command; linting is Ruff only (`E`, `F`, `I`, `UP`, `B`; line length 100; target `py310`).
- No lockfile or CI workflow is present, so `pyproject.toml` is the executable source of truth for dependencies and tooling.

## Key Paths

- `skillci/cli.py` defines all CLI commands and user-facing mode restrictions.
- `skillci/runner.py` wires lint, local tests, and LLM tests; update this when adding evaluator behavior.
- `skillci/parser/skill_parser.py` parses only `SKILL.md` frontmatter/body and backtick references under `references/`, `scripts/`, and `assets/`.
- `skillci/parser/config_parser.py` loads `skillci.yaml`, then deep-merges sibling `skillci.local.yaml` if present.
- `skillci/evaluator/local_trigger_evaluator.py` contains the hardcoded local scoring weights and `DOMAIN_TERMS`.
- `examples/api-doc-writer/` is the reference skill used by CLI and runner tests.

## CLI Quirks

- `skillci test` accepts only `--mode local` and `--mode llm`; `both` exists in the config enum/docs but exits with code 2 in the CLI.
- `skillci snapshot <path>` always runs the local evaluator and writes `.skillci/baselines/<skill-name>/<timestamp>.json` plus `latest.json`.
- `skillci test <path> --compare latest` is the only comparison mode; named baselines are not implemented.
- `skillci report` only supports `--format markdown` and always renders a fresh local test report.
- For LLM tests in automation, use `--provider mock`; real OpenAI-compatible calls require the `llm` extra and `OPENAI_API_KEY` or judge config.

## Skill Config Gotchas

- `skillci.yaml` must include `skill` and `cases`; relative `skill` paths resolve from the config file directory.
- Keep secrets in `skillci.local.yaml`; it is gitignored and automatically overrides matching nested fields in `skillci.yaml`.
- Baselines under `.skillci/` are gitignored; do not expect them in a fresh checkout.
- Local trigger scoring uses character-level tokenization for Chinese and a small hardcoded domain vocabulary, so new domains often require extending `DOMAIN_TERMS` and tests together.

## Testing Notes

- Tests are plain pytest files under `tests/`; there is no `conftest.py` or fixture-heavy setup.
- Focused verification is cheap: run the matching `tests/test_*.py` file, then `python -m pytest -v` and `ruff check .` before claiming completion.

## Version Release Checklist

Complete these checks before releasing a new version to ensure version consistency.

### Version Locations to Sync

1. **`pyproject.toml`** — `version = "x.y.z"`
2. **`skillci/__init__.py`** — `__version__ = "x.y.z"`
3. **`README.md`** — release badge: `release-vx.y.z`
4. **`README_zh.md`** — release badge: `release-vx.y.z`

### Config Documentation Check

If the release involves config field changes (add, rename, delete), sync these:

- Configuration tables in `README.md` and `README_zh.md`
- Example `skillci.yaml` / `skillci.local.yaml` code blocks
- Field priority notes (if changed)

### Release Flow

```bash
# 1. Bump version (4 locations)
# pyproject.toml, skillci/__init__.py, README.md badge, README_zh.md badge

# 2. Run tests and lint
python -m pytest -v
ruff check .

# 3. Commit
git add -A && git commit -m "chore: bump version to x.y.z"

# 4. Delete old tag (if exists)
git tag -d vx.y.z && git push origin :refs/tags/vx.y.z

# 5. Create new tag
git tag -a vx.y.z -m "Release vx.y.z: <brief description>"

# 6. Push
git push && git push --tags
```

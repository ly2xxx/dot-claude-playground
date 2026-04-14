# JSON Pretty-Print CLI — Implementation Summary

## What Was Built

A standalone Python CLI tool that reads a JSON config file and pretty-prints it
with ANSI syntax highlighting. It lives under `skilo_lab/json-pretty-print/` in
the repository, following the same layout as existing tools in `skilo_lab/`.

### Key features

| Feature | Detail |
|---|---|
| `--file` flag | Required. Path to the JSON file to read |
| `--indent N` | Optional. Indentation width (default: 2 spaces) |
| `--no-color` | Disable ANSI colour codes (useful when piping output) |
| Syntax highlighting | Uses **pygments** `JsonLexer` + `TerminalFormatter` |
| Graceful fallback | If pygments is not installed, plain formatted JSON is printed |
| Exit codes | `0` success · `1` file-not-found or invalid JSON · `2` argparse error |

---

## Files Changed

| File | Status | Description |
|---|---|---|
| `skilo_lab/json-pretty-print/scripts/json_pretty_print.py` | **New** | Main CLI script (108 lines) |
| `skilo_lab/json-pretty-print/tests/test_json_pretty_print.py` | **New** | Test suite (208 lines, 28 tests) |
| `skilo_lab/json-pretty-print/requirements.txt` | **New** | Runtime + test dependencies |

All three files were committed in a single commit (`91bbea2`) on branch
`worktree-agent-ab2bcdb4`.

---

## Tests Added

28 pytest tests organised across four classes:

| Class | Tests | Coverage area |
|---|---|---|
| `TestLoadJson` | 5 | File loading, missing file, invalid JSON, empty object, array |
| `TestPrettyFormat` | 4 | Default/custom indent, round-trip validity, Unicode preservation |
| `TestColorize` | 3 | Return type, text survival, ANSI code presence |
| `TestPrintJson` | 6 | Exit codes, output content, valid JSON output, error messages |
| `TestCLI` | 10 | Subprocess integration: flags, exit codes, help, output correctness |

All 28 tests pass (`28 passed in 1.03s`).

**Run tests with:**
```bash
python -m pytest skilo_lab/json-pretty-print/tests/ -v
```

---

## Usage Example

```bash
# Pretty-print with syntax highlighting (default when stdout is a TTY)
python skilo_lab/json-pretty-print/scripts/json_pretty_print.py --file config.json

# Plain text (useful when piping or redirecting)
python skilo_lab/json-pretty-print/scripts/json_pretty_print.py --file config.json --no-color

# 4-space indent
python skilo_lab/json-pretty-print/scripts/json_pretty_print.py --file config.json --indent 4
```

---

## Caveats

- **pygments is a runtime dependency** — the script degrades gracefully to plain
  JSON if it is missing, but colour output requires `pip install pygments`.
- **No stdin support** — the tool intentionally only supports file-based input
  via `--file`; piping JSON via stdin was not in scope.
- **Colour is always applied** when `--no-color` is omitted, regardless of
  whether stdout is a TTY. This ensures consistent behaviour when output is
  captured in tests or CI but colour was explicitly requested by the user.
- The tool is pure Python stdlib + pygments; no additional frameworks were
  introduced into the repository.

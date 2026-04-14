"""
Tests for tools/json_pretty/cli.py

Covers:
  - Happy path: valid JSON file is loaded and pretty-printed
  - Edge cases: empty object, nested structures, arrays, unicode
  - Error paths: missing file, invalid JSON, path-is-a-directory
  - CLI flag: --file, --indent, --plain
  - Highlighting: pygments integration (mocked)
"""

import json
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Make the package importable when running from repo root
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.json_pretty.cli import (
    highlight_json,
    load_json,
    pretty_format,
    run,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_json_file(tmp_path: Path) -> Path:
    """A well-formed JSON file with simple key/value pairs."""
    data = {"name": "test", "version": "1.0.0", "enabled": True}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def nested_json_file(tmp_path: Path) -> Path:
    """A JSON file with nested objects and arrays."""
    data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {"user": "admin", "password": "secret"},
        },
        "features": ["auth", "logging", "metrics"],
    }
    path = tmp_path / "nested.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def unicode_json_file(tmp_path: Path) -> Path:
    """A JSON file containing non-ASCII characters."""
    data = {"greeting": "こんにちは", "emoji": "✅"}
    path = tmp_path / "unicode.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def empty_object_json_file(tmp_path: Path) -> Path:
    """A JSON file containing an empty object."""
    path = tmp_path / "empty.json"
    path.write_text("{}", encoding="utf-8")
    return path


@pytest.fixture
def array_json_file(tmp_path: Path) -> Path:
    """A JSON file whose root element is an array."""
    data = [1, "two", {"three": 3}]
    path = tmp_path / "array.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def invalid_json_file(tmp_path: Path) -> Path:
    """A file that is not valid JSON."""
    path = tmp_path / "bad.json"
    path.write_text("{not: valid json}", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# load_json tests
# ---------------------------------------------------------------------------

class TestLoadJson:
    def test_loads_valid_file(self, simple_json_file: Path) -> None:
        data = load_json(str(simple_json_file))
        assert data["name"] == "test"
        assert data["version"] == "1.0.0"
        assert data["enabled"] is True

    def test_raises_for_missing_file(self, tmp_path: Path) -> None:
        missing = str(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_json(missing)

    def test_raises_for_invalid_json(self, invalid_json_file: Path) -> None:
        with pytest.raises(json.JSONDecodeError):
            load_json(str(invalid_json_file))

    def test_raises_for_directory(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not a file"):
            load_json(str(tmp_path))

    def test_loads_unicode(self, unicode_json_file: Path) -> None:
        data = load_json(str(unicode_json_file))
        assert data["greeting"] == "こんにちは"

    def test_loads_array(self, array_json_file: Path) -> None:
        data = load_json(str(array_json_file))
        assert isinstance(data, list)
        assert data[0] == 1

    def test_loads_empty_object(self, empty_object_json_file: Path) -> None:
        data = load_json(str(empty_object_json_file))
        assert data == {}


# ---------------------------------------------------------------------------
# pretty_format tests
# ---------------------------------------------------------------------------

class TestPrettyFormat:
    def test_default_indent(self) -> None:
        result = pretty_format({"a": 1})
        assert result == '{\n  "a": 1\n}'

    def test_custom_indent(self) -> None:
        result = pretty_format({"a": 1}, indent=4)
        assert result == '{\n    "a": 1\n}'

    def test_unicode_preserved(self) -> None:
        result = pretty_format({"emoji": "✅"})
        assert "✅" in result

    def test_nested_structure(self) -> None:
        data = {"outer": {"inner": "value"}}
        result = pretty_format(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_array_root(self) -> None:
        result = pretty_format([1, 2, 3])
        assert json.loads(result) == [1, 2, 3]


# ---------------------------------------------------------------------------
# highlight_json tests
# ---------------------------------------------------------------------------

class TestHighlightJson:
    def test_plain_flag_skips_highlighting(self) -> None:
        json_str = '{"a": 1}'
        result = highlight_json(json_str, force_plain=True)
        assert result == json_str

    def test_non_tty_skips_highlighting(self) -> None:
        """When stdout is not a TTY, output should be returned as-is."""
        json_str = '{"a": 1}'
        with patch("sys.stdout.isatty", return_value=False):
            result = highlight_json(json_str, force_plain=False)
        assert result == json_str

    def test_highlighting_applied_on_tty_with_pygments(self) -> None:
        """When stdout is a TTY and pygments is available, output differs from plain."""
        import tools.json_pretty.cli as cli_module

        if not cli_module.PYGMENTS_AVAILABLE:
            pytest.skip("pygments not installed")

        json_str = '{\n  "key": "value"\n}'
        with patch("sys.stdout.isatty", return_value=True):
            result = highlight_json(json_str, force_plain=False)
        # Pygments adds ANSI escape codes; the raw JSON string should be a substring
        assert '"key"' in result

    def test_no_pygments_returns_plain(self) -> None:
        """When PYGMENTS_AVAILABLE is False, plain string is returned."""
        import tools.json_pretty.cli as cli_module

        json_str = '{"a": 1}'
        original = cli_module.PYGMENTS_AVAILABLE
        try:
            cli_module.PYGMENTS_AVAILABLE = False
            with patch("sys.stdout.isatty", return_value=True):
                result = highlight_json(json_str, force_plain=False)
            assert result == json_str
        finally:
            cli_module.PYGMENTS_AVAILABLE = original


# ---------------------------------------------------------------------------
# run() integration tests
# ---------------------------------------------------------------------------

class TestRun:
    def test_happy_path_returns_zero(self, simple_json_file: Path, capsys) -> None:
        exit_code = run(str(simple_json_file), indent=2, plain=True)
        assert exit_code == 0

    def test_happy_path_output_is_valid_json(self, simple_json_file: Path, capsys) -> None:
        run(str(simple_json_file), indent=2, plain=True)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["name"] == "test"

    def test_missing_file_returns_one(self, tmp_path: Path, capsys) -> None:
        exit_code = run(str(tmp_path / "missing.json"), plain=True)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_invalid_json_returns_one(self, invalid_json_file: Path, capsys) -> None:
        exit_code = run(str(invalid_json_file), plain=True)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_custom_indent_in_output(self, simple_json_file: Path, capsys) -> None:
        run(str(simple_json_file), indent=4, plain=True)
        captured = capsys.readouterr()
        # 4-space indent means lines start with 4 spaces
        assert "    " in captured.out

    def test_nested_json_output(self, nested_json_file: Path, capsys) -> None:
        exit_code = run(str(nested_json_file), indent=2, plain=True)
        assert exit_code == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["database"]["port"] == 5432
        assert "auth" in parsed["features"]

    def test_unicode_in_output(self, unicode_json_file: Path, capsys) -> None:
        run(str(unicode_json_file), indent=2, plain=True)
        captured = capsys.readouterr()
        assert "こんにちは" in captured.out

    def test_array_root_output(self, array_json_file: Path, capsys) -> None:
        exit_code = run(str(array_json_file), indent=2, plain=True)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert json.loads(captured.out) == [1, "two", {"three": 3}]

    def test_empty_object_output(self, empty_object_json_file: Path, capsys) -> None:
        exit_code = run(str(empty_object_json_file), indent=2, plain=True)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {}

    def test_directory_path_returns_one(self, tmp_path: Path, capsys) -> None:
        exit_code = run(str(tmp_path), plain=True)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err


# ---------------------------------------------------------------------------
# CLI argument parsing tests (via argparse/sys.argv)
# ---------------------------------------------------------------------------

class TestCLI:
    def test_missing_file_flag_exits_nonzero(self) -> None:
        """--file is required; omitting it should cause argparse to exit with code 2."""
        with pytest.raises(SystemExit) as exc_info:
            with patch("sys.argv", ["cli.py"]):
                import importlib
                import tools.json_pretty.cli as cli_module
                # Re-invoke main directly to trigger argparse error
                cli_module.main()
        assert exc_info.value.code != 0

    def test_file_flag_accepted(self, simple_json_file: Path, capsys) -> None:
        with patch("sys.argv", ["cli.py", "--file", str(simple_json_file), "--plain"]):
            with pytest.raises(SystemExit) as exc_info:
                import tools.json_pretty.cli as cli_module
                cli_module.main()
        assert exc_info.value.code == 0

    def test_indent_flag(self, simple_json_file: Path, capsys) -> None:
        with patch("sys.argv", ["cli.py", "--file", str(simple_json_file), "--indent", "4", "--plain"]):
            with pytest.raises(SystemExit) as exc_info:
                import tools.json_pretty.cli as cli_module
                cli_module.main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "    " in captured.out

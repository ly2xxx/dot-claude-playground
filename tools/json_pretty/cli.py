#!/usr/bin/env python3
"""
json-pretty: A CLI tool that reads a JSON config file and pretty-prints it
with syntax highlighting.

Usage:
    python cli.py --file path/to/config.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


def load_json(file_path: str) -> dict:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Parsed JSON as a Python dict (or list for JSON arrays).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def pretty_format(data: object, indent: int = 2) -> str:
    """Serialize data to a pretty-printed JSON string.

    Args:
        data: Python object to serialize.
        indent: Number of spaces per indentation level.

    Returns:
        Formatted JSON string.
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def highlight_json(json_str: str, force_plain: bool = False) -> str:
    """Apply syntax highlighting to a JSON string.

    If pygments is not installed or the output is not a TTY (and
    force_plain is False), returns the string unchanged.

    Args:
        json_str: The JSON string to highlight.
        force_plain: When True, skip syntax highlighting.

    Returns:
        Highlighted (or plain) string.
    """
    if force_plain or not PYGMENTS_AVAILABLE or not sys.stdout.isatty():
        return json_str

    return highlight(json_str, JsonLexer(), TerminalFormatter())


def run(file_path: str, indent: int = 2, plain: bool = False) -> int:
    """Core logic: load, format, and print a JSON file.

    Args:
        file_path: Path to the JSON file.
        indent: Indentation level for pretty-printing.
        plain: Disable syntax highlighting.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    try:
        data = load_json(file_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in '{file_path}': {exc}", file=sys.stderr)
        return 1

    formatted = pretty_format(data, indent=indent)
    output = highlight_json(formatted, force_plain=plain)
    print(output, end="")
    # Ensure a trailing newline when highlight strips it
    if not output.endswith("\n"):
        print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pretty-print a JSON config file with syntax highlighting.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --file config.json
  python cli.py --file config.json --indent 4
  python cli.py --file config.json --plain
        """,
    )

    parser.add_argument(
        "--file",
        required=True,
        metavar="PATH",
        help="Path to the JSON file to pretty-print.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        metavar="N",
        help="Number of spaces per indentation level (default: 2).",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        default=False,
        help="Disable syntax highlighting (useful for piping output).",
    )

    args = parser.parse_args()
    sys.exit(run(args.file, indent=args.indent, plain=args.plain))


if __name__ == "__main__":
    main()

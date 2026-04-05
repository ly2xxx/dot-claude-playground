"""
Step definitions for cv-polish BDD tests.
Assertions only — Claude is never called here.
All file state comes from fixtures restored by environment.py.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from behave import given, when, then, step
from behave import step_matcher

step_matcher("parse")


# ─── Helpers ────────────────────────────────────────────────────────────────

def run_claude(context, prompt, timeout=300):
    cmd = context.claude_cmd + ["-p", prompt]
    env = os.environ.copy()
    env["CLAUDE_CODE_DISABLE_IDE"] = "true"
    try:
        result = subprocess.run(cmd, cwd=context.work_dir, capture_output=True,
                                text=True, env=env, timeout=timeout)
        context.last_output     = result.stdout
        context.last_stderr     = result.stderr
        context.last_returncode = result.returncode
        return result
    except subprocess.TimeoutExpired:
        raise AssertionError(f"Claude timed out after {timeout}s")


def assets(context) -> Path:
    return context.work_dir / "assets"


def find_new_docx(context, exclude: list[str] | None = None) -> Path | None:
    """Return the first .docx in assets/ not in the exclusion list."""
    skip = set(exclude or ["YL-CV-2024.docx"])
    for f in assets(context).glob("*.docx"):
        if f.name not in skip:
            return f
    return None


def docx_text(path: Path) -> str:
    from docx import Document
    return "\n".join(p.text for p in Document(str(path)).paragraphs)


def get_output_text(context) -> str:
    if not hasattr(context, "_output_text"):
        output = getattr(context, "output_file", find_new_docx(context))
        assert output is not None, "No output .docx found in assets/"
        context._output_text = docx_text(output)
    return context._output_text


# ─── GIVEN ──────────────────────────────────────────────────────────────────

@given("the SKILL.md is loaded")
def step_skill_loaded(context):
    path = context.work_dir / ".claude" / "skills" / "cv-polish" / "SKILL.md"
    assert path.exists(), f"SKILL.md not found at {path}"


@given('the assets directory contains "{filename}"')
def step_assets_has(context, filename):
    assert (assets(context) / filename).exists(), f"Fixture {filename} missing"


@given('"{filepath}" already exists')
def step_pre_create_file(context, filepath):
    src  = assets(context) / "YL-CV-2024.docx"
    dest = context.work_dir / filepath
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dest)
    context.original_sizes[filepath] = dest.stat().st_size


# ─── WHEN ─────────────────────────────────────────────────────────────────

@when('I ask Claude to "{prompt}"')
def step_ask_claude(context, prompt):
    if context.mock_mode == "replay":
        print(f"♻️  Replay — skipping Claude for: {prompt}")
        context._output_text = None   # reset cached docx text for this scenario
        return
    context._output_text = None
    print(f"🤖 Running Claude: {prompt}")
    run_claude(context, prompt)


# ─── THEN — stdout ────────────────────────────────────────────────────────

@then("the stdout should reference CV content")
def step_stdout_references_cv(context):
    signals = ["yang li", "barclays", "j.p. morgan", "glasgow", "platform", "python"]
    out = context.last_output.lower()
    found = [s for s in signals if s in out]
    assert found, (
        "Claude stdout doesn't reference any CV content.\n"
        f"Expected one of: {signals}\nStdout: {context.last_output[:400]}"
    )
    print(f"✅ Stdout references: {found}")


# ─── THEN — file/directory existence ─────────────────────────────────────

@then('"{path}" should be a directory')
def step_is_dir(context, path):
    d = context.work_dir / path
    assert d.is_dir(), f"Directory not found: {path}"
    print(f"✅ Directory exists: {path}")


@then('at least one .docx should exist under "{dirpath}"')
def step_docx_in_dir(context, dirpath):
    d = context.work_dir / dirpath
    files = list(d.glob("*.docx"))
    assert files, f"No .docx files in {dirpath}"
    print(f"✅ Found in {dirpath}: {[f.name for f in files]}")


@then('"{filepath}" should still exist')
def step_file_still_exists(context, filepath):
    assert (context.work_dir / filepath).exists(), f"{filepath} was deleted or not found"
    print(f"✅ Still exists: {filepath}")


@then('"{filepath}" should exist')
def step_file_exists(context, filepath):
    path = context.work_dir / filepath
    assert path.exists(), f"{filepath} not found"
    context.current_file = path
    print(f"✅ Exists: {filepath}")


@then('a new .docx file should exist in "assets/" besides the original')
def step_new_docx_exists(context):
    f = find_new_docx(context)
    assert f is not None, (
        f"No new .docx found in assets/ besides YL-CV-2024.docx.\n"
        f"Files: {[x.name for x in assets(context).glob('*.docx')]}"
    )
    context.output_file = f
    print(f"✅ New output: {f.name}")


@then('a new .docx file should exist in "assets/" besides "{existing}"')
def step_new_docx_besides(context, existing):
    f = find_new_docx(context, exclude=["YL-CV-2024.docx", existing])
    assert f is not None, f"No new .docx found alongside {existing}"
    context.output_file = f
    print(f"✅ New file alongside {existing}: {f.name}")


# ─── THEN — output filename ───────────────────────────────────────────────

@then('the output filename should match "{pattern}"')
def step_filename_matches(context, pattern):
    import fnmatch
    f = getattr(context, "output_file", find_new_docx(context))
    assert f, "No output file found"
    assert fnmatch.fnmatch(f.name, pattern), (
        f"Filename '{f.name}' does not match '{pattern}'"
    )
    print(f"✅ Filename matches '{pattern}': {f.name}")


@then('the output file extension should be ".docx"')
def step_ext_is_docx(context):
    f = getattr(context, "output_file", find_new_docx(context))
    assert f and f.suffix == ".docx", f"Expected .docx, got '{f.suffix if f else 'none'}'"
    print("✅ Extension is .docx")


# ─── THEN — filename contains (OR-chain, regex matcher) ──────────────────

step_matcher("re")

@then(r'the output filename should contain (?P<raw_alts>"[^"]+"(?:\s+or\s+"[^"]+")*)')
def step_filename_contains_any(context, raw_alts):
    terms = re.findall(r'"([^"]+)"', raw_alts)
    f = getattr(context, "output_file", find_new_docx(context))
    assert f, "No output file found"
    found = [t for t in terms if t.lower() in f.name.lower()]
    assert found, f"Filename '{f.name}' contains none of {terms}"
    print(f"✅ Filename contains: {found}")

step_matcher("parse")


# ─── THEN — file content ──────────────────────────────────────────────────

@then('"{filepath}" should contain "{text}"')
def step_file_contains(context, filepath, text):
    path = context.work_dir / filepath
    assert path.exists(), f"{filepath} not found"
    content = path.read_text(errors="replace")
    assert text.lower() in content.lower(), (
        f"'{text}' not found in {filepath}.\nPreview: {content[:300]}"
    )
    print(f"✅ {filepath} contains '{text}'")


@then('"{filepath}" should have more than {n:d} lines')
def step_file_has_lines(context, filepath, n):
    path = context.work_dir / filepath
    lines = path.read_text(errors="replace").splitlines()
    assert len(lines) > n, f"{filepath} has {len(lines)} lines, expected >{n}"
    print(f"✅ {filepath} has {len(lines)} lines")


# ─── THEN — .docx content (OR-chain, regex matcher) ──────────────────────

step_matcher("re")

@then(r'the output \.docx should contain (?P<raw_alts>"[^"]+"(?:\s+or\s+"[^"]+")*)')
def step_docx_contains_any(context, raw_alts):
    terms = re.findall(r'"([^"]+)"', raw_alts)
    content = get_output_text(context)
    found = [t for t in terms if t.lower() in content.lower()]
    assert found, (
        f"None of {terms} found in output .docx.\n"
        f"Preview: {content[:400]}"
    )
    print(f"✅ .docx contains: {found}")

step_matcher("parse")


@then('the output .docx should not contain "{text}"')
def step_docx_not_contain(context, text):
    content = get_output_text(context)
    assert text.lower() not in content.lower(), (
        f"Forbidden phrase '{text}' found in output .docx.\n"
        "SKILL.md: avoid weak/passive verbs and first-person language."
    )
    print(f"✅ .docx does not contain '{text}'")


@then('the output .docx should contain one of "{comma_sep}"')
def step_docx_contains_one_of(context, comma_sep):
    terms = [t.strip() for t in comma_sep.split(",")]
    content = get_output_text(context)
    found = [t for t in terms if t.lower() in content.lower()]
    assert found, (
        f"None of the strong action verbs found: {terms}.\n"
        "SKILL.md: use achievement-focused verbs (Delivered, Drove, Built…)"
    )
    print(f"✅ Strong verbs found: {found}")


@then('the output .docx should not start any sentence with "I "')
def step_docx_no_first_person(context):
    content = get_output_text(context)
    violations = [l.strip() for l in content.splitlines() if l.strip().startswith("I ")]
    assert not violations, (
        f"Found {len(violations)} sentences starting with 'I ':\n"
        + "\n".join(f"  {v}" for v in violations[:5])
    )
    print("✅ No sentences start with 'I '")


@then('the output .docx should contain at least {n:d} metric patterns')
def step_docx_has_metrics(context, n):
    content = get_output_text(context)
    matches = re.findall(r'%|\d+x|\d+\+|from \d|to \d|\d+ hours|\d+ minutes|\d+ days', content)
    assert len(matches) >= n, (
        f"Only {len(matches)} metric patterns found, expected at least {n}.\n"
        "SKILL.md: quantify ≥70% of achievements."
    )
    print(f"✅ Found {len(matches)} metric patterns")

"""
Behave environment for cv-polish SKILL.md testing.
Record-replay pattern — see bdd-skill-testing SKILL.md for full explanation.

Modes (CLAUDE_MOCK env var):
  replay  (default) — restore fixtures, skip Claude, instant + free
  record            — run real Claude, snapshot outputs as fixtures
  real              — run real Claude every time (slow, costs credits)

Workflow:
  # Record once:
  $env:CLAUDE_MOCK="record"; behave features/

  # Replay forever after:
  behave features/

  # Re-record after SKILL.md changes:
  $env:CLAUDE_MOCK="record"; behave features/
"""

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

CV_POLISH_ROOT = Path(__file__).parent.parent.parent   # cv-polish/
SKILL_MD_SRC   = CV_POLISH_ROOT / "SKILL.md"
ASSETS_SRC     = CV_POLISH_ROOT / "assets"
FIXTURES_DIR   = CV_POLISH_ROOT / "tests" / "fixtures"


def _slug(scenario) -> str:
    return re.sub(r"[^\w]+", "_", scenario.name).strip("_").lower()


def _snapshot(src: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*"):
        if f.is_file():
            out = dest / f.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)


def _restore(fixture_dir: Path, sandbox: Path):
    for f in fixture_dir.rglob("*"):
        if f.is_file() and f.name != "stdout.txt":
            out = sandbox / f.relative_to(fixture_dir)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)


def before_all(context):
    context.mock_mode = os.environ.get("CLAUDE_MOCK", "replay").lower()

    if context.mock_mode in ("record", "real"):
        cli = shutil.which("claude") or shutil.which("claude-code")
        if not cli:
            raise EnvironmentError("Claude CLI not found. Install: npm install -g @anthropic-ai/claude-code")
        context.claude_cmd = [cli, "--dangerously-skip-permissions"]
    else:
        context.claude_cmd = None

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import docx  # noqa: F401
    except ImportError:
        raise ImportError("Run: pip install python-docx")

    print(f"\n✅ Mode:      {context.mock_mode}")
    print(f"✅ Fixtures:  {FIXTURES_DIR}")
    print(f"✅ SKILL.md:  {SKILL_MD_SRC}")


def before_scenario(context, scenario):
    context.scenario_slug = _slug(scenario)
    context.fixture_dir   = FIXTURES_DIR / context.scenario_slug

    context.temp_dir = tempfile.mkdtemp(prefix="cvpolish_bdd_")
    context.work_dir = Path(context.temp_dir)

    # SKILL.md into sandbox
    skill_dir = context.work_dir / ".claude" / "skills" / "cv-polish"
    skill_dir.mkdir(parents=True)
    shutil.copy(SKILL_MD_SRC, skill_dir / "SKILL.md")

    # Input fixture: real CV file
    assets = context.work_dir / "assets"
    assets.mkdir()
    (assets / "archive").mkdir()
    cv_fixture = ASSETS_SRC / "YL-CV-2024.docx"
    if cv_fixture.exists():
        shutil.copy(cv_fixture, assets / "YL-CV-2024.docx")

    # Restore Claude's recorded outputs for replay mode
    context.last_output = ""
    if context.mock_mode == "replay":
        if context.fixture_dir.exists():
            _restore(context.fixture_dir, context.work_dir)
            stdout_f = context.fixture_dir / "stdout.txt"
            context.last_output = stdout_f.read_text() if stdout_f.exists() else ""
            print(f"♻️  Restored: {context.scenario_slug}")
        else:
            print(f"⚠️  No fixture: '{context.scenario_slug}' — run CLAUDE_MOCK=record first")

    subprocess.run(["git", "init"],                                  cwd=context.work_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"],       cwd=context.work_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name",  "Test User"],     cwd=context.work_dir, capture_output=True)

    context.last_stderr     = ""
    context.last_returncode = 0
    context.original_sizes  = {}


def after_scenario(context, scenario):
    if context.mock_mode == "record" and scenario.status != "failed":
        if context.fixture_dir.exists():
            shutil.rmtree(context.fixture_dir)
        _snapshot(context.work_dir, context.fixture_dir)
        (context.fixture_dir / "stdout.txt").write_text(context.last_output)
        print(f"\n💾 Recorded: {context.fixture_dir.name}")

    if scenario.status == "failed":
        print(f"\n❌ Sandbox preserved: {context.temp_dir}")
    else:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


def after_all(context):
    print(f"\n{'='*55}\ncv-polish tests done  [mode: {context.mock_mode}]\n{'='*55}")

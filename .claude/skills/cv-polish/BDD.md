# BDD Tests — cv-polish

Tests live in `tests/features/` and use a **record-replay** pattern.
Fixtures are stored in `tests/fixtures/` (one folder per scenario).

## Run (replay — default)

```bash
cd .claude/skills/cv-polish/tests
behave features/
```

No env var needed. Restores recorded fixtures and asserts instantly — no Claude calls.

## Re-record after SKILL.md changes

```powershell
$env:CLAUDE_MOCK="record"; behave features/
```

Re-runs every scenario against real Claude and overwrites all fixtures.

## Re-record a single scenario

```powershell
$env:CLAUDE_MOCK="record"; behave features/ --name "Output uses strong action verbs"
```

## Modes

| `CLAUDE_MOCK`  | Behaviour                                      |
|----------------|------------------------------------------------|
| `replay` (default) | Restore fixtures, skip Claude — fast & free |
| `record`       | Run real Claude, snapshot outputs as fixtures  |
| `real`         | Run real Claude every time (slow, costs credits) |

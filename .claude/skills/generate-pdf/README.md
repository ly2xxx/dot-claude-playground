# Generate PDF Skill

## Caveats

One caveat worth flagging: `generate-pdf/SKILL.md:5` has `disable-model-invocation: true`. That blocks automatic triggering from user prompts, but explicit invocation via the Skill tool from inside another skill should still work. If you find it doesn't fire when called this way, removing that flag (or leaving it off) is the fix.



## Testing

```bash
/generate-pdf /c/code/DevOps-labs/python-apps/myproject/README.md
```

- Expect output at `output/pdfs/README.pdf`.
- Use the full path from `C:\` or a path relative to `.claude/skills/generate-pdf/`.
- For testing without the full path, create a symlink (Windows `mklink /J`) from inside the skill directory: `mklink /J myproject ..\..\..\code\DevOps-labs\python-apps\myproject`.


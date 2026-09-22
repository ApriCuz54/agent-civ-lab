# Activating the git repository

This folder is a complete, ready-to-share project. `device_bash` was unavailable when it
was created (a Windows update was blocking Claude's local shell), so git wasn't initialized
on your machine automatically. Two one-time options:

## Option A — restore the authored history (recommended)
A full git history (one commit, authored by you with Claude as co-author) ships as
`history.bundle`. From inside this folder:

```bash
git clone history.bundle tmp && mv tmp/.git . && rm -rf tmp
rm history.bundle GIT_SETUP.md        # optional: drop the bootstrap files
git status                            # you're now on a normal repo
```

## Option B — start fresh history
```bash
git init && git add -A && git commit -m "agent-civ-lab: initial commit"
rm history.bundle GIT_SETUP.md        # optional
```

## Then publish (either option)
```bash
git branch -M main
git remote add origin https://github.com/<you>/agent-civ-lab.git
git push -u origin main
```

`history.bundle` is a normal git bundle: `git bundle verify history.bundle` will confirm it.

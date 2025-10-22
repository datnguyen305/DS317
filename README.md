# 🧩 Project Setup & Pre-commit Guide

### 1️⃣ Initial Setup (Run only once after cloning)

Run:

```bash
make setup
```

This command will:

- Install necessary Python libraries (requirements.txt)
- Install and activate pre-commit hooks (including commit convention enforcement)

### 2️⃣ Before committing any changes

Run:

```bash
make check_precommit
```

This command will:

- Check all code formatting (Black, isort)
- Check for linting errors (flake8)

⚠️ **If any files were modified (by Black/format), you need to:**

```bash
git add .
git commit -m "feat: your message..."
```

# Commit Message Convention

### Format

`<type>(optional scope): <description>`
Example: `feat(pre-event): add speakers section`

### 1. Type

Available types are:

- **feat** → Changes about addition or removal of a feature. Ex: `feat: add table on landing page`, `feat: remove table from landing page`
- **fix** → Bug fixing, followed by the bug. Ex: `fix: illustration overflows in mobile view`
- **docs** → Update documentation (README.md)
- **style** → Updating style, and not changing any logic in the code (reorder imports, fix whitespace, remove comments)
- **chore** → Installing new dependencies, or bumping deps
- **refactor** → Changes in code, same output, but different approach
- **ci** → Update github workflows, husky
- **test** → Update testing suite, cypress files
- **revert** → when reverting commits
- **perf** → Fixing something regarding performance (deriving state, using memo, callback)
- **vercel** → Blank commit to trigger vercel deployment. Ex: `vercel: trigger deployment`

### 2. Optional Scope

Labels per page Ex: `feat(pre-event): add date label`

The scope in a commit message specifies which part or module of the project the change affects. It’s optional but useful for clarity — especially in large projects or monorepos.

### 3. Description

**If there are multiple changes, then commit one by one**

- After colon, there are a single space Ex: `feat: add something`
- When using `fix` type, state the issue Ex: `fix: file size limiter not working`
- Use imperative, and present tense: "change" not "changed" or "changes"
- Don't use capitals in front of the sentence
- Don't add full stop (.) at the end of the sentence

### 4. Some git command

```py
# === Branching ===
git branch                      # list all branches
git checkout -b <branch>        # create and switch to new branch
git checkout <branch>           # switch to existing branch
git branch -d <branch>          # delete local branch

# === Staging & Commit ===
git add .                       # stage all changes
git add <file>                  # stage specific file
git commit -m "feat(auth): add login feature"   # commit with message
git commit --amend              # edit last commit
git commit --amend --no-edit     # modify last commit without changing message
git commit --amend -m "new msg"  # modify last commit message

# === Push & Pull ===
git push origin <branch>        # push branch to remote
git pull                        # pull latest changes
git fetch                       # fetch without merging

# === Merge & Rebase ===
git merge <branch>              # merge branch into current
git rebase <branch>             # rebase current branch onto another
git rebase --continue           # continue after conflict fix

# === Check status & history ===
git status                      # show current changes

# === Undo / Reset ===
git reset --soft <commit>        # move HEAD to commit, keep changes staged
git reset --mixed <commit>       # move HEAD, keep changes unstaged
git reset --hard <commit>        # move HEAD and delete all later changes
git revert <commit>              # create a new commit that undoes the given one

# === Stash (save unfinished work) ===
git stash                        # temporarily save current changes
git stash list                   # show all stashes
git stash apply                  # re-apply last stash (keep it in list)
git stash pop                    # apply and remove last stash
git stash drop                   # delete a stash
```

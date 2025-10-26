# 🚀 Git Push Guide - What to Push and What NOT to Push

## ❌ NEVER PUSH THESE (CRITICAL!)

### 🔐 API Keys and Secrets
- ❌ `.env` - Contains your actual API keys
- ❌ `.env.local` - Frontend environment variables
- ❌ Any file with API keys or secrets
- ✅ `.env.example` - Template file (SAFE to push)

**Why?** API keys cost money and can be abused if exposed publicly!

### 🔑 Checking for Exposed Keys

Before pushing, verify:
```bash
# Check if .env is tracked
git status

# If .env appears, DO NOT PUSH!
# Remove it from staging:
git reset HEAD .env
```

---

## ✅ SAFE TO PUSH

### Backend Files
- ✅ `backend/` - All Python source code
  - ✅ `main.py`
  - ✅ `agents/*.py`
  - ✅ `orchestrator/*.py`
  - ✅ `utils/*.py`
  - ✅ `postprocessors/*.py`
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Template (no real keys)

### Frontend Files
- ✅ `frontend/` - All source code
  - ✅ `app/*.tsx`
  - ✅ `components/*.tsx`
  - ✅ `lib/*.ts`
  - ✅ `styles/*.css`
  - ✅ `public/*` - Images, logos
- ✅ `package.json` - Node dependencies
- ✅ `tsconfig.json` - TypeScript config
- ✅ `next.config.mjs` - Next.js config
- ✅ `tailwind.config.ts` - Tailwind config

### Configuration Files
- ✅ `README.md` - Project documentation
- ✅ `PROJECT_STATUS.md` - Status documentation
- ✅ `QUICK_START.md` - Quick reference
- ✅ `.gitignore` - Git ignore rules
- ✅ `rules.json` - Development rules

### Sample Data
- ✅ `data/*.txt` - Sample case files (no real client data)

### Scripts
- ✅ `start_backend.ps1` - Startup script
- ✅ `start_frontend.ps1` - Startup script

---

## ⚠️ OPTIONAL (Your Choice)

### Test Scripts
- ⚠️ `temp/*.py` - Test scripts
  - **Pros**: Helpful for other developers
  - **Cons**: Clutters repository
  - **Recommendation**: Push a few key tests, ignore the rest

### Documentation
- ⚠️ `*_COMPLETE.md` - Completion summaries
  - **Recommendation**: Keep for project history

### Lock Files
- ⚠️ `package-lock.json` / `pnpm-lock.yaml`
  - **Recommendation**: PUSH for consistent dependencies
- ⚠️ Already in repo, keep it

### IDE Settings
- ⚠️ `.windsurf/` - IDE memory
  - **Recommendation**: DON'T PUSH (personal settings)

---

## ❌ NEVER PUSH (Generated/Temporary)

### Build Artifacts
- ❌ `node_modules/` - Node dependencies (huge!)
- ❌ `.next/` - Next.js build output
- ❌ `__pycache__/` - Python cache
- ❌ `*.pyc` - Compiled Python files
- ❌ `build/`, `dist/` - Build outputs

### Logs and Databases
- ❌ `*.log` - Log files
- ❌ `temp/orchestrator_logs.log` - Runtime logs
- ❌ `*.db`, `*.sqlite` - Database files

### OS and IDE Files
- ❌ `.DS_Store` - macOS metadata
- ❌ `Thumbs.db` - Windows thumbnails
- ❌ `.vscode/` - VSCode settings
- ❌ `.idea/` - PyCharm settings

---

## 🔍 Pre-Push Checklist

Before running `git push`, verify:

### 1. Check Status
```bash
git status
```

### 2. Look for Red Flags
❌ If you see any of these, DO NOT PUSH:
- `.env`
- `.env.local`
- `node_modules/`
- `*.log` files
- `.windsurf/`

### 3. Review Changes
```bash
git diff
```

### 4. Check for Secrets
```bash
# Search for potential API keys in staged files
git diff --cached | grep -i "api_key\|secret\|password"
```

### 5. Verify .gitignore is Working
```bash
# These should return nothing:
git ls-files | grep ".env$"
git ls-files | grep "node_modules"
```

---

## 🚨 Emergency: Accidentally Pushed Secrets?

If you accidentally pushed `.env` or API keys:

### 1. Immediately Revoke Keys
- Go to OpenAI/Anthropic dashboard
- Delete the exposed API keys
- Generate new ones

### 2. Remove from Git History
```bash
# Remove file from history (dangerous!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (overwrites remote)
git push origin --force --all
```

### 3. Update Keys
- Add new keys to `.env` (local only)
- Never push `.env` again!

---

## 📋 Recommended Git Workflow

### Initial Setup
```bash
# Check .gitignore is working
cat .gitignore

# Verify .env is ignored
git status | grep ".env"
# Should NOT appear in output
```

### Before Each Commit
```bash
# 1. Check what's being added
git status

# 2. Review changes
git diff

# 3. Add files selectively
git add backend/
git add frontend/
git add README.md
# etc.

# 4. Commit with clear message
git commit -m "feat: Add attorney brief generator"

# 5. Push to remote
git push origin main
```

### Safe Add Commands
```bash
# Add specific directories
git add backend/
git add frontend/app/
git add frontend/components/

# Add specific files
git add README.md
git add requirements.txt
git add package.json

# NEVER do this blindly:
# git add .  # Can accidentally add secrets!
```

---

## 📊 Summary Table

| File/Folder | Push? | Reason |
|-------------|-------|--------|
| `.env` | ❌ NEVER | Contains API keys |
| `.env.example` | ✅ YES | Template only |
| `backend/*.py` | ✅ YES | Source code |
| `frontend/` | ✅ YES | Source code |
| `node_modules/` | ❌ NEVER | Generated, huge |
| `.next/` | ❌ NEVER | Build output |
| `__pycache__/` | ❌ NEVER | Python cache |
| `*.log` | ❌ NEVER | Runtime logs |
| `data/*.txt` | ✅ YES | Sample data |
| `temp/*.py` | ⚠️ OPTIONAL | Test scripts |
| `README.md` | ✅ YES | Documentation |
| `requirements.txt` | ✅ YES | Dependencies |
| `package.json` | ✅ YES | Dependencies |
| `.gitignore` | ✅ YES | Git rules |
| `.windsurf/` | ❌ NEVER | IDE settings |
| `*.pyc` | ❌ NEVER | Compiled Python |

---

## 🎯 Quick Commands

### Check What Will Be Pushed
```bash
git status
git diff --cached
```

### Safe Push
```bash
# Add only source code
git add backend/ frontend/ *.md requirements.txt package.json

# Commit
git commit -m "Your message"

# Push
git push origin main
```

### Verify .env is NOT Tracked
```bash
git ls-files | grep "\.env$"
# Should return nothing
```

---

## ✅ Final Checklist Before Push

- [ ] `.env` is NOT in `git status`
- [ ] `.env.local` is NOT in `git status`
- [ ] No `node_modules/` in `git status`
- [ ] No `*.log` files in `git status`
- [ ] No API keys in code comments
- [ ] `.gitignore` is up to date
- [ ] Only source code and docs being pushed
- [ ] Commit message is clear

---

**Remember**: When in doubt, DON'T PUSH! You can always add files later, but removing secrets from Git history is painful!

🔐 **NEVER PUSH `.env` FILES!** 🔐

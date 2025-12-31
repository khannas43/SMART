# Quick Start: Ubuntu/WSL Terminal Commands
## Auto Identification of Beneficiaries (AI-PLATFORM-03)

This guide provides exact commands to navigate and execute scripts from Ubuntu/WSL terminal.

---

## 🗂️ Folder Paths

### Absolute Paths (Use these directly)

**Main project directory:**
```bash
/mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
```

**Scripts directory:**
```bash
/mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary/scripts
```

**Source code directory:**
```bash
/mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary/src
```

**Config directory:**
```bash
/mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary/config
```

**Python venv:**
```bash
/mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

---

## 🚀 Quick Navigation & Setup

### Step 1: Navigate to Project Directory

**From Desktop (default terminal location):**
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
```

**Or from Home (~):**
```bash
cd ~/../../mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
```

**Or using absolute path:**
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
```

### Step 2: Activate Python Virtual Environment

```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

You should see `(.venv)` in your prompt.

### Step 3: Verify Current Directory

```bash
pwd
# Should show: /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

ls -la scripts/
# Should list all test scripts
```

---

## 📝 Executing Scripts

### Option 1: Navigate to Scripts Directory First

```bash
# Navigate to scripts folder
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary/scripts

# Activate venv (if not already activated)
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Execute scripts
python load_sample_rules.py
python test_train_models.py --scheme-code CHIRANJEEVI
```

### Option 2: Run from Project Root (Recommended)

```bash
# Navigate to project root
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

# Activate venv
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Execute scripts with full path
python scripts/load_sample_rules.py
python scripts/test_train_models.py --scheme-code CHIRANJEEVI
python scripts/test_rule_management.py --scheme-code CHIRANJEEVI --test all
python scripts/test_batch_evaluation.py --test batch-all --limit 50
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 50
```

---

## 🔧 Complete Setup Commands (Copy-Paste Ready)

### One-Time Setup

```bash
# 1. Navigate to project
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

# 2. Activate virtual environment
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# 3. Verify Python path
which python
# Should show: /mnt/c/Projects/SMART/ai-ml/.venv/bin/python

# 4. Verify scripts exist
ls -la scripts/*.py
```

---

## 📋 Step-by-Step Execution

### Step 1: Load Sample Eligibility Rules

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/load_sample_rules.py
```

### Step 2: Check Training Data Availability

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test_train_models.py --check-only
```

### Step 3: Train ML Model for a Scheme

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test_train_models.py --scheme-code CHIRANJEEVI
```

### Step 4: Test Rule Management

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test_rule_management.py --scheme-code CHIRANJEEVI --test all
```

### Step 5: Run Batch Evaluation

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test_batch_evaluation.py --test batch-all --limit 50
```

### Step 6: End-to-End Test

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 50
```

---

## 🔍 Troubleshooting Path Issues

### If "No such file or directory" Error

**Check if path exists:**
```bash
ls -la /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
```

**If path doesn't exist, find your actual project location:**
```bash
find /mnt/c -name "03_identification_beneficiary" -type d 2>/dev/null
```

### If Python Script Not Found

**Make sure you're in the right directory:**
```bash
pwd
# Should be: /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

# List scripts
ls scripts/*.py
```

**Or use absolute path:**
```bash
python /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary/scripts/load_sample_rules.py
```

### If venv Not Activating

**Check if venv exists:**
```bash
ls -la /mnt/c/Projects/SMART/ai-ml/.venv/bin/python
```

**If not found, create it:**
```bash
cd /mnt/c/Projects/SMART/ai-ml
python3 -m venv .venv
source .venv/bin/activate
pip install -r use-cases/03_identification_beneficiary/requirements.txt
```

---

## 📌 Quick Reference: Copy-Paste Commands

### Complete Setup & Execution (All-in-One)

```bash
# Navigate and activate
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && \
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && \
echo "✅ Setup complete. Current directory: $(pwd)" && \
echo "✅ Python: $(which python)"
```

### Load Rules
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && \
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && \
python scripts/load_sample_rules.py
```

### Train Model
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && \
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && \
python scripts/test_train_models.py --scheme-code CHIRANJEEVI
```

### Test Everything
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && \
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && \
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 50
```

---

## 💡 Pro Tips

### Create an Alias (Optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# SMART Project Aliases
alias smart-cd='cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary'
alias smart-venv='source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate'
alias smart-setup='smart-cd && smart-venv'
```

Then reload:
```bash
source ~/.bashrc
```

Now you can simply:
```bash
smart-setup
python scripts/load_sample_rules.py
```

---

## ✅ Verification Checklist

Run these to verify your setup:

```bash
# 1. Check current directory
pwd
# Expected: /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

# 2. Check venv is active
which python
# Expected: /mnt/c/Projects/SMART/ai-ml/.venv/bin/python

# 3. Check scripts exist
ls scripts/*.py | head -5
# Expected: Should list load_sample_rules.py, test_*.py files

# 4. Check Python can import modules
python -c "import sys; sys.path.append('src'); from rule_manager import RuleManager; print('✅ Imports OK')"
```

---

**🎉 You're all set! Use the exact paths above to execute any script.**


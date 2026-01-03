# Running Data Processing Scripts

**Purpose:** Instructions for running combine, validate, and split scripts  
**Environment:** WSL2 (Ubuntu 24.04)  
**Python:** `/mnt/c/Projects/SMART/ai-ml/.venv/bin/python`

---

## Option 1: Using WSL2 Terminal (Recommended)

### Step 1: Open WSL2 Terminal

1. **Open Ubuntu terminal** (WSL2)
   - Press `Windows Key` → Type "Ubuntu" → Open
   - Or use Cursor's integrated WSL terminal

### Step 2: Navigate to Project Directory

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
```

### Step 3: Activate Virtual Environment

```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

### Step 4: Run Scripts

```bash
# Combine all batches
python scripts/combine_batches.py

# Validate the data
python scripts/validate_training_data.py

# Create train/val/test splits
python scripts/split_training_data.py
```

---

## Option 2: Using WSL from Windows PowerShell

If you prefer to stay in PowerShell, use `wsl` command:

```powershell
# Navigate to project (Windows path)
cd C:\Projects\SMART\ai-ml\use-cases\03_identification_beneficiary

# Run scripts via WSL
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/combine_batches.py"

wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/validate_training_data.py"

wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/split_training_data.py"
```

---

## Option 3: Create Batch Script (Windows)

Create a file `run_data_processing.bat`:

```batch
@echo off
echo Running data processing scripts...
echo.

echo [1/3] Combining batches...
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/combine_batches.py"

echo.
echo [2/3] Validating data...
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/validate_training_data.py"

echo.
echo [3/3] Creating train/val/test splits...
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/split_training_data.py"

echo.
echo Done!
pause
```

Then run:
```powershell
.\run_data_processing.bat
```

---

## Quick Commands (Copy-Paste)

### In WSL Terminal:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/combine_batches.py
python scripts/validate_training_data.py
python scripts/split_training_data.py
```

### In Windows PowerShell:

```powershell
cd C:\Projects\SMART\ai-ml\use-cases\03_identification_beneficiary
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary && source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate && python scripts/combine_batches.py && python scripts/validate_training_data.py && python scripts/split_training_data.py"
```

---

## Expected Output

### combine_batches.py
```
Loading batch_01_pension.json...
  ✓ Added 25 schemes
Loading batch_02_health.json...
  ✓ Added 25 schemes
...
✓ Combined 500 schemes into data/training/schemes_raw.json
```

### validate_training_data.py
```
Validation Results:
Total schemes: 500
Valid: 500
Invalid: 0

✓ All schemes are valid!
```

### split_training_data.py
```
✓ Split complete:
  Train: 350 schemes (70.0%)
  Val: 75 schemes (15.0%)
  Test: 75 schemes (15.0%)
```

---

## Troubleshooting

### Issue: "No batch files found"

**Solution:** Check that batch files are in the correct location:
```bash
ls data/training/batches/batch_*.json
```

### Issue: "Python was not found"

**Solution:** Use WSL2 terminal or use full path:
```bash
/mnt/c/Projects/SMART/ai-ml/.venv/bin/python scripts/combine_batches.py
```

### Issue: "Module not found"

**Solution:** Activate venv first:
```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

---

**Last Updated:** 2024-12-30


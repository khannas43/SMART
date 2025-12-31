# Quick Start Guide - Golden Record Notebook

## You're in JupyterLab! Here's what to do:

### Step 1: Navigate to the Notebook

**In the left sidebar (file browser):**
1. Click the **folder icon** (first icon in the left sidebar)
2. Navigate through folders:
   - `use-cases/`
   - `golden_record/`
   - `notebooks/`
   - Double-click `01_data_exploration.ipynb`

### Step 2: Open the Notebook

The notebook will open in a new tab. You'll see cells with code and markdown.

### Step 3: Run the Notebook

1. **Select the first code cell** (usually has `# Import libraries`)
2. Press **`Shift + Enter`** to run the cell
3. Continue running cells one by one with **`Shift + Enter`**
   - Or use **`Ctrl + Enter`** to run without advancing to next cell

### Alternative: Open from Launcher

1. Click **"Python 3"** button in the Launcher tab
2. This opens a new notebook
3. You'll need to manually navigate or copy code from `01_data_exploration.ipynb`

### Keyboard Shortcuts

- **`Shift + Enter`**: Run cell and move to next
- **`Ctrl + Enter`**: Run cell (stay in same cell)
- **`A`**: Insert cell above
- **`B`**: Insert cell below
- **`M`**: Convert to markdown cell
- **`Y`**: Convert to code cell
- **`D D`**: Delete cell (press D twice)

### Tips

- The notebook will connect to your PostgreSQL database (`smart_warehouse`)
- Make sure MLflow is running on `http://127.0.0.1:5000`
- The notebook will log results to MLflow experiment `smart/golden_record/baseline_v1`

## Troubleshooting

**If cells don't run:**
- Check that the kernel is selected (top right shows "Python 3")
- If not, go to **Kernel** → **Change Kernel** → Select Python 3

**If imports fail:**
- Make sure you're using the correct Python kernel (the one from `.venv`)
- Check Kernel → Change Kernel → Python 3 (should show venv path)

**If database connection fails:**
- Verify PostgreSQL is running and accessible at `172.17.16.1:5432`
- Check database `smart_warehouse` exists and has data

Ready to explore your data! 🚀


# Frontend Installation Instructions

## PowerShell Execution Policy Issue

If you encounter the error:
```
npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled on this system
```

## Solutions (Choose One)

### Option 1: Use Command Prompt (CMD) - Recommended

**Simplest solution** - Use CMD instead of PowerShell:

1. Open Command Prompt (cmd.exe)
2. Navigate to the frontend directory:
   ```cmd
   cd C:\Projects\SMART\portals\citizen\frontend
   ```
3. Run npm install:
   ```cmd
   npm install
   ```

### Option 2: Change PowerShell Execution Policy (Requires Admin)

If you want to use PowerShell, you need to change the execution policy:

1. Open PowerShell as Administrator (Right-click → Run as Administrator)
2. Run this command:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Type `Y` when prompted
4. Close and reopen PowerShell
5. Navigate to frontend directory and run `npm install`

**Note**: This changes the policy for your current user only, which is safe.

### Option 3: Bypass Policy for Single Command

Run npm with bypass flag (works but less convenient):
```powershell
powershell -ExecutionPolicy Bypass -Command "npm install"
```

---

## Normal Installation Steps

Once you can run npm:

```bash
# 1. Install dependencies
npm install

# 2. Create environment file (optional - defaults work)
# Copy .env.example to .env if you want to customize API URL

# 3. Start development server
npm run dev
```

The application will be available at: `http://localhost:3001`

---

## Troubleshooting

### If npm install fails with network errors:
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

### If you get permission errors:
- Make sure you're not running from a restricted directory
- Try running as Administrator (if needed)

### If dependencies conflict:
```bash
# Delete node_modules and package-lock.json
rm -r node_modules package-lock.json

# Reinstall
npm install
```

---

**Recommended**: Use Option 1 (CMD) - it's the simplest and doesn't require admin rights!


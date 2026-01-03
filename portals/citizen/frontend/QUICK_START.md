# Quick Start Guide - Citizen Portal Frontend

## Installation & Setup

### 1. Install Dependencies

**Using Command Prompt (Recommended)**:
```cmd
cd C:\Projects\SMART\portals\citizen\frontend
npm install
```

**Using PowerShell (if execution policy allows)**:
```powershell
cd C:\Projects\SMART\portals\citizen\frontend
npm install
```

If you get execution policy error, use Command Prompt (cmd.exe) instead.

### 2. Start Development Server

```bash
npm run dev
```

### 3. Access the Application

Open your browser and go to:
```
http://localhost:3000/citizen
```

## Configuration

- **Port**: 3000
- **Base Path**: `/citizen`
- **API Proxy**: `/citizen/api/*` → `http://localhost:8080/citizen/api/v1/*`

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Troubleshooting

### Port 3000 Already in Use

If port 3000 is already in use (e.g., by Nginx), you can:
1. Stop Nginx: `sudo service nginx stop` (in WSL)
2. Or use a different port (update `vite.config.ts`)

### Assets Not Loading

- Ensure you're accessing via `/citizen` path (not root)
- Check browser console for errors
- Verify base path in `vite.config.ts` is `/citizen/`

### API Calls Failing

- Verify backend is running on port 8080
- Check proxy configuration in `vite.config.ts`
- Ensure backend context path is `/citizen/api/v1`

## Next Steps

1. ✅ Install dependencies (`npm install`)
2. ✅ Start dev server (`npm run dev`)
3. ⏳ Start backend service (port 8080)
4. ⏳ Test login flow

For detailed information, see:
- `README.md` - Full documentation
- `NGINX_INTEGRATION.md` - Nginx setup details
- `INSTALL_INSTRUCTIONS.md` - Installation troubleshooting


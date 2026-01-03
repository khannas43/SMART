# Frontend - Nginx Integration Guide

## Configuration Summary

The Citizen Portal frontend is configured to work with Nginx reverse proxy:

- **Base Path**: `/citizen`
- **Development Server Port**: `3000`
- **Production**: Served via Nginx on port 3000

## URLs

- **Development**: `http://localhost:3000/citizen`
- **Production**: `http://localhost:3000/citizen`

## Configuration Details

### Vite Configuration (`vite.config.ts`)

```typescript
base: '/citizen/',
server: {
  port: 3000,
  strictPort: true,
  proxy: {
    '/citizen/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
    },
  },
},
build: {
  base: '/citizen/',
  // ...
}
```

### React Router Configuration (`src/main.tsx`)

```typescript
<BrowserRouter basename="/citizen">
  <App />
</BrowserRouter>
```

## Development Setup

### Option 1: Direct Vite Dev Server (Recommended for Development)

1. Start the frontend dev server:
   ```bash
   cd portals/citizen/frontend
   npm install
   npm run dev
   ```

2. Access at: `http://localhost:3000/citizen`

3. Vite will handle:
   - Serving frontend assets at `/citizen`
   - Proxying API calls from `/citizen/api/*` to backend at `http://localhost:8080`

### Option 2: Via Nginx (Production-like Setup)

1. Build the frontend:
   ```bash
   npm run build
   ```

2. Copy `dist` folder to a location accessible by Nginx (e.g., `/var/www/citizen-portal/`)

3. Update Nginx config to serve static files:
   ```nginx
   location /citizen {
       alias /var/www/citizen-portal;
       try_files $uri $uri/ /citizen/index.html;
       
       # Cache static assets
       location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   
   location /citizen/api {
       proxy_pass http://citizen_backend;
       # ... proxy headers ...
   }
   ```

## Important Notes

1. **Base Path**: All routes in the React app are relative to `/citizen`
   - `/citizen/login` (not just `/login`)
   - `/citizen/dashboard` (not just `/dashboard`)

2. **API Proxy**: In development, Vite proxies `/citizen/api/*` to `http://localhost:8080/citizen/api/v1/*`

3. **Build Output**: The build output uses base path `/citizen/`, so all asset paths in the built HTML will be prefixed with `/citizen/`

4. **React Router**: Using `basename="/citizen"` ensures all navigation works correctly with the base path

## Troubleshooting

### Assets Not Loading (404 errors)

- Ensure Vite `base` config is set to `/citizen/`
- Check that build output has correct base path
- Verify Nginx is serving from correct directory

### Routes Not Working (404 on navigation)

- Ensure React Router has `basename="/citizen"`
- Check that all route definitions start with `/citizen/` or are relative

### API Calls Failing

- Verify proxy configuration in `vite.config.ts`
- Check backend is running on port 8080
- Ensure backend context path is `/citizen/api/v1`

## Testing

1. **Development**:
   ```bash
   npm run dev
   # Visit http://localhost:3000/citizen
   ```

2. **Production Build**:
   ```bash
   npm run build
   # Serve dist folder via Nginx
   # Visit http://localhost:3000/citizen
   ```


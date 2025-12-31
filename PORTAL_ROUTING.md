# SMART Platform - Portal Routing Configuration

## Overview

All SMART Platform portals are accessible through a single port (default: **3000**) with path-based routing. This provides a unified entry point while maintaining independent backend services.

## Portal URLs

All portals are accessible via the same port with different path prefixes:

- **Citizen Portal**: `http://localhost:3000/citizen`
- **Departmental Portal**: `http://localhost:3000/dept`
- **AI/ML Insight Portal**: `http://localhost:3000/insight`
- **Administration & Monitoring Portal**: `http://localhost:3000/monitor`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser)                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ http://localhost:3000/{portal}/*
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Nginx Reverse Proxy (Port 3000)                 │
│                                                              │
│  /citizen  → upstream citizen_backend (localhost:8080)      │
│  /dept     → upstream dept_backend (localhost:8081)         │
│  /insight  → upstream aiml_backend (localhost:8082)         │
│  /monitor  → upstream monitor_backend (localhost:8083)      │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌─────▼──────┐
│ Citizen      │   │  Dept Service   │   │ AIML       │
│ Service      │   │  (Port 8081)    │   │ Service    │
│ (Port 8080)  │   │                 │   │ (Port 8082)│
│              │   │                 │   │            │
│ context-path:│   │ context-path:   │   │ context-   │
│ /citizen/    │   │ /dept/api/v1    │   │ path:      │
│ api/v1       │   │                 │   │ /insight/  │
└──────────────┘   └─────────────────┘   │ api/v1     │
                                         └────────────┘
```

## Backend Service Configuration

Each portal's backend service runs on its own port with a context path that includes the portal prefix:

| Portal | Backend Port | Context Path | Full URL Path |
|--------|--------------|--------------|---------------|
| Citizen | 8080 | `/citizen/api/v1` | `http://localhost:3000/citizen/api/v1/*` |
| Departmental | 8081 | `/dept/api/v1` | `http://localhost:3000/dept/api/v1/*` |
| AI/ML Insight | 8082 | `/insight/api/v1` | `http://localhost:3000/insight/api/v1/*` |
| Monitor | 8083 | `/monitor/api/v1` | `http://localhost:3000/monitor/api/v1/*` |

## Setup Instructions

### 1. Install Nginx

**Windows (using Chocolatey):**
```powershell
choco install nginx
```

**Linux/Ubuntu:**
```bash
sudo apt update
sudo apt install nginx
```

**macOS:**
```bash
brew install nginx
```

### 2. Configure Nginx

Copy the `nginx.conf` file from the project root to your Nginx configuration directory:

**Linux/macOS:**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/smart-platform
sudo ln -s /etc/nginx/sites-available/smart-platform /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

**Windows:**
```powershell
# Copy nginx.conf to: C:\nginx\conf\nginx.conf
# Or create: C:\nginx\conf\conf.d\smart-platform.conf
# Then restart Nginx service
```

### 3. Start Backend Services

Start each portal's backend service on its configured port:

```bash
# Terminal 1 - Citizen Portal
cd portals/citizen/backend/services/citizen-service
mvn spring-boot:run  # Runs on port 8080

# Terminal 2 - Departmental Portal
cd portals/dept/backend/services/dept-service
mvn spring-boot:run  # Runs on port 8081

# Terminal 3 - AI/ML Insight Portal
cd portals/aiml/backend/services/aiml-service
mvn spring-boot:run  # Runs on port 8082

# Terminal 4 - Monitor Portal
cd portals/monitor/backend/services/monitor-service
mvn spring-boot:run  # Runs on port 8083
```

### 4. Start Nginx

**Linux:**
```bash
sudo systemctl start nginx
# or
sudo service nginx start
```

**Windows:**
```powershell
# Start Nginx service from Services or run:
C:\nginx\nginx.exe
```

**macOS:**
```bash
sudo nginx
```

### 5. Verify Setup

Test each portal endpoint:

```bash
# Citizen Portal Health Check
curl http://localhost:3000/citizen/api/v1/actuator/health

# Departmental Portal Health Check
curl http://localhost:3000/dept/api/v1/actuator/health

# AI/ML Insight Portal Health Check
curl http://localhost:3000/insight/api/v1/actuator/health

# Monitor Portal Health Check
curl http://localhost:3000/monitor/api/v1/actuator/health
```

## Changing the Port

To use a different port (e.g., 8080 instead of 3000):

1. Update `nginx.conf`:
   ```nginx
   server {
       listen 8080;  # Change from 3000 to 8080
       ...
   }
   ```

2. Update this documentation with the new port number

3. Reload Nginx:
   ```bash
   sudo nginx -s reload  # Linux/macOS
   # or restart Nginx service on Windows
   ```

## Frontend Configuration

When configuring React frontends, set the base path in the build configuration:

### React Router (v6)
```typescript
import { BrowserRouter } from 'react-router-dom';

<BrowserRouter basename="/citizen">
  {/* Routes */}
</BrowserRouter>
```

### Vite Configuration
```javascript
// vite.config.js
export default {
  base: '/citizen/',
  // ...
}
```

### Create React App
```json
// package.json
{
  "homepage": "/citizen"
}
```

### API Base URL
```typescript
// Frontend API service configuration
const API_BASE_URL = '/citizen/api/v1';  // Relative path works with proxy
// or
const API_BASE_URL = 'http://localhost:3000/citizen/api/v1';
```

## Development Workflow

### Option 1: Direct Backend Access (Development)

For development, you can access backends directly without Nginx:

- Citizen: `http://localhost:8080/citizen/api/v1`
- Dept: `http://localhost:8081/dept/api/v1`
- AIML: `http://localhost:8082/insight/api/v1`
- Monitor: `http://localhost:8083/monitor/api/v1`

### Option 2: Through Nginx (Production-like)

Access through Nginx for production-like testing:

- Citizen: `http://localhost:3000/citizen/api/v1`
- Dept: `http://localhost:3000/dept/api/v1`
- AIML: `http://localhost:3000/insight/api/v1`
- Monitor: `http://localhost:3000/monitor/api/v1`

## CORS Configuration

If frontends are served from different origins, configure CORS in Spring Boot:

```java
@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                    .allowedOrigins("http://localhost:3000")
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                    .allowedHeaders("*")
                    .allowCredentials(true);
            }
        };
    }
}
```

## Docker Deployment

For Docker deployment, update `docker-compose.yml`:

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - citizen-service
      - dept-service
      - aiml-service
      - monitor-service

  citizen-service:
    build: ./portals/citizen/backend/services/citizen-service
    ports:
      - "8080:8080"
    # ... other config

  # ... other services
```

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:
1. Change the port in `nginx.conf`
2. Or stop the service using port 3000

### Backend Service Not Accessible

1. Verify backend service is running: `curl http://localhost:8080/citizen/api/v1/actuator/health`
2. Check Nginx error logs: `tail -f /var/log/nginx/error.log`
3. Verify Nginx configuration: `nginx -t`

### 404 Errors

1. Ensure context-path matches in both Spring Boot config and Nginx routing
2. Check that backend service is running on correct port
3. Verify Nginx upstream configuration points to correct backend port

### CORS Issues

1. Configure CORS in Spring Boot applications
2. Ensure Nginx passes correct headers: `X-Forwarded-Proto`, `X-Forwarded-Host`

## Security Considerations

1. **Production**: Use HTTPS and configure SSL certificates in Nginx
2. **Authentication**: Implement authentication at API Gateway level or in each service
3. **Rate Limiting**: Configure rate limiting in Nginx for DDoS protection
4. **Headers**: Add security headers (X-Frame-Options, X-Content-Type-Options, etc.)

## Next Steps

- [ ] Configure frontend applications with base paths
- [ ] Set up SSL/HTTPS for production
- [ ] Configure authentication at gateway level
- [ ] Add rate limiting and security headers
- [ ] Set up monitoring and logging


# Quick Start Guide - Citizen Service

## Prerequisites Check

Before running, ensure:
- ✅ Java 17+ is installed (`java -version`)
- ✅ Maven is installed (`mvn -version`)
- ✅ PostgreSQL is running
- ✅ Database `smart_citizen` exists

## Quick Start (3 Steps)

### 1. Navigate to Service Directory
```bash
cd portals/citizen/backend/services/citizen-service
```

### 2. Build and Run
```bash
mvn clean spring-boot:run
```

This will:
- Clean previous builds
- Compile the project
- Run Flyway migrations (first time only)
- Start the Spring Boot service

### 3. Access Swagger UI
Open your browser and navigate to:
```
http://localhost:8080/citizen/api/v1/swagger-ui.html
```

## What to Expect

### First Run
- Flyway will create all database tables
- Service will start on port 8080
- Swagger UI will be available

### Console Output
You should see:
```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.0)

...
Flyway Migrations Applied
...
Started CitizenServiceApplication in X.XXX seconds
```

## Verify It's Working

### 1. Health Check
```bash
curl http://localhost:8080/citizen/api/v1/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "UP",
    "service": "Citizen Service"
  }
}
```

### 2. Swagger UI
Open in browser:
```
http://localhost:8080/citizen/api/v1/swagger-ui.html
```

You should see:
- All 8 controller groups (Citizens, Schemes, Applications, etc.)
- All 53 endpoints listed
- "Try it out" buttons for each endpoint

## Common Issues

### Issue: Port 8080 already in use
**Solution:** Change port in `application.yml`:
```yaml
server:
  port: 8081
```

### Issue: Database connection failed
**Solution:** 
1. Verify PostgreSQL is running
2. Check database exists: `CREATE DATABASE smart_citizen;`
3. Verify credentials in `application.yml`

### Issue: Flyway migration failed
**Solution:**
1. Check database exists
2. Ensure UUID extension is available: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
3. Check migration files are in correct location

## Testing Endpoints

Once Swagger UI is open:
1. Expand any controller (e.g., "Citizens")
2. Click on an endpoint (e.g., "GET /citizens")
3. Click "Try it out"
4. Fill in parameters (if any)
5. Click "Execute"
6. View response

## Next Steps

After service is running:
- Test endpoints via Swagger UI
- Integrate with frontend
- Add authentication tokens (when auth-service is ready)


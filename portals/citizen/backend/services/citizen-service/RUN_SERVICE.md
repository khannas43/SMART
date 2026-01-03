# How to Run Citizen Service

## Prerequisites

1. **Java 17+** installed and configured
2. **Maven** installed (or use Maven wrapper)
3. **PostgreSQL** running with `smart_citizen` database created
4. **Database credentials** configured in `application.yml`

## Step 1: Verify Database Setup

Ensure PostgreSQL is running and the database exists:

```sql
-- Connect to PostgreSQL and create database if not exists
CREATE DATABASE smart_citizen;
```

Verify database connection details in:
- `portals/citizen/config/application.yml`

## Step 2: Build the Project

Navigate to the service directory and build:

```bash
cd portals/citizen/backend/services/citizen-service
mvn clean install
```

Or if using Maven wrapper:
```bash
./mvnw clean install
```

## Step 3: Run the Service

### Option 1: Using Maven
```bash
mvn spring-boot:run
```

### Option 2: Using Maven Wrapper
```bash
./mvnw spring-boot:run
```

### Option 3: Using Java directly (after building)
```bash
java -jar target/citizen-service-1.0.0-SNAPSHOT.jar
```

## Step 4: Verify Service is Running

Check the console output for:
```
Started CitizenServiceApplication in X.XXX seconds
```

## Step 5: Access API Documentation

Once the service is running, access Swagger UI at:

**Swagger UI (Interactive):**
```
http://localhost:8080/citizen/api/v1/swagger-ui.html
```

**OpenAPI JSON Specification:**
```
http://localhost:8080/citizen/api/v1/api-docs
```

**Health Check:**
```
http://localhost:8080/citizen/api/v1/health
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready` or check service status
- Verify database `smart_citizen` exists
- Check credentials in `application.yml`
- Verify port 5432 is accessible

### Port Already in Use
- Change port in `application.yml`: `server.port: 8081`
- Or stop the process using port 8080

### Flyway Migration Errors
- Ensure database is empty or baseline is set
- Check migration files are in `src/main/resources/db/migration/`
- Verify PostgreSQL UUID extension is available

### Build Errors
- Ensure Java 17+ is installed: `java -version`
- Ensure Maven is installed: `mvn -version`
- Clean and rebuild: `mvn clean install -U`

## Quick Start Commands

```bash
# Navigate to service directory
cd portals/citizen/backend/services/citizen-service

# Build project
mvn clean install

# Run service
mvn spring-boot:run
```

## Expected Output

When service starts successfully, you should see:
- Spring Boot banner
- Database connection logs
- Flyway migration logs (if first run)
- "Started CitizenServiceApplication" message
- Server running on port 8080

## Next Steps

After service is running:
1. Open Swagger UI in browser
2. Test endpoints using "Try it out" feature
3. Verify health endpoint returns status
4. Check Flyway migrations were applied


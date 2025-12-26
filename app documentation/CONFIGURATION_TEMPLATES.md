# SMART Platform - Configuration Templates Reference

This document provides a quick reference for all Spring Boot configuration templates created for the SMART Platform.

## Portal-Level Configuration Files

Configuration files are located in `portals/{portal}/config/` directory.

### Portal Configurations Created

1. **Citizen Portal** (`portals/citizen/config/`)
   - `application.yml` - Base configuration
   - `application-dev.yml` - Development environment
   - `application-prod.yml` - Production environment

2. **Department Portal** (`portals/dept/config/`)
   - `application.yml` - Base configuration
   - `application-dev.yml` - Development environment

3. **AI/ML Portal** (`portals/aiml/config/`)
   - `application.yml` - Base configuration (includes MLflow config)
   - `application-dev.yml` - Development environment

4. **Monitor Portal** (`portals/monitor/config/`)
   - `application.yml` - Base configuration
   - `application-dev.yml` - Development environment

## Service-Level Configuration Files

Service-specific configurations are located in `portals/{portal}/backend/services/{service}/src/main/resources/application.yml`.

### Service Configurations Created

1. **Citizen Service** (`portals/citizen/backend/services/citizen-service/src/main/resources/application.yml`)
2. **Auth Service** (`portals/citizen/backend/services/auth-service/src/main/resources/application.yml`)
3. **AIML Service** (`portals/aiml/backend/services/aiml-service/src/main/resources/application.yml`)

## Database Configuration

All configurations use the same database connection:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/smart
    username: sameer
    password: anjali143
    driver-class-name: org.postgresql.Driver
```

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `smart`
- Username: `sameer`
- Password: `anjali143`

## Server Ports

Each portal/service uses different ports to avoid conflicts:

- **Citizen Portal**: `8080`
- **Department Portal**: `8081`
- **AI/ML Portal**: `8082`
- **Monitor Portal**: `8083`
- **Auth Service**: `8090`

## MLflow Configuration

AI/ML Portal includes MLflow configuration:

```yaml
mlflow:
  tracking:
    uri: http://127.0.0.1:5000
```

## Environment-Specific Settings

### Development (`application-dev.yml`)
- Hibernate DDL auto: `update`
- SQL logging: Enabled
- CORS: Configured for localhost development
- Debug logging: Enabled

### Production (`application-prod.yml`)
- Environment variables for sensitive data
- Hibernate DDL auto: `validate`
- SQL logging: Disabled
- File logging: Enabled
- Security: JWT secret configuration

## Using Configuration Files

### Option 1: Copy to Service Resources
Copy portal-level configs to service resources directory:

```bash
# Example for citizen-service
cp portals/citizen/config/application*.yml portals/citizen/backend/services/citizen-service/src/main/resources/
```

### Option 2: Reference Portal Config
Services can reference portal-level configs using Spring's config import:

```yaml
spring:
  config:
    import: optional:file:../../../../config/application.yml
```

### Option 3: Use Spring Profiles
Activate profiles using environment variables or command line:

```bash
# Activate dev profile
export SPRING_PROFILES_ACTIVE=dev

# Or when running
java -jar app.jar --spring.profiles.active=dev
```

## Customization

### Override Database for Specific Service
Edit service's `application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/custom_db
    username: custom_user
    password: custom_password
```

### Add Environment Variables
Use environment variables in production:

```yaml
spring:
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/smart}
    username: ${DB_USERNAME:sameer}
    password: ${DB_PASSWORD:anjali143}
```

Set environment variables:
```bash
export DB_URL=jdbc:postgresql://localhost:5432/smart
export DB_USERNAME=sameer
export DB_PASSWORD=anjali143
```

## Testing Configurations

Test database connection:
```bash
cd /mnt/c/Projects/SMART
python scripts/test-database-connection.py
```

Test MLflow connection:
```bash
cd /mnt/c/Projects/SMART
python scripts/test-mlflow-connection.py
```

## Notes

- All configurations include Flyway for database migrations
- HikariCP connection pooling is configured
- Health check endpoints are enabled for monitoring
- CORS is configured for development environments
- Logging is configured for different environments

## Related Documentation

- [Development Configuration](DEVELOPMENT_CONFIG.md) - Detailed configuration reference
- [Installation Guide](INSTALLATION.md) - Installation instructions
- [Test Scripts](../scripts/README.md) - Connection test scripts


# SMART Platform - Deployment Guide

## Overview

### Development/Testing Setup

For development and testing, all portals are accessible via a **single port (3000)** with path-based routing using Nginx reverse proxy:

- **Citizen Portal**: `http://localhost:3000/citizen`
- **Departmental Portal**: `http://localhost:3000/dept`
- **AI/ML Insight Portal**: `http://localhost:3000/insight`
- **Administration & Monitoring Portal**: `http://localhost:3000/monitor`

See [Portal Routing Configuration](PORTAL_ROUTING.md) for detailed setup.

### Production Deployment

Each portal in the SMART platform is **completely self-contained** and can be deployed independently to different network locations within Rajasthan State Government Data Centers. Each portal folder contains everything needed for deployment: frontend, backend services, database, configuration, and deployment scripts.

## Deployment Architecture

### 1. Citizen Portal Deployment

**Target Network**: Public-facing network  
**Location**: `portals/citizen/`

**Components**:
- Frontend: `portals/citizen/frontend/`
- Backend Services:
  - `citizen-service`
  - `auth-service`
  - `notification-service`
  - `file-service`
- Database: PostgreSQL (schema in `portals/citizen/database/`)
- Configuration: `portals/citizen/config/`
- i18n: `portals/citizen/i18n/` (English, Hindi, Rajasthani)

**Deployment Steps**:
1. Build React frontend:
   ```bash
   cd portals/citizen/frontend
   npm install
   npm run build
   ```

2. Build Spring Boot services:
   ```bash
   cd portals/citizen/backend/services/citizen-service
   mvn clean package
   # Repeat for other services
   ```

3. Run database migrations:
   ```bash
   cd portals/citizen/database
   # Run migrations from migrations/ folder
   ```

4. Deploy using Docker:
   ```bash
   cd portals/citizen
   docker-compose -f docker/docker-compose.yml up -d
   ```

5. Or deploy using Kubernetes:
   ```bash
   kubectl apply -f portals/citizen/k8s/
   ```

### 2. Departmental User Portal Deployment

**Target Network**: Internal government network  
**Location**: `portals/dept/`

**Components**:
- Frontend: `portals/dept/frontend/`
- Backend Services:
  - `dept-service`
  - `auth-service`
  - `user-service`
  - `notification-service`
  - `file-service`
- Database: PostgreSQL (schema in `portals/dept/database/`)
- Configuration: `portals/dept/config/`
- i18n: `portals/dept/i18n/` (English, Hindi, Rajasthani)

**Deployment Steps**:
1. Build React frontend:
   ```bash
   cd portals/dept/frontend
   npm install
   npm run build
   ```

2. Build Spring Boot services:
   ```bash
   cd portals/dept/backend/services/dept-service
   mvn clean package
   # Repeat for other services
   ```

3. Run database migrations:
   ```bash
   cd portals/dept/database
   # Run migrations from migrations/ folder
   ```

4. Deploy using Docker or Kubernetes (same as citizen portal)

### 3. AI/ML Insight Portal Deployment

**Target Network**: Analytics network (may require higher security)  
**Location**: `portals/aiml/`

**Components**:
- Frontend: `portals/aiml/frontend/`
- Backend Services:
  - `aiml-service`
  - `auth-service`
- Database: PostgreSQL (schema in `portals/aiml/database/`)
- Configuration: `portals/aiml/config/`
- AI/ML Models: From root `ai-ml/models/`

**Deployment Steps**:
1. Build React frontend:
   ```bash
   cd portals/aiml/frontend
   npm install
   npm run build
   ```

2. Build Spring Boot services:
   ```bash
   cd portals/aiml/backend/services/aiml-service
   mvn clean package
   ```

3. Deploy ML models (from root `ai-ml/` directory)

4. Run database migrations:
   ```bash
   cd portals/aiml/database
   # Run migrations from migrations/ folder
   ```

5. Deploy using Docker or Kubernetes

### 4. Administration and Monitoring Portal Deployment

**Target Network**: Admin network (highest security)  
**Location**: `portals/monitor/`

**Components**:
- Frontend: `portals/monitor/frontend/`
- Backend Services:
  - `monitor-service`
  - `auth-service`
- Database: PostgreSQL (schema in `portals/monitor/database/`)
- Configuration: `portals/monitor/config/`

**Deployment Steps**:
1. Build React frontend:
   ```bash
   cd portals/monitor/frontend
   npm install
   npm run build
   ```

2. Build Spring Boot services:
   ```bash
   cd portals/monitor/backend/services/monitor-service
   mvn clean package
   ```

3. Run database migrations:
   ```bash
   cd portals/monitor/database
   # Run migrations from migrations/ folder
   ```

4. Deploy using Docker or Kubernetes

## Docker Deployment

Each portal has its own Docker configuration:

### Example: Deploy Citizen Portal with Docker

```bash
cd portals/citizen
docker-compose -f docker/docker-compose.yml up -d
```

The `docker-compose.yml` file in each portal includes:
- Frontend container
- All backend service containers
- Database container
- Nginx container (for serving frontend)

## Kubernetes Deployment

Each portal has its own Kubernetes manifests:

### Example: Deploy Citizen Portal with Kubernetes

```bash
kubectl apply -f portals/citizen/k8s/
```

The `k8s/` folder in each portal includes:
- Deployment manifests for all services
- Service manifests
- ConfigMaps
- Secrets
- Ingress configuration

## Environment Configuration

Each portal has environment-specific configuration in `portals/{portal}/config/`:
- `application.yml` - Base configuration
- `application-dev.yml` - Development environment
- `application-staging.yml` - Staging environment
- `application-prod.yml` - Production environment

## Database Strategy

### Separate Databases Per Portal

Each portal has its own PostgreSQL database:
- **Citizen Portal**: `smart_citizen` database
- **Dept Portal**: `smart_dept` database
- **AIML Portal**: `smart_aiml` database
- **Monitor Portal**: `smart_monitor` database

### Database Migrations

Each portal manages its own database migrations:
- Migrations located in `portals/{portal}/database/migrations/`
- Use Flyway or Liquibase for migration management
- Run migrations as part of deployment process

## Network Considerations

- **Citizen Portal**: Accessible from public internet
- **Dept Portal**: Internal government network only
- **AIML Portal**: Restricted network, may require VPN
- **Monitor Portal**: Admin network, highest security

## Security

- Each portal should have its own SSL certificates
- Database connections should use encrypted connections
- Services should communicate over secure channels
- Authentication handled by `auth-service` in each portal

## Monitoring

- Each portal has health check endpoints
- Monitor portal can aggregate metrics from all portals
- Log aggregation per portal (can be centralized if needed)

## Backup and Recovery

- Database backups per portal
- Configuration backups per portal
- Disaster recovery plans per portal
- Each portal can be restored independently

## Deployment Scripts

Each portal includes deployment scripts in `portals/{portal}/scripts/deploy/`:
- `deploy.sh` - Main deployment script
- `build.sh` - Build script
- `migrate.sh` - Database migration script

## Benefits of Self-Contained Structure

1. **Complete Independence**: Each portal can be deployed without dependencies on other portals
2. **Network Isolation**: Portals can be deployed to different networks easily
3. **Independent Scaling**: Each portal can scale independently
4. **Easy Maintenance**: All portal-related code and config in one place
5. **Clear Ownership**: Clear separation of concerns
6. **Faster Deployment**: No need to coordinate with other portals

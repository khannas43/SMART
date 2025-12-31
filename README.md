# SMART Platform

SMART (State Management and Analytics for Rajasthan Transformation) Platform for Rajasthan Government.

## Project Overview

SMART Platform consists of 4 **completely self-contained** portals serving different user groups:

1. **Citizen Portal** (`portals/citizen/`) - Public-facing portal for citizens
2. **Departmental User Portal** (`portals/dept/`) - Internal portal for government departments
3. **AI/ML Insight Portal** (`portals/aiml/`) - Analytics and insights dashboard
4. **Administration and Monitoring Portal** (`portals/monitor/`) - System administration and monitoring

## Architecture

- **Frontend**: React (Mobile-compatible, Multilingual)
- **Backend**: Java Spring Boot Microservices
- **Database**: PostgreSQL
- **AI/ML**: 27 use cases integrated across portals
- **Deployment**: Separate, independent deployments for each portal in Rajasthan State Govt. Data Centers

## Portal Structure

Each portal is **completely self-contained** with:
- ✅ Frontend (React application)
- ✅ Backend services (Spring Boot microservices)
- ✅ Database (schemas, migrations, seeds)
- ✅ Configuration files
- ✅ Internationalization (i18n) - for citizen and dept portals
- ✅ Docker and Kubernetes configs
- ✅ Deployment scripts
- ✅ Tests

This structure allows each portal to be developed, tested, and deployed **independently** to different network locations.

## Key Directories

- **`portals/`** - Self-contained portal applications
- **`shared-services/`** - Shared services (auth, notification, file, etc.)
- **`ai-ml/`** - 27 AI/ML use cases (shared across portals)
- **`shared/`** - Shared code and utilities (components, common, types)

## Portal Access URLs

All portals are accessible via a single port (default: **3000**) with path-based routing:

- **Citizen Portal**: `http://localhost:3000/citizen`
- **Departmental Portal**: `http://localhost:3000/dept`
- **AI/ML Insight Portal**: `http://localhost:3000/insight`
- **Administration & Monitoring Portal**: `http://localhost:3000/monitor`

See [Portal Routing Configuration](PORTAL_ROUTING.md) for detailed setup instructions.

## Getting Started

See individual portal README files for setup instructions:
- [Citizen Portal](portals/citizen/README.md)
- [Department Portal](portals/dept/README.md)
- [AI/ML Portal](portals/aiml/README.md)
- [Monitor Portal](portals/monitor/README.md)

## Documentation

- [Project Structure](project-structure.md) - Detailed folder structure
- [Architecture](ARCHITECTURE.md) - System architecture overview
- [Deployment Guide](DEPLOYMENT.md) - Deployment instructions for each portal
- [Folder Structure](FOLDER-STRUCTURE.txt) - Visual folder tree

## Benefits of Self-Contained Structure

1. **Complete Independence**: Each portal can be deployed without dependencies
2. **Network Isolation**: Portals can be deployed to different networks
3. **Independent Scaling**: Each portal scales independently
4. **Easy Maintenance**: All portal code in one place
5. **Clear Ownership**: Clear separation of concerns
6. **Faster Deployment**: No coordination needed between portals

# SMART Platform - Project Structure

## Overview

This document describes the folder structure for the SMART Platform. Each portal is **completely self-contained** with its own frontend, backend services, database, configuration, and supporting directories. This allows for independent deployment to different network locations within Rajasthan State Government Data Centers.

## Root Structure

```
SMART/
├── portals/                    # Self-contained portal applications
│   ├── citizen/               # Citizen Portal (complete)
│   ├── dept/                  # Departmental User Portal (complete)
│   ├── aiml/                  # AI/ML Insight Portal (complete)
│   └── monitor/               # Administration & Monitoring Portal (complete)
│
├── shared-services/            # Shared services (used by multiple portals)
│   ├── api-gateway/          # API Gateway service
│   ├── auth-service/         # Authentication & Authorization
│   ├── user-service/         # User management
│   ├── notification-service/ # Notifications
│   ├── file-service/         # File upload/download
│   └── common-service/       # Shared business logic
│
├── ai-ml/                     # AI/ML use cases (shared across portals)
│   ├── models/               # ML models
│   ├── pipelines/           # Data pipelines
│   ├── use-cases/           # 27 AI/ML use cases
│   ├── training/            # Model training scripts
│   └── inference/           # Inference services
│
├── shared/                    # Shared code and utilities
│   ├── common/              # Common utilities (Java)
│   ├── components/          # Shared React components
│   ├── hooks/              # Shared React hooks
│   ├── utils/              # Shared utilities
│   ├── constants/          # Shared constants
│   └── types/              # TypeScript types/interfaces
│
└── docs/                      # Documentation
    ├── api/                # API documentation
    ├── deployment/         # Deployment guides
    ├── architecture/       # Architecture docs
    └── user-guides/        # User guides
```

## Portal Structure (Self-Contained)

Each portal follows this complete structure:

```
portals/{portal-name}/
├── frontend/                  # React frontend application
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── components/      # Portal-specific components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service calls
│   │   ├── hooks/          # Custom hooks
│   │   ├── utils/          # Utilities
│   │   ├── store/          # State management
│   │   ├── routes/         # Routing configuration
│   │   ├── styles/         # Styles and themes
│   │   └── assets/         # Images, fonts, etc.
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                   # Backend microservices
│   └── services/
│       ├── {portal}-service/ # Portal-specific service
│       └── [shared services] # Auth, notification, etc. as needed
│
├── database/                  # Database management
│   ├── schemas/            # Database schemas
│   ├── migrations/         # Flyway/Liquibase migrations
│   ├── seeds/             # Seed data
│   └── scripts/           # Database scripts
│
├── config/                    # Configuration files
│   ├── application.yml     # Application config
│   ├── application-dev.yml # Development config
│   ├── application-prod.yml # Production config
│   └── nginx.conf          # Nginx configuration
│
├── i18n/                      # Internationalization (if applicable)
│   └── locales/            # Translation files
│       ├── en/             # English
│       ├── hi/             # Hindi
│       └── rj/             # Rajasthani
│
├── scripts/                   # Utility scripts
│   ├── build/              # Build scripts
│   └── deploy/             # Deployment scripts
│
├── docker/                    # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── k8s/                       # Kubernetes configurations
│   ├── deployment.yaml
│   └── service.yaml
│
├── tests/                     # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
│
└── README.md                  # Portal-specific documentation
```

## Portal-Specific Services

### Citizen Portal
- `citizen-service` - Core citizen services
- `auth-service` - Authentication (from shared-services)
- `notification-service` - Notifications (from shared-services)
- `file-service` - File handling (from shared-services)

### Department Portal
- `dept-service` - Core department services
- `auth-service` - Authentication (from shared-services)
- `user-service` - User management (from shared-services)
- `notification-service` - Notifications (from shared-services)
- `file-service` - File handling (from shared-services)

### AI/ML Portal
- `aiml-service` - AI/ML services
- `auth-service` - Authentication (from shared-services)

### Monitor Portal
- `monitor-service` - Monitoring services
- `auth-service` - Authentication (from shared-services)

## Service Structure (Example)

Each microservice follows this structure:

```
backend/services/{service-name}/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/smart/{service}/
│   │   │       ├── {Service}Application.java
│   │   │       ├── controller/    # REST controllers
│   │   │       ├── service/       # Business logic
│   │   │       ├── repository/    # Data access
│   │   │       ├── model/         # Entity models
│   │   │       ├── dto/           # Data transfer objects
│   │   │       ├── config/        # Configuration classes
│   │   │       └── exception/     # Exception handlers
│   │   └── resources/
│   │       ├── application.yml
│   │       └── application-{env}.yml
│   └── test/
├── pom.xml (or build.gradle)
├── Dockerfile
└── README.md
```

## AI/ML Structure

```
ai-ml/
├── use-cases/              # 27 AI/ML use cases
│   ├── use-case-01/       # Each use case in separate folder
│   ├── use-case-02/
│   └── ...
├── models/                # Trained models
│   ├── model-registry/
│   └── model-versions/
├── pipelines/             # Data processing pipelines
│   ├── data-ingestion/
│   ├── data-preprocessing/
│   └── feature-engineering/
├── training/              # Training scripts
│   ├── notebooks/        # Jupyter notebooks
│   └── scripts/          # Training scripts
└── inference/             # Inference services
```

## Deployment Strategy

Each portal is **completely independent** and can be deployed separately:

1. **Citizen Portal**: Deployed with its own services, database, and config
2. **Dept Portal**: Deployed with its own services, database, and config
3. **AIML Portal**: Deployed with its own services, database, and config
4. **Monitor Portal**: Deployed with its own services, database, and config

Each portal folder contains everything needed for deployment:
- Frontend build
- Backend services
- Database migrations
- Configuration files
- Docker/Kubernetes configs
- Deployment scripts

## Shared Components

- **shared/components/**: Reusable React components (buttons, forms, tables, etc.)
- **shared/common/**: Java common utilities, exceptions, validators
- **shared/types/**: TypeScript interfaces shared between frontend and backend

## Database Strategy

- **Separate databases per portal**: Each portal has its own database schema
- **Migrations managed per portal**: Database migrations are portal-specific
- **Schema definitions**: Located in `portals/{portal}/database/schemas/`

## Configuration Management

- **Portal-specific configs**: Each portal has its own config directory
- **Environment-specific**: Dev, staging, and production configs per portal
- **Service configs**: Each service has its own application.yml files

## Multilingual Support

- **Portal-specific i18n**: Translation files in `portals/{portal}/i18n/locales/`
- **Supported languages**: English (en), Hindi (hi), Rajasthani (rj)
- **Not all portals require i18n**: Only citizen and dept portals have i18n folders

## Benefits of This Structure

1. **Complete Independence**: Each portal can be developed, tested, and deployed independently
2. **Clear Ownership**: All portal-related code is in one place
3. **Easy Deployment**: Everything needed for a portal is in its folder
4. **Network Isolation**: Portals can be deployed to different networks easily
5. **Maintainability**: Changes to one portal don't affect others
6. **Scalability**: Each portal can scale independently

# Administration and Monitoring Portal

System administration and monitoring portal for managing the SMART platform.

## Portal Structure

```
monitor/
├── frontend/                    # React frontend application
│   ├── public/
│   ├── src/
│   │   ├── components/         # Portal-specific components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service calls
│   │   ├── hooks/             # Custom hooks
│   │   ├── utils/             # Utilities
│   │   ├── store/             # State management
│   │   ├── routes/            # Routing configuration
│   │   ├── styles/            # Styles and themes
│   │   └── assets/            # Images, fonts, etc.
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                     # Backend microservices
│   └── services/
│       ├── monitor-service/   # Monitoring services
│       └── auth-service/      # Authentication (shared)
│
├── database/                    # Database management
│   ├── schemas/               # Database schemas
│   ├── migrations/            # Database migrations
│   ├── seeds/                 # Seed data
│   └── scripts/               # Database scripts
│
├── config/                     # Configuration files
│   ├── application.yml        # Application config
│   ├── application-dev.yml    # Development config
│   ├── application-prod.yml   # Production config
│   └── nginx.conf             # Nginx configuration
│
├── scripts/                    # Utility scripts
│   ├── build/                 # Build scripts
│   └── deploy/                # Deployment scripts
│
├── docker/                     # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── k8s/                        # Kubernetes configurations
│   ├── deployment.yaml
│   └── service.yaml
│
├── tests/                      # Test files
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
│
└── README.md                   # This file
```

## Features
- System monitoring and health checks
- User administration
- Service management
- Log viewing and analysis
- Performance metrics
- Configuration management
- Mobile-responsive design

## Tech Stack
- **Frontend**: React 18+, TypeScript, React Router
- **Backend**: Java Spring Boot Microservices
- **Database**: PostgreSQL
- **State Management**: Redux/Zustand
- **Monitoring**: Custom monitoring libraries

## Setup

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend/services/monitor-service
mvn clean install
mvn spring-boot:run
```

## Deployment

This portal is completely self-contained and can be deployed independently to Rajasthan State Government Data Centers.

### Docker Deployment
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

## Services Included

- **monitor-service**: Core monitoring and administration services
- **auth-service**: Authentication and authorization

## Monitoring Capabilities

The monitor portal can monitor:
- All other portals (citizen, dept, aiml)
- All microservices across the platform
- Database health and performance
- System resources and metrics
- Application logs and errors

# Departmental User Portal

Internal portal for government department users to manage citizen services and applications.

## Portal Structure

```
dept/
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
│       ├── dept-service/      # Department-specific services
│       ├── auth-service/      # Authentication (shared)
│       ├── user-service/      # User management (shared)
│       ├── notification-service/ # Notifications (shared)
│       └── file-service/      # File handling (shared)
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
├── i18n/                       # Internationalization
│   └── locales/               # Translation files
│       ├── en/                # English
│       ├── hi/                # Hindi
│       └── rj/                # Rajasthani
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
- Application processing
- Document verification
- Dashboard and analytics
- User management
- Multilingual support (English, Hindi, Rajasthani)
- Mobile-responsive design

## Tech Stack
- **Frontend**: React 18+, TypeScript, React Router
- **Backend**: Java Spring Boot Microservices
- **Database**: PostgreSQL
- **State Management**: Redux/Zustand
- **i18n**: i18next

## Setup

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend/services/dept-service
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

- **dept-service**: Core department portal services
- **auth-service**: Authentication and authorization
- **user-service**: User management
- **notification-service**: Email/SMS notifications
- **file-service**: File upload and download

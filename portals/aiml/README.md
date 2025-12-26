# AI/ML Insight Portal

Analytics and insights dashboard powered by 27 AI/ML use cases.

## Portal Structure

```
aiml/
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
│       ├── aiml-service/      # AI/ML services
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
- AI/ML insights and predictions
- Data visualization dashboards
- Trend analysis
- Report generation
- Mobile-responsive design

## Tech Stack
- **Frontend**: React 18+, TypeScript, React Router
- **Backend**: Java Spring Boot Microservices
- **Database**: PostgreSQL
- **State Management**: Redux/Zustand
- **Charts**: Chart.js/Recharts

## Setup

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend/services/aiml-service
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

- **aiml-service**: Core AI/ML services and model inference
- **auth-service**: Authentication and authorization

## AI/ML Integration

This portal integrates with the 27 AI/ML use cases located in the root `ai-ml/` directory. The `aiml-service` provides REST APIs for:
- Model inference
- Batch predictions
- Model health checks
- Data visualization endpoints

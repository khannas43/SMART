# SMART Platform - Architecture Overview

## System Architecture

The SMART platform follows a microservices architecture with separate frontend portals and backend services.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Rajasthan State Govt.                     │
│                      Data Centers                            │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌─────▼──────┐
│   Citizen    │   │  Dept Portal    │   │ AIML Portal│
│   Portal     │   │                 │   │            │
└───────┬──────┘   └────────┬────────┘   └─────┬──────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │  API Gateway   │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌─────▼──────┐
│ Auth Service │   │ Citizen Service │   │ Dept Service│
└───────┬──────┘   └────────┬────────┘   └─────┬──────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │  PostgreSQL    │
                    │   Database     │
                    └────────────────┘
```

## Portal Architecture

Each portal follows this structure:

### Frontend (React)
- **Components**: Reusable UI components
- **Pages**: Route-based page components
- **Services**: API communication layer
- **State Management**: Redux/Zustand for global state
- **Routing**: React Router for navigation
- **i18n**: Multilingual support

### Backend (Spring Boot Microservices)
- **Controllers**: REST API endpoints
- **Services**: Business logic layer
- **Repositories**: Data access layer
- **Models**: Entity models
- **DTOs**: Data transfer objects
- **Config**: Configuration classes

## AI/ML Integration

27 AI/ML use cases are integrated across portals:

1. **Data Ingestion**: Collect data from various sources
2. **Data Preprocessing**: Clean and prepare data
3. **Feature Engineering**: Extract relevant features
4. **Model Training**: Train ML models
5. **Model Inference**: Serve predictions via `aiml-service`
6. **Model Monitoring**: Track model performance

## Communication Flow

1. **User Request**: User accesses portal (React frontend)
2. **API Call**: Frontend makes API call to API Gateway
3. **Authentication**: API Gateway validates with Auth Service
4. **Routing**: API Gateway routes to appropriate microservice
5. **Business Logic**: Microservice processes request
6. **Database**: Microservice queries/updates PostgreSQL
7. **AI/ML**: If needed, calls AIML service for predictions
8. **Response**: Response sent back through API Gateway to frontend

## Data Flow

```
Portal → API Gateway → Microservice → Database
                              │
                              └──→ AIML Service → ML Models
```

## Security Architecture

- **Authentication**: JWT tokens via Auth Service
- **Authorization**: Role-based access control (RBAC)
- **API Security**: API Gateway handles rate limiting, CORS
- **Data Security**: Encrypted database connections
- **Network Security**: Firewall rules per portal network

## Scalability

- **Horizontal Scaling**: Each service can scale independently
- **Load Balancing**: Nginx/API Gateway for load distribution
- **Database Scaling**: Read replicas for read-heavy operations
- **Caching**: Redis for session and data caching (optional)

## Deployment Strategy

- **Separate Deployments**: Each portal deployed independently
- **Containerization**: Docker for consistent deployments
- **Orchestration**: Kubernetes for production (optional)
- **CI/CD**: Automated build and deployment pipelines

## Technology Stack Summary

### Frontend
- React 18+
- TypeScript
- React Router
- State Management (Redux/Zustand)
- i18next
- UI Libraries (Material-UI/Ant Design)

### Backend
- Java 17+
- Spring Boot 3.x
- Spring Security
- Spring Data JPA
- PostgreSQL Driver

### Database
- PostgreSQL 14+

### Infrastructure
- Docker
- Kubernetes (optional)
- Nginx
- API Gateway (Spring Cloud Gateway/Zuul)

### AI/ML
- Python (for ML models)
- TensorFlow/PyTorch (for model training)
- REST API (for model serving)


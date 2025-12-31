# Citizen Portal

Public-facing portal for citizens of Rajasthan to access government services.

## Portal Structure

```
citizen/
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
│       ├── citizen-service/   # Citizen-specific services
│       ├── auth-service/      # Authentication (shared)
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
- Service requests and applications
- Document submission
- Status tracking
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
cd backend/services/citizen-service
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

- **citizen-service**: Core citizen portal services
- **auth-service**: Authentication and authorization
- **notification-service**: Email/SMS notifications
- **file-service**: File upload and download

## Development Planning

Comprehensive development planning documents are available:

- **[Planning Summary](./PLANNING_SUMMARY.md)** - High-level overview and quick reference
- **[Screens & Modules Map](./SCREENS_MODULES_MAP.md)** - Complete mapping of 40 screens across 10 modules
- **[Development Plan](./DEVELOPMENT_PLAN.md)** - Comprehensive 21-week development plan with all phases
- **[Implementation Roadmap](./IMPLEMENTATION_ROADMAP.md)** - Quick reference roadmap with priorities and milestones
- **[Sprint Breakdown](./SPRINT_BREAKDOWN.md)** - Detailed task breakdown for each sprint
- **[Technical Architecture](./TECHNICAL_ARCHITECTURE.md)** - System architecture and technical design

These documents provide detailed information about:
- **40 screens across 10 modules** - Complete screen specifications and mapping
- Development phases and timeline
- Feature breakdown and priorities
- Technical architecture and design
- Sprint planning and task breakdown
- Risk assessment and mitigation
- Success metrics and milestones

## Portal Modules

The Citizen Portal consists of 10 modules with 40 screens:

1. **Authentication & Profile** (6 screens) - Jan Aadhaar, Raj SSO, MFA, Profile management
2. **Scheme Discovery** (6 screens) - AI-driven discovery, eligibility, recommendations
3. **Consent & Application** (5 screens) - Consent, applications, document upload
4. **Benefits & Entitlements** (7 screens) - 360° profile, DBT tracking, forecasting
5. **Documents & Certificates** (4 screens) - Document library, e-Vault, digital signatures
6. **24 Hours Service Delivery** (4 screens) - Service catalog, requests, tracking
7. **Notifications** (1 screen) - Multi-channel preferences
8. **Opt-out & Preferences** (1 screen) - Scheme opt-out management
9. **Account Management** (2 screens) - Account and security settings
10. **Help & Support** (4 screens) - FAQ, tickets, routing

See [SCREENS_MODULES_MAP.md](./SCREENS_MODULES_MAP.md) for complete details.
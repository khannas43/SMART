# Eligibility Scoring & 360° Profiles - Design Document

📄 **Full Technical Design Document**: See `docs/TECHNICAL_DESIGN.md`

This is a summary document. For complete technical details, architecture, API specifications, and implementation guidelines, refer to the comprehensive technical design document.

## Quick Reference

### Key Components

1. **Eligibility Scoring**: XGBoost regression model (0-100 score)
2. **Income Band Inference**: RandomForest classification (5 classes)
3. **Graph Clustering**: Neo4j Louvain algorithm
4. **Anomaly Detection**: Isolation Forest + rules

### Technology Stack

- **Backend**: Spring Boot 3.x + Java 17
- **Frontend**: React 18 + TypeScript
- **Databases**: PostgreSQL + Neo4j
- **ML**: Python 3.12 + scikit-learn + XGBoost
- **MLOps**: MLflow 2.8+

### Key APIs

- `GET /api/v1/profiles/360/{gr_id}` - Full 360° profile
- `GET /api/v1/eligibility/score` - Eligibility scoring
- `GET /api/v1/profiles/graph/family-network/{gr_id}` - Graph visualization
- `GET /api/v1/analytics/benefits/undercoverage` - Analytics

### Data Sources

- **PostgreSQL**: Golden records, relationships, benefits, profiles
- **Neo4j**: Graph database for network operations
- **MLflow**: Model tracking and registry

## Architecture Overview

```
Frontend (React) → Spring Boot APIs → PostgreSQL/Neo4j → ML Models
```

## Relationship Types

| Type | Icon | Color | Description |
|------|------|-------|-------------|
| SPOUSE | 👫 | Red | Married partners |
| CHILD | 👨‍👩‍👧‍👦 | Teal | Parent → Child |
| PARENT | 👨‍👩‍👧‍👦 | Green | Child → Parent |
| SIBLING | 👨‍👩‍👧‍👦 | Pink | Brothers/Sisters |
| CO_RESIDENT | 🏠 | Purple | Same address |
| CO_BENEFIT | 💰 | Yellow | Same benefits |
| EMPLOYEE_OF | 💼 | Blue | Employment |
| BUSINESS_PARTNER | 🤝 | Green | Business |
| SHG_MEMBER | 👥 | Dark Purple | SHG member |

## Performance Targets

- Eligibility Score API: <200ms
- Profile 360 API: <500ms
- Graph Network API: <1s
- Profile Recompute: <5s

## Documentation

- **Technical Design**: `docs/TECHNICAL_DESIGN.md` (Complete)
- **Neo4j Setup**: `docs/NEO4J_SETUP.md`
- **API Integration**: `docs/CITIZEN_PORTAL_INTEGRATION.md`
- **Quick Start**: `QUICK_START.md`

---

For complete details, see `docs/TECHNICAL_DESIGN.md`.


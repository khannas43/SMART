# Golden Record Creation & Maintenance - Use Case Specification

**Document Version:** 1.0  
**Last Updated:** 2024-12-26  
**Use Case ID:** AI-PLATFORM-01

## 1. Overview

### 1.1 Purpose
This document specifies the requirements, design, and implementation approach for the Golden Record Creation & Maintenance use case, which serves as a foundational Tier 1 capability for the SMART Rajasthan AI/ML platform.

### 1.2 Business Context
In a multi-departmental government system with 34+ schemes and 171+ services, citizen data exists in fragmented sources with potential duplicates, conflicts, and inconsistencies. The Golden Record system creates and maintains a single, verified source of truth for citizen attributes, enabling accurate eligibility assessment and reducing errors.

## 2. Functional Requirements

### 2.1 Deduplication
- **FR-01**: System SHALL identify duplicate citizen records across all data sources
- **FR-02**: System SHALL use probabilistic matching with ML models (Fellegi-Sunter or Siamese NN)
- **FR-03**: System SHALL automatically merge records with >95% match confidence
- **FR-04**: System SHALL flag records with 80-95% confidence for manual review
- **FR-05**: System SHALL use multiple features: fuzzy string matching, phonetic encoding, geospatial distance

### 2.2 Conflict Reconciliation
- **FR-06**: System SHALL reconcile conflicting attribute values from different sources
- **FR-07**: System SHALL rank attribute versions using ensemble classifier (XGBoost + rules)
- **FR-08**: System SHALL consider recency, source authority, and completeness in ranking
- **FR-09**: System SHALL output confidence scores for each reconciled attribute

### 2.3 Best Truth Selection
- **FR-10**: System SHALL select the "best truth" for each citizen attribute
- **FR-11**: System SHALL use rule-based + ML survival analysis to predict staleness
- **FR-12**: System SHALL retrain models weekly on labeled admin corrections

### 2.4 Golden Record Management
- **FR-13**: System SHALL maintain unified Golden Record in JSON/document store
- **FR-14**: System SHALL track metadata: sources, confidence scores, last_updated
- **FR-15**: System SHALL maintain 360° profile extensions: family tree, entitlements ledger
- **FR-16**: System SHALL provide real-time APIs for eligibility checks

## 3. Non-Functional Requirements

### 3.1 Performance
- **NFR-01**: Deduplication processing SHALL complete within 24 hours for daily batch
- **NFR-02**: Real-time API responses SHALL be <200ms for eligibility checks
- **NFR-03**: Conflict resolution TAT SHALL be <24 hours

### 3.2 Accuracy
- **NFR-04**: Deduplication precision SHALL be >95%
- **NFR-05**: Deduplication recall SHALL be >95%
- **NFR-06**: Golden Record accuracy SHALL be >99%
- **NFR-07**: False positive rate in deduplication SHALL be <1%
- **NFR-08**: Downstream eligibility errors SHALL be <0.5% (quarterly audit)

### 3.3 Coverage
- **NFR-09**: Golden Record coverage SHALL be >90% of Jan Aadhaar base

### 3.4 Governance
- **NFR-10**: System SHALL comply with DPDP Act 2023 (consent tracking, PII minimization)
- **NFR-11**: System SHALL monitor for bias (demographic parity checks)
- **NFR-12**: System SHALL maintain audit trail of all merges and conflicts
- **NFR-13**: System SHALL integrate with OpenMetadata for lineage tracking

## 4. Technical Architecture

### 4.1 Data Flow
```
Data Sources (Jan Aadhaar, Raj D.Ex, 34+ Schemes, 171+ Services)
    ↓
Data Ingestion Pipeline
    ↓
Deduplication Module (ML Model)
    ↓
Conflict Reconciliation Module (XGBoost + Rules)
    ↓
Best Truth Selection Module (Survival Analysis)
    ↓
Golden Record Store (PostgreSQL + pgvector)
    ↓
API Layer (FastAPI)
    ↓
Spring Boot Backend
```

### 4.2 ML Models

#### 4.2.1 Deduplication Models
- **Option 1**: Fellegi-Sunter Probabilistic Record Linkage
- **Option 2**: Siamese Neural Networks for similarity learning
- **Features**: Name (fuzzy + phonetic), DOB, Address (geospatial), Income, Occupation

#### 4.2.2 Conflict Reconciliation
- **Model**: XGBoost Gradient Boosting Classifier
- **Rules Engine**: Source authority hierarchy, recency weights
- **Output**: Ranked attribute versions with confidence scores

#### 4.2.3 Best Truth Selection
- **ML Component**: Survival Analysis (Cox Proportional Hazards)
- **Rule Component**: Source authority, recency, completeness
- **Training**: Weekly retraining on admin corrections

### 4.3 Technology Stack
- **ML Framework**: scikit-learn, XGBoost, PyTorch/TensorFlow
- **API**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Backend**: Spring Boot (Java)
- **Vector Storage**: pgvector for embeddings
- **Document Store**: PostgreSQL JSONB

## 5. Data Model

### 5.1 Golden Record Schema
```sql
CREATE TABLE golden_records (
    record_id UUID PRIMARY KEY,
    jan_aadhaar VARCHAR(12) UNIQUE,
    attributes JSONB,  -- All citizen attributes with confidence scores
    sources JSONB,  -- Source tracking for each attribute
    metadata JSONB,  -- Confidence scores, last_updated, version
    family_tree JSONB,  -- Relationship graph
    entitlements_ledger JSONB,  -- Scheme entitlements history
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER
);
```

### 5.2 Deduplication Matches
```sql
CREATE TABLE deduplication_matches (
    match_id UUID PRIMARY KEY,
    record_1_id UUID,
    record_2_id UUID,
    match_score DECIMAL(5,4),
    confidence_level VARCHAR(20),  -- auto_merge, manual_review, reject
    status VARCHAR(20),  -- pending, merged, rejected
    resolved_at TIMESTAMP
);
```

### 5.3 Conflict Log
```sql
CREATE TABLE conflict_log (
    conflict_id UUID PRIMARY KEY,
    record_id UUID,
    attribute_name VARCHAR(100),
    conflicting_values JSONB,  -- {source: value, confidence, timestamp}
    resolution JSONB,  -- Selected value and reasoning
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP
);
```

## 6. API Specifications

### 6.1 Get Golden Record
```
GET /api/v1/golden-record/{jan_aadhaar}
Response: {
    record_id: UUID,
    jan_aadhaar: string,
    attributes: {...},
    confidence_scores: {...},
    sources: {...}
}
```

### 6.2 Check Eligibility
```
POST /api/v1/golden-record/eligibility-check
Body: {
    jan_aadhaar: string,
    scheme_id: string
}
Response: {
    eligible: boolean,
    confidence: decimal,
    missing_attributes: [...],
    recommended_action: string
}
```

### 6.3 Trigger Deduplication
```
POST /api/v1/golden-record/deduplicate
Body: {
    batch_id: string,
    source: string
}
Response: {
    job_id: string,
    status: string
}
```

## 7. Governance & Compliance

### 7.1 DPDP Act 2023 Compliance
- Consent tracking for all data usage
- PII minimization (store only necessary attributes)
- Right to access and correction
- Data retention policies

### 7.2 Bias Monitoring
- Demographic parity checks (age, gender, caste, income)
- Fairness metrics tracking
- Regular bias audits

### 7.3 Audit Trail
- All merges logged with timestamps
- Conflict resolutions tracked
- Source lineage maintained
- Change history preserved

## 8. Success Metrics

### 8.1 Quality Metrics
- Deduplication Precision: >95%
- Deduplication Recall: >95%
- Golden Record Accuracy: >99%
- False Positive Rate: <1%

### 8.2 Coverage Metrics
- Golden Record Coverage: >90% of Jan Aadhaar base

### 8.3 Performance Metrics
- Conflict Resolution TAT: <24 hours
- API Response Time: <200ms

### 8.4 Business Metrics
- Downstream Eligibility Errors: <0.5% (quarterly)
- Manual Review Queue Size: <1000 pending

## 9. Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
- Database schema setup
- Data ingestion pipeline
- Basic deduplication (rule-based)

### Phase 2: ML Models (Weeks 5-12)
- Fellegi-Sunter implementation
- Siamese NN development
- XGBoost conflict resolution
- Survival analysis model

### Phase 3: Integration (Weeks 13-16)
- FastAPI microservice
- Spring Boot integration
- Real-time APIs
- Admin interface

### Phase 4: Governance (Weeks 17-20)
- DPDP compliance module
- Bias monitoring
- Audit trail system
- OpenMetadata integration

## 10. Risks & Mitigations

### Risk 1: Low Deduplication Accuracy
- **Mitigation**: Start with conservative thresholds, iterate based on feedback

### Risk 2: Data Quality Issues
- **Mitigation**: Implement data quality checks in ingestion pipeline

### Risk 3: Performance at Scale
- **Mitigation**: Use vector search (pgvector), batch processing, caching

### Risk 4: Compliance Violations
- **Mitigation**: Early DPDP compliance implementation, regular audits

## 11. Dependencies

### External
- Jan Aadhaar API access
- Raj D.Ex data pipeline
- Departmental system APIs
- Validation source APIs

### Internal
- PostgreSQL database with pgvector
- FastAPI infrastructure
- Spring Boot backend
- OpenMetadata instance

## 12. Future Enhancements

- Real-time streaming deduplication
- Graph neural networks for relationship inference
- Multi-modal matching (images, documents)
- Federated learning across departments


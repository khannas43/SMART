# SMART Platform - Data Integration & CDC Strategy

This folder contains the comprehensive strategy and documentation for Change Data Capture (CDC) and Data Masking implementation across the SMART platform.

## Overview

The SMART platform requires bidirectional data synchronization between:
- **smart_warehouse** (AI/ML analytical database) ↔ **smart_citizen** (Citizen portal database)

This synchronization is critical for:
1. **Warehouse → Citizen**: Delivering eligibility insights, ML-driven recommendations, and profile updates to citizens
2. **Citizen → Warehouse**: Syncing citizen-submitted data updates back to the warehouse for model retraining and data enrichment

## Technology Stack

- **CDC Engine**: Debezium (Apache Kafka Connect)
- **Message Broker**: Apache Kafka
- **Data Masking**: Apache Ranger
- **Source Databases**: PostgreSQL (smart_warehouse, smart_citizen)

## Document Structure

### 📄 [CDC and Data Masking Strategy](./docs/CDC_DATA_MASKING_STRATEGY.md)
Comprehensive documentation covering:
- Architecture overview
- Debezium connector configurations
- Data mapping and transformation rules
- Bidirectional sync strategy
- Conflict resolution
- Apache Ranger data masking policies
- Implementation phases
- Monitoring and error handling

### 📄 [Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md)
Step-by-step guide for implementing CDC:
- Prerequisites and setup
- Database configuration
- Infrastructure deployment
- Connector setup and testing

### 📄 [Data Mapping Reference](./docs/DATA_MAPPING_REFERENCE.md)
Detailed mapping between source and target tables:
- Table-to-table mappings
- Field-level transformations
- Filtering rules

### 📁 [Config](./config/)
Configuration files for:
- Debezium connectors
- Kafka topics
- Apache Ranger policies

### 📁 [Scripts](./scripts/)
Utility scripts for:
- Database setup (WAL configuration)
- Connector deployment
- Monitoring and health checks

## Quick Start

⚠️ **Note**: This is a planning document. Implementation will be done at a later stage.

To get started when ready:
1. Review [CDC and Data Masking Strategy](./docs/CDC_DATA_MASKING_STRATEGY.md)
2. Check [Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md) for prerequisites
3. Follow the phased implementation approach

## Status

**Current Status**: 📋 Planning Phase  
**Implementation Target**: To be determined  
**Last Updated**: 2024-12-29

---

For questions or updates to this strategy, please refer to the technical design documents in the `ai-ml/use-cases/` folders.


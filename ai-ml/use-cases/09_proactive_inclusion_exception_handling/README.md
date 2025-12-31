# Proactive Inclusion & Exception Handling

**Use Case ID:** AI-PLATFORM-09  
**Version:** 1.0  
**Status:** 🚧 In Development

## Overview

The Proactive Inclusion & Exception Handling system identifies potentially excluded or underserved citizens and groups (e.g., tribals, PwD, unemployed youth, single women, remote hamlets) using Golden Record, 360° profiles, and network analytics. It surfaces targeted, context-aware scheme suggestions and nudges in the citizen portal/app and departmental workflows, and flags "exceptions" where usual rules may not capture genuine need.

## Features

### 1. Underserved Household Detection
- Inclusion Gap Score calculation
- Vulnerability indicator integration
- Local coverage benchmark comparison
- Priority household tagging

### 2. Exception Pattern Detection
- Anomaly detection on 360° feature space
- Exception categorization (recently disabled, migrant workers, etc.)
- Human review routing for exceptions

### 3. Nudge and Recommendation Logic
- Context-aware scheme suggestions
- Multi-channel nudge delivery
- Priority-based action selection

## Architecture

### Components

1. **InclusionGapScorer**: Calculates inclusion gap scores
2. **ExceptionPatternDetector**: Detects atypical circumstances
3. **PriorityHouseholdIdentifier**: Identifies priority households
4. **NudgeGenerator**: Generates context-aware nudges
5. **InclusionOrchestrator**: Coordinates end-to-end workflow

### Integration Points

- **AI-PLATFORM-02** (360° Profile): Vulnerability flags, under-coverage analytics
- **AI-PLATFORM-03** (Eligibility Engine): Predicted eligibility
- **AI-PLATFORM-08** (Eligibility Checker): Recommendations

## Database Schema

The `inclusion` schema contains:
- Priority household records
- Inclusion gap scores
- Exception flags
- Nudge delivery records
- Effectiveness analytics

## Quick Start

### 1. Setup Database

```bash
cd ai-ml/use-cases/09_proactive_inclusion_exception_handling
./scripts/setup_database.sh
```

### 2. Verify Configuration

```bash
python scripts/check_config.py
```

### 3. Test Inclusion Detection

```bash
python scripts/test_inclusion_workflow.py
```

## API Endpoints

**Base URL:** `/inclusion`

- `GET /inclusion/priority?family_id={id}` - Get priority status and nudges for family
- `GET /inclusion/priority-list?block_id={id}` - List priority households for field workers
- `POST /inclusion/nudge-delivery` - Schedule and record nudge delivery

## Status

**Current Status**: 🚧 In Development

- ✅ Database schema (in progress)
- ⏳ Configuration files
- ⏳ Core services
- ⏳ Spring Boot REST APIs
- ⏳ Testing scripts
- ⏳ Documentation

---

**Last Updated:** 2024-12-30


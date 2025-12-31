# Eligibility Checker & Recommendations

**Use Case ID:** AI-PLATFORM-08  
**Version:** 1.0  
**Status:** 🚧 In Development

## Overview

The Eligibility Checker & Recommendations system provides an interactive tool (web/app/chatbot) where citizens can quickly see which schemes they are eligible for, might be eligible for, or are ineligible for, with clear explanations and next steps.

The system uses ML and rule logic from Auto Identification (AI-PLATFORM-03) plus 360° profiles (AI-PLATFORM-02) to rank "best fit" schemes and personalize recommendations, not just list everything.

## Features

### 1. Eligibility Checking
- **Logged-in Users**: Direct eligibility evaluation using Golden Record + 360° Profile
- **Guest Users**: Questionnaire-based eligibility checking with approximate results
- **Anonymous Mode**: Basic eligibility checks with limited accuracy

### 2. Scheme Ranking & Recommendations
- Priority scoring based on eligibility, impact, under-coverage, and time sensitivity
- Top recommendations (short list) and other potentially relevant schemes
- Filters by domain, department, family member, time effort

### 3. Explanation Generation
- Human-readable explanations in simple language
- Available in multiple languages (English, Hindi, etc.)
- Shows why eligible/not eligible with next steps

## Architecture

### Components

1. **EligibilityChecker**: Main service for performing eligibility checks
2. **SchemeRanker**: Ranks schemes based on multiple factors
3. **ExplanationGenerator**: Generates human-readable explanations
4. **QuestionnaireHandler**: Handles guest user questionnaires

### Integration Points

- **AI-PLATFORM-03** (Auto Identification): Eligibility evaluation engine
- **AI-PLATFORM-02** (360° Profile): Profile data and vulnerability indicators
- **AI-PLATFORM-01** (Golden Record): Identity and demographic data

## Database Schema

The `eligibility_checker` schema contains:

- `eligibility_checks`: Records of eligibility checks performed
- `scheme_eligibility_results`: Individual scheme eligibility results
- `recommendation_sets`: Generated recommendation sets for users
- `recommendation_items`: Individual schemes in recommendations
- `questionnaire_templates`: Templates for guest questionnaires
- `explanation_templates`: NLG templates for explanations
- `eligibility_check_analytics`: Aggregated analytics
- `eligibility_checker_audit_logs`: Audit logs for compliance

## Quick Start

### 1. Setup Database

```bash
cd ai-ml/use-cases/08_eligibility_checker_recommendation
./scripts/setup_database.sh
```

### 2. Verify Configuration

```bash
python scripts/check_config.py
```

### 3. Test Eligibility Checker

```bash
python scripts/test_eligibility_checker.py
```

## API Endpoints

**Base URL:** `/eligibility`

- `POST /eligibility/check` - Perform eligibility check
- `GET /eligibility/recommendations?family_id={id}` - Get recommendations for logged-in user
- `GET /eligibility/questionnaire` - Get questionnaire template
- `GET /eligibility/schemes/{scheme_code}` - Get eligibility for specific scheme

## Status

**Current Status**: 🚧 In Development

- ✅ Database schema (8 tables)
- ✅ Configuration files
- 🚧 Core services (in progress)
- ⏳ Spring Boot REST APIs
- ⏳ Testing scripts
- ⏳ Documentation

---

**Last Updated:** 2024-12-30


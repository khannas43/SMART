# Entitlement & Benefit Forecast for Citizens

**Use Case ID:** AI-PLATFORM-10  
**Version:** 1.0  
**Status:** 🚧 In Development

## Overview

The Entitlement & Benefit Forecast system predicts future entitlements and benefit amounts at household level over a chosen horizon (e.g., 1–3 years) based on demographics, income band, current and potential scheme enrolments, and announced scheme/policy parameters. The system exposes forecasts to citizens (personal financial planning view) and to planners (demand and budget insights).

## Features

### 1. Baseline Projection
- Projects current enrolled schemes forward
- Assumes eligibility continues and known benefit schedules apply
- Monthly/quarterly/annual breakdowns

### 2. Scenario-aware Forecasting
- "Status Quo" scenario: No new schemes
- "Act on Recommendations" scenario: Includes probable future enrolments
- "Policy Change" scenario: Under proposed policy changes (for planners)

### 3. Time-series & Behavioral Models
- For aggregate forecasting (planning use cases)
- Captures seasonality, dropout rates, progression patterns
- Simplified view for citizens

## Architecture

### Components

1. **BaselineForecaster**: Projects current enrolled schemes
2. **ScenarioForecaster**: Adds future enrolments from recommendations
3. **TimeSeriesForecaster**: Aggregate forecasting (optional)
4. **ForecastOrchestrator**: Coordinates end-to-end workflow

### Integration Points

- **AI-PLATFORM-02** (360° Profile): Household profiles, benefit history
- **AI-PLATFORM-03** (Eligibility Engine): Predicted eligible schemes
- **AI-PLATFORM-08** (Eligibility Checker): Recommendations
- **Golden Records**: Demographics, life stage events

## Database Schema

The `forecast` schema contains:
- Forecast records
- Scenario projections
- Benefit schedules
- Policy change tracking
- Aggregation data (for planning)

## Quick Start

### 1. Setup Database

```bash
cd ai-ml/use-cases/10_entitlement_benefit_forecast
./scripts/setup_database.sh
```

### 2. Verify Configuration

```bash
python scripts/check_config.py
```

### 3. Test Forecast Generation

```bash
python scripts/test_forecast_workflow.py
```

## API Endpoints

**Base URL:** `/forecast`

- `GET /forecast/benefits?family_id={id}&horizon=12m` - Get benefit forecast for household
- `GET /forecast/scenarios?family_id={id}&scenario={name}` - Get scenario forecast
- `GET /forecast/aggregate?level={block|district|state}` - Get aggregate forecasts (planning)

## Status

**Current Status**: 🚧 In Development

- ⏳ Database schema
- ⏳ Configuration files
- ⏳ Core services
- ⏳ Spring Boot REST APIs
- ⏳ Testing scripts
- ⏳ Documentation

---

**Last Updated:** 2024-12-30


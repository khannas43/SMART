# Shared Services

This directory contains services that are shared across multiple portals. These services are copied into each portal's `backend/services/` directory as needed.

## Services

- **api-gateway**: API Gateway service (if centralized routing is needed)
- **auth-service**: Authentication and Authorization service
- **user-service**: User management service
- **notification-service**: Email/SMS notification service
- **file-service**: File upload and download service
- **common-service**: Shared business logic and utilities

## Usage

These services are copied to portal-specific locations:
- `portals/citizen/backend/services/auth-service/`
- `portals/dept/backend/services/auth-service/`
- etc.

Each portal maintains its own copy of shared services to ensure complete independence and self-contained deployment.

## Development

When updating shared services:
1. Make changes in this directory
2. Copy updated service to relevant portals
3. Test in each portal context
4. Deploy independently per portal


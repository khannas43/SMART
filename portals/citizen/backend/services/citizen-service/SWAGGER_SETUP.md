# Swagger/OpenAPI Documentation Setup

## ✅ Swagger/OpenAPI Configuration Complete

API documentation has been set up using Springdoc OpenAPI (Swagger UI) for the Citizen Portal backend service.

## Configuration

### 1. OpenApiConfig
Created configuration class with:
- **API Information**: Title, description, version (1.0.0)
- **Contact Information**: Email, name, URL
- **License**: Government of Rajasthan
- **Servers**: Development (localhost:8080) and Production

### 2. Springdoc Configuration (application.yml)
```yaml
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
    enabled: true
    operations-sorter: method
    tags-sorter: alpha
    doc-expansion: none
  default-consumes-media-type: application/json
  default-produces-media-type: application/json
```

### 3. Swagger Annotations Added
- `@Tag` - Added to controllers for grouping endpoints
- `@Operation` - Added to endpoints with summary and description
- `@Parameter` - Added to path variables with descriptions

## Access URLs

Once the service is running:

### Swagger UI (Interactive Documentation)
```
http://localhost:8080/citizen/api/v1/swagger-ui.html
```

### OpenAPI JSON Specification
```
http://localhost:8080/citizen/api/v1/api-docs
```

## Controller Tags

1. **Citizens** - Citizen account and profile management
2. **Schemes** - Government schemes management
3. **Applications** - Service application management
4. **Documents** - Document upload and management
5. **Notifications** - Notification management
6. **Payments** - Payment processing
7. **Feedback** - Feedback and complaints
8. **Health** - Health check endpoints

## Features

✅ Interactive API documentation
✅ Try it out functionality for testing endpoints
✅ Request/response schemas
✅ Authentication support (JWT) - Can be configured
✅ Grouped by tags
✅ Sorted operations and tags
✅ JSON/OpenAPI specification export

## Next Steps

1. Add more detailed descriptions to remaining endpoints
2. Add example requests/responses
3. Configure JWT authentication in Swagger UI
4. Add response codes documentation
5. Add request/response examples

## Notes

- Swagger UI is enabled by default in development
- API docs are available at `/api-docs` endpoint
- All endpoints are documented with tags and operations
- Path variables have parameter descriptions
- The documentation will automatically update as controllers are modified


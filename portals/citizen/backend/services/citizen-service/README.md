# Citizen Service

Main backend service for SMART Citizen Portal.

## Technology Stack

- **Java**: 17
- **Spring Boot**: 3.2.0
- **Spring Data JPA**: Data persistence
- **Spring Security**: Authentication & Authorization
- **PostgreSQL**: Database
- **Flyway**: Database migrations
- **Lombok**: Boilerplate reduction
- **MapStruct**: DTO mapping
- **JWT**: Token-based authentication

## Building

```bash
mvn clean install
```

## Running

```bash
mvn spring-boot:run
```

The service will start on port 8080 with context path `/citizen/api/v1`

## API Documentation

Once running, access Swagger UI at:
- `http://localhost:8080/citizen/api/v1/swagger-ui.html`

## Database

- Database: `smart_citizen`
- Migrations: `src/main/resources/db/migration`

## Project Structure

```
src/main/java/com/smart/citizen/
├── config/          # Configuration classes
├── controller/      # REST controllers
├── service/         # Business logic
├── repository/      # JPA repositories
├── entity/          # JPA entities
├── dto/             # Data Transfer Objects
├── mapper/          # MapStruct mappers
├── exception/       # Exception handling
└── security/        # Security configuration
```


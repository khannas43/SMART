# Shared Common Utilities (Java)

This directory contains shared Java utilities, classes, and common code used across all microservices.

## Contents

- **Utilities**: Helper classes, validators, formatters
- **Exceptions**: Custom exception classes
- **Constants**: Shared constants
- **DTOs**: Common data transfer objects
- **Enums**: Shared enumerations
- **Config**: Common configuration classes

## Usage

Include as a dependency in microservice `pom.xml` or `build.gradle`:

```xml
<dependency>
    <groupId>com.smart</groupId>
    <artifactId>common</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Guidelines

- Keep utilities stateless
- Use proper Java package structure
- Document public APIs
- Write unit tests


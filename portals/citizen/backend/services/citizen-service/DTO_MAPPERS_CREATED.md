# DTO Classes and MapStruct Mappers Created

## ✅ DTO Classes and Mappers Created

All DTO (Data Transfer Object) classes and MapStruct mapper interfaces have been created for API communication.

## Common DTOs

### 1. ApiResponse<T>
Generic response wrapper for all API responses
- `success` - Boolean indicating success/failure
- `message` - Response message
- `data` - Response data (generic type)
- `timestamp` - Response timestamp
- `errorCode` - Error code for failures
- Static factory methods: `success()`, `error()`

### 2. PagedResponse<T>
Generic wrapper for paginated responses
- `content` - List of items
- `page` - Current page number
- `size` - Page size
- `totalElements` - Total number of elements
- `totalPages` - Total number of pages
- `first`, `last` - Flags for first/last page

## Entity-Specific DTOs

### Citizen DTOs
1. **CitizenRequest**
   - Fields: mobileNumber, aadhaarNumber, email, fullName, dateOfBirth, gender, address fields, pincode
   - Validation: @NotBlank, @Pattern, @Email, @Size

2. **CitizenUpdateRequest**
   - Fields: email, fullName, dateOfBirth, gender, address fields, pincode
   - Validation: @Email, @Pattern, @Size

3. **CitizenResponse**
   - All citizen fields including id, status, verificationStatus, timestamps

### Scheme DTOs
1. **SchemeRequest**
   - Fields: code, name, description, category, department, eligibilityCriteria (Map), dates, status
   - Validation: @NotBlank, @Size

2. **SchemeResponse**
   - All scheme fields including id, timestamps

### Service Application DTOs
1. **ServiceApplicationRequest**
   - Fields: schemeId, serviceType, applicationType, subject, description, priority, expectedCompletionDate, applicationData
   - Validation: @NotBlank, @Size

2. **ServiceApplicationResponse**
   - All application fields including id, applicationNumber, citizen/scheme details, status, dates

3. **ApplicationStatusUpdateRequest**
   - Fields: status, currentStage, comments
   - Validation: @NotBlank

### Document DTOs
1. **DocumentRequest**
   - Fields: applicationId, documentType, filePath, documentName, fileSize, mimeType
   - Validation: @NotBlank, @Size

2. **DocumentResponse**
   - All document fields including id, verification details, timestamps

### Notification DTOs
1. **NotificationResponse**
   - All notification fields including id, type, channel, status, read status, timestamps, metadata

### Payment DTOs
1. **PaymentRequest**
   - Fields: applicationId, amount, currency, paymentMethod, description
   - Validation: @NotNull, @DecimalMin, @NotBlank, @Size

2. **PaymentResponse**
   - All payment fields including id, transactionId, status, gateway details, timestamps

### Feedback DTOs
1. **FeedbackRequest**
   - Fields: type, category, subject, message, rating, applicationId
   - Validation: @NotBlank, @Min, @Max, @Size

2. **FeedbackResponse**
   - All feedback fields including id, status, resolution details, timestamps

## MapStruct Mappers

### 1. CitizenMapper
- `toEntity(CitizenRequest)` - Maps request to entity
- `toResponse(Citizen)` - Maps entity to response
- `updateEntityFromRequest(CitizenUpdateRequest, Citizen)` - Updates entity from request

### 2. SchemeMapper
- `toEntity(SchemeRequest)` - Maps request to entity
- `toResponse(Scheme)` - Maps entity to response
- `updateEntityFromRequest(SchemeRequest, Scheme)` - Updates entity from request

### 3. ServiceApplicationMapper
- `toEntity(ServiceApplicationRequest)` - Maps request to entity (ignores auto-generated fields)
- `toResponse(ServiceApplication)` - Maps entity to response (includes nested entity details)

### 4. DocumentMapper
- `toEntity(DocumentRequest)` - Maps request to entity (ignores auto-generated fields)
- `toResponse(Document)` - Maps entity to response (includes nested entity IDs)

### 5. NotificationMapper
- `toResponse(Notification)` - Maps entity to response (includes nested entity IDs)

### 6. PaymentMapper
- `toEntity(PaymentRequest)` - Maps request to entity (ignores auto-generated fields)
- `toResponse(Payment)` - Maps entity to response (includes nested entity IDs)

### 7. FeedbackMapper
- `toEntity(FeedbackRequest)` - Maps request to entity (ignores auto-generated fields)
- `toResponse(Feedback)` - Maps entity to response (includes nested entity IDs)

## Features

✅ Bean Validation annotations (@NotBlank, @NotNull, @Email, @Pattern, @Size, @Min, @Max, @DecimalMin)
✅ Lombok annotations for boilerplate reduction (@Data, @Builder, @AllArgsConstructor, @NoArgsConstructor)
✅ MapStruct configuration with Spring component model
✅ Proper mapping configurations (ignore auto-generated fields, nested entity mapping)
✅ Generic response wrappers for consistent API responses
✅ Pagination support with PagedResponse

## Mapper Configuration

- **Component Model**: `spring` - Mappers are Spring beans
- **Unmapped Target Policy**: `IGNORE` - Ignores unmapped target properties
- **Mapping Strategies**: 
  - Ignore auto-generated fields (id, timestamps) in toEntity methods
  - Map nested entities to IDs in toResponse methods
  - Support for nested entity name mapping (e.g., citizen.fullName -> citizenName)

## Next Steps

1. Create Service layer with business logic
2. Create REST Controllers
3. Add exception handling and error responses
4. Add request/response logging
5. Add API documentation (Swagger/OpenAPI)


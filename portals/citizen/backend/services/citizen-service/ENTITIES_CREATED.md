# Entity Classes Created

## ✅ All Entity Classes Created

All JPA entity classes have been created based on the database schema in `portals/citizen/database/schemas/01_citizen_schema.sql`.

## Entity Classes

### 1. BaseEntity
- Base class with common fields: `id`, `createdAt`, `updatedAt`
- Uses UUID as primary key
- JPA Auditing enabled

### 2. Citizen
- Maps to `citizens` table
- Fields: aadhaarNumber, mobileNumber, email, fullName, dateOfBirth, gender, address fields, status, verificationStatus
- Enums: CitizenStatus, VerificationStatus
- Indexes: mobile_number, aadhaar_number, status

### 3. Scheme
- Maps to `schemes` table
- Fields: code, name, description, category, department, eligibilityCriteria (JSON), dates, status
- Enum: SchemeStatus
- Indexes: code, category, status

### 4. ServiceApplication
- Maps to `service_applications` table
- Relationships: ManyToOne with Citizen and Scheme
- Fields: applicationNumber, serviceType, applicationType, subject, description, priority, status, stages, assignment
- Enums: Priority, ApplicationStatus
- Indexes: citizen_id, scheme_id, status, application_number

### 5. Document
- Maps to `documents` table
- Relationships: ManyToOne with Citizen and ServiceApplication
- Fields: documentType, fileName, filePath, fileSize, mimeType, verification details
- Enum: VerificationStatus
- Indexes: citizen_id, application_id, document_type, verification_status

### 6. ApplicationStatusHistory
- Maps to `application_status_history` table
- Relationship: ManyToOne with ServiceApplication
- Fields: status, previousStatus, statusDate, changedBy, notes
- Indexes: application_id, status, status_date

### 7. Notification
- Maps to `notifications` table
- Relationship: ManyToOne with Citizen
- Fields: notificationType, title, message, priority, isRead, actionUrl, related entities
- Enums: NotificationType, Priority
- Indexes: citizen_id, notification_type, is_read, created_at

### 8. Payment
- Maps to `payments` table
- Relationships: ManyToOne with Citizen and ServiceApplication
- Fields: transactionId, paymentMethod, amount, currency, paymentStatus, gateway details, refund details
- Enums: PaymentMethod, PaymentStatus, RefundStatus
- Indexes: citizen_id, application_id, transaction_id, payment_status, payment_date

### 9. Feedback
- Maps to `feedback` table
- Relationship: ManyToOne with Citizen
- Fields: feedbackType, subject, message, rating, category, status, response
- Enums: FeedbackType, FeedbackStatus, Priority
- Indexes: citizen_id, feedback_type, status, created_at

## Features

✅ All entities extend BaseEntity for common fields
✅ Proper JPA annotations (@Entity, @Table, @Column, etc.)
✅ Database indexes defined matching schema
✅ Relationships configured (ManyToOne with proper foreign keys)
✅ Enums used for status fields
✅ Lombok annotations for getters/setters
✅ Proper data types matching database schema

## Next Steps

1. Create Repository interfaces for each entity
2. Create DTO classes for API responses
3. Create MapStruct mappers
4. Create Service layer
5. Create REST Controllers


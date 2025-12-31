# Department API Information Collection Template

**Purpose**: Template for collecting department API information needed for connector configuration

**Use Case**: AI-PLATFORM-05 - Auto Application Submission Post-Consent

---

## Information to Collect from Each Department

Fill out this template for each department/scheme that needs API integration:

---

### Department Information

**Department Name**: _______________________  
**Scheme Code**: _______________________  
**Contact Person**: _______________________  
**Contact Email**: _______________________  
**Contact Phone**: _______________________  
**Date Collected**: _______________________

---

### API Endpoint Information

**Base URL**: 
```
Example: https://api.health.rajasthan.gov.in
```

**Endpoint Path** (for application submission):
```
Example: /v1/applications/submit
```

**Full Endpoint URL**:
```
Example: https://api.health.rajasthan.gov.in/v1/applications/submit
```

**API Protocol**:
- [ ] REST
- [ ] SOAP
- [ ] API Setu
- [ ] Other: _______________

---

### Authentication Information

**Authentication Type**:
- [ ] API Key
- [ ] OAuth 2.0
- [ ] Basic Authentication
- [ ] WS-Security (for SOAP)
- [ ] Other: _______________

**Authentication Details**:

**For API Key**:
- API Key: _______________________
- Header Name: _______________________ (e.g., `X-API-Key`)
- Location: Header / Query Parameter / Other

**For OAuth 2.0**:
- Token URL: _______________________
- Client ID: _______________________
- Client Secret: _______________________
- Scope: _______________________
- Grant Type: _______________________

**For Basic Auth**:
- Username: _______________________
- Password: _______________________

**For WS-Security**:
- Username: _______________________
- Password: _______________________
- WSDL URL: _______________________

---

### API Request Format

**Request Method**: 
- [ ] POST
- [ ] PUT
- [ ] GET
- [ ] Other: _______________

**Content Type**:
- [ ] application/json
- [ ] application/xml
- [ ] application/x-www-form-urlencoded
- [ ] Other: _______________

**Request Payload Structure**:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Required Fields**:
1. _______________________
2. _______________________
3. _______________________

**Optional Fields**:
1. _______________________
2. _______________________

**Field Mapping Requirements**:
- Do field names need to match exactly? Yes / No
- Any special formatting required? _______________________
- Any field transformations needed? _______________________

---

### API Response Format

**Success Response Structure**:
```json
{
  "status": "success",
  "application_number": "...",
  "message": "..."
}
```

**Success Response Fields**:
- Application Number Field: _______________________
- Status Field: _______________________
- Error Message Field (if any): _______________________

**Error Response Structure**:
```json
{
  "status": "error",
  "error_code": "...",
  "message": "..."
}
```

**Common Error Codes**:
1. _______________________ - _______________________
2. _______________________ - _______________________

---

### Special Requirements

**Rate Limiting**:
- Requests per minute: _______________________
- Requests per hour: _______________________
- Any throttling rules? _______________________

**Timeouts**:
- Connection timeout (seconds): _______________________
- Read timeout (seconds): _______________________

**Retry Policy**:
- Should we retry on failure? Yes / No
- Which status codes to retry? _______________________
- Maximum retries: _______________________

**Additional Headers Required**:
```
Header Name: Value
Example: X-Request-ID: {{uuid}}
```

---

### Testing Information

**Test Environment Endpoint**:
```
Example: https://test-api.health.rajasthan.gov.in/v1/applications/submit
```

**Test Credentials**:
- API Key / Token: _______________________
- Valid Test Application ID: _______________________

**Sample Request**:
```bash
curl -X POST https://test-api... \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```

**Sample Response**:
```json
{
  "status": "success",
  "application_number": "APP-2024-001234"
}
```

---

### Documentation

**API Documentation URL**: _______________________  
**WSDL URL** (for SOAP): _______________________  
**Postman Collection**: _______________________  
**Swagger/OpenAPI Spec**: _______________________

---

### Notes

**Additional Information**:
```
Any other relevant information, special requirements, or notes:
```

---

## How to Use This Template

1. **Fill out one template per department/scheme**
2. **Save as**: `DEPARTMENT_API_INFO_[DEPARTMENT_NAME].md`
3. **Share with**: Development team for connector configuration
4. **Update**: Connector configuration using `scripts/update_connector_config.py`

---

## Example: Health Department

**Department Name**: Health Department  
**Scheme Code**: CHIRANJEEVI  
**Base URL**: `https://api.health.rajasthan.gov.in`  
**Endpoint Path**: `/v1/applications/submit`  
**Auth Type**: OAuth 2.0  
**Content Type**: application/json  

**Payload Example**:
```json
{
  "application_id": "APP-2024-001234",
  "scheme_code": "CHIRANJEEVI",
  "beneficiary": {
    "name": "Ram Kumar",
    "dob": "1980-01-15",
    "aadhaar": "123456789012"
  }
}
```

---

**Template Version**: 1.0  
**Last Updated**: 2024-12-30


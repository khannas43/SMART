# Testing the Auth Endpoint

## Step 1: Restart the Service

The AuthController was just created, so you need to restart the service:

```bash
# Stop the current service (Ctrl+C in the terminal where it's running)

# Then restart:
mvn clean spring-boot:run
```

**Important:** Use `mvn clean spring-boot:run` (not just `mvn spring-boot:run`) to ensure the new controller is compiled.

---

## Step 2: Verify the Endpoint is Available

After restarting, you can verify the endpoint exists in two ways:

### Option A: Check Swagger UI

1. Open: `http://localhost:8081/citizen/api/v1/swagger-ui.html`
2. Look for **"Authentication"** section in the list of API groups
3. You should see **POST /auth/test-token** endpoint

### Option B: Check OpenAPI JSON

1. Open: `http://localhost:8081/citizen/api/v1/v3/api-docs`
2. Search for "Authentication" or "/auth/test-token"
3. If you see it in the JSON, the endpoint is available

### Option C: Direct API Test

You can also test it directly using curl or browser:

```bash
# Using curl:
curl -X POST "http://localhost:8081/citizen/api/v1/auth/test-token?username=test-user"

# Or open in browser:
http://localhost:8081/citizen/api/v1/auth/test-token?username=test-user
```

---

## Step 3: Use the Test Token Endpoint

Once the service is restarted and you see the "Authentication" section:

1. Expand the **Authentication** section
2. Click on **POST** `/auth/test-token`
3. Click **Try it out**
4. (Optional) Change the `username` parameter or leave default "test-user"
5. Click **Execute**
6. Copy the `token` value from the response

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzUxMiJ9...",
    "tokenType": "Bearer",
    "username": "test-user",
    "expiresIn": "24 hours"
  },
  "message": "Test token generated successfully. Use this token in the 'Authorize' button in Swagger UI."
}
```

---

## Step 4: Authorize in Swagger UI

1. Click the **Authorize** button (🔒) at the top right of Swagger UI
2. In the "Value" field, enter: `Bearer <your-token>`
   - Replace `<your-token>` with the token from Step 3
   - Example: `Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0ZXN0LXVzZXI...`
3. Click **Authorize**
4. Click **Close**

Now all protected endpoints will use this token automatically!

---

## Troubleshooting

### Still don't see "Authentication" section?

1. **Make sure you restarted the service** - New controllers only appear after restart
2. **Check for compilation errors** - Look at the console output when starting
3. **Clear browser cache** - Try hard refresh (Ctrl+F5) on Swagger UI page
4. **Check the OpenAPI JSON** - Visit `/v3/api-docs` to see if the endpoint is there

### Compilation errors?

If you see errors about `ApiResponse`, make sure the DTOs are compiled. Run:
```bash
mvn clean compile
```

Then restart with:
```bash
mvn spring-boot:run
```


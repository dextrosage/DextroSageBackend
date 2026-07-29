# DextroSage Backend API Documentation (Web Devs Guide)

A simple, professional API documentation for web and mobile frontend developers (React, Angular, Vue, Flutter, Android, iOS) integrating with the **DextroSage FastAPI Backend**.

---

# Base URL

### Local Development
```http
http://localhost:3000
```

### Interactive API Documentation (Swagger UI)
```http
http://localhost:3000/docs
```

---

# Authentication

The backend uses **JWT Bearer Tokens** with **Refresh Token Rotation**.

### Token Types

| Token Type | Response Field | Purpose | Lifetime |
|---|---|---|---|
| **Access Token** | `accesstoken` | Pass in `Authorization` header for protected routes | `30 minutes` |
| **Refresh Token** | `refreshtoken` | Pass in `Authorization` header to get new tokens at `/auth/refresh` | `7 days` |

### Headers Format

For protected endpoints:
```http
Authorization: Bearer <access_token>
```

For `/auth/refresh`:
```http
Authorization: Bearer <refresh_token>
```

---

# Authentication Endpoints (`/auth`)

---

## 1. GET /auth/week5

### Description
Health/ping test route.

### Auth Required
No

### Response (`200 OK`)
```json
{
  "status": "From week 5"
}
```

---

## 2. POST /auth/signup

### Description
Registers a new user. The backend automatically generates a username and password, saving them and dispatching an email notification to the registered user.

### Auth Required
**Yes** (Requires Admin Access Token)

### Headers
```http
Authorization: Bearer <admin_access_token>
```

### Request Body
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "USER"
}
```
*Note: `role` can be `"ADMIN"` or `"USER"`.*

### Response (`201 Created`)
```json
{
  "status": "Entry successful",
  "email": "john@example.com"
}
```

### Errors
- `401 Unauthorized`: Missing, expired, or invalid token.
- `403 Forbidden`: Authenticated user does not have `ADMIN` role (`{"detail": "Admin priviledges needed"}`).
- `409 Conflict`: Email already exists.
- `422 Unprocessable Entity`: Validation failure (invalid email format).

---

## 3. POST /auth/login

### Description
Authenticates user with username, password, and role. Returns tokens and a `phone_required` flag upon success.

### Auth Required
No

### Request Body
```json
{
  "username": "USR-A1B2C3D4",
  "password": "GeneratedPassword123!",
  "role": "USER"
}
```

### Response (`200 OK`)
```json
{
  "accesstoken": "<jwt_access_token>",
  "refreshtoken": "<jwt_refresh_token>",
  "phone_required": true,
  "profile_required": true,
  "pwd_change_required": true,
  "role": "USER"
}
```
*Note: If `pwd_change_required` is `true`, the frontend must prompt the user to update their temporary password using the `PATCH /auth/change/password` endpoint first before checking `phone_required`.*

### Errors
- `401 Unauthorized`: Invalid credentials or mismatched role.

---

## 4. PATCH /auth/verify/phone

### Description
Registers and associates a 10-digit phone number for the currently authenticated user.

### Auth Required
**Yes** (Requires Access Token)

### Headers
```http
Authorization: Bearer <access_token>
```

### Request Body
```json
{
  "phno": "9876543210"
}
```
*Note: `phno` must be exactly 10 characters.*

### Response (`200 OK`)
```json
{
  "status": "9876543210 added Successfully"
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `422 Unprocessable Entity`: Validation failure (phone length != 10 or missing field).

---

## 5. PATCH /auth/change/password

### Description
Registers a new password replacing the temporary password assigned on account creation.

### Auth Required
**Yes** (Requires Access Token)

### Headers
```http
Authorization: Bearer <access_token>
```

### Request Body
```json
{
  "password": "NewSecurePassword123!"
}
```

### Response (`200 OK`)
```json
{
  "status": "Password added Successfully"
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `422 Unprocessable Entity`: Validation failure.

---

## 6. POST /auth/refresh

### Description
Exchanges a valid refresh token for a new pair of access and refresh tokens. Rotates stored token hash in database.

### Auth Required
**Yes** (Requires Refresh Token)

### Headers
```http
Authorization: Bearer <refresh_token>
```

### Response (`200 OK`)
```json
{
  "accesstoken": "<new_jwt_access_token>",
  "refreshtoken": "<new_jwt_refresh_token>"
}
```

### Errors
- `401 Unauthorized`: Invalid, expired, or already revoked refresh token.

---

## 7. POST /auth/logout

### Description
Logs out the user by removing their active session refresh token from the database.

### Auth Required
**Yes** (Requires Access Token)

### Headers
```http
Authorization: Bearer <access_token>
```

### Response (`200 OK`)
```json
{
  "status": "Logout successful"
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `404 Not Found`: Active session not found in database.

---

## 8. POST /auth/sadmin/signup

### Description
Registers a new user account in the system. This endpoint is restricted strictly to Super Administrators. The backend automatically generates credentials, registers the record, and dispatches them to the user's email address.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Request Body
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "USER"
}
```
*Note: `role` can be `"ADMIN"`, `"USER"`, or `"SADMIN"`.*

### Response (`201 Created`)
```json
{
  "status": "Entry successful",
  "email": "jane@example.com"
}
```

### Errors
- `401 Unauthorized`: Missing, expired, or invalid token.
- `403 Forbidden`: Authenticated user is not a Super Admin (`{"detail": "Super Admin priviledges needed"}`).
- `409 Conflict`: Email, username, or phone already exists.
- `422 Unprocessable Entity`: Validation failure.

---

## 9. POST /auth/add/profile

### Description
Creates and saves a profile for the currently logged-in user. On first login, the user must submit their developer profile using this endpoint.

### Auth Required
**Yes** (Requires Access Token)

### Headers
```http
Authorization: Bearer <access_token>
```

### Request Body
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "linkedin": "https://linkedin.com/in/username",
  "github": "https://github.com/username",
  "skills": ["React", "TypeScript", "FastAPI"],
  "experience": [
    {
      "company": "Tech Corp",
      "designation": "Software Engineer",
      "start_date": "2024-01-01",
      "end_date": null,
      "currently_working": true
    }
  ],
  "education": [
    {
      "college": "State University",
      "degree": "Bachelor of Technology",
      "branch": "Computer Science",
      "start_date": "2020-08-01",
      "end_date": "2024-05-31"
    }
  ],
  "address": {
    "street": "123 Main St",
    "city": "Techville",
    "state": "California",
    "country": "USA",
    "pincode": "94016"
  }
}
```

### Response (`200 OK`)
```json
{
  "status": "profile created"
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `422 Unprocessable Entity`: Validation failure.

---

## 10. GET /auth/credentials

### Description
Retrieves the logged-in user's name, email, registered phone number (or `null`), and verification requirement status flags.

### Auth Required
**Yes** (Requires Access Token)

### Headers
```http
Authorization: Bearer <access_token>
```

### Response (`200 OK`)
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phno": "9876543210",
  "phone_required": false,
  "profile_required": false,
  "pwd_change_required": false
}
```
*Note: `phno` is `null` if the user has not verified a phone number yet.*

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `404 Not Found`: User not found.

---

# User Management Endpoints (`/user`)

Endpoints available to authenticated users (`USER` or `ADMIN`).

---

## 1. GET /user/members

### Description
Retrieves a list of all registered members.

### Auth Required
**Yes** (Access Token)

### Response (`200 OK`)
```json
[
  {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "phno": "9876543210",
    "email": "john@example.com",
    "role": "USER"
  }
]
```

---

## 2. GET /user/sessions

### Description
Retrieves all active session IDs belonging to the currently authenticated user.

### Auth Required
**Yes** (Access Token)

### Response (`200 OK`)
```json
[
  {
    "session_id": "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
  }
]
```

---

## 3. DELETE /user/delete/session/{session_id}/user

### Description
Revokes a specific active session belonging to the currently logged-in user.

### Auth Required
**Yes** (Access Token)

### Path Parameters
- `session_id` (string): The ID of the session to terminate.

### Response (`200 OK`)
```json
{
  "status": "Session deleted"
}
```

---

## 4. DELETE /user/delete/all/sessions/user

### Description
Revokes all active sessions for the currently logged-in user.

### Auth Required
**Yes** (Access Token)

### Response (`200 OK`)
```json
{
  "status": "All sessions deleted"
}
```

---

## 5. DELETE /user/delete/user/

### Description
Deletes the currently logged-in user's own account and clears all their sessions.

### Auth Required
**Yes** (Access Token)

### Response (`200 OK`)
```json
{
  "status": "User deleted"
}
```

---

## 6. GET /user/profile

### Description
Retrieves the profile details of the currently logged-in user.

### Auth Required
**Yes** (Access Token)

### Response (`200 OK`)
```json
{
  "linkedin": "https://linkedin.com/in/username",
  "github": "https://github.com/username",
  "skills": ["React", "TypeScript", "FastAPI"],
  "experience": [
    {
      "company": "Tech Corp",
      "designation": "Software Engineer",
      "start_date": "2024-01-01",
      "end_date": null,
      "currently_working": true
    }
  ],
  "education": [
    {
      "college": "State University",
      "degree": "Bachelor of Technology",
      "branch": "Computer Science",
      "start_date": "2020-08-01",
      "end_date": "2024-05-31"
    }
  ],
  "address": {
    "street": "123 Main St",
    "city": "Techville",
    "state": "California",
    "country": "USA",
    "pincode": "94016"
  }
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `404 Not Found`: Profile not found.

---

## 7. GET /user/member/{user_id}/profile

### Description
Retrieves the profile details of another registered member/user by their `user_id`.

### Auth Required
**Yes** (Access Token)

### Path Parameters
- `user_id` (string): The ID of the user whose profile is to be retrieved.

### Response (`200 OK`)
```json
{
  "linkedin": "https://linkedin.com/in/username",
  "github": "https://github.com/username",
  "skills": ["React", "TypeScript", "FastAPI"],
  "experience": [
    {
      "company": "Tech Corp",
      "designation": "Software Engineer",
      "start_date": "2024-01-01",
      "end_date": null,
      "currently_working": true
    }
  ],
  "education": [
    {
      "college": "State University",
      "degree": "Bachelor of Technology",
      "branch": "Computer Science",
      "start_date": "2020-08-01",
      "end_date": "2024-05-31"
    }
  ],
  "address": {
    "street": "123 Main St",
    "city": "Techville",
    "state": "California",
    "country": "USA",
    "pincode": "94016"
  }
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `404 Not Found`: Profile not found for the given `user_id`.

---

# Admin Management Endpoints (`/admin`)

Endpoints restricted strictly to users with the **`ADMIN`** role. Non-admin users calling these endpoints will receive a `403 Forbidden` error.

---

## 1. GET /admin/members

### Description
Retrieves details of all users/members in the system.

### Auth Required
**Yes** (Admin Access Token)

### Response (`200 OK`)
```json
[
  {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "phno": "9876543210",
    "email": "john@example.com",
    "role": "USER"
  }
]
```

### Errors
- `403 Forbidden`: `{"detail": "Admin priviledges needed"}`

---

## 2. GET /admin/member/sessions

### Description
Retrieves all active sessions of the currently logged-in administrator.

### Auth Required
**Yes** (Admin Access Token)

### Response (`200 OK`)
```json
[
  {
    "session_id": "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
  }
]
```

---

## 3. DELETE /admin/delete/session/{session_id}/member

### Description
Deletes/invalidates a specific session belonging to the currently logged-in administrator.

### Auth Required
**Yes** (Admin Access Token)

### Path Parameters
- `session_id` (string): The ID of the session to delete.

### Response (`200 OK`)
```json
{
  "status": "Session deleted"
}
```

---

## 4. DELETE /admin/delete/all/sessions/member/

### Description
Clears all active sessions for the currently logged-in administrator.

### Auth Required
**Yes** (Admin Access Token)

### Response (`200 OK`)
```json
{
  "status": "All sessions deleted"
}
```

---

## 5. DELETE /admin/delete/members

### Description
Deletes the currently logged-in administrator's account completely and purges all their active sessions.

### Auth Required
**Yes** (Admin Access Token)

### Response (`200 OK`)
```json
{
  "status": "User deleted"
}
```

---

## 6. GET /admin/member/{user_id}/profile

### Description
Retrieves the profile details of any registered member/user by their `user_id`.

### Auth Required
**Yes** (Admin Access Token)

### Path Parameters
- `user_id` (string): The ID of the user whose profile is to be retrieved.

### Response (`200 OK`)
```json
{
  "linkedin": "https://linkedin.com/in/username",
  "github": "https://github.com/username",
  "skills": ["React", "TypeScript", "FastAPI"],
  "experience": [
    {
      "company": "Tech Corp",
      "designation": "Software Engineer",
      "start_date": "2024-01-01",
      "end_date": null,
      "currently_working": true
    }
  ],
  "education": [
    {
      "college": "State University",
      "degree": "Bachelor of Technology",
      "branch": "Computer Science",
      "start_date": "2020-08-01",
      "end_date": "2024-05-31"
    }
  ],
  "address": {
    "street": "123 Main St",
    "city": "Techville",
    "state": "California",
    "country": "USA",
    "pincode": "94016"
  }
}
```

### Errors
- `401 Unauthorized`: Invalid or expired access token.
- `403 Forbidden`: User is not an administrator.
- `404 Not Found`: Profile not found for the given `user_id`.

---

# Super Admin Management Endpoints (`/super-admin`)

Endpoints restricted strictly to users with the **`SADMIN`** role. Non-sadmin users calling these endpoints will receive a `403 Forbidden` error.

---

## 1. GET /super-admin/member/{user_id}/sessions

### Description
Retrieves all active sessions of a specified member by their `user_id`.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Path Parameters
- `user_id` (string): The ID of the targeted user.

### Response (`200 OK`)
```json
[
  {
    "session_id": "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
  }
]
```

---

## 2. DELETE /super-admin/delete/session/{session_id}/member

### Description
Deletes/invalidates a specified member's active session.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Path Parameters
- `session_id` (string): The ID of the session to delete.

### Response (`200 OK`)
```json
{
  "status": "Session deleted"
}
```

---

## 3. DELETE /super-admin/delete/all/sessions/member/{user_id}

### Description
Clears all active sessions for a specified member by `user_id`.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Path Parameters
- `user_id` (string): Target user ID.

### Response (`200 OK`)
```json
{
  "status": "All sessions deleted"
}
```

---

## 4. DELETE /super-admin/delete/{user_id}/members

### Description
Deletes a member account completely and purges all their sessions.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Path Parameters
- `user_id` (string): Target user ID to delete.

### Response (`200 OK`)
```json
{
  "status": "User deleted"
}
```

---

## 5. GET /super-admin/member/sessions

### Description
Retrieves all active session IDs of the currently logged-in super administrator.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Response (`200 OK`)
```json
[
  {
    "session_id": "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
  }
]
```

---

## 6. DELETE /super-admin/delete/all/sessions/member

### Description
Revokes all active sessions for the currently logged-in super administrator.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Response (`200 OK`)
```json
{
  "status": "All sessions deleted"
}
```

---

## 7. DELETE /super-admin/delete/members

### Description
Deletes the currently logged-in super administrator's own account and clears all their sessions.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Response (`200 OK`)
```json
{
  "status": "User deleted"
}
```

---

## 8. GET /super-admin/member/profile

### Description
Retrieves the profile details of the currently logged-in super administrator.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Response (`200 OK`)
Same as `GET /user/profile`.

---

## 9. GET /super-admin/member/{user_id}/profile

### Description
Retrieves the profile details of a specified member by `user_id`.

### Auth Required
**Yes** (Requires Super Admin Access Token)

### Headers
```http
Authorization: Bearer <super_admin_access_token>
```

### Path Parameters
- `user_id` (string): The ID of the user whose profile is to be retrieved.

### Response (`200 OK`)
```json
{
  "linkedin": "https://linkedin.com/in/username",
  "github": "https://github.com/username",
  "skills": ["React", "TypeScript", "FastAPI"],
  "experience": [
    {
      "company": "Tech Corp",
      "designation": "Software Engineer",
      "start_date": "2024-01-01",
      "end_date": null,
      "currently_working": true
    }
  ],
  "education": [
    {
      "college": "State University",
      "degree": "Bachelor of Technology",
      "branch": "Computer Science",
      "start_date": "2020-08-01",
      "end_date": "2024-05-31"
    }
  ],
  "address": {
    "street": "123 Main St",
    "city": "Techville",
    "state": "California",
    "country": "USA",
    "pincode": "94016"
  }
}
```

---

# Authentication Flow

```text
 User Credentials ────────► POST /auth/login ────────► Receive Tokens (accesstoken, refreshtoken) & phone_required
                                                                 │
                                                                 ├───► phone_required == true? ──► PATCH /auth/verify/phone
                                                                 │                                            │
                                                                 ▼                                            ▼
                                                    Store Tokens in Client Storage ◄──────────────────────────┘
                                                                 │
                                                                 ▼
                                                    Call Protected Endpoints
                                                   (Header: Bearer accesstoken)
                                                                 │
                                                                 ▼
 Access Token Expired? ◄─────────────────────────────── Is Access Token Expired?
         │
        YES
         │
         ▼
POST /auth/refresh (Header: Bearer refreshtoken)
         │
         ├───► Success (200): Save new tokens, retry original request
         └───► Failed (401): Clear storage & Redirect to Login Screen
```

---

# Validation Rules

| Field | Endpoint | Constraint | Frontend Notes |
|---|---|---|---|
| `name` | `POST /auth/signup` | String | Full name |
| `email` | `POST /auth/signup` | Valid Email format | Must be unique |
| `role` | Signup / Login | `"ADMIN"` or `"USER"` | Case sensitive |
| `phno` | `PATCH /auth/verify/phone` | Exactly 10 characters | Phone number verification |

---

# Frontend Integration Examples

### JavaScript Fetch Example

```javascript
const API_URL = "http://localhost:8000";

// Login and conditionally handle phone verification
async function loginAndInit(username, password, role) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail);

  localStorage.setItem("accesstoken", data.accesstoken);
  localStorage.setItem("refreshtoken", data.refreshtoken);

  // If phone number verification is required, prompt user
  if (data.phone_required) {
    console.log("Redirecting to phone number verification page...");
  }
}

// Verify phone
async function verifyPhoneNumber(phoneNumber) {
  const token = localStorage.getItem("accesstoken");
  const res = await fetch(`${API_URL}/auth/verify/phone`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ phno: phoneNumber })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail);
  return data;
}
```

---

# Error Handling

| Status Code | Cause | Frontend Action |
|---|---|---|
| `401 Unauthorized` | Token expired / invalid credentials | Call `/auth/refresh` or redirect user to login page |
| `403 Forbidden` | Non-admin calling `/admin/*` route | Show "Access Denied" message |
| `404 Not Found` | Session or user not found | Show error notification |
| `409 Conflict` | Email or phone number exists | Highlight input field |
| `422 Unprocessable Entity` | Validation error (e.g. invalid phone) | Display validation message |
| `500 Server Error` | Database/server error | Show fallback "Try again later" error |

---

# API Summary Table

| Method | Endpoint | Auth Required | Role Required | Description |
|---|---|---|---|---|
| `GET` | `/auth/week5` | No | Public | Ping / Health check |
| `POST` | `/auth/signup` | **Yes** | **ADMIN** | Register user (Dispatches credentials via email) |
| `POST` | `/auth/sadmin/signup` | **Yes** | **SADMIN** | Register user, admin, or sadmin account |
| `POST` | `/auth/login` | No | Public | Login & receive tokens & phone/profile status |
| `PATCH` | `/auth/verify/phone` | **Yes** | USER / ADMIN / SADMIN | Register user phone number |
| `POST` | `/auth/add/profile` | **Yes** | USER / ADMIN / SADMIN | Create user/admin/sadmin profile |
| `GET` | `/auth/credentials` | **Yes** | USER / ADMIN / SADMIN | Retrieve user name, phno, and verification requirements |
| `POST` | `/auth/refresh` | **Yes** | Refresh Token | Refresh token pair |
| `POST` | `/auth/logout` | **Yes** | Access Token | Invalidate current session |
| `GET` | `/user/members` | **Yes** | USER / ADMIN / SADMIN | View list of all members |
| `GET` | `/user/sessions` | **Yes** | USER / ADMIN / SADMIN | View own active sessions |
| `DELETE` | `/user/delete/session/{session_id}/user` | **Yes** | USER / ADMIN / SADMIN | Delete own specific session |
| `DELETE` | `/user/delete/all/sessions/user` | **Yes** | USER / ADMIN / SADMIN | Delete all own active sessions |
| `DELETE` | `/user/delete/user/` | **Yes** | USER / ADMIN / SADMIN | Delete own account |
| `GET` | `/admin/members` | **Yes** | **ADMIN** | View list of all members |
| `GET` | `/admin/member/sessions` | **Yes** | **ADMIN** | View admin's own active sessions |
| `DELETE` | `/admin/delete/session/{session_id}/member` | **Yes** | **ADMIN** | Delete admin's own specific session |
| `DELETE` | `/admin/delete/all/sessions/member/` | **Yes** | **ADMIN** | Delete all own sessions of admin |
| `DELETE` | `/admin/delete/members` | **Yes** | **ADMIN** | Delete admin's own account |
| `GET` | `/super-admin/member/{user_id}/sessions` | **Yes** | **SADMIN** | View member's active sessions |
| `GET` | `/super-admin/member/sessions` | **Yes** | **SADMIN** | View super admin's own active sessions |
| `DELETE` | `/super-admin/delete/session/{session_id}/member` | **Yes** | **SADMIN** | Delete a member's specific session |
| `DELETE` | `/super-admin/delete/all/sessions/member/{user_id}` | **Yes** | **SADMIN** | Delete all sessions of a member |
| `DELETE` | `/super-admin/delete/all/sessions/member` | **Yes** | **SADMIN** | Delete all own sessions of super admin |
| `DELETE` | `/super-admin/delete/{user_id}/members` | **Yes** | **SADMIN** | Delete a member's account |
| `DELETE` | `/super-admin/delete/members` | **Yes** | **SADMIN** | Delete super admin's own account |
| `GET` | `/super-admin/member/profile` | **Yes** | **SADMIN** | View super admin's own profile details |
| `GET` | `/super-admin/member/{user_id}/profile` | **Yes** | **SADMIN** | View member's profile details |

---

# Complete Website Flow & Webpages Guide

If you want to build the frontend website from scratch to work with these backend endpoints, here is how the pages look, how they behave, and how the endpoint validation flows step-by-step:

## 1. Authentication & Signup
*   **Sign Up Screen (`POST /auth/signup`)**:
    *   **Access Restricted**: Only users with the **`ADMIN`** role can register new users.
    *   **Fields**: `name` (text input), `email` (email input), and `role` (`"USER"` or `"ADMIN"` dropdown).
    *   **Behavior**: When the admin submits this form, it registers the account and sends the auto-generated password directly to the user's email address.
*   **Sign In Screen (`POST /auth/login`)**:
    *   **Fields**: `username` (user email), `password` (text/password input), and `role` (`"USER"` or `"ADMIN"` selector).
    *   **Response Payload**: Returns `accesstoken`, `refreshtoken`, `phone_required` (boolean), and `profile_required` (boolean).
    *   **Client Actions**: Store tokens in client storage (`localStorage` / cookies) and immediately evaluate the validation flags.

---

## 2. Post-Login Verification Wizard (Conditional Flow)
After successful login, the frontend intercepts the user and runs them through a sequential wizard. Users are blocked from accessing the main dashboards until both requirements are satisfied.

### Step A: Phone Number Registration (`PATCH /auth/verify/phone`)
*   **Trigger**: If the login response returns `phone_required: true`.
*   **Screen**: Displays a phone number input text field.
*   **Constraints**: Enforces a 10-digit number validation.
*   **Submit**: Sends `{ "phno": "9876543210" }` with the access token. On success, transitions to the profile wizard (Step B) if `profile_required: true`, otherwise redirects directly to the Dashboard.

### Step B: Developer Profile Setup (`POST /user/add/profile` or `POST /admin/add/profile`)
*   **Trigger**: If `profile_required: true` (either from login response directly, or after completing Step A).
*   **Screen**: A detailed profile configuration wizard split into 5 sections:
    1.  **Professional Links** (LinkedIn & GitHub URL fields):
        *   Required inputs.
        *   Allows free-form URL entries. If the user omits the protocol (e.g. types `www.linkedin.com` or `github.com`), the client automatically prepends `https://` on submission to prevent double-prefixing.
    2.  **Developer Skills**: A single text input accepting a comma-separated list of skills (e.g. `React, TypeScript`).
    3.  **Mailing Address**: Street/Landmark, City, State, Country, and Pincode (all fields are required).
    4.  **Work History (Optional)**: A sub-form (Company, Designation, Start Date, End Date, Active checkbox) with an "Add Experience" button that appends entries to a local list.
    5.  **Academic Records (At Least 1 Required)**:
        *   A sub-form (College, Degree, Branch, Start Date, End Date) with an "Add Education" button.
        *   **Validation UX**: If the user tries to submit the form without adding an academic record, the browser natively prevents submission and displays a native **"Please fill in this field."** validation tooltip pointing directly to the College / School text field.
        *   **Helper**: If the user fills out the text fields but forgets to click "Add Education", the client automatically packages the typed inputs as the required record on submission.
    *   **Submit**: Calls `/admin/add/profile` for admin users, or `/user/add/profile` for standard users. On success, redirects to the corresponding dashboard.

---

## 3. Standard User Portal (`/user`)
Logged-in users with the `USER` role see a layout with two main tabs:

### Tab 1: Members Directory (Dashboard)
*   **Path**: `GET /user/members`
*   **Screen**: A grid of member cards showcasing their Name, Email, and Phone number.
*   **CV Preview**: Clicking any member card opens a fullscreen detailed CV view of that person, displaying their LinkedIn/GitHub links, skills, address details, academic timeline, and professional experience timeline.
    *   **Endpoint**: Fetches developer CV via `GET /user/member/{user_id}/profile`.

### Tab 2: Profile Settings (Profile)
*   **Screen**: Displays the user's account details (Name, Email, Phone number).
*   **Own CV Preview**: Includes a **"View Developer Profile"** button. Clicking this fetches and displays their own completed CV details (`GET /user/profile`).
*   **Active Sessions**: Displays a card list of all active sessions for this account (`GET /user/sessions`), excluding the current browser session.
    *   **Revoke Single Session**: Clicking "Revoke" deletes that specific session (`DELETE /user/delete/session/{session_id}/user`).
    *   **Revoke All Sessions**: Terminating all other sessions (`DELETE /user/delete/all/sessions/user`) revokes all active tokens, signing the user out.
*   **Delete Account**: A "Delete My Account" button prompts confirmation and deletes the user's registry completely (`DELETE /user/delete/user/`).

---

## 4. Admin Management Portal (`/admin`)
Logged-in users with the `ADMIN` role see a layout with two main tabs:

### Tab 1: Member Management (Dashboard)
*   **Path**: `GET /admin/members`
*   **Screen**: A grid of member cards, similar to the user portal, but with administration buttons.
*   **Register Member Modal**: A button to open a registration popup to create new user/admin accounts (`POST /auth/signup`).
*   **Admin Card Actions**:
    1.  **Click Card (CV Preview)**: Opens a fullscreen CV page displaying the member's developer profile details (`GET /admin/member/{user_id}/profile`).
    2.  **Sessions Button**: Navigates to a member session inspector page (`GET /admin/member/{user_id}/sessions`) showing all active sessions for that user (excluding the active admin session), with a button to revoke individual session IDs (`DELETE /admin/delete/session/{session_id}/member`).
    3.  **Delete Button**: Opens confirmation modal to delete the user account completely (`DELETE /admin/delete/{user_id}/members`).

### Tab 2: Admin Profile Settings (Profile)
*   **Screen**: Displays administrator account details.
*   **Own CV Preview**: Clicking the **"View Developer Profile"** button fetches and displays their own CV details (`GET /user/profile`).
*   **Active Sessions**: Displays all active sessions for the administrator account, allowing them to selectively revoke specific sessions or revoke all other sessions.

---

## Step-by-Step UI Flow Examples

Here is exactly what a user and an admin see from the moment they open the website:

### A. Standard User UI Flow

1.  **Website Opens (Root / Login Screen)**:
    *   **What is shown**: A clean, centered card with username and password text fields, a Role selector toggled to `"USER"`, and a "Sign In" button.
    *   **Action**: User inputs credentials and clicks "Sign In".
2.  **Redirect Guard (Intermediate Phase)**:
    *   **What is shown**: A loading screen check.
    *   **Scenario A (New User - Password Change Required)**:
        *   The login endpoint returns `pwd_change_required: true`.
        *   **Transition**: The website immediately displays the **Update Your Password Screen**.
        *   **What is shown**: Input fields requesting a new password and confirmation. Once submitted (`PATCH /auth/change/password`), the flow continues to phone verification.
    *   **Scenario B (New User - Unverified Phone)**:
        *   The login endpoint returns `phone_required: true`.
        *   **Transition**: The website immediately updates to show the **Phone Registration Screen**.
        *   **What is shown**: An input field requesting a 10-digit number. Once the user enters the number and submits, the wizard progresses to the Profile Setup.
    *   **Scenario C (Existing User - Missing Profile)**:
        *   The login response returns `phone_required: false` but `profile_required: true`.
        *   **Transition**: The website immediately displays the **Complete Your Profile Screen**.
        *   **What is shown**: A multi-section form with professional links, skills, address inputs, and work/academic sub-forms. The user must fill out all required fields, add at least one academic record, and click "Submit Profile and Finish".
    *   **Scenario D (Returning User - Fully Verified)**:
        *   The login response returns both `phone_required: false` and `profile_required: false`.
        *   **Transition**: The website redirects directly to the **User Dashboard**.
3.  **User Dashboard (Members Directory)**:
    *   **What is shown**: A navigation sidebar with two links: "Dashboard" and "Profile". The main content area displays a grid of cards representing all registered organization members (admins and standard users). Each card displays the member's Name, Email, and Phone number.
    *   **Action**: Clicking a card switches the view to a fullscreen **Developer CV Page** displaying the selected member's comprehensive developer history (skills, address, academic credentials, and work history). Clicking the "Back" button returns them to the directory grid.
4.  **User Profile Page**:
    *   **What is shown**:
        *   **Account Details Card**: Displays the user's name, email, and verified phone number.
        *   **View Profile Button**: Clicking this retrieves and shows their own developer CV details.
        *   **Active Sessions Card**: Displays cards for other active login sessions (session ID, login time, and location/browser details). Each session has a "Revoke" button. A main button at the top allows the user to terminate all other sessions.
        *   **Delete Account Card**: A button to permanently delete their own account.

---

### B. Admin User UI Flow

1.  **Website Opens (Root / Login Screen)**:
    *   **What is shown**: The same sign-in portal. The administrator inputs credentials, selects `"ADMIN"` as the Role, and clicks "Sign In".
2.  **Redirect Guard (Intermediate Phase)**:
    *   **Transition**: Similar check for `pwd_change_required`, `phone_required` and `profile_required`. If required, the admin is routed through the Password Change, Phone Verification, and Profile Setup screens. Once verified, the website redirects to the **Admin Dashboard**.
3.  **Admin Dashboard (Member Management)**:
    *   **What is shown**: A navigation sidebar with "Dashboard" and "Profile" links. The main view displays:
        *   **Action Bar**: A "Register Member" button that opens a registration form modal to create new accounts.
        *   **Directory Grid**: A grid of member cards with three active control buttons:
            1.  **Card Body Click**: Opens the member's fullscreen **Developer CV Page** (showing their detailed developer credentials and timeline).
            2.  **Sessions Button**: Navigates to a dedicated **Member Sessions Page** showing all active sessions for that member. Clicking "Revoke" on a session terminates that session for the user.
            3.  **Delete Button**: Completely deletes the user's account from the database.
4.  **Admin Profile Page**:
    *   **What is shown**: Shows the administrator's account information, a "View Developer Profile" button to view their own completed admin CV, and a list of active login sessions for the admin account to revoke.

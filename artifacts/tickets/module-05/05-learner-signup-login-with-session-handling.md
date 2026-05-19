# Title

Learner signup/login with session handling

# Context (Why)

Slice 2 moves beyond the anonymous demo and gives learners their own account context. A signed-in learner is needed for search personalization later and for attaching bookings to the correct user account in `My Bookings`.

# Scope (What)

- Create learner signup and login endpoints.
- Create session handling that lets the application identify the signed-in learner on later requests.
- Support logout.
- Persist learner account records.

# Interface Contract (Inputs/Outputs/Data Shapes)

- Signup request:
  - `POST /api/learners/signup`
  ```json
  {
    "name": "string",
    "email": "string",
    "password": "string"
  }
  ```
- Signup success: `201`
  ```json
  {
    "learner_id": "uuid",
    "email": "string",
    "name": "string"
  }
  ```
- Login request:
  - `POST /api/learners/login`
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- Login success: `200`
  ```json
  {
    "learner_id": "uuid",
    "email": "string",
    "name": "string",
    "session_status": "active"
  }
  ```
- Logout request:
  - `POST /api/learners/logout`
- Error responses:
  - `400` invalid or missing fields
  - `401` invalid credentials
  - `409` duplicate email on signup

# Acceptance Criteria (Testable Conditions)

- Given a new email address, when a client sends `POST /api/learners/signup` with valid fields, then the API returns `201` and the learner record is stored.
- Given an existing learner account, when a client sends `POST /api/learners/login` with correct credentials, then the API returns `200` and creates an active session.
- Given invalid login credentials, when `POST /api/learners/login` is called, then the API returns `401`.
- Given a duplicate email is used during signup, when `POST /api/learners/signup` is called, then the API returns `409`.
- Given a signed-in learner, when `POST /api/learners/logout` is called, then the session is cleared and later protected learner-only requests no longer treat that session as active.

# Constraints (Rules to Follow)

- Use the project's existing auth/session pattern if one exists; otherwise choose one session approach and use it consistently for all learner-auth tickets.
- Do not invent social login or password-reset flows.
- Use the existing database connection and error format.

# Anti-Scope (What NOT to Build)

- No provider auth.
- No password reset.
- No OAuth or social login.
- No role-management beyond learner access.
- No booking search or list behavior in this ticket.

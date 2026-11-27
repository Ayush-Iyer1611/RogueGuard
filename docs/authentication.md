# RogueGuard local authentication

RogueGuard now includes a local operator sign-in gate for its synthetic analyst workbench.

## First launch

When the local auth table is empty, the app presents an initial setup screen. The first operator creates the administrator account. Public self-registration is then disabled; subsequent launches show the sign-in form.

Usernames are normalised to lowercase and restricted at account creation to 3–32 letters, digits, dots, underscores, or hyphens. Passwords must contain at least 12 characters and are limited to 256 UTF-8 bytes during setup.

## Password storage

The app does not store plaintext passwords. Each password is hashed with PBKDF2-HMAC-SHA256 using 600,000 iterations and an independently generated 16-byte random salt. The salt and derived hash are stored in the local SQLite database.

## SQL injection controls

Authentication queries bind usernames and other values with SQLite placeholders. User input is never concatenated into SQL statements. The password value is passed to the password-hash function; it is not used to construct a query.

The automated authentication tests include a login attempt using a SQL-injection-shaped username (operator' OR 1=1 --) and verify that it is treated as a literal value and does not authenticate.

## Failed-login handling

Five consecutive failed attempts for a normalised username trigger a five-minute temporary lockout. A successful login clears that username's failed-attempt record. Failed sign-ins use a generic message so the UI does not reveal whether a username exists.

## Session and security boundaries

- Authentication is local to this Streamlit application and its SQLite database.
- The authenticated username and role are held in Streamlit session state. Reloading the browser session may require the operator to sign in again.
- The lockout is keyed by username, not source IP; this is a simple local-demo control, not an enterprise anti-abuse system.
- The initial operator is the only account created by this interface. There is no SSO, MFA, password reset, self-service registration, or authenticated multi-user approval.
- A person with operating-system access to the local database or project files can tamper with this local prototype.
- This feature does not protect the app as a public internet service. Do not expose the local Streamlit server to an untrusted network or enter real production credentials.

The separate response-lab reviewer field remains an analyst-entered label. It is not linked to this local account and must not be described as enforced two-person enterprise authentication.

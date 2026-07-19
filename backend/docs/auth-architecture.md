**CHEQ Auth Architecture Plan**

The authentication structure is between the Resource Server and Confirmation Server.

We can implement an OAuth 2.0 Client Credentials Grant. The confirmation server will call the resource server, and no human will log in at this step. The client credentials grant is the OAuth 2.0 flow designed for this.

**Actors and Roles**

| Actors | Roles |
| :---- | :---- |
| Resource Server | Protects the endpoints, validates tokens using Auth0’s cached JWKS public key |
| Confirmation Server | Holds client credentials, requests access tokens and calls the resource server |
| Authorisation Server(Auth0) | Provides the client credentials at registration(via Dashboard/Application),issues tokens via token endpoint, manages client registry  |

**Credentials Setup**

Auth0 generates the client\_id and client\_secret for the confirmation server when it is registered as a Machine to Machine application in the Auth0 dashboard. These credentials are stored in the confirmation server's environment variables since this is only a proof of concept.

**Auth0**

The following will be handled by Auth0

1. Client registry database
2. The endpoints that issue access tokens
3. Auth0 publishes its public signing keys via JWKS, resource server fetches and caches these to validate JWTs

**Confirmation Server Set up**

What needs to be built for the Confirmation Server:

1. **Token Lifecycle Management:** The Confirmation Server requests an access token from Auth0, caches it, and checks its expiration before making calls to the Resource Server. If the cached token is expired or close to expiring, it requests a new one.

2. **User Authentication & Identity Mapping:** The user authenticates locally to the Confirmation Server (e.g., via session, PIN, or biometrics). When calling the Resource Server, the Confirmation Server maps this local user identity to the transaction payload so the Resource Server has audit logs of who authorized the request.

3. **Secure API Communication:** All API calls to the Resource Server must include the valid cached machine-to-machine JWT access token.

**Cheq Object & Replay Protection**

The CHEQ object represents a digital check and must prevent duplication, tampering, and repudiation.

1. **Unique Identifiers:** Each CHEQ object contains a unique transaction ID (`cheq_id` UUID) and a timestamp window (`created_at` / `expires_at`).
2. **Double Signatures:**
   - **Signature 1 (Resource Server):** Cryptographically signs the CHEQ upon creation to certify its authenticity.
   - **Signature 2 (Confirmation Server):** Cryptographically signs the CHEQ after user authorization, ensuring non-repudiation.
3. **Idempotency & Replay Checks:** The Resource Server tracks processed `cheq_id`s in a database to ensure no transaction can be replayed or processed more than once.

**Full Authentication Sequence**

1. **Token Lifecycle / Initialization:**
   - Confirmation Server checks cache for valid M2M token.
   - If expired/missing, Confirmation Server → Auth0: `POST /oauth/token { client_id, client_secret }`
   - Auth0 → Confirmation Server: `{ access_token, expires_in }`

2. **Fetching CHEQ:**
   - Confirmation Server → Resource Server: `GET {resource_uri}/cheq` with Header `Authorization: Bearer <access_token>`
   - Resource Server: Validates M2M JWT using cached Auth0 JWKS public keys.
   - Resource Server → Confirmation Server: `{ CHEQ object }` (already containing Signature 1)

3. **User Confirmation:**
   - End-User authenticates with Confirmation Server.
   - User reviews the CHEQ details and approves/rejects it.
   - Confirmation Server signs the CHEQ payload (generating Signature 2).

4. **Submission & Verification:**
   - Confirmation Server → Resource Server: `POST {resource_uri}?accept` or `?reject` with Header `Authorization: Bearer <access_token>` + request payload `{ signed_cheq, user_id }`
   - Resource Server:
     - Validates M2M JWT.
     - Verifies `cheq_id` has not been processed before (idempotency check) and hasn't expired.
     - Cryptographically verifies both Signature 1 and Signature 2.
   - Resource Server → Confirmation Server: `{ 200 OK }`
   - Resource Server executes the transaction/booking.

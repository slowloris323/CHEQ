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

What needs to be built for the Confirmation Server

1. Token request on start-up:  confirmation server will call the Auth0 token endpoint using the client credentials and cache the returned access token

2. Calls to the resource server will include this access token

**Cheq Object**

The CHEQ object will have 2 signatures:

1. By the resource server, indicating that it issued a legitimate transaction

2.  For non-repudiation, the confirmation server signs the CHEQ object after the user confirms

Signature 1: The Resource server signs the Cheq on creation  
Signature 2: Confirmation server signs after the user's decision

**Full Authentication Sequence**

Confirmation Server → Auth0: POST /oauth/token { client\_id, client\_secret }  
Auth0 → Confirmation Server: { access\_token }

Confirmation Server → Resource Server: GET {resource\_uri}/cheq Bearer \<access\_token\>  
Resource Server: validates JWT locally using cached Auth0 JWKS public key.  
Resource Server → Confirmation Server: { CHEQ object }

\[User reviews and confirms\]

Confirmation Server → Resource Server: POST {resource\_uri}?accept or ?reject Bearer \<access\_token\> \+ signed CHEQ

Resource Server: validates JWT locally using cached Auth0 JWKS public key  
Resource Server → Confirmation Server: { 200 OK }

\[Resource server verifies both signatures, executes booking\]  

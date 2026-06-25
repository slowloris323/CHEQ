**CHEQ Auth Architecture Plan** 

The authentication structure is between the Resource Server and Confirmation Server.

We can implement an OAuth 2.0 Client Credentials Grant. The confirmation server will call the resource server, and no human will log in at this step. The client credentials grant is the OAuth 2.0 flow designed for this. 

**Actors and Roles**

| Actors | Roles |
| :---- | :---- |
| Resource Server | Issue the client ID and secret, issue the JWT Access tokens and protect the endpoints |
| Confirmation Server | Holds client credentials, requests access tokens and the cheq object |

**Credentials Set up** 

The resource server will create the credentials and share them with the confirmation server

1. The resource server generates the client\_id and client\_secret for the confirmation server  
2. The credentials will be stored in a database( the client secret would be encrypted)  
3. The client \_id and the client\_secret will be stored in the confirmation server’s environment variable 

**Resource Server Set up**

What needs to be built for the Resource Server

1. Client registry database   
   This will store the clients :  
- Client\_id   
- Client\_secret   
- Scopes  
- Creation  
2. The endpoints:  
- OAuth token endpoint that will take the grant type, client\_id and the client\_secret  
3. JWT validation middleware: this is intended to protect the endpoints by validating the token and scope to make sure the token is not expired, and the scope meets the requirements for the endpoint

**Confirmation Server Set up**

What needs to be built for the Confirmation Server

1. Token request on start-up:  confirmation server will call the OAuth token endpoint on the resource server using the client credentials and cache the return access token   
     
2. Calls to the resource server will include this access token

**Cheq Object**

The cheq object will have 2 signatures:

1. By the resource server indicating that it issued a legitimate transaction  
     
2.  For non-repudiation, the confirmation server signs the CHEQ object after the user confirms 

Signature 1: The Resource server signs the Cheq on creation  
Signature 2: Confirmation server signs after the user's decision

**Full Authentication Sequence**

\[Confirmation Server\] 								\[Resource Server\]   
1\. POST /oauth/token { client\_id, client\_secret } ──────\>   
\<────── { access\_token (JWT) }

 2\. GET {resource\_uri}/cheq Authorisation: Bearer ──────\>   
\<────── { CHEQ object (signed by resource server) } 

3\. \[User reviews and confirms\] 

4\. POST {resource\_uri}?accept/reject Authorisation: Bearer\<ac\_tkn\> Body: { CHEQ \+ confirmation ──────\> server signature }   
\<────── { 200 OK } 

5\. \[Resource server verifies both signatures, executes booking\]


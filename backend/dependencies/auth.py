import os
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.logger import get_logger

logger = get_logger("auth")
security = HTTPBearer()

# Pin the accepted Clerk issuer in production (https://clerk.insightgraph.dev).
# Without this, get_current_user() below trusts whatever issuer a token
# *claims* to be from and fetches that issuer's own JWKS to verify it - so a
# validly-signed token from a *different* Clerk instance (e.g. the dev
# instance, pk_test_/sk_test_) is accepted just as readily as a real
# production token, and its `sub` gets written into this same production
# database as a brand new user. Leave CLERK_ISSUER unset for local dev
# against a local backend, where the token's real issuer is the dev instance.
EXPECTED_ISSUER = os.environ.get("CLERK_ISSUER")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Validates the Clerk JWT token from the Authorization header and returns the user ID.
    """
    token = credentials.credentials
    try:
        unverified_claims = jwt.decode(token, options={"verify_signature": False})

        issuer = unverified_claims.get("iss")
        if not issuer:
            raise HTTPException(status_code=401, detail="Token missing issuer")

        if EXPECTED_ISSUER and issuer != EXPECTED_ISSUER:
            logger.warning(f"Rejected token from untrusted issuer: {issuer}")
            raise HTTPException(status_code=401, detail="Token issued by an untrusted authority")

        jwks_url = f"{issuer}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,                                                                          
            issuer=issuer
        )
        
        user_id = data.get("sub")
        if not user_id:
             raise HTTPException(status_code=401, detail="Token missing subject")
             
        return user_id
        
    except jwt.PyJWKClientError as e:
        logger.error(f"JWKS Error: {e}")
        raise HTTPException(status_code=401, detail="Could not verify key")
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth Validation Error: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")

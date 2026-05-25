import os
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.logger import get_logger

logger = get_logger("auth")
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Validates the Clerk JWT token from the Authorization header and returns the user ID.
    """
    token = credentials.credentials
    try:
        # Decode without verification just to extract the 'iss' (issuer)
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        
        issuer = unverified_claims.get("iss")
        if not issuer:
            raise HTTPException(status_code=401, detail="Token missing issuer")
            
        # Dynamically fetch the JWKS payload from Clerk
        jwks_url = f"{issuer}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Verify the signature cryptographically
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None, # By default, Next.js Clerk token requests might not set an explicit aud.
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
    except Exception as e:
        logger.error(f"Auth Validation Error: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")

import jwt
from pydantic import BaseModel, Field, ValidationError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from git_pal.config import load_config

EXPECTED_ISSUER = "git-pal-licensing"

class LicenseData(BaseModel):
    sub: str = Field(..., description="Subject (e.g., user email)")
    iss: str = Field(..., description="Issuer (e.g., 'git-pal-licensing')")
    exp: int = Field(..., description="Expiration timestamp (epoch seconds)")
    features: list[str] = Field(default_factory=list, description="Enabled features")
    nbf: int | None = None
    iat: int | None = None
    purchase_id: str | None = None

def _load_public_key() -> RSAPublicKey:
    try:
        public_key_pem = load_config().license.public_key.encode("utf-8")
        public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
        if not isinstance(public_key, RSAPublicKey):
            raise ValueError("Key is not a valid RSA Public Key.")
        return public_key
    except Exception as e:
        raise ValueError(f"Failed to load license public key from config: {e}")

def verify_license() -> LicenseData:
    """
    Offline verification of the configured JWT (RS256), enforcing issuer/exp/nbf.
    Returns LicenseData on success or raises ValueError.
    """
    public_key = _load_public_key()
    token = load_config().license_token
    try:
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            issuer=EXPECTED_ISSUER,
            options={"require": ["exp", "iss"]},
        )
        return LicenseData(**payload)
    except jwt.ExpiredSignatureError:
        raise ValueError("License has expired.")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid license issuer.")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid license: {e}")
    except ValidationError as e:
        raise ValueError(f"License data is malformed: {e}")

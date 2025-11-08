# SPDX-License-Identifier: MIT
from typing import Optional, List
import time
import hashlib
import os
import json
from pathlib import Path

import jwt
from pydantic import BaseModel, Field, ValidationError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from git_pal.config import load_config

EXPECTED_ISSUER = "git-pal-licensing"

class LicenseData(BaseModel):
    sub: str = Field(..., description="Subject (email)")
    iss: str = Field(..., description="Issuer")
    exp: int = Field(..., description="Expiry (epoch seconds)")
    features: List[str] = Field(default_factory=list)
    nbf: Optional[int] = None
    iat: Optional[int] = None
    purchase_id: Optional[str] = None

def _load_public_key() -> RSAPublicKey:
    try:
        public_key_pem = load_config().license.public_key.encode("utf-8")
        key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
        if not isinstance(key, RSAPublicKey):
            raise ValueError("Key is not an RSA public key")
        return key
    except Exception as e:
        raise ValueError(f"Failed to load license public key from config: {e}")

def verify_license() -> LicenseData:
    """Offline RS256 verify with issuer/exp required."""
    key = _load_public_key()
    token = load_config().license_token
    try:
        payload = jwt.decode(
            token,
            key=key,
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

# ---- Monetize helpers (breadcrumb only; no telemetry) ------------------------
def _machine_hash() -> str:
    base = "|".join([os.name, os.getenv("COMPUTERNAME",""), os.getenv("HOSTNAME",""), str(Path.home())])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

def write_receipt(purchase_id: Optional[str], sub: str, target_dir: Path) -> Path:
    """Write a local receipt.json (anti-leak breadcrumb)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "sub_hint": sub[:2] + "***" + (sub[-2:] if "@" in sub else ""),
        "purchase_id": purchase_id or "",
        "machine": _machine_hash(),
        "ts": int(time.time()),
    }
    p = target_dir / "receipt.json"
    p.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return p

import pytest
import time
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    # Safety: prevent accidental network calls in tests (offline licensing)
    # Note: This is a placeholder for network prevention
    # In production tests, you might use pytest-socket or similar
    pass

@pytest.fixture
def rsa_key_pair():
    """Generate RSA key pair for testing."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    pub = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv, pub

@pytest.fixture
def valid_license_token(rsa_key_pair):
    """Generate a valid license token."""
    from git_pal.licensing import EXPECTED_ISSUER
    priv, pub = rsa_key_pair
    now = int(time.time())
    token = jwt.encode(
        {"sub": "test@example.com", "iss": EXPECTED_ISSUER, "exp": now + 3600, "features": ["pro"]},
        priv,
        algorithm="RS256",
    )
    return token, pub

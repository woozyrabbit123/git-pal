import time
import jwt
from pathlib import Path

from git_pal import config as config_mod
from git_pal.licensing import verify_license, EXPECTED_ISSUER

def test_verify_license_happy(tmp_path, rsa_key_pair, monkeypatch):
    priv, pub = rsa_key_pair
    now = int(time.time())
    token = jwt.encode(
        {"sub": "u@example.com", "iss": EXPECTED_ISSUER, "exp": now + 3600, "features": ["pro"]},
        priv,
        algorithm="RS256",
    )
    # Write config
    cfg_path = tmp_path / "config.toml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(
        f'license_token = "{token}"\n\n[license]\npublic_key = """{pub.decode()}"""\n',
        encoding="utf-8",
    )
    # Point loader
    original_get_config_path = config_mod.get_config_path
    config_mod.get_config_path = lambda: cfg_path
    config_mod.load_config.cache_clear()

    try:
        # Verify
        data = verify_license()
        assert data.sub == "u@example.com"
        assert "pro" in data.features
    finally:
        config_mod.get_config_path = original_get_config_path
        config_mod.load_config.cache_clear()

def test_verify_license_expired(tmp_path, rsa_key_pair):
    priv, pub = rsa_key_pair
    now = int(time.time())
    # Token expired 1 hour ago
    token = jwt.encode(
        {"sub": "u@example.com", "iss": EXPECTED_ISSUER, "exp": now - 3600, "features": ["pro"]},
        priv,
        algorithm="RS256",
    )
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text(
        f'license_token = "{token}"\n\n[license]\npublic_key = """{pub.decode()}"""\n',
        encoding="utf-8",
    )

    original_get_config_path = config_mod.get_config_path
    config_mod.get_config_path = lambda: cfg_path
    config_mod.load_config.cache_clear()

    try:
        verify_license()
        assert False, "Should have raised ValueError for expired license"
    except ValueError as e:
        assert "expired" in str(e).lower()
    finally:
        config_mod.get_config_path = original_get_config_path
        config_mod.load_config.cache_clear()

def test_verify_license_invalid_issuer(tmp_path, rsa_key_pair):
    priv, pub = rsa_key_pair
    now = int(time.time())
    # Wrong issuer
    token = jwt.encode(
        {"sub": "u@example.com", "iss": "wrong-issuer", "exp": now + 3600, "features": ["pro"]},
        priv,
        algorithm="RS256",
    )
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text(
        f'license_token = "{token}"\n\n[license]\npublic_key = """{pub.decode()}"""\n',
        encoding="utf-8",
    )

    original_get_config_path = config_mod.get_config_path
    config_mod.get_config_path = lambda: cfg_path
    config_mod.load_config.cache_clear()

    try:
        verify_license()
        assert False, "Should have raised ValueError for invalid issuer"
    except ValueError as e:
        assert "issuer" in str(e).lower()
    finally:
        config_mod.get_config_path = original_get_config_path
        config_mod.load_config.cache_clear()

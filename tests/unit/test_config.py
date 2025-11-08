from pathlib import Path
import sys
import textwrap
from git_pal.config import get_config_path, load_config

def test_load_config_roundtrip(tmp_path, monkeypatch):
    # Point config path to tmp
    cfg_dir = tmp_path
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(cfg_dir))
        cfg_path = cfg_dir / "git-pal" / "config.toml"
    else:
        cfg_path = cfg_dir / ".config" / "git-pal" / "config.toml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = textwrap.dedent("""
    license_token = "ey.fake.token"

    [license]
    public_key = \"\"\"-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
fake
-----END PUBLIC KEY-----\"\"\"
    """)
    cfg_path.write_text(cfg, encoding="utf-8")

    # Patch function to point to our path
    def _fake_path():
        return cfg_path
    from git_pal import config as config_mod
    original_get_config_path = config_mod.get_config_path
    config_mod.get_config_path = _fake_path
    # Clear the LRU cache
    config_mod.load_config.cache_clear()

    try:
        # Load
        c = load_config()
        assert c.license.public_key.startswith("-----BEGIN PUBLIC KEY-----")
        assert isinstance(c.license_token, str)
        assert c.license_token == "ey.fake.token"
    finally:
        # Restore
        config_mod.get_config_path = original_get_config_path
        config_mod.load_config.cache_clear()

def test_config_path_linux(monkeypatch):
    """Test that config path is correct on Linux."""
    monkeypatch.setattr(sys, "platform", "linux")
    from pathlib import Path
    # Reload to pick up platform change
    path = get_config_path()
    assert ".config" in str(path)
    assert "git-pal" in str(path)
    assert path.name == "config.toml"

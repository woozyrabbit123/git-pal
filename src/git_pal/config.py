import sys
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, Field, ValidationError

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

class LicenseConfig(BaseModel):
    public_key: str = Field(..., description="Public key (PEM) for license verification.")

class Config(BaseModel):
    license: LicenseConfig
    license_token: str = Field(..., description="User's license token (JWT/JWS).")

def get_config_path() -> Path:
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "git-pal" / "config.toml"
    return Path.home() / ".config" / "git-pal" / "config.toml"

@lru_cache(maxsize=1)
def load_config() -> Config:
    config_path = get_config_path()
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Config file not found. Please create {config_path}\nSee README.md for configuration details."
        )
    try:
        with config_path.open("rb") as f:
            raw = tomllib.load(f)
        return Config(**raw)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Error parsing TOML config {config_path}: {e}")
    except ValidationError as e:
        raise ValueError(f"Invalid configuration in {config_path}:\n{e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")

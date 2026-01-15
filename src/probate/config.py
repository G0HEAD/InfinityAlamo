from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import os

import yaml
from pydantic import BaseModel, Field, ValidationError


class RunConfig(BaseModel):
    timezone: str = "America/Chicago"
    default_mode: Literal["yesterday", "today"] = "yesterday"
    max_cases_per_run: int = 500
    rate_limit_seconds: float = 1.0
    retries: int = 3


class OutputConfig(BaseModel):
    base_dir: str = "output"
    pdf_dir: str = "data/pdfs"
    logs_dir: str = "logs"


class AuthConfig(BaseModel):
    type: Literal["none", "basic", "form", "token"] = "none"
    username_env: str | None = None
    password_env: str | None = None
    token_env: str | None = None


class CountyConfig(BaseModel):
    name: str
    enabled: bool = True
    connector: str
    portal_url: str
    mode: Literal["requests", "playwright"] = "requests"
    auth: AuthConfig = Field(default_factory=AuthConfig)


class AppConfig(BaseModel):
    run: RunConfig = Field(default_factory=RunConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    counties: list[CountyConfig]


def _validate_auth_env(auth: AuthConfig) -> list[str]:
    missing: list[str] = []
    if auth.type in {"basic", "form"}:
        if not auth.username_env:
            missing.append("username_env")
        elif not os.getenv(auth.username_env):
            missing.append(auth.username_env)
        if not auth.password_env:
            missing.append("password_env")
        elif not os.getenv(auth.password_env):
            missing.append(auth.password_env)
    if auth.type == "token":
        if not auth.token_env:
            missing.append("token_env")
        elif not os.getenv(auth.token_env):
            missing.append(auth.token_env)
    return missing


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    data = yaml.safe_load(config_path.read_text()) or {}
    try:
        config = AppConfig.parse_obj(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid config: {exc}") from exc

    errors: list[str] = []
    for county in config.counties:
        errors.extend(_validate_auth_env(county.auth))
    if errors:
        raise ValueError(f"Missing auth env values: {', '.join(sorted(set(errors)))}")
    return config

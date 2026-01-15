from __future__ import annotations

import importlib
from typing import Type

from probate.config import CountyConfig
from probate.connectors.base import BaseConnector


def get_connector(connector_name: str, config: CountyConfig) -> BaseConnector:
    module = importlib.import_module(f"probate.connectors.{connector_name}")
    connector_cls: Type[BaseConnector] = getattr(module, "Connector")
    return connector_cls(config)

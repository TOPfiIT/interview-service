from loguru import logger
from typing import Any, Callable

from fastapi import FastAPI
from src.dependencies.registrator import dependencies_container


def setup_dependencies(app: FastAPI, mapper: dict[Any, Callable] | None = None) -> None:
    logger.info("Setting up dependencies")
    logger.info(f"Dependencies container: {dependencies_container}")
    if mapper is None:
        mapper = dependencies_container
    for interface, dependency in mapper.items():
        app.dependency_overrides[interface] = dependency
    logger.info(f"Dependencies mapping: {app.dependency_overrides}")

import logging
import os

from dotenv import load_dotenv, find_dotenv
from typing import Any

logger = logging.getLogger(__name__)


def _load_env_file() -> None:
    """Load .env and warn if it does not exist."""
    env_path = find_dotenv(".env", usecwd=True)
    if not env_path:
        logger.warning(".env file not found. Using process environment and defaults")
        return

    load_dotenv(env_path)

    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")
    if LOGGING_LEVEL:
        logger.setLevel(LOGGING_LEVEL)

    logger.info("Loaded environment variables from %s", env_path)


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def get_env(name: str, default: Any | None = None, cast=str):
    """
    Read an environment variable with a default and logging.

    If the variable is not set, or casting fails, the default is returned
    and a warning is logged.
    """
    raw = os.getenv(name)

    if raw is None or raw == "":

        if default is None:
            logger.error("%s not set and no default provided", name)
            return None

        logger.warning("%s not set. Falling back to default %r", name, default)
        return default

    if cast is str:
        return raw

    try:
        return cast(raw)
    except Exception:
        if default is None:
            logger.error("%s has invalid value %r and no default provided", name, raw)
            return None

        logger.warning(
            "%s has invalid value %r. Falling back to default %r", name, raw, default
        )
        return default


_load_env_file()

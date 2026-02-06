import logging

from app.core.settings import get_settings

settings = get_settings()
log_level = settings.level_logging

_LEVELS: dict[str, int] = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def setup_logging(level: str = logging.INFO) -> None:
    if isinstance(level, str):
        normalized = level.strip().upper()
        level = _LEVELS.get(normalized, logging.INFO)

    logging.basicConfig(
        level=level, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

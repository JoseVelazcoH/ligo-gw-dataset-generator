import logging
from rich.logging import RichHandler
from typing import Any


FORMAT: str = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log: logging = logging.getLogger("rich")


class Logger:

    @staticmethod
    def info(message: Any) -> None:
        log.info(f'[white]{message}[/]', extra={"markup": True})

    @staticmethod
    def warning(message: Any) -> None:
        log.warning(f'[bold yellow]{message}[/]', extra={"markup": True})

    @staticmethod
    def error(message: Any) -> None:
        log.error(f'[bold red]{message}[/]', extra={"markup": True})

    @staticmethod
    def critical(message: Any) -> None:
        log.critical(f'[bold red]{message}[/]', extra={"markup": True})

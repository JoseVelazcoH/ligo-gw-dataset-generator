import logging
from rich.logging import RichHandler
from typing import Any


FORMAT: str = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log: logging = logging.getLogger("rich")


class Logger:
    verbose: bool = True

    @classmethod
    def set_verbose(cls, verbose: bool) -> None:
        cls.verbose = verbose

    @classmethod
    def info(cls, message: Any, verbose: bool = True) -> None:
        if not verbose and not cls.verbose:
            return
        log.info(f'[white]{message}[/]', extra={"markup": True})

    @classmethod
    def warning(cls, message: Any) -> None:
        log.warning(f'[bold yellow]{message}[/]', extra={"markup": True})

    @classmethod
    def error(cls, message: Any) -> None:
        log.error(f'[bold red]{message}[/]', extra={"markup": True})

    @classmethod
    def critical(cls, message: Any) -> None:
        log.critical(f'[bold red]{message}[/]', extra={"markup": True})

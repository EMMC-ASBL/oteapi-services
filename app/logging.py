"""Setup Python logging."""

from __future__ import annotations

import logging
import logging.config
import sys
from copy import copy
from typing import TYPE_CHECKING

from app.settings import settings

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, ClassVar, Literal, Protocol

    class DebugParam(Protocol):
        debug: bool

    class ColorizeMessageLambda(Protocol):
        def __call__(self, level_name: Any) -> str: ...


_ansi_colors = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "reset": 39,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}
"""Mapping of color names to ANSI color codes.

Copied verbatim from `click.termui._ansi_colors`.
"""


def _interpret_color(color: int | tuple[int, int, int] | str, offset: int = 0) -> str:
    """Interpret a color value.

    Function copied verbatim from `click.termui._interpret_color()`.
    """
    if isinstance(color, int):
        return f"{38 + offset};5;{color:d}"

    if isinstance(color, (tuple, list)):
        r, g, b = color
        return f"{38 + offset};2;{r:d};{g:d};{b:d}"

    return str(_ansi_colors[color] + offset)


def colorize_message(message: str, color: str) -> str:
    """Colorize a message with the given color.

    Parameters:
        message: The message to colorize.
        color: The color to use for the message.

    Returns:
        The colorized message.


    Minimized version of the function `click.termui.style()`.
    """
    try:
        return f"\033[{_interpret_color(color)}m{message}"
    except KeyError as exc:
        raise ValueError(f"Invalid color: {color}") from exc


class ColourizedFormatter(logging.Formatter):
    """
    A custom log formatter class that:

    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.

    Class copied from `uvicorn.logging.ColourizedFormatter` modified to minimize dependencies.
    """

    level_name_colors: ClassVar[dict[int, ColorizeMessageLambda]] = {
        5: lambda level_name: colorize_message(str(level_name), "blue"),
        logging.DEBUG: lambda level_name: colorize_message(str(level_name), "cyan"),
        logging.INFO: lambda level_name: colorize_message(str(level_name), "green"),
        logging.WARNING: lambda level_name: colorize_message(str(level_name), "yellow"),
        logging.ERROR: lambda level_name: colorize_message(str(level_name), "red"),
        logging.CRITICAL: lambda level_name: colorize_message(
            str(level_name), "bright_red"
        ),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
    ) -> None:
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)  # pragma: no cover

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        return True  # pragma: no cover

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(recordcopy)


class DefaultFormatter(ColourizedFormatter):
    """Default log formatter for DataSpaces Python logger.

    Class copied verbatim from `uvicorn.logging.DefaultFormatter`.
    """

    def should_use_colors(self) -> bool:
        return sys.stderr.isatty()  # pragma: no cover


def setup_logging() -> None:
    """Setup OTEAPI Services Python logging."""
    logging_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default_uvicorn": {
                "()": "app.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s [%(name)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "formatter": "default_uvicorn",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "DEBUG" if settings.debug else "INFO",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_dict)

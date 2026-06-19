"""CLI Interface System - Clean abstraction for user-facing messages."""

import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import ClassVar


class MessageType(Enum):
    """Types of user-facing messages."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROMPT = "prompt"
    RESULT = "result"
    HEADER = "header"
    SEPARATOR = "separator"


class OutputMode(Enum):
    """Output rendering modes."""

    PLAIN = "plain"
    COLORED = "colored"
    MINIMAL = "minimal"


class CLIInterface:
    """Centralized interface for all CLI user interactions.

    Handles formatting, logging, and output consistently.
    """

    # ANSI color codes
    COLORS: ClassVar = {
        MessageType.INFO: "\033[94m",  # Blue
        MessageType.SUCCESS: "\033[92m",  # Green
        MessageType.WARNING: "\033[93m",  # Yellow
        MessageType.ERROR: "\033[91m",  # Red
        MessageType.PROMPT: "\033[96m",  # Cyan
        MessageType.RESULT: "\033[95m",  # Magenta
        MessageType.HEADER: "\033[1m",  # Bold
    }
    RESET: ClassVar = "\033[0m"

    def __init__(
        self,
        output_mode: OutputMode = OutputMode.COLORED,
        log_to_file: bool = True,
        log_level: int = logging.INFO,
    ) -> None:
        """Initialize the CLI interface.

        Args:
            output_mode: How to render output (colored, plain, minimal)
            log_to_file: Whether to log messages to file
            log_level: Logging level for file logs
        """
        self.output_mode = output_mode
        self.logger = self._setup_logging(log_to_file, log_level)

    def _setup_logging(self, log_to_file: bool, log_level: int) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("bld_generator")
        logger.setLevel(logging.DEBUG)

        if log_to_file:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(
                log_dir / f"bld_{datetime.now(tz=timezone.utc):%Y%m%d}.log",
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def _format_message(self, msg: str, msg_type: MessageType) -> str:
        """Format a message based on output mode."""
        if self.output_mode == OutputMode.MINIMAL:
            return msg

        if self.output_mode == OutputMode.COLORED and sys.stdout.isatty():
            color = self.COLORS.get(msg_type, "")
            return f"{color}{msg}{self.RESET}"

        # Plain mode - add prefixes
        prefixes = {
            MessageType.SUCCESS: "[✓] ",
            MessageType.ERROR: "[✗] ",
            MessageType.WARNING: "[!] ",
            MessageType.INFO: "[i] ",
        }
        prefix = prefixes.get(msg_type, "")
        return f"{prefix}{msg}"

    def message(self, msg: str, msg_type: MessageType = MessageType.INFO) -> None:
        """Display a general message to the user."""
        formatted = self._format_message(msg, msg_type)
        print(formatted)  # noqa: T201

        log_methods = {
            MessageType.ERROR: self.logger.error,
            MessageType.WARNING: self.logger.warning,
            MessageType.SUCCESS: self.logger.info,
            MessageType.INFO: self.logger.info,
        }
        log_method = log_methods.get(msg_type, self.logger.debug)
        log_method(msg)

    def success(self, msg: str) -> None:
        """Display a success message."""
        self.message(msg, MessageType.SUCCESS)

    def error(self, msg: str, exception: Exception | None = None) -> None:
        """Display an error message."""
        self.message(msg, MessageType.ERROR)
        if exception:
            self.logger.exception("Exception details:", exc_info=exception)

    def warning(self, msg: str) -> None:
        """Display a warning message."""
        self.message(msg, MessageType.WARNING)

    def info(self, msg: str) -> None:
        """Display an info message."""
        self.message(msg, MessageType.INFO)

    def header(self, msg: str, width: int = 60) -> None:
        """Display a header message."""
        if self.output_mode == OutputMode.MINIMAL:
            print(msg)  # noqa: T201
        else:
            separator = "=" * width
            centered = msg.center(width)
            formatted_sep = self._format_message(separator, MessageType.HEADER)
            formatted_msg = self._format_message(centered, MessageType.HEADER)
            print(f"\n{formatted_sep}\n{formatted_msg}\n{formatted_sep}")  # noqa: T201
        self.logger.debug("Header: %s", msg)

    def separator(self, char: str = "-", width: int = 60) -> None:
        """Display a separator line."""
        if self.output_mode != OutputMode.MINIMAL:
            print(char * width)  # noqa: T201

    def result(self, label: str, value: object, indent: int = 0) -> None:
        """Display a labeled result."""
        indent_str = " " * indent
        formatted_label = self._format_message(f"{label}:", MessageType.RESULT)
        print(f"{indent_str}{formatted_label} {value}")  # noqa: T201
        self.logger.debug("%s: %s", label, value)

    def list_items(
        self,
        items: list[str],
        numbered: bool = False,
        indent: int = 2,
    ) -> None:
        """Display a list of items."""
        indent_str = " " * indent
        for i, item in enumerate(items, 1):
            if numbered:
                print(f"{indent_str}{i}. {item}")  # noqa: T201
            else:
                print(f"{indent_str}• {item}")  # noqa: T201
        self.logger.debug("listed %d items", len(items))

    def table(
        self,
        headers: list[str],
        rows: list[list[str]],
        col_widths: list[int] | None = None,
    ) -> None:
        """Display a simple table."""
        if not col_widths:
            col_widths = [
                max(len(str(row[i])) for row in [headers, *rows])
                for i in range(len(headers))
            ]

        header_row = " | ".join(
            str(h).ljust(w) for h, w in zip(headers, col_widths, strict=True)
        )
        sep = "-+-".join("-" * w for w in col_widths)

        print(self._format_message(header_row, MessageType.HEADER))  # noqa: T201
        print(sep)  # noqa: T201

        for row in rows:
            row_str = " | ".join(
                str(cell).ljust(w) for cell, w in zip(row, col_widths, strict=True)
            )
            print(row_str)  # noqa: T201

        self.logger.debug("Displayed table with %d rows", len(rows))

    def prompt(self, question: str, default: str | None = None) -> str:
        """Prompt user for input."""
        prompt_text = f"{question} [{default}]: " if default else f"{question}: "
        formatted_prompt = self._format_message(prompt_text, MessageType.PROMPT)
        response = input(formatted_prompt).strip()

        if not response and default:
            response = default

        self.logger.debug("Prompt '%s' -> '%s'", question, response)
        return response

    def confirm(self, question: str, default: bool = False) -> bool:
        """Ask for yes/no confirmation."""
        default_str = "Y/n" if default else "y/N"
        response = self.prompt(f"{question} ({default_str})", "").lower()

        if not response:
            return default
        return response.startswith("y")

    def choice(
        self,
        question: str,
        options: list[str],
        default: int | None = None,
    ) -> int:
        """Present multiple choice options."""
        self.info(question)
        self.list_items(options, numbered=True)

        while True:
            default_str = str(default) if default is not None else None
            response = self.prompt("Enter choice number", default_str)

            try:
                chosen = int(response)
                if 1 <= chosen <= len(options):
                    return chosen - 1  # Return 0-indexed
                self.error(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                self.error("Please enter a valid number")

    def progress(self, current: int, total: int, label: str = "Progress") -> None:
        """Display a simple progress indicator."""
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 40
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        print(  # noqa: T201
            f"\r{label}: [{bar}] {percentage:.1f}% ({current}/{total})",
            end="",
            flush=True,
        )

        if current >= total:
            print()  # noqa: T201

    def clear_screen(self) -> None:
        """Clear the console screen."""
        cmd = ["cls"] if os.name == "nt" else ["clear"]
        subprocess.run(cmd, check=False)
        self.logger.debug("Screen cleared")

    def debug(self, msg: str) -> None:
        """Log debug message (not shown to user unless verbose mode)."""
        self.logger.debug(msg)

    def blank_line(self, count: int = 1) -> None:
        """Print blank lines."""
        print("\n" * (count - 1))  # noqa: T201


# Example usage
if __name__ == "__main__":
    import time

    # Initialize interface
    ui = CLIInterface(output_mode=OutputMode.COLORED)

    # Different message types
    ui.header("3BLD Analytic Generator")
    ui.info("Application started successfully")
    ui.success("Settings loaded")
    ui.warning("Some comm files are disabled")
    ui.error("Failed to load spreadsheet", Exception("File not found"))

    ui.blank_line()
    ui.separator()

    # Results
    ui.result("Buffer", "UF")
    ui.result("Letter Scheme", "Speffz")

    ui.blank_line()

    # lists
    ui.info("Available buffers:")
    ui.list_items(["UF", "UB", "DF", "DB"], numbered=True)

    ui.blank_line()

    # Table
    ui.info("Comm Statistics:")
    ui.table(
        headers=["Buffer", "Count", "Learned"],
        rows=[
            ["UF", "384", "280"],
            ["UB", "384", "150"],
        ],
    )

    ui.blank_line()

    # Prompts
    name = ui.prompt("Enter your name", default="User")
    ui.info(f"Hello, {name}!")

    if ui.confirm("Do you want to continue?", default=True):
        ui.success("Continuing...")
    else:
        ui.warning("Operation cancelled")

    ui.blank_line()

    # Multiple choice
    options = ["Drill stickers", "Practice algs", "Generate scramble"]
    chosen_idx = ui.choice("What would you like to do?", options)
    ui.success(f"You selected: {options[chosen_idx]}")

    ui.blank_line()

    # Progress
    for i in range(1, 101):
        ui.progress(i, 100, "Loading")
        time.sleep(0.02)

    ui.success("All operations complete!")

# MoneyPrinterV2 - An Application that automates the process of making money online.
# Copyright (C) 2024  FujiwaraChoki
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from termcolor import colored

def error(message: str, show_emoji: bool = True) -> None:
    """
    Prints an error message.

    Args:
        message (str): The error message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "❌" if show_emoji else ""
    print(colored(f"{emoji} {message}", "red"))

def success(message: str, show_emoji: bool = True) -> None:
    """
    Prints a success message.

    Args:
        message (str): The success message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "✅" if show_emoji else ""
    print(colored(f"{emoji} {message}", "green"))

def info(message: str, show_emoji: bool = True) -> None:
    """
    Prints an info message.

    Args:
        message (str): The info message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "ℹ️" if show_emoji else ""
    print(colored(f"{emoji} {message}", "magenta"))

def warning(message: str, show_emoji: bool = True) -> None:
    """
    Prints a warning message.

    Args:
        message (str): The warning message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "⚠️" if show_emoji else ""
    print(colored(f"{emoji} {message}", "yellow"))

def question(message: str, show_emoji: bool = True) -> str:
    """
    Prints a question message and returns the user's input.

    Args:
        message (str): The question message
        show_emoji (bool): Whether to show the emoji

    Returns:
        user_input (str): The user's input
    """
    emoji = "❓" if show_emoji else ""
    return input(colored(f"{emoji} {message}", "magenta"))

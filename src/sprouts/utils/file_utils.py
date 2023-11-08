import logging
import json
import os

logger = logging.getLogger(__name__)


def read_file_string(filename: str) -> str:
    """Read the content of a file and return a string of its contents."""
    if verify_file(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return ""


def read_file_lines(filename: str) -> list[str]:
    """Read the content of a file and return its lines."""
    if verify_file(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    else:
        return []


def read_json(filename: str) -> dict:
    """Read the content of a json file and return its contents."""
    if verify_file(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {}


def verify_file(filename: str) -> str:
    """
    Check if a file exists in the given path and return it if found.

    If the file does not exist, iterate through a list of common file
    extensions and check if the file exists with each extension.
        If the file exists with any of the extensions, return the
        filename with the extension.

        If the file does not exist with any of the extensions, return
        an empty string.

    Args:
        filename (str): The name or path of the file to check.

    Returns:
        str: The filename with the extension if the file exists,
             otherwise an empty string.
    """
    # File extensions to iterate through incase user forgot the extensionaaaaaaaa
    # Sort by most used and opened (subjective)
    extensions = [
        ".txt",
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".md",
        ".csv",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".sh",
        ".bash",
        ".jpg",
        ".png",
        ".pdf",
        ".docx",
        ".xlsx",
        ".pptx",
        ".php",
        ".go",
        ".rb",
        ".xml",
        ".yml",
        ".yaml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".rst",
        ".log",
        ".vbs",
        ".bat",
        ".ps1",
        ".psm1",
        ".psd",
        ".zsh",
        ".fish",
        ".ksh",
        ".csh",
        ".tcsh",
        ".awk",
        ".sed",
        ".pl",
        ".pm",
        ".tcl",
        ".r",
        ".sql",
        ".sqlite",
        ".db",
        ".db3",
        ".dbf",
        ".mdb",
        ".accdb",
        ".sdf",
        ".ods",
        ".xls",
    ]

    file = ""
    if os.path.exists(filename):
        # The file exists, so return the filename
        logger.debug(f"File (relative path) exists: {filename}")
        file = filename
    elif os.path.exists(os.path.abspath(filename)):
        # The file exists, so return the filename
        logger.debug(f"File (absolute path) exists: {filename}")
        file = os.path.abspath(filename)
    else:
        # The file does not exist, so iterate through the extensions
        for extension in extensions:
            if os.path.exists(filename + extension):
                logger.debug(f"File (relative path) exists: {filename + extension}")
                file = filename + extension
                break
            elif os.path.exists(os.path.abspath(filename + extension)):
                logger.debug(
                    f"File (absolute path) exists: {os.path.abspath(filename + extension)}"
                )
                file = os.path.abspath(filename + extension)
                break

    return file


def get_file_dir(filepath: str) -> str:
    """
    Get the directory of a filepath.

    Args:
        filepath (str): The path to the module.

    Returns:
        str: The directory of the module.
    """
    return os.path.dirname(os.path.abspath(filepath))


def get_parent_dir(filepath: str, times: int = 1) -> str:
    """
    Get the parent directory of a file.

    Args:
        filepath (str): The path to the file.
        times (int, Optional): The number of times to traverse up the
            directory tree.

    Returns:
        str: The parent directory of the file.
    """
    path = os.path.abspath(filepath)
    for _ in range(times + 1):
        path = os.path.dirname(path)

    logger.debug(
        f"Traversed [{filepath}] {times} times to get parent directoroy filepath: {path}"
    )
    return path


def join(*args: str) -> str:
    """
    Join multiple paths together.

    Args:
        *args (str): The paths to join.

    Returns:
        str: The joined paths.
    """
    return os.path.join(*args)

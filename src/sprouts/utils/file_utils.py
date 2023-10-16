import json
import os
import re


def read_file_string(filename: str) -> str:
    """Read the content of a file and return a string of its contents."""
    if exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()


def read_file_lines(filename: str) -> list[str]:
    """Read the content of a file and return its lines."""
    if exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]


def read_json(filename: str) -> dict:
    """Read the content of a json file and return its contents."""
    if exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)


def read_input_lines() -> list[str]:
    """Read input from the user and return a list of lines."""
    print("Enter a blank line to stop.")
    lines = []
    print("> ", end="")
    while True:
        # Read input from the user until a blank line is entered
        line = input("")
        if line == "":
            # A blank line was entered, so stop reading input
            break

        lines.append(line)

    # Strip all values in the list and return list of non-blank lines
    return [line.strip() for line in lines if line.strip() != ""]


def input_(
    valid_input: list[str] | str = "",
    invalid_input: list[str] | str = "",
    message: str = ">",
) -> str:
    """
    Read input from the user and return it if it is valid.

    `valid_input` is a `list` or regex pattern of valid inputs.
    `invalid_input` is a `list` or regex pattern of invalid inputs.
    Do not use both at the same time.

    Args:
        message: The message to display to the user for each
            input attempt.
        valid_input: A list or regex pattern of valid inputs.
        invalid_input: A list or regex pattern of invalid inputs.

    Returns:
        The user's input if it is valid.
    """
    # Convert valid and invalid input lists to lowercase
    if valid_input:
        if isinstance(valid_input, list):
            # List of valid input was provided and not a regex pattern
            # Convert all items in the list to lowercase
            valid_input = [str(item).casefold() for item in valid_input]
    elif invalid_input:
        if isinstance(invalid_input, list):
            # List of invalid input was provided and not a regex pattern
            # Convert all items in the list to lowercase
            invalid_input = [str(item).casefold() for item in invalid_input]
    elif valid_input and invalid_input:
        # Both valid and invalid input was provided
        raise ValueError(
            "Only `valid_input` or `invalid_input` can be used, " \
            "not both."
        )
    else:
        # Neither valid nor invalid input was provided
        raise ValueError("Either `valid_input` or `invalid_input` must be" \
                         "used.")

    while True:
        # Read input from the user and check that it is either in the
        # list or matches the regex pattern
        user_input = input(f"{message} ")
        invalid_message = "Invalid input, please try again."

        if isinstance(valid_input, list) or isinstance(invalid_input, list):
            # For lists of valid or invalid input instead of a regex pattern
            if invalid_input and (user_input.casefold() in invalid_input):
                # The user entered an invalid input from `invalid_input`,
                # so ask them to try again
                print(invalid_message)
                continue
            elif valid_input and (user_input.casefold() in valid_input):
                # The user entered a valid input, so return it
                return user_input
            else:
                # The user entered an invalid input, but it was not inside
                # `invalid_input`, still ask them to try again
                print(invalid_message)
                continue

        else:
            # For a regex pattern instead of a list of valid or invalid inputs
            if (valid_input and not re.search(valid_input, user_input)) or (
                invalid_input and re.search(invalid_input, user_input)
            ):
                # The user entered an invalid input, so ask them to try again
                print("Invalid input, please try again.")
                continue
            else:
                # The user entered a valid input, so return it
                return user_input


def exists(filename: str) -> str:
    """
    Check if a file exists in the given path. If the file does not exist, iterate through a list of common file extensions
    and check if the file exists with each extension. If the file exists with any of the extensions, return the filename
    with the extension. If the file does not exist with any of the extensions, return an empty string.

    Args:
        filename (str): The name of the file to check.

    Returns:
        str: The filename with the extension if the file exists, otherwise an empty string.
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
        file = filename
    elif os.path.exists(os.path.abspath(filename)):
        # The file exists, so return the filename
        file = os.path.abspath(filename)
    else:
        # The file does not exist, so iterate through the extensions
        for extension in extensions:
            if os.path.exists(filename + extension):
                file = filename + extension
                break
            elif os.path.exists(os.path.abspath(filename + extension)):
                file = os.path.abspath(filename + extension)
                break

    return file


def get_module_dir(filepath: str) -> str:
    """
    Get the directory of a module.

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
    for _ in range(times):
        path = os.path.dirname(path)

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
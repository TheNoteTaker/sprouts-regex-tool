import json
import os
import re
import string


def read_file_string(filename: str) -> str:
    """Read the content of a file and return a string of its contents."""
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error:\n\tFile '{filename}' not found.")
        return ""
    except Exception as e:
        print(f"Error reading file:\n\t{e}")
        return ""


def read_file_lines(filename: str) -> list[str]:
    """Read the content of a file and return its lines."""
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error:\n\tFile '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file:\n\t{e}")
        return []


def read_json(filename: str) -> dict:
    """Read the content of a json file and return its contents."""
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error:\n\tFile '{filename}' not found.")
        return {}
    except Exception as e:
        print(f"Error reading file:\n\t{e}")
        return {}


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
        message: str = ">"
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
            valid_input = [item.casefold() for item in valid_input]
    elif invalid_input:
        if isinstance(invalid_input, list):
            # List of invalid input was provided and not a regex pattern
            # Convert all items in the list to lowercase
            invalid_input = [item.casefold() for item in invalid_input]
    elif not valid_input or not invalid_input:
        # Neither valid nor invalid input was provided
        raise ValueError("Either `valid_input` or `invalid_input` must be "
                         "used.")
    else:
        # Both valid and invalid input was provided
        raise ValueError("Only `valid_input` or `invalid_input` can be used, "
                         "not both.")

    while True:
        # Read input from the user and check that is either in the
        # list or matches the regex pattern
        user_input = input(f"{message} ")

        if isinstance(valid_input, list) or isinstance(invalid_input, list):
            # For lists of valid or invalid input instead of a regex pattern
            if invalid_input and (user_input.casefold() in invalid_input):
                # The user entered an invalid input from `invalid_input`,
                # so ask them to try again
                print("Invalid input, please try again.")
                continue
            elif valid_input and (user_input.casefold() in valid_input):
                # The user entered a valid input, so return it
                return user_input
            else:
                # The user entered an invalid input, but it was not inside
                # `invalid_input`, still ask them to try again
                print("Invalid input, please try again.")
                continue

        else:
            # For a regex pattern instead of a list of valid or invalid inputs
            if ((valid_input and not re.search(valid_input, user_input))
                    or (invalid_input and
                        re.search(invalid_input, user_input))):
                # The user entered an invalid input, so ask them to try again
                print("Invalid input, please try again.")
                continue
            else:
                # The user entered a valid input, so return it
                return user_input


def exists(filename: str) -> str:
    """Return filename if the file exists, otherwise return ""."""
    # File extensions to iterate through incase user forgot the extension
    extensions = [".txt", ".json", ".csv"]
    file = ""
    if os.path.exists(filename):
        # The file exists, so return the filename
        file = filename
    else:
        # The file does not exist, so iterate through the extensions
        for extension in extensions:
            if os.path.exists(filename + extension):
                file = filename + extension
                break

    return file

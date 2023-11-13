import logging
import re

logger = logging.getLogger(__name__)


def split_delimited_string(data: str, delimiters: list = []) -> list[list[str]]:
    """
    Creates a nested `list` from a delimited list of values.

    A separator is a line which is blank (i.e. contains only
    whitespace), or contains a valid separator character as `-`,
    `=`, or `~`. The amount of separator characters does not
    matter.

    Args:
        data (str): String to split into sections.
        separators (list, optional): Delimiter values that indicate
            the start of a new section. Only the first value in each
            line will be checked against the values found in.
            Try to avoid passing " " as a separator as this can
            cause issues with splitting the data. Prefer using
            builtin `split()` method instead. Defaults to using
            `_identify_delimiters`.

    Returns:
        list[list[str]]: Nested `list` split into sections based on
            values found in `separators`.
    """
    # Set default separators if none given
    if not delimiters:
        try:
            delimiters, _, _ = identify_delimiters(data)
        except TypeError:
            # No delimiters found
            logger.debug(
                "No delimiters found in data. Likely only one "
                "section exists. Data wil only be split by newlines."
            )
            return data.strip().split("\n")

    # Create regex pattern from delimiters
    re_pattern = "|".join(delimiters)

    # Split initial data, then split by delimiters
    logger.debug(
        f"Using split_delimited_list function with regex pattern: {repr(re_pattern)}"
    )

    # Split data by delimiters, then remove newlines and create sections
    split_data = re.split(re_pattern, data)
    split_data = [section.split() for section in split_data]

    logger.debug(f"Split data into {len(split_data)} sections.")
    return split_data


def identify_delimiters(data: str | list[str]) -> tuple[dict, str, str] | None:
    """
    Uses regex patterns to try and identify a delimiter.

    If `data` is a string, then each value should be on a new line.
    This method will look for any non-alphabetic or non-numerical
    value at the beginning of a line or any line that contains two
    or more newline/carriage return characters.

    Args:
        data (str | list): Data to identify the delimiter of.

    Returns:
        tuple[dict, str, str] | None: A tuple containing a
            dictionary with the identified delimiters and their
            frequency, the most common delimiter, and the least
            common delimiter. If no delimiter is found, returns
            `None`.
    """
    # Regex pattern to find delimiters in a string
    regex_pattern = r"^[^a-zA-Z0-9\n]+$|(?:[\n\r]){2,}"

    # Convert data to a string if it is a list
    if isinstance(data, list):
        data = "\n".join(data)

    # Get all non-alphanumeric characters at the beginning of a line
    matches = re.findall(regex_pattern, data, flags=re.MULTILINE)

    # Count matches
    if matches:
        match_counts = {}
        # Sort matches based on length to account for duplicate
        # characters (such as "-" and "--")
        matches.sort(key=len, reverse=True)

        for match in matches:
            # get the count of each match
            match_counts[match] = data.count(match)

            # Remove the match from the data
            data = data.replace(match, "")

        # Set the max and min delimiters
        max_delim = max(match_counts, key=match_counts.get)
        min_delim = min(match_counts, key=match_counts.get)

        logger.debug(f"Found the following delimiters: {match_counts}")
        return match_counts, max_delim, min_delim
    else:
        # No delimiters found
        logger.debug("No delimiters found in data")
        return None


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


# Refactoring the 'input_' function for optimized and pythonic code


def input_(
    constraint: list[str] | str,
    message: str = ">",
    reverse_constraint: bool = False,
    regex: bool = False,
    total_attempts: int = -1,
) -> str:
    """
    Read input from the user and return it if it is valid.

    `constraint` is either a list of valid inputs or a regex pattern
    of valid inputs. `constraint` can also be used to invalidate
    input by setting `reverse_constraint` to `True`.

    Optionally, `total_attempts` can be set to limit the number of
    attempts the user has to enter valid input.

    Args:
        message: The message to display to the user for each input
            attempt. Defaults to `">"`.
        constraint: A list or regex pattern of valid inputs if
            `reverse_constraint` is `False`, or invalid inputs if
            `reverse_constraint` is `True`.
        reverse_constraint: Whether to reverse the constraint.
            If `True`, then `constraint` will be checked against as
            invalid inputs.

            If `False`, then `constraint` will be checked against as
            valid inputs.

            Defaults to `False`.
        regex: Whether to treat `constraint` as a regex pattern.
        total_attempts: Total allowed attempts to get valid input. If
            set to `-1`, then there is no limit to the number of
            attempts. Defaults to `-1`.
    Returns:
        The user's input if it is valid.
    """
    # Convert constraint to a list and a raw str if it is a string
    if isinstance(constraint, str):
        constraint = [rf"{constraint}"]

    # Convert constraint list to str values
    constraint = stringify_list(constraint)

    # Convert constraint to a regex pattern if `regex` is `True`
    if regex:
        constraint = re.compile(f"^(?:{'|'.join(constraint)})$")

        # Log constraint
        logger.debug(
            f"Getting user input with regex pattern constraint "
            f"[reverse_constraint={reverse_constraint}]: {constraint.pattern}"
        )

    # Get input from the user
    while True:
        # Get input from the user
        user_input = input(f"{message}")

        # Check if input is valid
        if regex:
            # Check if input matches regex pattern
            if bool(constraint.findall(user_input)) != reverse_constraint:
                # Input is valid, so return it
                return user_input
        else:
            # Check if input is in constraint
            if (user_input in constraint) != reverse_constraint:
                # Input is valid, so return it
                return user_input

        total_attempts -= 1
        logger.debug(f"Invalid input given: {user_input}")

        # Input is invalid
        if total_attempts == 0:
            logger.debug("Maximum number of attempts reached getting user "
                         "input. Returning empty string.")
            return ""


def flatten_list(data: list[list], depth: int = 1) -> list:
    """
    Recursively flattens a nested `list` to the given depth.

    Args:
        data: The `list` to flatten.
        depth: The depth to flatten the `list` to. Defaults to 1.

    Returns:
        The flattened `list`.
    """
    if depth <= 0:
        return data

    ret = []
    for item in data:
        if isinstance(item, list):
            ret.extend(flatten_list(item, depth - 1))
        else:
            ret.append(item)

    return ret


def intify_list(data: list, sort: bool = False) -> list:
    """
    Converts all values in a list to integers.

    Discards any values that cannot be converted to integers.

    Args:
        data: The `list` to convert.
        sort: Whether to sort the `list` after converting to integers.
            Defaults to `False`.

    Returns:
        The converted `list`.
    """
    if sort:
        return sorted([int(item) for item in data if item.isnumeric()])
    else:
        return [int(item) for item in data if item.isnumeric()]


def stringify_list(data: list) -> list:
    """
    Converts all values in a list to strings.

    Args:
        data: The `list` to convert.

    Returns:
        The converted `list`.
    """
    return [str(item) for item in data]


def count_occurrences(data: list) -> dict:
    """
    Counts the number of occurrences of each value in a `list`.

    Flattens the `data` before counting occurrences.

    Args:
        data: The `list` to count the occurrences of each value in.

    Returns:
        A `dict` containing the number of occurrences of each value in
            the `list`.
    """
    counts = {}
    for item in data:
        if item in counts:
            counts[item] += 1
        else:
            counts[item] = 1

    return counts

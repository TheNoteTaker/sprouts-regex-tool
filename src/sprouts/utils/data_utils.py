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
        delimiters, _, _ = identify_delimiters(data)

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

        logger.debug(
            f"Found the following delimiters: {match_counts}"
        )
        return match_counts, max_delim, min_delim
    else:
        logger.debug(f"No delimiters found in data")
        # No delimiters found
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
        logger.error(
            "`input_` method requires either `valid_input` or `invalid_input`, "
            f"not both. Current values - valid_input: {valid_input} - "
            f"invalid_input: {invalid_input} - message: {message}"
        )
        raise ValueError("Only `valid_input` or `invalid_input` can be used, not both.")
    else:
        # Neither valid nor invalid input was provided
        logger.error(
            "`input_` method requires either `valid_input` or `invalid_input`."
        )
        raise ValueError("Either `valid_input` or `invalid_input` must be used.")

    while True:
        # Read input from the user and check that it is either in the
        # list or matches the regex pattern
        user_input = input(f"{message} ")
        invalid_message = "Invalid input, please try again."
        total_attempts = 0

        if isinstance(valid_input, list) or isinstance(invalid_input, list):
            # For lists of valid or invalid input instead of a regex pattern
            if invalid_input and (user_input.casefold() in invalid_input):
                # The user entered an invalid input from `invalid_input`,
                # so ask them to try again
                print(invalid_message)
                total_attempts += 1
                continue
            elif valid_input and (user_input.casefold() in valid_input):
                # The user entered a valid input, so return it
                total_attempts += 1
                logger.debug(
                    f"Valid input provided after {total_attempts} "
                    f"attempts: {user_input}"
                )

                return user_input
            else:
                # The user entered an invalid input, but it was not inside
                # `invalid_input`, still ask them to try again
                total_attempts += 1
                print(invalid_message)
                continue

        else:
            # For a regex pattern instead of a list of valid or invalid inputs
            if (valid_input and not re.search(valid_input, user_input)) or (
                invalid_input and re.search(invalid_input, user_input)
            ):
                # The user entered an invalid input, so ask them to try
                # again
                total_attempts += 1
                print("Invalid input, please try again.")
                continue
            else:
                # The user entered a valid input, so return it
                total_attempts += 1
                logger.debug(
                    f"Valid input provided after {total_attempts} "
                    f"attempts: {user_input}"
                )
                return user_input

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

    Args:
        data: The `list` to convert.
        sort: Whether to sort the `list` after converting to integers.
            Defaults to `False`.

    Returns:
        The converted `list`.
    """
    if sort:
        return sorted([int(item) for item in data])
    else:
        return [int(item) for item in data]

def stringify_list(data: list) -> list:
    """
    Converts all values in a list to strings.

    Args:
        data: The `list` to convert.

    Returns:
        The converted `list`.
    """
    return [str(item) for item in data]
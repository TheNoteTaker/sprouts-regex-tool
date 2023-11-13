from . import flatten_list, stringify_list


class Regex:
    """
    A utility class for generating regular expression patterns.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def create_regex_patern(
        data: list,
        lpad: str = "",
        rpad: str = "",
    ) -> str:
        """
        Generates a regular expression pattern from a `list` of strings.

        Optionally, you can specify an `lpad` and `rpad` string, 
        which will be added at the beginning and end of the pattern. 
        This is useful for adding whitespace to the beginning and end 
        of each string.

        Examples:

            >>> Regex.create_regex_patern(["1", "2", "3"])
            "^(1|2|3)$"

            >>> Regex.create_regex_patern(["1", "2", "3"], lpad="\s*?")
            "^\s*?(1|2|3)$"

            >>> Regex.create_regex_patern(["1", "2", "3"], lpad="\s*?", rpad="\s*?")
            "^\s*?(1|2|3)\s*?$"

        Args:
            data (list): A `list` of strings to generate the pattern
                from.
            lpad (str, optional): A string to add to the beginning
                of the pattern. Defaults to "".
            rpad (str, optional): A string to add to the end of the
                pattern. Defaults to "".

        Returns:
            str: The generated regular expression pattern.
        """
        # Pre-process data - flatten, stringify, and deduplicate
        data = flatten_list(data)
        data = stringify_list(data)
        data = list(set(data))

        # Create regex pattern
        pattern = rf"^{lpad}({'|'.join(data)}){rpad}$"

        return pattern

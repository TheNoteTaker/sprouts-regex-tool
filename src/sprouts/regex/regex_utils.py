from sprouts.regex.regex_collections import RegexCollection
from sprouts import utils
import re


class RegexSearch:
    def __init__(self):
        pass

    def __getattr__(self, item):
        """Return `item` from the `re` module."""
        return getattr(re, item)

    @staticmethod
    def concat_patterns(patterns: list[str],
                        sep: str = "|",
                        anchors: bool = True,
                        ) -> str:
        """
        Concatenate multiple regex patterns into one pattern.

        Concatenate multiple regex patterns into one pattern by first
        stripping the pattern wrapper and adding the `sep` between each
        pattern. Then add beginning and ending anchors to the overall
        pattern.

        Args:
            patterns: The patterns to concatenate.
            sep: The separator to use between each pattern.
            anchors: Whether to add beginning and ending anchors to the
                overall pattern.

        Returns:
            The concatenated regex pattern.

        """
        # Remove the pattern wrapper from each pattern
        ret = [RegexSearch.strip_pattern(pattern) for pattern in patterns]

        if anchors:
            return "^(?:" + f"{sep}".join(ret) + ")$"
        else:
            return "(?:" + f"{sep}".join(ret) + ")"

    @staticmethod
    def strip_pattern(pattern: str) -> str:
        """Remove the regex pattern wrapper if it exists"""
        return re.sub(r"^\^|\$$", "", pattern).strip()

    @staticmethod
    def add_anchors(pattern: str) -> str:
        """Add the regex pattern anchors if they don't exist"""
        # Add beginning anchor
        if pattern[0] != "^":
            pattern = "^" + pattern

        # Add ending anchor
        if pattern[-1] != "$":
            pattern = pattern + "$"

        return pattern

    @staticmethod
    def add_group_wrapper(pattern: str) -> str:
        """Add the regex non-capture wrapper"""
        return "(?:" + pattern + ")"

    @staticmethod
    def add_capture_wrapper(pattern: str) -> str:
        """Add the regex capture group wrapper"""
        return "(" + pattern + ")"

    @staticmethod
    def file_search(filename: str, pattern: str) -> list[str]:
        """Search a file for a regex pattern and return the matches."""
        return re.findall(
            pattern=rf"{pattern}",
            string=utils.read_file_string(filename),
            flags=re.MULTILINE
        )

    @staticmethod
    def file_multi_search(filename: str, patterns: RegexCollection) \
            -> list[str]:
        """Search a file for multiple regex patterns and return the matches."""
        # Concatenate all the patterns together
        pattern = RegexSearch.concat_patterns(*patterns)
        return RegexSearch.file_search(filename, pattern)

    @staticmethod
    def compare_lists(base_list: list[str] | list[list[str]],
                      compare_lists: list[str] | list[list[str]]) \
            -> tuple[list[str], list[str]]:
        """
        Compare two lists and return the items that exist in both lists.

        Unpacks `base_list` and `compare_lists` if they are nested
        lists. Locates all items in `compare_lists` that exist in
        `base_list` and returns them. Also returns items that were not
        found in `base_list`.

        Args:
            base_list: `list`(s) to compare against.
            compare_lists: `list`(s) to compare.

        Returns:
            A `tuple` containing:
                - [0]: A `list` of items that exist in `base_list`.
                - [1]: A `list` of items that do not exist in
                    `base_list`.
        """
        # Flatten lists
        base_list = utils.flatten(base_list)
        compare_lists = utils.flatten(compare_lists)

        # Concatenate all `base_list` patterns together and then remove anchors
        base_pattern = RegexSearch.concat_patterns(base_list)[1:-1]

        # Return all items in `compare_lists` that exist in `base_list`
        found_items = re.findall(
            base_pattern,
            " ".join(compare_lists),
            re.MULTILINE
        )
        missing_items = [item for item in compare_lists
                         if item not in found_items]
        return found_items, missing_items

    @staticmethod
    def _replace_or(string: str) -> str:
        """Replace the word `or` with the pipe character `|`"""
        return re.sub(
            pattern=r"\s*\bor\b\s*",
            repl="|",
            string=string,
            flags=re.MULTILINE
        )

    @staticmethod
    def _replace_capture_group(string: str) -> str:
        """Replace the word `group` with the non-capture group wrapper `?:`"""
        return re.sub(
            pattern=r"\bgroup\b<\s*(.*)>",
            repl=RegexSearch.add_capture_wrapper(r"\1"),
            string=string,
            flags=re.MULTILINE
        )

    @staticmethod
    def _replace_spaces(string: str) -> str:
        """Replace spaces with the regex whitespace character"""
        # Replace multiple spaces with a variable length whitespace character
        ret = re.sub(
            pattern=r"\s{2,}",
            repl=r"\\s*",
            string=string,
            flags=re.MULTILINE
        )

        # Replace single spaces with the regex whitespace character
        return re.sub(
            pattern=r"\s",
            repl=r"\\s",
            string=ret,
            flags=re.MULTILINE
        )

    @staticmethod
    def _replace_letters(string: str) -> str:
        """Replace the word `alphabet` with the regex alphabet character"""
        return re.sub(
            pattern=r"\b[a-zA-Z]+\b",
            repl=r"\\w+",
            string=string,
            flags=re.MULTILINE
        )

    @staticmethod
    def _replace_numeric(string: str) -> str:
        """Replace numeric characters with the regex numeric character"""
        # Replace multiple numeric characters with a variable length numeric
        # character
        ret = re.sub(
            pattern=r"\b\d+\b",
            repl=r"\\d+",
            string=string,
            flags=re.MULTILINE
        )

        # Replace single numeric characters with the regex numeric character
        return re.sub(
            pattern=r"\d",
            repl=r"\\d",
            string=ret,
            flags=re.MULTILINE
        )

    @staticmethod
    def generate_regex_pattern() -> str:
        """
        Generate a regex pattern based on user input.

        Gets user input and then replaces the values in `pattern` with
        regex equivalents. Then add the regex wrappers and anchors.

        If `general_search` is `True`, then the letters and spaces will
        be replaced with the regex equivalents `\\w` and `\\s`
        respectively.

        Returns:
            The generated regex pattern.
        """

        # Get user input
        pattern = input("Enter an example of an item you want to match:\n>")
        general_search = input("Do you want to perform a more "
                               "general search? [Y/n]\n>").casefold()

        # Replace the values in `pattern` with regex equivalents
        ret = RegexSearch._replace_capture_group(pattern)
        ret = RegexSearch._replace_or(ret)
        if general_search not in ["n", "no", "0", "false", "f"]:
            # Use `\w` and `\s` to replace letters and spaces with optional `+`
            ret = RegexSearch._replace_letters(ret)
            ret = RegexSearch._replace_numeric(ret)

        ret = RegexSearch._replace_spaces(ret)

        # Add the regex wrappers
        ret = RegexSearch.add_group_wrapper(ret)
        ret = RegexSearch.add_anchors(ret)

        return ret


if __name__ == "__main__":
    pass

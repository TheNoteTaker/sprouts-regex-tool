from typing import Sequence, Any, TypeVar
from abc import ABC, abstractmethod
from sprouts import utils
import re

T = TypeVar('T', str, str)


class RegexPattern:

    def __init__(self, pattern: str = ""):
        self.pattern = ""
        self.regex = None
        self.set_pattern(pattern)

    def __str__(self) -> str:
        """Return the pattern string."""
        return self.pattern

    def __getattr__(self, item):
        """Return `item` from the `re` module."""
        return self.regex.__getattribute__(item)

    def set_pattern(self, pattern: str) -> None:
        """Set the pattern string and compile it for future use."""
        self.pattern = pattern
        self.regex = re.compile(self.pattern, re.M)


class RegexCollection(ABC):
    """A class for storing multiple regex patterns."""

    def __init__(self):
        pass

    def __str__(self) -> str:
        """Return the collection of regex patterns."""
        return self.to_string()

    @abstractmethod
    def __iter__(self):
        """Return an iterator for the collection of regex patterns."""
        pass

    @abstractmethod
    def add_patterns(self,
                     *patterns: str | Sequence[T]) -> None:
        """Add regex patterns to the collection."""
        pass

    @abstractmethod
    def remove_pattern(self, pattern: str) -> int:
        """
        Remove a pattern from the collection.

        Args:
            pattern: The pattern to remove.

        Returns:
            1 if the pattern was removed,
            -1 if the pattern was not found.
        """
        pass

    @abstractmethod
    def to_list(self) -> list[str]:
        """Return the collection of regex patterns."""
        pass

    @abstractmethod
    def load_from_file(self, filename: str) -> None:
        """Load regex patterns from a file."""
        pass

    @abstractmethod
    def to_string(self, sep: str = "\n") -> str:
        """Return the collection of regex patterns."""
        pass

    def load_from_input(self) -> None:
        """Load regex patterns from user input."""
        self.add_patterns(*utils.read_input_lines())

    def total_patterns(self) -> int:
        """Return the total number of regex patterns."""
        return len(self.regex_patterns)

    def clear_patterns(self) -> None:
        """Clear all patterns from the collection."""
        self.regex_patterns.clear()

    def remove_duplicates(self) -> None:
        """Remove duplicate patterns from the collection."""
        self.regex_patterns = utils.unique_list(self.regex_patterns)

    def is_empty(self) -> bool:
        """Return True if the collection is empty, False otherwise."""
        return self.total_patterns() == 0

    def get_pattern(self, index):
        """Return the pattern at the specified index."""
        try:
            return self.regex_patterns[index]
        except IndexError:
            return None
        except KeyError:
            return None


class RegexList(RegexCollection):
    """A class for storing multiple regex patterns."""

    def __init__(self):
        self.regex_patterns = []
        super().__init__()

    def __iter__(self):
        """Return an iterator for the collection of regex patterns."""
        return iter(self.regex_patterns)

    def to_string(self, sep: str = "\n") -> str:
        """Return the collection of regex patterns."""
        return f"{sep}".join(self.to_list())

    def load_from_file(self, filename: str) -> None:
        """Load regex patterns from a file."""
        self.add_patterns(*utils.read_file_lines(filename))
        print(f"Loaded patterns from {filename}")

    def add_patterns(self, *patterns: str) -> None:
        """Add regex patterns to the collection."""
        for pattern in patterns:
            self.regex_patterns.append(RegexPattern(pattern))

    def remove_pattern(self, pattern: str) -> int:
        """
        Remove a pattern from the collection.

        Args:
            pattern: The pattern to remove.

        Returns:
            1 if the pattern was removed,
            -1 if the pattern was not found.
        """
        obj = None
        # Look for the pattern in regex_patterns
        for regex_obj in self.regex_patterns:
            if regex_obj.pattern == pattern:
                obj = regex_obj
                break

        try:
            # If the pattern was found, remove it from the list.
            self.regex_patterns.remove(obj)

        except ValueError:
            return -1

        return 1

    def to_list(self) -> list[str]:
        """Return the collection of regex patterns."""
        # Add together all the patterns found in the `patterns` collection.
        return [f"{pattern}" for pattern in self.regex_patterns]


class RegexDict(RegexCollection):

    def __init__(self):
        self.regex_patterns = {}
        super().__init__()

    def __iter__(self):
        """Return an iterator for the collection of regex patterns."""
        return iter(self.regex_patterns.values())

    def to_string(self, sep: str = "\n") -> str:
        """Return the collection of regex patterns."""
        strings = []
        for k, v in self.regex_patterns.items():
            if isinstance(v, list):
                # Key has a `list` of patterns instead of a single string.
                pattern_str = ", ".join([str(pattern) for pattern in v])
            else:
                # Key has a single pattern instead of a `list` of patterns.
                pattern_str = str(v)

            strings.append(f"{k}:{pattern_str}")

        # Return the `list` of patterns as a string
        return sep.join(strings)

    def add_patterns(self, patterns: Sequence[T] | str) -> None:
        """Add regex patterns to the collection."""
        if isinstance(patterns, dict):
            # A `dict` of patterns was provided
            for name, pattern in patterns.items():
                if isinstance(pattern, list):
                    # A `list` of patterns was provided for the key
                    self.regex_patterns[name] = []
                    for sub_pattern in pattern:
                        self.regex_patterns[name].append(
                            RegexPattern(sub_pattern))
                else:
                    self.regex_patterns[name] = RegexPattern(pattern)
        elif isinstance(patterns, list):
            # A `list` of patterns was provided
            for i in range(len(patterns)):
                self.regex_patterns[i] = RegexPattern(patterns[i])
        else:
            # A single pattern was provided
            self.regex_patterns[len(self.regex_patterns)] \
                = RegexPattern(patterns)

    def load_from_file(self, filename: str) -> None:
        """Load regex patterns from a file."""
        self.regex_patterns = utils.read_json(filename)
        print(f"Loaded patterns from {filename}")

    def remove_pattern(self, pattern: str) -> int:
        """
        Remove a pattern from the collection.

        Args:
            pattern: The pattern to remove.

        Returns:
            1 if the pattern was removed,
            -1 if the pattern was not found.
        """
        try:
            # If the pattern was found, remove it from the collection.
            self.regex_patterns.pop(pattern)

        except KeyError:
            # The Pattern was not found in keys, so search values
            for name, regex_obj in self.regex_patterns.items():
                if regex_obj.pattern == pattern:
                    self.regex_patterns.pop(name)
                    return 1
            else:
                # The Pattern was not found in values, so return -1
                return -1

        return 1

    def to_list(self) -> list[list[str | Any]]:
        """Return the `list` of regex patterns."""
        ret = []
        for name, pattern in self.regex_patterns.items():
            pattern_string = []
            if isinstance(pattern, list):
                # Key has a `list` of patterns instead of a single string.
                for sub_pattern in pattern:
                    pattern_string.append(str(sub_pattern))
            else:
                # Key has a single pattern instead of a `list` of patterns.
                pattern_string.append(str(pattern))

            # Add the name and pattern to the `list` of patterns.
            ret.append([name, pattern_string])

        return ret


if __name__ == "__main__":
    pass

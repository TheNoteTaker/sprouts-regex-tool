from regex_pattern_collections import RegexDict, RegexList
from regex_search import RegexSearch


class RegexInput(RegexSearch):
    
    def __init__(self,
                 pattern_file: str = "",
                 obj_type: str = "dict"
                 ):
        super().__init__()
        self.config_file = pattern_file

        # Create a collection of regex patterns based on the `obj_type`
        if obj_type == "dict":
            print(f"Empty Regex{obj_type.title()} collection created...")
            self.patterns = RegexDict()
        elif obj_type == "list":
            print(f"Empty Regex{obj_type.title()} collection created...")
            self.patterns = RegexList()
        else:
            raise ValueError(f"Invalid `obj_type` value: {obj_type}")

    def __str__(self):
        """Return the collection of regex patterns in a string format"""
        return self.to_string()

    def __iter__(self):
        """Return an iterator for the collection of regex patterns."""
        return iter(self.patterns)

    @staticmethod
    def search(filename: str, pattern: str) -> list[str]:
        """Search a file for a regex pattern and return the matches."""
        return super().file_search(filename, pattern)

    def add_patterns(self, *patterns: list[str] | str | dict[str, str]) -> None:
        """Add regex patterns to the collection."""
        if isinstance(patterns, dict):
            # Assume a dictionary of patterns was provided
            self.patterns.add_patterns({k: v for k, v in patterns.items()})
        elif isinstance(patterns, list):
            # Assume a list of patterns was provided
            self.patterns.add_patterns(*patterns)
        else:
            # Assume a single pattern was provided
            self.patterns.add_patterns(*patterns)

    def remove_patterns(self, pattern: str) -> int:
        """Remove pattern(s) from the collection."""
        return self.patterns.remove_pattern(pattern)

    def to_string(self, sep: str = "\n") -> str:
        """Return the collection of regex patterns in a string format"""
        # Add together all the patterns found in the `patterns` collection.
        return self.patterns.to_string(sep)

    def multi_search(self, filename: str) -> list[str]:
        """Search a file for multiple regex patterns and return the matches."""
        return super().file_multi_search(filename, self.patterns)

    def load_from_file(self, filename: str) -> None:
        """Load regex patterns from a file."""
        self.patterns.load_from_file(filename)

    def get_pattern(self, index):
        """Return a pattern from the `patterns` at the given index."""
        return self.patterns.get_pattern(index)

    def total_patterns(self):
        """Return the total number of patterns in the collection."""
        return self.patterns.total_patterns()


if __name__ == "__main__":
    test_patterns = [
        "^\\$(?!0.00)\\d+\\.\\d{2}$",
        "^\\d{4,5}?$",
        "^\\d+\\.0{2}$",
        "^\\^|\\$$"
    ]
    driver = RegexInput()
    print(driver.search("^\$(?!0.00)\d+\.\d{2}$"))
    print(driver.multi_search())
    print(driver.to_string())
    print(driver.add)

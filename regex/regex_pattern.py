import re


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


if __name__ == "__main__":
    driver = RegexPattern()
    driver.set_pattern("Hello")
    print(driver)

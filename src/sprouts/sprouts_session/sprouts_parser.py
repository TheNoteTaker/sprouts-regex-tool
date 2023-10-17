from .. import utils
from ..regex import RegexPattern

MODULE_DIR = utils.get_file_dir(__file__)
# Get filepath of patterns.json file
path = utils.join(utils.get_parent_dir(MODULE_DIR) + "/data/patterns.json")
# Verify the filepath is valid
if not utils.exists(path):
    print(
        f"This program requires the `patterns.json` file. This file is missing.\nExpected filepath: {path}"
    )
    while True:
        path = input("Please enter the path to the `patterns.json` file:\n>")
        if not utils.exists(path):
            print("File was not found...")
        else:
            break
REGEX_PATTERNS_PATH = path


class ShipmentParser:
    def __init__(self, filename: str = REGEX_PATTERNS_PATH) -> None:
        """
        Initializes a SproutsParser object with the specified filename.

        Args:
            filename (str): The path to the JSON file containing the
                Sprouts patterns.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        self.patterns = {}
        if not utils.exists(filename):
            raise FileNotFoundError(f"File '{filename}' not found.")
        else:
            self._load_patterns(utils.read_json(filename))

    def _load_patterns(self, patterns: dict) -> None:
        """Load regex patterns from a `dict`."""
        self.patterns = {k: RegexPattern(v) for k, v in patterns.items()}

    def parse_list(
        self, data: str | list[str]
    ) -> list[list[RegexPattern] | RegexPattern]:
        """
        Parses `data` by class regex patterns.

        Uses the regex patterns in `patterns` to parse `data`. The
        Patterns are ranked by priority in a top-down fashion, so the
        first pattern to match will be used.

        Args:
            data (str | list[str]): The data to parse.

        Returns:
            A list of lists of `RegexPattern` objects or `RegexPattern`
            objects.
        """
        # Convert `data` to a string if it is a list
        if isinstance(data, list):
            data = "\n".join(utils.flatten(data))

        for pattern in self.patterns.values():
            # Find all matches for the pattern in the data
            matches = pattern.findall(data)

            if matches:
                return matches

        return []


class ShipmentList:
    """
    A class to manage shipments for the Sprouts Shipments Parser.

    Attributes:
        shipments (list): A list of non-parsed shipments.
        parsed_shipments (list): A list of parsed shipments.
        parser (ShipmentParser): An instance of the ShipmentParser
            class.
        shipment_amount (int): The total number of shipments.
        scan_columns (int): The number of shipments entered directly
            from an invoice scan.
        str_width (int): The width of the output string.

    Methods:
        __iter__(): Returns an iterator for the shipments list.
        shipments_menu(): Displays the shipments menu and prompts
            the user for input.
        _get_shipment_data(): Prompts the user for shipment data and
            adds it to the list of shipments.
        parse_shipment(shipments): Parses the list of shipments.
        add_shipments(shipments, sep='|'): Adds parsed shipments to
            the list of shipments.
        get_shipments(): Returns the list of shipments.
    """

    def __init__(self, shipments: list[list[str]] = []):
        self.shipments = []
        self.parsed_shipments = []
        self.parser = ShipmentParser()
        self.shipment_amount = 0
        self.scan_columns = 0

        if shipments:
            self.add_shipments(shipments)

    def __iter__(self):
        if self.parsed_shipments:
            return iter(self.parsed_shipments)
        else:
            return iter(self.shipments)

    def __str__(self) -> str:
        ret = ""
        if self.parsed_shipments:
            shipments = self.parsed_shipments
        else:
            shipments = self.shipments

        # Remove empty shipments and separators
        shipment_list = [
            shipment
            for shipment in shipments
            if shipment not in ["|", "", " "] and shipment is not None
        ]

        for i, shipment in enumerate(shipment_list):
            ret += f"Shipment {i + 1}: {', '.join(shipment)}\n"

        return ret

    def parse_shipment(self, shipments: list) -> list:
        """Parse the `list` of shipments."""
        return self.parser.parse_list(shipments)

    def add_shipments(self, shipments: list[list[str]], sep: str = "|") -> None:
        """
        Add parsed shipments to the list of shipments.

        `shipments` can be a `list` containing sublists of strings where
        each sublist will be a shipment or a single `list` of strings
         where that list is a single shipment.

        The `sep` argument is used to separate shipments in the list
        of shipments and should be left as the default value of "|"
        to not cause any issues with the table segmentor.

        Args:
            shipments: The shipments to add, consisting of non-parsed
                shipment(s).
            sep: The separator to use between shipments.

        Returns:
            None
        """
        if not isinstance(shipments, list):
            shipments = [shipments]

        for shipment in shipments:
            self.parsed_shipments.append(self.parse_shipment(shipment))
            self.shipments.append(shipment)

            # Separate shipments with a dashed line
            self.shipments.append(sep)
            self.parsed_shipments.append(sep)

        # Remove the last separator
        self.shipments.pop(-1)
        self.parsed_shipments.pop(-1)

        # Update object state
        self.shipment_amount = len(self.shipments)

    def get_shipments(self) -> list:
        """Return the list of shipments."""
        return self.parsed_shipments or self.shipments


if __name__ == "__main__":
    pass

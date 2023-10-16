from textwrap import fill
from .. import utils
from ..regex import RegexPattern

MODULE_DIR = utils.get_module_dir(__file__)
REGEX_PATTERNS_PATH = utils.join(
    utils.get_parent_dir(MODULE_DIR) + "/data/patterns.json"
)


class ShipmentParser:
    def __init__(self, filename: str = REGEX_PATTERNS_PATH) -> None:
        """
        Initializes a SproutsParser object with the specified filename.

        Args:
            filename (str): The path to the JSON file containing the Sprouts patterns.

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

        Uses the regex patterns in `patterns` to parse `data`.
        The Patterns are ranked by priority in a top-down fashion,
        so the first pattern to match will be used.

        Args:
            data (str | list[str]): The data to parse.

        Returns:
            A list of lists of `RegexPattern` objects or `RegexPattern` objects.
        """
        # Convert `data` to a string if it is a list
        if isinstance(data, list):
            data = "\n".join(utils.flatten(data))

        for pattern in self.patterns.values():
            # Find all matches for the pattern in the data
            matches = pattern.findall(data)

            if matches:
                return matches


class ShipmentManager:
    """
    A class to manage shipments for the Sprouts Shipments Parser.

    Attributes:
        shipments (list): A list of non-parsed shipments.
        parsed_shipments (list): A list of parsed shipments.
        parser (ShipmentParser): An instance of the ShipmentParser class.
        shipment_amount (int): The total number of shipments.
        scan_columns (int): The number of shipments entered directly from an invoice scan.
        str_width (int): The width of the output string.

    Methods:
        __iter__(): Returns an iterator for the shipments list.
        shipments_menu(): Displays the shipments menu and prompts the user for input.
        _get_shipment_data(): Prompts the user for shipment data and adds it to the list of shipments.
        parse_shipment(shipments): Parses the list of shipments.
        add_shipments(shipments, sep='|'): Adds parsed shipments to the list of shipments.
        get_shipments(): Returns the list of shipments.
    """

    def __init__(self):
        self.shipments = []
        self.parsed_shipments = []
        self.parser = ShipmentParser()
        self.shipment_amount = 0
        self.scan_columns = 0
        self.str_width = 80

    def __iter__(self):
        return iter(self.shipments)

    def shipments_menu(self) -> None:
        print("Welcome to the Sprouts Shipments Parser!")
        print(
            fill(
                "System will try to parse your data to create a visual "
                "representation for you.",
                self.str_width,
            )
            + "\n"
        )

        print(
            fill(
                "To start, enter the total number of shipments you will be "
                "entering (including invoice scan shipments)",
                self.str_width,
            )
        )
        print("==========================")

        self.shipment_amount = int(
            utils.input_(
                valid_input="^[1-9][0-9]*$", message="Enter Total Shipments:"
            )
        )

        print(
            "\n"
            + fill(
                "Enter the number of shipments that are being "
                "entered directly from an invoice scan (not from PO "
                "Reconciliation or Invoice Review)",
                self.str_width,
            )
        )
        print("==========================")

        self.scan_columns = int(
            utils.input_(
                valid_input="^[1-9][0-9]*$",
                message="Enter Number of Invoice Scan Columns:",
            )
        )

        self._get_shipment_data()

    def _get_shipment_data(self) -> None:
        shipments = []
        if self.scan_columns:
            # Get scan shipments if any
            for scan_shipment in range(self.scan_columns):
                print(
                    "\n"
                    + fill(
                        f"Scan {scan_shipment + 1} "
                        f"(Type each piece of data on a new line or paste "
                        f"your entire data set already separated on new "
                        f"lines):",
                        self.str_width,
                    )
                )
                shipments.append(utils.read_input_lines())

        # Get all normal shipments
        for shipment in range(self.shipment_amount - self.scan_columns):
            print(
                "\n"
                + fill(
                    f"Shipment {shipment + 1} "
                    f"(Type each piece of data on a new line or paste your "
                    f"entire data set already separated on new lines):",
                    self.str_width,
                )
            )
            shipments.append(utils.read_input_lines())

        # Add all shipments to the list of shipments
        self.add_shipments(shipments)

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

        # Remove the last separator
        self.shipments.pop(-1)

        # Update object state
        self.shipment_amount = len(self.shipments)

    def get_shipments(self) -> list:
        """Return the list of shipments."""
        return self.parsed_shipments or self.shipments


if __name__ == "__main__":
    pass

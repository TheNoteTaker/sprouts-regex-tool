from textwrap import fill
import sprouts.utils as utils
from sprouts.regex.regex_collections import RegexPattern


class ShipmentManager:

    def __init__(self):
        self.shipments = []
        self.shipment_amount = 0
        self.scan_columns = 0
        self.str_width = 80

    def __str__(self):
        pass

    def shipments_menu(self) -> None:
        print("Welcome to the Sprouts Shipments Parser!")
        print(
            fill("System will try to parse your data to create a visual "
                 "representation for you.", self.str_width) + "\n"
        )

        print(
            fill("To start, enter the total number of shipments you will be "
                 "entering (including invoice scan shipments)", self.str_width)
        )
        print("==========================")

        self.shipment_amount = int(utils.input_(valid_input="^[1-9][0-9]*$",
                                                message="Enter Total Shipments:"
                                                ))

        print(
            "\n"
            + fill("Enter the number of shipments that are being "
                   "entered directly from an invoice scan (not from PO "
                   "Reconciliation or Invoice Review)", self.str_width)
        )
        print("==========================")

        self.scan_columns = int(utils.input_(
            valid_input="^[1-9][0-9]*$",
            message="Enter Number of Invoice Scan Columns:"
        ))

        self._get_shipment_data()

    def _get_shipment_data(self) -> None:
        shipments = []
        if self.scan_columns:
            # Get scan shipments if any
            for scan_shipment in range(self.scan_columns):
                print(
                    "\n"
                    + fill(f"Scan {scan_shipment + 1} "
                           f"(Type each piece of data on a new line or paste "
                           f"your entire data set already separated on new "
                           f"lines):", self.str_width)
                )
                shipments.append(utils.read_input_lines())

        # Get all normal shipments
        for shipment in range(self.shipment_amount - self.scan_columns):
            print(
                "\n"
                + fill(f"Shipment {shipment + 1} "
                       f"(Type each piece of data on a new line or paste your "
                       f"entire data set already separated on new lines):",
                       self.str_width)
            )
            shipments.append(utils.read_input_lines())

        # Add all shipments to the list of shipments
        self.add_shipments(shipments)

    def add_shipments(self, shipments: list, sep: str = "|") -> None:
        """Add shipments to the list of shipments."""
        for shipment in shipments:
            self.shipments.append(shipment)
            # Separate shipments with a dashed line
            self.shipments.append(sep)

        # Remove the last separator
        self.shipments.pop(-1)

        # Update the shipment amount
        self.shipment_amount = len(self.shipments)

    def get_shipments(self) -> list:
        """Return the list of shipments."""
        return self.shipments


class ShipmentParser:

    def __init__(self, filename: str = "data/patterns.json") -> None:
        self.patterns = {}
        if not utils.exists(filename):
            raise FileNotFoundError(f"File '{filename}' not found.")
        else:
            self._load_patterns(utils.read_json(filename))

    def _load_patterns(self, patterns: dict) -> None:
        """Load regex patterns from a `dict`."""
        self.patterns = {k: RegexPattern(v) for k, v in patterns.items()}

    def parse_list(self, data: str | list[str]
                   ) -> list[list[RegexPattern] | RegexPattern]:
        """
        Parses `data` by class regex patterns.

        Uses the regex patterns in `patterns` to parse `data`.
        The Patterns are ranked by priority in a top-down fashion,
        so the first pattern to match will be used.

        Args:
            data: The data to parse.

        Returns:
            A `l
        """
        ret = []
        # Convert `data` to a string if it is a list
        if isinstance(data, list):
            data = "\n".join(utils.flatten(data))

        for pattern in self.patterns.values():
            # Find all matches for the pattern in the data
            matches = pattern.findall(data)
            if matches:
                # Add the matches to the list of matches
                return matches


if __name__ == "__main__":
    # driver = ShipmentManager()
    # driver.shipments_menu()
    # print(driver.get_shipments())
    shipment_one = utils.read_file_lines("data/sample_data_01.txt")
    shipment_two = utils.read_file_lines("data/sample_data_02.txt")
    shipment_three = utils.read_file_lines("data/sample_data_03.txt")
    driver = ShipmentParser()
    print(driver.parse_list(shipment_one))
    print(driver.parse_list(shipment_two))
    print(driver.parse_list(shipment_three))

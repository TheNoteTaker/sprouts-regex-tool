import re

from sprouts.regex import RegexSearch
from textwrap import fill
import sprouts.utils as utils


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
    SETUP_ONE = re.compile(r'''
        ^                                    # Beginning of line
        (?P<item>\d{4,5})(?!\n(?P=item))\n*  # Match vendor item
        (?P<rcv>\d+)\n*                      # Match units received
        \$(?P<dlr>(?!0.00)\d+\.\d{2})        # Match dollar amount
        $                                    # End of line
        ''', re.VERBOSE | re.MULTILINE)
    SETUP_TWO = re.compile(r'''
        ^                                    # Beginning of line
        (?P<item>\d{4,5})(?!\n(?P=item))\n*  # Match vendor item
        (?P<rcv>\d+\.0{2})                   # Match units received
        $                                    # End of line
        ''', re.VERBOSE | re.MULTILINE)
    SETUP_THREE = re.compile(r'''
        ^                                    # Beginning of line
        (?P<item>\d{4,5}?)(?!\n(?P=item))    # Match vendor item
        $                                    # End of line
    ''', re.VERBOSE | re.MULTILINE)

    def __init__(self) -> None:
        self.patterns = utils.read_json("data/patterns.json")
        pass

    def __str__(self) -> str:
        pass

    def _parse_data(self, data: str | list[str]) -> tuple[list, list, list]:
        """
        Parses `data` by class regex patterns.

        Uses the class regex patterns to parse `data` and return a
        `list` containing a `list` per regex pattern of all found
        matches in `data`.

        Args:
            data: The data to parse.

        Returns:

        """
        ret = []
        # Convert `data` to a string if it is a list
        if isinstance(data, list):
            data = "\n".join(utils.flatten(data))

        # setup_one = Vendor item + units received + dollar amount
        setup_one = ShipmentParser.SETUP_ONE.findall(data)
        # setup_two = Vendor item + units received
        setup_two = ShipmentParser.SETUP_TWO.findall(data)
        # setup_three = Vendor item
        setup_three = ShipmentParser.SETUP_THREE.findall(data)

        return setup_one, setup_two, setup_three

    def parse_shipment(self, shipment: str | list[str]) -> list:
        # setup_one = Vendor item + units received + dollar amount
        # setup_two = Vendor item + units received
        # setup_three = Vendor item
        setup_one, setup_two, setup_three = self._parse_data(shipment)

        return setup_one if setup_one \
            else setup_two if setup_two \
            else setup_three if setup_three \
            else []


if __name__ == "__main__":
    # driver = ShipmentManager()
    # driver.shipments_menu()
    # print(driver.get_shipments())
    data = utils.read_file_lines("data/sample_data_02.txt")
    driver = ShipmentParser()
    print(driver.parse_shipment(data))

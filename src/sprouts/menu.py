from textwrap import fill
from .tables import RegexTable
from . import utils


class InteractiveMenu:
    def __init__(self, line_length: int = 80) -> None:
        self.str_width = line_length
        self.shipment_regex = "^\d+$"

    def _get_total_shipments(self) -> tuple[int, int]:
        """
        Gets the total number of shipments and scan columns.

        Prompts the user to enter the total number of shipments and
        the number of scan columns that are being entered directly
        from an invoice scan.

        Returns:
            `tuple`: A tuple containing the total number of
                shipments and the number of shipments being entered
                directly from an invoice scan.
        """
        print("Welcome to the Sprouts Shipments Manager!")
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

        shipment_amount = int(
            utils.input_(
                valid_input=self.shipment_regex,
                message="Enter Total Shipments:",
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

        # The number of scan columns cannot be greater than the total
        # number of shipments
        scan_column_amount = int(
            min(
                int(
                    utils.input_(
                        valid_input=self.shipment_regex,
                        message="Enter Number of Invoice Scan Columns:",
                    )
                ),
                int(shipment_amount),
            )
        )

        return shipment_amount, scan_column_amount

    def _get_shipment_data(
        self,
        shipment_amount: int,
        scan_column_amount: int = 0,
    ) -> list[list[str]]:
        """
        Get shipment data from the user.

        Args:
            shipment_amount (int): The number of normal shipments
                to get.
            scan_column_amount (int, optional): The number of scan
                shipments to get. Defaults to 0.

        Returns:
            list: A list of all the shipments.
        """
        shipments = []
        if scan_column_amount:
            # Get scan shipments if any
            for scan_shipment in range(scan_column_amount):
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
        for shipment in range(shipment_amount - scan_column_amount):
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
        return shipments

    def shipments_menu(self) -> list[list[list[str]], int, int]:
        # Get the total number of shipments and the number of scan columns
        shipment_amount, scan_column_amount = self._get_total_shipments()

        # Get the shipment data (rows)
        shipments = self._get_shipment_data(shipment_amount, scan_column_amount)

        return [shipments, shipment_amount, scan_column_amount]

    def table_menu(self, tables: list[RegexTable]) -> (int, int):
        if not tables:
            return 0

        # Display options
        print("Please select one of the following tables:")
        for i, table in tables.items():
            print(
                f"Table {i+1} - "
                f"Total: {table.unique_values[1]} | "
                f"Rows: {len(table.rows)} | "
                f"Columns: {table.num_columns} | "
                f"Duplicates: {table.duplicates[1]} | "
                f"Non-Duplicates: {table.non_duplicates[1]} | "
                f"Overlap: {table.overlap[1]} | "
            )

        # Get user table choice
        choice = utils.input_(
            message="Enter your choice:",
            valid_input=[key + 1 for key in tables.keys()],
        )
        print()  # Newline separator

        return int(choice) - 1

    def grid_table_input(self) -> int:
        grid = utils.input_(
            message="Use grid tables? [y/N]: ",
            valid_input=["y", "n", "yes", "no", "", "1", "2"],
        )
        print() # Newline separator

        if grid.casefold() in ["y", "yes", "1"] or grid is None:
            return 1
        else:
            return 0

    def edit_menu(
        self, table: RegexTable, exit_strings: list[str] = ["exit", ""]
    ) -> list[int]:
        print("\n==========Edit Menu==========")
        row_index = utils.input_(
            message="1. Select row to edit (left/right numbers):",
            valid_input=[str(i) for i in range(table.num_rows)] + exit_strings,
        )
        # Check if user wants to exit
        if self._check_exit_condition(row_index, exit_strings):
            return []

        # Get column number to edit
        column_index = utils.input_(
            message="2. Select column to edit (top/bottom numbers):",
            valid_input=[str(i) for i in range(table.num_columns)]
            + exit_strings,
        )
        # Check if user wants to exit
        if self._check_exit_condition(column_index, exit_strings):
            return []

        # Convert to int
        try:
            row_index = int(row_index)
            column_index = int(column_index)
        except ValueError:
            print(f"ERROR: Invalid input!: {column_index}")
            return []

        # Adjust row index for headers
        if row_index > 0:
            row_index -= 1
            is_header = False
        else:
            is_header = True

        # Set valid input based on if the selected cell is a header
        if is_header:
            valid_input = "^(?:[\d\w]+|exit|)$"
        else:
            valid_input = "^(?:\d+|exit|)$"
            
        # Get replacement value
        replace = utils.input_(
            message="3. Replace cell with:",
            # First pattern is for rows, second is
            # for headers
            valid_input=valid_input,
        )
        # Check if user wants to exit
        if self._check_exit_condition(replace, exit_strings):
            return []

        return [row_index, column_index, replace]

    def _check_exit_condition(
        self, user_input: str, exit_strings: list[str]
    ) -> bool:
        for exit_string in exit_strings:
            if user_input == exit_string:
                return True

        return False

    def main_menu(self) -> int:
        # Create options
        options = [
            "create table",
            "select a table",
            "print all tables",
            "edit a table",
            "get regex patterns",
        ]
        valid_input = f"^[1-{len(options)}]$"

        # Display options
        for i, option in enumerate(options):
            print(f"{i+1}. {option.title()}")

        # Get user input
        choice = utils.input_(
            message="Enter your choice:", valid_input=valid_input
        )
        print()  # Newline separator

        return choice

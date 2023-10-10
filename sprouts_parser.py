import file
from regex_file import RegexInput
from markdown_table import TableOrganizer, RegexTable
from typing import Sequence
from data import DataParser


class SproutsParser(DataParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex_file = RegexInput(kwargs.get("type") or "dict")
        self.tables = TableOrganizer()
        self._parser = DataParser()
        self.pad_char = "_"
        self.patterns = {
            "DOLLAR_AMOUNT": "^\\$(?!0.00)\\d+\\.\\d{2}$",
            "VENDOR_ITEM": "^\\d{4,5}?$",
            "UNITS_RECEIVED": "^\\d+\\.0{2}$",
            "RE_STRIPPER": "^\\^|\\$$"
        }

    @staticmethod
    def get_headers(data: list[str] | int, offset: int = 0) -> list[str]:
        """Return the headers for the data."""
        # Convert rows to monotonic segments
        headers = []

        header_count = (data if type(data) == int else len(data))

        # Create the headers
        for i in range(header_count - offset):
            headers.append(f"Shipment {i + 1}")

        return headers

    def _create_table(self,
                      rows: Sequence[str] | Sequence[Sequence[str]],
                      headers: Sequence[str] | Sequence[Sequence[str]],
                      ) -> None:
        """Create a `RegexTable` and add it to `tables`."""
        self.add_table(TableOrganizer.create_table(rows, headers))

    def _segment(self,
                 data: list[str],
                 max_rows: int,
                 ignore: str = "|") -> list[list[str]]:

        try:
            # Attempt multiple segmentation methods and see which returns
            # The most accurate results
            duplicates = self._parser.segment_duplicates(data, ignore)
            separator = self._parser.segment_separator(data, ignore)
            # Get a padded list of stringify data for monotonic segmentation
            data = self._parser.pad_list(self._parser.stringify(data),
                                         pad="0",
                                         justify="l",
                                         remove=ignore)
            monotonic = self._parser.segment_monotonic(data)

        except ValueError as e:
            # If the data cannot be segmented, raise an error
            # Likely to be caused by an invalid `pad_char` value because
            # arithmetic is performed on the data.
            raise ValueError(f"Error segmenting data: {e}\n"
                             f"value: {data}\n")
        else:
            if max_rows:
                # Return the segmented data in the most accurate order
                if len(separator) == max_rows:
                    return separator
                elif len(monotonic) == max_rows:
                    return monotonic
                elif len(duplicates) == max_rows:
                    return duplicates
                else:
                    # No segmentation methods returned the
                    # correct number of rows
                    raise ValueError(f"Error segmenting data: No segmentation"
                                     f"methods returned the correct number of"
                                     f"rows.\nvalue: {data}")
            else:
                # Return the segmented data in the most accurate order
                return separator or monotonic or duplicates

    def table(self, index: int) -> RegexTable:
        """Return the table at `index`."""
        return self.tables.get_table(index)

    def create_table(self,
                     rows: list[str] | tuple[str],
                     headers: list[str] | tuple[str] = None,
                     invoice_scan: int = 1,
                     ignore: str = "|",
                     missing_label: str = "----",
                     scan_missing_label: str = "////",
                     incorrect_label: str = "!!!!",
                     ) -> None:
        """
        Create a `RegexTable` and add it to `tables`.

        If `invoice_scan` is 1 or greater, the leftmost columns will up
        to `invoice_scan` amount will become scan columns. This means
        that when values are missing from other columns but are in
        these columns, the content of the cells in the other columns
        will be replaced with "////". List overlap generated will not
        take into account scan columns.

        If `invoice_scan` is 0, there will be no scan columns and list
        overlap will be generated based on all columns (not including
        the "Total Values" column).

        Args:
            rows: A `list` of strings or a `list` of `list`s of strings
                to be used for the table rows.
            headers: A `list` of strings or a `list` of `list`s of
                strings to be used for the table headers.
            invoice_scan: The number of columns to use as scan columns.
            ignore: A `str` of characters to filter out of the list.
            missing_label: The label to use for blanks in cells when
                the value is in at least one row and is in a scan
                column.
            scan_missing_label: The label to use for blanks in cells
                when the value is not in any rows and is in a scan
                column.
            incorrect_label: The label to use for blanks in cells when
                the value is not in any rows and is not in a scan
                column.

        Returns:
            None
        """
        final_rows = []

        if not rows:
            # `rows` is empty
            print("No rows provided")
            return

        # Flatten `rows` if it is a list of lists
        rows = self._parser.flatten(rows)

        # Remove leading zeros from `rows` (to sync with `total_values`)
        rows = self._parser.remove_leading(rows, "0")

        # Convert `rows` to a list of strings for proper segmentation
        rows = self._parser.stringify(rows)

        # Get unique values, sorted and filtered, for Total Values column
        total_values = self._parser.unique_list(rows,
                                                sort=True,
                                                remove=ignore)

        # Segment data for table rows
        if headers:
            rows = self._segment(rows, len(headers))
        else:
            rows = self._segment(rows, 0)

        # If invalid `invoice_scan` value, set to 1
        try:
            if invoice_scan < 0 or invoice_scan > len(rows):
                invoice_scan = 0
        except TypeError:
            invoice_scan = 0

        # Separate scan column rows from other column rows
        scan_column_rows = []
        for j in range(invoice_scan):
            try:
                scan_column_rows.append(rows.pop(0))
            except IndexError as e:
                # There are no more rows to pop
                raise IndexError(f"Error popping rows: {e}\nvalue: {rows}")

        # Create empty containers for the filled rows
        filled_rows = []
        filled_scan_column_rows = []
        for _ in range(len(total_values)):
            filled_rows.append([])
            filled_scan_column_rows.append([])

        # Go through `total_values` and fill in the blank cells in rows with:
        #   "----" for values in scan and at least one row
        #   "////" for values in scan but not in any rows
        #   "!!!!" for values not in scan
        # values that are in scan columns but not in other columns
        for i in range(len(total_values)):
            # Remove padding for comparison reasons
            value = total_values[i]
            # ==========Check if the value is in both scan and row==========
            if invoice_scan:
                # Check if `value` is in any scan list at all
                in_scan = value in [item for sublist in scan_column_rows
                                    for item in sublist]
            else:
                # If not using invoice scan, don't use scan column labeling
                in_scan = True

            # Check if `value` is in any non-scan list at all
            in_rows = value in [item for sublist in rows
                                for item in sublist]

            # Iterate through scan column rows to create
            # "----", "////", and "!!!!" cells
            for row in scan_column_rows:
                if value not in row and not in_scan:
                    # The value is not in the row or any scan column "!!!!"
                    filled_scan_column_rows[i].append(incorrect_label)
                elif value not in row and in_scan:
                    # The value is not in the row but is in a scan column "----"
                    filled_scan_column_rows[i].append(missing_label)
                else:
                    # The value is in the row
                    filled_scan_column_rows[i].append(value)
                    in_scan = True

            # Iterate through non-scan column rows to create
            # "----", "////", and "!!!!" cells
            for row in rows:
                # Check if the value exists in the current row
                value_found = value in row
                if not value_found and in_scan:
                    # The value is not in the row but is in a scan column
                    if in_rows:
                        # Value is in at least one row "----"
                        filled_rows[i].append(missing_label)
                    else:
                        # Value is not in any rows "////"
                        filled_rows[i].append(scan_missing_label)
                elif not value_found and not in_scan:
                    # The value is not in the row or in a scan column "!!!!"
                    filled_rows[i].append(incorrect_label)
                else:
                    # The value is in the row "value"
                    filled_rows[i].append(value)

        # Combine the total values, scan column rows, and other column rows
        for i in range(len(filled_scan_column_rows)):
            # Add the scan column rows to the other column rows
            final_rows.append(filled_scan_column_rows[i] + filled_rows[i])

            # Insert the total values into the last column
            final_rows[i].append(total_values[i])

        # Check the number of headers passed as args the same length as the
        # number of table columns
        if not headers or len(headers) < len(final_rows[0]) - 1:
            headers = []
            # Update the headers for the scan columns if any exist
            for i in range(invoice_scan):
                headers.append(f"Scan {i + 1}")

            # Update the headers for the non-scan columns
            headers.extend(self.get_headers(len(final_rows[0]) - 1,
                                            offset=invoice_scan))

        # Insert the "Total Values" column at the end of the headers
        headers.append("Total Values")

        # Pad final rows with `pad_char`
        max_length = self._parser.get_max_str_length(total_values)
        padded_rows = [self._parser.pad_list(row,
                                             pad=self.pad_char,
                                             max_length=max_length,
                                             ignore=f"{scan_missing_label}"
                                                    f"{missing_label}"
                                                    f"{incorrect_label}"
                                             )
                       for row in final_rows]

        # Create the table
        self._create_table(final_rows, headers)

    def add_table(self, table: RegexTable) -> None:
        """Add a `RegexTable` to `tables`."""
        self.tables.add_table(table)

    def parse_data_monotonic(self, data: list[str]) -> list[list[str]]:
        """Parses a `list` and returns headers and rows for the data."""
        # Returns:
        #   [0]: Monotonic segments
        #   [1]: Headers
        return [self.segment_monotonic(data), self.get_headers(data)]

    def get_patterns(self) -> str:
        """Return all regex patterns in all stored tables."""
        ret = ""
        for table in self.tables:
            ret += table.patterns.to_string()

        return ret


if __name__ == "__main__":
    # Driver code
    sprouts_parser = SproutsParser()

    # Determine if config file exists

    # Load patterns from config file if they exist

    # Prompt user to use data file or input data
    print("System will try to parse your data. Shipments should be separated "
          "by a blank line if you select data file.\n")
    print(f"1. Use data file")
    print("2. Input data")
    user_choice = file.input_(["1", "2"])

    # If user chooses to use data file, load data from file
    filename = file.exists("data.txt")
    if user_choice == "1":
        while not filename:
            # Prompt user to enter a valid filename until one is entered or
            # the user chooses to exit
            print(f"File does not exist. Please enter valid "
                  "filename (0 to exit):")

            # Get user input for filename
            filename = file.exists(input("Filename: "))

            if filename in ["exit", "0", "e"]:
                # User chooses to exit
                print("Exiting...")
                exit(0)

        # Get row data from file
        rows = file.read_file_lines(filename)
    else:
        # Prompt user to input data since they chose not to use a file
        # Get total number of shipments
        shipment_amount = int(file.input_("^[1-9][0-9]*$",
                                          message="Enter Total Shipments: "))
        rows = []
        # for shipment in range(shipment_amount):
        #     # Get data for each shipment
        #     print(f"\nShipment {shipment + 1} "
        #           f"(Type each vendor item on a new line):")
        #     rows.append(file.read_input_lines())
        #     # Separate shipments with a dashed line
        #     rows.append("|")
        rows = [["000001", "0324", "17842", "001", "3281"],
                ["|"],
                ["0002", "9243", "7131", "9942", "9999"],
                ["|"],
                ]

    # Create a table
    sprouts_parser.create_table(rows=rows[:-1], invoice_scan=0)

    # Print the table
    table = sprouts_parser.tables.get_table(-1)
    print(table.to_string())

    print("patterns:", sprouts_parser.get_patterns())
    print("Overlap:", sprouts_parser.table(-1).overlap)
    print("Total", sprouts_parser.table(-1).unique_values)

    print([f"{item}" for item in table.rows_pattern])
    print(table.columns_pattern)

from data import DataParser
from regex_pattern_collections import RegexDict
from regex_search import RegexSearch


class MarkdownTable:

    def __init__(self):
        self.headers = []
        self.rows = []
        self.columns = []
        self.num_columns = 0
        self._max_str_length = 0
        self.duplicates = [{}, 0]
        self.non_duplicates = [[], 0]
        self.unique_values = [[], 0]
        self.overlap = [{}, 0]
        self.has_totals_col = False
        self.has_scan_col = False

    def __str__(self) -> str:
        """Return the Markdown table."""
        return self.to_string("center")

    def _get_table_separator(self, position: str = "center") -> str:
        """Returned a positioned table separator."""
        position = position.casefold()
        if position == "center":
            return "| " + " | ".join(["-" * self._max_str_length
                                      for _ in self.headers]) + " |\n"
        elif position == "left":
            return "| " + " | ".join([":" + "-" * (self._max_str_length - 1)
                                      for _ in self.headers]) + " |\n"
        elif position == "right":
            return "| " + " | ".join(["-" * (self._max_str_length - 1) + ":"
                                      for _ in self.headers]) + " |\n"
        elif position == "xcenter":
            return ("| "
                    + " | ".join([":" + "-" * (self._max_str_length - 2) + ":"
                                  for _ in self.headers])
                    + " |\n"
                    )

    def _get_longest_value(self) -> int:
        """Return the largest length of all strings in `rows` and `headers`."""
        try:
            # Get the highest length value from headers
            max_header_num = max(map(lambda x: len(str(x)), self.headers))
        except ValueError as e:
            # If there are no headers, set the value to 0
            max_header_num = 0

        try:
            # Get the highest length value from rows
            max_row_num = max(map(lambda x: len(str(x)),
                                  [value for row in self.rows
                                   for value in row]
                                  )
                              )
        except ValueError as e:
            # If there are no rows, set the value to 0
            max_row_num = 0

        # Return the highest value
        return max(max_header_num, max_row_num)

    def _update_max_str_length(self) -> None:
        """Update the `_max_str_length` attribute."""
        self._max_str_length = self._get_longest_value()

    def _set_column_bools(self):
        """Update `has_totals_col` and `has_scan_col`."""
        for header in self.headers:
            if "scan" in header.casefold():
                self.has_scan_col = True
            if "total" in header.casefold():
                self.has_totals_col = True

    def _set_overlap(self):
        """Update `overlap` with all duplicate non-scan column values"""
        self.overlap[0].clear()
        # Set end index for checking columns for overlap
        end = len(self.headers) if not self.has_totals_col \
            else len(self.headers) - 1

        # Set start index to first non-scan column index
        start = 0
        if self.has_scan_col:
            # Skip all scan columns
            for i in range(self.num_columns):
                if "scan" in self.headers[i].casefold():
                    start = i + 1

        # Get all values that appear in more than one non-scan column
        for value in self.unique_values[0]:
            count = 0
            for column in self.columns[start:end]:
                if value in column:
                    # Value was found in a non-scan column
                    count += 1

                if count > 1:
                    # Value appears in more than one non-scan column
                    self.overlap[0][value] = count

    def _update_table_stats(self) -> None:
        """
        Identifies duplicate values in `rows`.

        Finds all duplicate values in `rows` and returns a `tuple` containing
        the duplicate values, non-duplicate values, and unique values. Then
        updates the `duplicates`, `non_duplicates`, and `unique_values` with:
            - A `dict` of duplicate values and count of occurrences.
            - A `list` of non-duplicate values.
            - A `list` of all unique values

        Returns:
            None
        """
        # Strings to remove from `rows` when counting duplicates, non-dups, etc.
        remove_strings = ["////", "!!!!", "----", "====", "****", "~~~~"]

        # Flatten `rows` into a single list
        rows = [value for row in self.rows
                for value in row]
        # Get all unique values and sort them
        unique_values = sorted(set(rows))

        # Remove `remove_strings` from `unique_values`
        for string in remove_strings:
            try:
                # `string` found in `unique_values`
                unique_values.remove(string)
            except ValueError:
                # `string` not found in `unique_values`
                pass

        # Create containers for the duplicate and non-duplicate values
        duplicate_values = {}
        non_duplicate_values = []

        # Count the number of times each value appears in `lines`
        for value in unique_values:
            value_count = rows.count(value)
            # If there is a "total values" column in the table, subtract 1
            # to make sure it is not counted as a duplicate
            if self.has_totals_col:
                value_count -= 1

            if value_count > 1:
                # There is more than one instance of `value` in `lines`
                duplicate_values[value] = value_count
            else:
                # There is only one instance of `value` in `lines`
                non_duplicate_values.append(value)

        # Update the table stats
        self.duplicates = [duplicate_values, len(duplicate_values)]
        self.non_duplicates = [non_duplicate_values, len(non_duplicate_values)]
        self.unique_values = [unique_values, len(unique_values)]
        self._set_columns()
        self._set_overlap()

    def max_row_length(self) -> int:
        """Return the length of the longest row."""
        self._update_max_str_length()
        return self._max_str_length

    def to_string(self, position: str = "center") -> str:
        """Return the Markdown table as a string."""
        # Add the headers
        table = ("| "
                 + " | ".join(self.format_list(self.headers, position))
                 + " |\n")

        # Add the header separator
        table += self._get_table_separator(position)

        # Check that each row has the same number of columns as the headers
        for i in range(len(self.rows)):
            if len(self.rows[i]) < self.num_columns:
                # Add empty strings to the row if it has fewer columns
                self.rows[i].extend([" " * self._max_str_length
                                     for _ in
                                     range(self.num_columns - len(self.rows[i]))
                                     ])

        # Center all rows
        rows = [self.format_list(row, position) for row in self.rows]

        # Add the rows to the table
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"

        return table

    def format_list(self,
                    values: list[str],
                    position: str = "center"
                    ) -> list[str]:
        """Return a list of centered strings."""
        position = position.casefold()
        self._update_max_str_length()
        if position == "center" or position == "xcenter":
            return [value.center(self._max_str_length) for value in values]
        elif position == "left":
            return [value.ljust(self._max_str_length) for value in values]
        elif position == "right":
            return [value.rjust(self._max_str_length) for value in values]
        else:
            raise ValueError(f"Invalid `position` value: {position}")

    def _set_columns(self) -> None:
        """Create vertical columns from all rows."""
        columns = []
        for i in range(self.num_columns):
            current_column = []
            for j in range(len(self.rows)):
                current_column.append(self.rows[j][i])

            columns.append(current_column)

        self.columns = columns

    def add_row(self, values: list | tuple) -> None:
        """Add a row to the Markdown table."""
        # Check that row columns would not exceed the number of headers
        if len(values) > self.num_columns:
            error_message = ("Row columns exceed the number of headers:\n"
                             f"Num headers: {self.num_columns}\n"
                             f"Num row columns: {len(values)}\n"
                             f"Headers: {self.headers} "
                             f"| type: {type(self.headers)}\n"
                             f"Row: {values} | type: {type(values)}"
                             )
            raise ValueError(error_message)

        # Add the row to the table
        self.rows.append(values)

        # Update the `_max_str_length` attribute
        self._update_max_str_length()
        self._update_table_stats()

    def add_header(self, value: str) -> None:
        """Add a header to the Markdown table."""
        # Add the header
        self.headers.append(value)

        # Update the number of columns
        self.num_columns += 1

        # Update the `_max_str_length` attribute
        self._update_max_str_length()
        self._set_column_bools()


class RegexTable(MarkdownTable):

    def __init__(self):
        super().__init__()
        self.patterns = RegexDict()

    def _update_table_stats(self) -> None:
        super()._update_table_stats()
        self._set_patterns()

    def _set_patterns(self) -> None:
        """Update the regex patterns for the table."""
        # Set the regex patterns
        patterns = {
            "duplicates": RegexSearch.concat_patterns(
                [str(k) for k, v in self.duplicates[0].items() if v > 1]
            ),
            "non-duplicates": RegexSearch.concat_patterns(
                self.non_duplicates[0]
            ),
            "unique": RegexSearch.concat_patterns(
                self.unique_values[0]
            ),
            "overlap": RegexSearch.concat_patterns(
                list(self.overlap[0])
            ),
            "rows": [f"{RegexSearch.concat_patterns(DataParser.flatten(row))}"
                     for row in self.rows
                     ],
            "columns": [
                f"{RegexSearch.concat_patterns(DataParser.flatten(col))}"
                for col in self.columns
                ],
        }

        # Add the patterns to the collection
        self.patterns.add_patterns(patterns)

        # Update attributes to point to the patterns
        self.duplicates_pattern = self.patterns.get_pattern("duplicates")
        self.non_duplicates_pattern = self.patterns.get_pattern(
            "non-duplicates")
        self.unique_values_pattern = self.patterns.get_pattern("unique")
        self.overlap_pattern = self.patterns.get_pattern("overlap")
        self.rows_pattern = self.patterns.get_pattern("rows")
        self.columns_pattern = self.patterns.get_pattern("columns")


class TableOrganizer:

    def __init__(self):
        self.tables = []

    def __str__(self):
        """Return all markdown tables in `tables` in a string format."""
        return "\n\n".join([str(table) for table in self.tables])

    def __iter__(self):
        """Return an iterator for `tables`."""
        return iter(self.tables)

    @staticmethod
    def create_table(rows: list[list[str]] | list[tuple[str]],
                     headers: list[str] | tuple[str],
                     ) -> RegexTable:
        """Create and return a `RegexTable`."""
        table = RegexTable()

        # Add headers
        for header in headers:
            table.add_header(header)

        # Add rows
        for row in rows:
            table.add_row(row)

        # Add the table to `tables`
        return table

    def add_table(self, table: RegexTable) -> None:
        """Add a `RegexTable` to `tables`."""
        self.tables.append(table)

    def list_tables(self, position: str = "center") -> None:
        """Print all tables in `tables`."""
        for table in self.tables:
            print(table.to_string(position))

    def pop_table(self, index: int = 0) -> RegexTable:
        """Remove and return a table from `tables`."""
        try:
            return self.tables.pop(index)
        except IndexError as e:
            print(f"Error removing table: {e}")

    def get_table(self, index: int = 0) -> RegexTable:
        """Return a table from `tables`."""
        try:
            # If `index` is negative, return the last table
            if index < 0:
                index = len(self.tables) - 1

            return self.tables[index]
        except IndexError as e:
            print(f"Error getting table: {e}")

    def enum_tables(self) -> enumerate[RegexTable]:
        """Return an enumerated list of tables."""
        return enumerate(self.tables)

    def total_tables(self) -> int:
        """Return the total number of tables."""
        return len(self.tables)


if __name__ == "__main__":
    # Testing MarkdownTable
    print("==========Testing MarkdownTable==========")
    driver = MarkdownTable()

    # Add headers
    driver.add_header("Header 1")
    driver.add_header("Header 2")
    driver.add_header("Header 3")

    # Edge case: Add a header with a longer length than the rows
    driver.add_header("Header 4")

    # Add rows
    driver.add_row(["one", "two", "three"])
    driver.add_row(["one", "two", "three"])
    driver.add_row(["one", "two", "three"])

    # Edge case: Add a row with fewer columns than the headers
    driver.add_row(["one", "two"])

    # Corner case: Add a row with more columns than the headers
    driver.add_row(["one", "two", "three", "four"])

    # Print the table
    print(driver.to_string("left"))
    print(driver.to_string("right"))
    print(driver.to_string("center"))
    print(driver.to_string("xcenter"))

    # Testing TableOrganizer
    print("==========Testing TableOrganizer==========")

    # Add tables
    org = TableOrganizer()
    org.add_table(driver)
    org.add_table(driver)
    org.add_table(driver)

    # Print tables
    org.list_tables()

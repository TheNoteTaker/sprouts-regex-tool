from ..utils import unique_list, get_max_str_length, flatten
from ..regex import RegexSearch, RegexDict


class MarkdownTable:
    def __init__(self):
        self.headers = []
        self.rows = []
        self.columns = []
        self.num_columns = 0
        self.num_rows = 0
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

    def _get_table_separator(
        self, position: str = "center", grid: bool = False
    ) -> str:
        """
        Returns a positioned table separator.

        Args:
        - position (str): The position of the separator.
            Can be "center", "left", "right", or "xcenter".
        - grid (bool): Whether to use a grid separator or not.

        Returns:
        - str: The table separator string.
        """
        position = position.casefold()
        start = "| " if not grid else "- | "
        end = " |\n" if not grid else " | -\n"
        if position == "center":
            return (
                start
                + " | ".join(["-" * self._max_str_length for _ in self.headers])
                + end
            )
        elif position == "left":
            return start + " | ".join(
                [":" + "-" * (self._max_str_length - 1) for _ in self.headers]
            )
        elif position == "right":
            return (
                start
                + " | ".join(
                    [
                        "-" * (self._max_str_length - 1) + ":"
                        for _ in self.headers
                    ]
                )
                + end
            )
        elif position == "xcenter":
            return (
                start
                + " | ".join(
                    [
                        ":" + "-" * (self._max_str_length - 2) + ":"
                        for _ in self.headers
                    ]
                )
                + end
            )

    def _get_header_str(
        self, position: str = "center", grid: bool = False
    ) -> str:
        """
        Returns a string representation of the table header.

        Args:
            position (str): The alignment of the header cells.
                Can be "left", "center", or "right".
            grid (bool): Whether or not to include grid lines in
                the header.

        Returns:
            `str`: A string representation of the table header.
        """
        separator = self._get_table_separator(position, grid)
        # Show index 0 if grid is True, otherwise show normal
        # boundaries
        if grid:
            # Create header indexes list
            header_indexes = self.format_list(
                [str(i) for i in range(len(self.headers))]
            )

            # Create the header string with the index
            start = (
                "  | "
                + " | ".join(self.format_list(header_indexes, position))
                + " |\n"
            )

            end = " | 0\n"
        else:
            start = "| "
            end = " |\n"

        # Create the header string
        header_str = (
            (start + separator + "0 | " if grid else start)
            + " | ".join(self.format_list(self.headers, position))
            + end
        )

        return header_str

    def _get_rows_str(
        self,
        rows: list[list[str]],
        position: str = "center",
        grid: bool = False,
    ) -> str:
        """
        Returns a string representation of the table rows.

        Args:
            rows (list[list[str]]): The rows to be formatted.
            position (str): The alignment of the row cells.
                Can be "left", "center", or "right".
            grid (bool): Whether or not to include grid lines in
                the rows.

        Returns:
            `str`: A string representation of the table rows.
        """
        # Create the rows string
        rows_str = ""
        for index, row in enumerate(rows):
            start = "| " if not grid else f"{index + 1} | "
            end = " |\n" if not grid else f" | {index + 1}\n"

            # Add row separator inbetween rows
            if grid:
                rows_str += self._get_table_separator(position, grid)

            # Create the row string
            rows_str += (
                start + " | ".join(self.format_list(row, position)) + end
            )

        return rows_str

    def _get_longest_value(self) -> int:
        """Return the largest length of all strings in `rows` and `headers`."""
        # Get the highest length value from headers
        max_header_num = get_max_str_length(self.headers)

        # Get the highest length value from rows
        max_row_num = get_max_str_length(self.rows)

        # Return the highest value
        return max(max_header_num, max_row_num)

    def _set_column_bools(self):
        """Update `has_totals_col` and `has_scan_col`."""
        self.has_totals_col = False
        self.has_scan_col = False

        for header in self.headers:
            if "scan" in header.casefold():
                self.has_scan_col = True
            if "total" in header.casefold():
                self.has_totals_col = True

    def _set_overlap(self):
        """Update `overlap` with all duplicate non-scan column values"""
        self.overlap[0].clear()
        # Set end index for checking columns for overlap
        end = (
            len(self.headers)
            if not self.has_totals_col
            else len(self.headers) - 1
        )

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

    def _set_columns(self) -> None:
        """Create vertical columns from all rows."""
        columns = []
        for i in range(self.num_columns):
            current_column = []
            for j in range(len(self.rows)):
                current_column.append(self.rows[j][i])

            columns.append(current_column)

        self.columns = columns

    def _update_counts(self) -> None:
        """
        Update the first index, count, of several attributes.

        This method updates the following attributes of the 
        MarkdownTable object:
        - `num_rows`: the number of rows in the table
        - `num_columns`: the number of columns in the table
        - `duplicates[1]`: the number of duplicate rows in the table
        - `non_duplicates[1]`: the number of non-duplicate rows in the 
            table
        - `unique_values[1]`: the number of unique values in the table
        - `overlap[1]`: the number of overlapping values in the table

        Returns:
            None
        """
    def _update_counts(self) -> None:
        """Update `num_rows` and `num_columns`."""
        self.num_rows = len(self.rows)
        self.num_columns = len(self.headers)
        self.duplicates[1] = len(self.duplicates[0])
        self.non_duplicates[1] = len(self.non_duplicates[0])
        self.unique_values[1] = len(self.unique_values[0])
        self.overlap[1] = len(self.overlap[0])

    def _update_table_stats(self) -> None:
        """
        Identifies duplicate values in `rows`.

        Finds all duplicate values in `rows` and returns a `tuple`
        containing the duplicate values, non-duplicate values, and
        unique values. Then updates the `duplicates`, `non_duplicates`,
        and `unique_values` with:
            - A `dict` of duplicate values and count of occurrences.
            - A `list` of non-duplicate values.
            - A `list` of all unique values

        Also updates `_max_str_length`, `overlap`, and column booleans
        for `has_totals_col` and `has_scan_col`.

        Returns:
            None
        """
        # Strings to remove from `rows` when counting duplicates, non-dups, etc.
        remove_strings = ["////", "!!!!", "----", "====", "****", "~~~~"]

        # Flatten `rows` into a single list
        rows = flatten(self.rows)
        # Get all unique values and sort them
        unique_values = unique_list(rows, sort=True, remove=remove_strings)

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
        self._update_max_str_length()
        self._update_counts()
        self._set_columns()
        self._set_overlap()

    def _update_max_str_length(self) -> None:
        """Update the `_max_str_length` attribute."""
        self._max_str_length = self._get_longest_value()

    def add_row(self, values: list | tuple) -> None:
        """Add a row to the Markdown table."""
        # Check that row columns would not exceed the number of headers
        if len(values) > self.num_columns:
            error_message = (
                "Row columns exceed the number of headers:\n"
                f"Num headers: {self.num_columns}\n"
                f"Num row columns: {len(values)}\n"
                f"Headers: {self.headers} "
                f"| type: {type(self.headers)}\n"
                f"Row: {values} | type: {type(values)}"
            )
            raise ValueError(error_message)

        # Add the row to the table
        self.rows.append(values)
        self._update_table_stats()

    def remove_row(self, index: int) -> None:
        """Remove a row from the Markdown table."""
        try:
            self.rows.pop(index)
        except IndexError:
            print("Invalid row index!")
        finally:
            self._update_table_stats()

    def add_header(self, value: str) -> None:
        """Add a header to the Markdown table."""
        # Add the header
        self.headers.append(value)

        # Update the `_max_str_length` attribute
        self._update_table_stats()

    def remove_column(self, index: int) -> None:
        """Remove a column from the Markdown table."""
        try:
            self.headers.pop(index)
            for row in self.rows:
                row.pop(index)
        except IndexError:
            print("Invalid column index!")
        finally:
            self._update_table_stats()

    def edit(self, row: int, col: int, new: str) -> None:
        """Edits values in the table, then updates the table stats."""
        print(f"Row: {row} | Col: {col} | New: {new}")  # TODO remove
        try:
            if self.rows:
                if row == 0:
                    print(f"Editing header {self.headers[col]} to {new}")  # TODO remove
                    self.headers[col] = new
                    print("After changes:", self.headers[col])
                else:
                    print(f"Editing row {self.rows[row][col]} to {new}")  # TODO remove
                    self.rows[row][col] = new
                    print("After changes:", self.rows[row][col])  # TODO remove
            else:
                print("There are no rows in the table!")
        except IndexError:
            print("Invalid row or column index!")
        finally:
            self._update_table_stats()


    def format_list(
        self, values: list[str], position: str = "center"
    ) -> list[str]:
        """Return a list of centered strings."""
        position = position.casefold()
        self._update_max_str_length()
        if position == "center" or position == "xcenter":
            return [str(value).center(self._max_str_length) for value in values]
        elif position == "left":
            return [str(value).ljust(self._max_str_length) for value in values]
        elif position == "right":
            return [str(value).rjust(self._max_str_length) for value in values]
        else:
            raise ValueError(f"Invalid `position` value: {position}")

    def max_row_length(self) -> int:
        """Return the length of the longest row."""
        self._update_max_str_length()
        return self._max_str_length

    def to_string(self, position: str = "center", grid: bool = False) -> str:
        """Return the Markdown table as a string."""
        # Header string
        table = self._get_header_str(position, grid)

        # Header separator
        table_separator = self._get_table_separator(position, grid)
        if not grid:
            table += table_separator

        # Insert empty string values into row cells for rows that have
        # fewer columns than the number of headers
        for i in range(len(self.rows)):
            if len(self.rows[i]) < self.num_columns:
                self.rows[i].extend(
                    [
                        " " * self._max_str_length
                        for _ in range(self.num_columns - len(self.rows[i]))
                    ]
                )

        # Center all rows and add them to the table
        rows = [self.format_list(row, position) for row in self.rows]
        table += self._get_rows_str(rows, position, grid)

        if grid:
            # Add the row indexes separator
            table += table_separator

            # Get the row indexes
            row_indexes = self.format_list(
                [str(i) for i in range(len(self.headers))]
            )

            # Add the row indexes to the table
            table += "  | " + " | ".join(row_indexes) + " |\n"

        return table


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
            "unique": RegexSearch.concat_patterns(self.unique_values[0]),
            "overlap": RegexSearch.concat_patterns(list(self.overlap[0])),
            "rows": [],
            "columns": [],
        }

        # Sanitize rows and columns
        sanitized_rows = []
        sanitized_columns = []
        for row in self.rows:
            # Sanitize
            sanitized_row = []
            for item in unique_list(row):
                if item in self.unique_values[0]:
                    sanitized_row.append(item.strip())

            if sanitized_row:
                sanitized_rows.append(
                    RegexSearch.concat_patterns(sanitized_row)
                )

        for col in self.columns:
            sanitized_column = []
            for item in col:
                if item in self.unique_values[0]:
                    sanitized_column.append(item.strip())

            if sanitized_column:
                sanitized_columns.append(
                    RegexSearch.concat_patterns(sanitized_column)
                )

        # Add sanitized rows and columns to the patterns
        patterns["rows"] = sanitized_rows

        patterns["columns"] = sanitized_columns

        # Add the patterns to the collection
        self.patterns.add_patterns(patterns)

        # Update attributes to point to the patterns
        self.duplicates_pattern = self.patterns.get_pattern("duplicates")
        self.non_duplicates_pattern = self.patterns.get_pattern(
            "non-duplicates"
        )
        self.unique_values_pattern = self.patterns.get_pattern("unique")
        self.overlap_pattern = self.patterns.get_pattern("overlap")
        self.row_patterns = self.patterns.get_pattern("rows")
        self.column_patterns = self.patterns.get_pattern("columns")

    def get_pattern(self, pattern: str) -> str:
        """Return the regex pattern for `pattern`."""
        return self.patterns.get_pattern(pattern)

    def get_patterns(self) -> dict[str, str]:
        """Return the regex patterns."""
        return self.patterns.to_dict()

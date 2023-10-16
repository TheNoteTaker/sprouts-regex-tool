from ..utils import unique_list, get_max_str_length
from ..regex import RegexSearch, RegexDict


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
        # Get the highest length value from headers
        max_header_num = get_max_str_length(self.headers)

        # Get the highest length value from rows
        max_row_num = get_max_str_length(self.rows)

        # Return the highest value
        return max(max_header_num, max_row_num)

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

    def _set_columns(self) -> None:
        """Create vertical columns from all rows."""
        columns = []
        for i in range(self.num_columns):
            current_column = []
            for j in range(len(self.rows)):
                current_column.append(self.rows[j][i])

            columns.append(current_column)

        self.columns = columns

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

    def _update_max_str_length(self) -> None:
        """Update the `_max_str_length` attribute."""
        self._max_str_length = self._get_longest_value()

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
            "non-duplicates")
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

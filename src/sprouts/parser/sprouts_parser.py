from .. import utils
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class Table:
    """
    A class representing a table of data.

    Attributes:
        df (pd.DataFrame): The pandas `DataFrame` containing the
            table data.
        scan_col_df (pd.DataFrame): A `DataFrame` containing all
            columns that begin with "Scan".
        shipment_col_df (pd.DataFrame): A `DataFrame` containing all
            columns that begin with "Shipment".
        headers (list[str]): A `list` of column headers for the
            `DataFrame` in `df`.

    Methods:
        __init__(self, filename: str, *args, **kwargs) -> None:
            Initialize a `Table` object.
        __str__(self) -> str:
            Return a string representation of the `DataFrame`.
        _pre_process_file(self, filepath: str, num_scan_col: int = 1) -> list[pd.Series]:
            Pre-process a file before parsing it with `pd.read_csv`.
        _isolate_columns(self) -> None:
            Creates `scan_columns` and `shipment_columns` attributes.
        _gen_headers(self, max_: int, header_one_cols: int, header_one: str, header_two: str) -> list[str]:
            Generate a `list` of numbered column headers up to `max_`.
        _create_series(self, data: list[str], name: str = "", sort: bool = True) -> pd.Series:
            Create a pandas `Series` from the given data.
        _create_series_from_list(self, data: list[list[str]], headers: list[str], sort: bool = True) -> list[pd.Series]:
            Create a `dict` of `Series` objects from a `list` of lists.
        _fill_missing_values(self, df_row: pd.Series) -> None:
            Conditionally fills `NaN` values in a `pd.Series` object.
        align_series_list(self, data: list[pd.Series]) -> list[pd.Series]:
            Sorts and aligns indexes and values of all `Series` in `data`.
    """

    def __init__(self, filename: str, num_scan_col: int = 0, *args, **kwargs) -> None:
        """
        Initialize a `Table` object.

        Args:
            filename (str): The path to the file to be parsed.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        self.scan_col_df = None
        self.shipment_col_df = None
        self.headers = {}
        self.num_scan_col = num_scan_col

        base_data = self._pre_process_file(filename, self.num_scan_col)

        # Create a DataFrame from the pre-processed data
        self.df = pd.concat(
            base_data,
            *args,
            axis=1,
            keys=self.headers["names"],
            **kwargs,
        )

        # Create scan_columns and shipment_columns attributes
        self.scan_col_df, self.shipment_col_df = self._isolate_columns(self.df)

        # Fill missing values based on custom logic
        self.df.apply(self._fill_missing_values, axis=1)

        self.compare = Comparator(self.df)

    def __str__(self) -> str:
        """
        Returns a string representation of the `Table` object.
        """
        return str(self.df)

    def _pre_process_file(self, filepath: str, num_scan_col: int) -> list[pd.Series]:
        """
        Pre-process a file before parsing it with `pd.read_csv`.

        Args:
            filepath (str): Filepath of the file to pre-process.
            num_scan_col (int): The number of scan columns to include
                in the pre-processed data. Defaults to 0 (treat all
                columns as normal shipments).

        Returns:
            list[pd.Series]: A `list` containing the pre-processed data
                from `filepath`.
        """
        section_series = {}
        # Get the contents of the file
        file_contents = utils.read_file_string(filepath)

        # Split the file contents into sections
        sections = utils.split_delimited_string(file_contents)

        # Generate column headers
        self._gen_headers(
            max_=len(sections),
            header_one_cols=num_scan_col,
            header_one="Scan",
            header_two="Shipment",
        )

        # Convert sections to a Series objects and align them
        section_series = self._create_series_from_list(
            sections, self.headers.get("names")
        )
        section_series = self.align_series_list(section_series)

        logger.info(f"Pre-processed file [{filepath}].")
        logger.debug(f"Total series created: {len(section_series)}")

        return section_series

    def _isolate_columns(self, df: pd.DataFrame) -> list[pd.DataFrame, pd.DataFrame]:
        """
        Identifies "Scan" columns and "Shipment" columns in `df`.

        This method iterates through the existing column names in
        `df` and creates a `pd.DataFrame` for each set of relevant
        columns. Relevant columns are those that begin with "Scan"
        for "Scan" columns and "Shipment" for "Shipment" columns.

        Args:
            df (pd.DataFrame): The `DataFrame` to isolate columns
                from.

        Returns:
            list[pd.DataFrame, pd.DataFrame]: A `list` containing
                two `DataFrames`, the firstcontaining all "Scan"
                columns and the second containing all "Shipment"
                columns.
        """
        ret = []

        # Get all scan columns
        scan_columns = [
            df[col] for col in df.columns if col.casefold().startswith("scan")
        ]

        # Get all shipment columns
        shipment_columns = [
            df[col] for col in df.columns if col.casefold().startswith("shipment")
        ]

        if scan_columns:
            ret.append(
                pd.concat(
                    [
                        df[col]
                        for col in df.columns
                        if col.casefold().startswith("scan")
                    ],
                    axis=1,
                )
            )
        else:
            logger.warning(
                "No scan columns found in DataFrame passed to _isolate_columns()"
            )
            ret.append(pd.DataFrame())

        if shipment_columns:
            ret.append(
                pd.concat(
                    shipment_columns,
                    axis=1,
                )
            )
        else:
            logger.warning(
                "No shipment columns found in DataFrame passed to _isolate_columns()"
            )
            ret.append(pd.DataFrame())

        if not shipment_columns and not scan_columns:
            logger.warning(
                "No scan or shipment columns found in DataFrame passed "
                "to _isolate_columns()"
            )

        return ret

    def _gen_headers(
        self,
        max_: int,
        header_one_cols: int,
        header_one: str,
        header_two: str,
    ) -> dict[str, list[str] | list[list[int]]]:
        """
        Generate a `dict` of numbered column headers up to `max_`.

        This method allows for creating two different headers that
        pick up where the other left off. Also sets the `headers`
        attribute.

        Example:

        - `max_ = 6`
        - `header_one_cols = 3`
        - `header_one = "Scan"`
        - `header_two = "Shipment"`

        The following headers will be created:

        `[Scan 1, Scan 2, Scan 3, Shipment 4, Shipment 5, Shipment 6]`

        Args:
            max_: The total number of columns in the `DataFrame`.
            header_one_cols: The number of columns to use for the
                first header.
            header_one: The text to use for the first header.
            header_two: The text to use for the second header.

        Returns:
            A `dict` in the format:
                "names": [list of column names],
                "indices": [[list of scan column indices],
                           [list of shipment column indices]]
        """
        logger.debug("Generating column headers...")
        headers = {
            "names": [],
            "indices": [[], []],
        }
        index = 0

        # Ensure num_scan_col is within range
        if header_one_cols < 0:
            header_one_cols = 0
        elif header_one_cols > max_:
            header_one_cols = max_

        # Create column 1 headers
        for i in range(header_one_cols):
            col_one_header = f"{header_one.title()} {i + 1}"
            headers["names"].append(col_one_header)
            headers["indices"][0].append(index)
            index += 1

        # Create column 2 headers
        for i in range(header_one_cols, max_):
            col_two_header = f"{header_two.title()} {i + 1}"
            headers["names"].append(col_two_header)
            headers["indices"][1].append(index)
            index += 1

        self.headers = headers
        logger.debug(f"Column headers generated: {self.headers}")

    def _create_series(
        self, data: list[str], name: str = "", sort: bool = True
    ) -> pd.Series:
        """
        Create a pandas `Series` from the given data.

        `data` is converted to a `set` to remove duplicates, then
        sorted numerically if `sort` is `True`.

        Args:
            data (list[str]): The data to create the `Series` from.
            name (str, optional): The name of the `Series`.
                Defaults to "".
            sort (bool, optional): Whether to sort `data`. Attempts
                numerical sort and falls back to default `sorted`
                upon failure. Defaults to `True`.

        Returns:
            pd.Series: The pandas`Series` created from `data`.
        """

        # Sort data into numerical order if enabled
        if sort:
            try:
                sorted_list = sorted(set([int(i) for i in data]))
            except ValueError:
                # Data cannot be sorted numerically
                sorted_list = sorted(set(data))

            # Convert data back to a list of strings
            data = [str(i) for i in sorted_list]

        # Create a pandas series from the data
        return pd.Series(data, name=name)

    def _create_series_from_list(
        self,
        data: list[list[str]],
        headers: list[str],
        sort: bool = True,
    ) -> list[pd.Series]:
        """
        Create a `dict` of `Series` objects from a `list` of lists.

        Args:
            data (list[list[str]]): A `list` of lists containing
                the data to be converted to `Series` objects.
            headers (list[str]): A `list` of strings containing
                the labels for the `Series` objects.
            sort (bool, optional): Whether to sort the `Series`
                objects by index. Defaults to `True`.

        Returns:
            list[pd.Series]: A `list` of pandas `Series` objects.
        """
        return [
            self._create_series(list(set(data[i])), name=headers[i], sort=sort)
            for i in range(len(data))
        ]

    def _fill_missing_values(self, df_row: pd.Series) -> None:
        """
        Conditionally fills `NaN` values in a `pd.Series` object.

        This method is meant to be used with `pd.apply` on a
        balanced `DataFrame` and fills missing values in a pandas
        `Series` object based on the following conditions (in order):

            1. If the value already exists, leave it alone.
            2. If the value exists in at least one scan column and
               at least one shipment column, fill with "-----".
            3. If the value exists in at least one scan column and
                 no shipment columns, fill with "/////".
            4. If the value does not exist in any scan columns,
                 fill with "!!!!!".

        Args:
            df_row (pd.Series): The pandas `Series` object to be filled
                with missing values. This should be provided by
                `pd.apply`.
        """
        # If there are no scan columns in the table
        if self.num_scan_col <= 0:
            for col in df_row.index:
                if pd.isna(df_row[col]):
                    df_row[col] = "-----"

            return df_row

        # Check if the index exists in any 'Scan' or 'Shipment' columns
        try:
            in_scan = (self.scan_col_df == df_row.name).any(axis=1)
        except KeyError as e:
            logger.error(
                "KeyError occurred while trying to check if index "
                f"'{df_row.name}' exists in any 'Scan' columns. "
            )
            in_scan = pd.Series(False)

        try:
            in_shipment = (self.shipment_col_df == df_row.name).any(axis=1)
        except KeyError as e:
            logger.error(
                "KeyError occurred while trying to check if index "
                f"'{df_row.name}' exists in any 'Shipment' columns. "
            )
            in_shipment = pd.Series(False)

        # Apply the fill logic to the df_row based on the conditions
        for col in df_row.index:
            # Check for NaN value before proceeding (It will not be NaN
            # if it has the value matching the index)
            if pd.isna(df_row[col]):
                # Case 1: Exists in both 'Scan' and 'Shipment' -> "-----"
                if in_scan.any() and in_shipment.any():
                    df_row[col] = "-----"

                # Case 2: Exists in a 'Scan' but not any 'Shipment' -> "/////"
                elif in_scan.any() and not in_shipment.any():
                    df_row[col] = "/////"

                # Case 3: Does not exist in any 'Scan' -> "!!!!!"
                elif not in_scan.any():
                    df_row[col] = "!!!!!"

        return df_row

    def align_series_list(
        self,
        data: list[pd.Series],
    ) -> list[pd.Series]:
        """
        Sorts and aligns indexes and values of all `Series` in `data`.

        Reindexes a `list` of pandas `Series` objects to include
        all unique values across all `Series` objects, and puts
        them in order.

        Args:
            data (list[pd.Series]): A list of pandas Series objects
                to be reindexed.

        Returns:
            list[pd.Series]: A list of reindexed pandas `Series`
                objects.
        """
        if not data:
            raise ValueError("No data given to align_series()")

        # Get all unique values
        unique_values = sorted(set().union(*[series.values for series in data]))

        # Reindex all series to include all unique values (and put them
        # in order)
        reindexed_series = [
            pd.Series(index=s.values, data=s.values).reindex(unique_values)
            for s in data
        ]
        logger.debug(
            f"Reindexed {len(reindexed_series)} series. All series now contain "
            f"{len(reindexed_series[0])} elements."
        )

        return reindexed_series


class Comparator:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def _discard_filler_values(self, data: set[str]) -> set[str]:
        """
        Discard filler values from a set of values.

        Args:
            data (set[str]): The set of values to discard filler values
                from.

        Returns:
            set[str]: The set of values with filler values removed.
        """
        if data and not isinstance(data, set):
            data = set(data)

        return data.difference({"-----", "/////", "!!!!!"})

    def get_header_indices(self, headers: list[str]) -> dict[str, list[int]]:
        """
        Gets the indices of each header type in `headers` in `df`.

        Treats each header in `headers` as a search pattern and searches
        for matches in the column headers of `df`. Returns a `dict`
        containing the indices of where each header type was found in
        `df`.

        Example:

        - `headers = ["Scan", "Shipment"]`
        - `df.columns = ["Scan 1", "Scan 2", "Shipment 3", "Shipment
          4"]`

        The following `dict` would be returned:

            `{"Scan": [0, 1], "Shipment": [2, 3]}`

        Args:
            headers (list[str]): `list` of header types to search for.

        Returns:
            dict[str, list[int]]: A `dict` containing the indices of
                where each header type was found in `df`.
        """
        ret = {}
        for header in headers:
            # Get all column headers that match the header pattern
            matches = [
                col for col in self.df.columns if header.casefold() in col.casefold()
            ]

            # Get the index of each header
            ret[header] = [self.df.columns.get_loc(match) for match in matches]

        logger.debug(f"Found {len(ret)} header indices for headers: {headers}")
        return ret

    def get_unique_values(self, column_indexes: list[int]) -> list[str]:
        """
        Returns a `list` of unique values in the specified columns.

        Args:
            column_indexes (list[int]): List of column indexes to
                retrieve values from.

        Returns:
            list[str]: List of unique values in the specified
                columns.
        """
        if not self.validate_indexes(column_indexes):
            return []

        unique_values = [set(self.df.iloc[:, idx]) for idx in column_indexes]

        logger.debug(
            f"Found {len(unique_values)} unique values " f"for indexes {column_indexes}"
        )
        return unique_values

    def get_values(self, column_indexes: list[int]) -> list[str]:
        """
        Returns a `list` of all values in the specified columns.

        Args:
            column_indexes (list[int]): List of column indexes to
                retrieve values from.

        Returns:
            list[str]: List of all values in the specified columns.
        """
        if not self.validate_indexes(column_indexes):
            return []

        return list(self.df.iloc[:, column_indexes].values.flatten())

    def get_duplicates(self, column_indexes: list[int]) -> list[str]:
        """
        Returns all duplicates in the specified columns.

        Args:
            column_indexes (list[int]): A `list` of column
                indexes to search for duplicates.

        Returns:
            list[str]: A `list` of all values that appear more
                than once in the specified columns.
        """
        # Get all values in all columns (in list form)
        all_values_list = self.get_values(column_indexes)

        # Get all values that appear more than once
        duplicate_values = list(
            self._discard_filler_values(
                [val for val in all_values_list if list(all_values_list).count(val) > 1]
            )
        )

        logger.info(
            f"Found {len(duplicate_values)} duplicates values "
            f"for indexes: {column_indexes}"
        )
        return duplicate_values

    def get_overlap(self, column_indexes: list[int]) -> list[str]:
        """
        Returns a overlapping values in the specified columns.

        Gets the intersection of all values in the specified
        columns.

        Args:
            column_indexes (list[int]): A `list` of column indexes
                to check for overlap.

        Returns:
            list[str]: A list of values that overlap in all columns
                specified by column_indexes.
        """
        if not self.validate_indexes(column_indexes, min_=2):
            return []

        unique_values = self.get_unique_values(column_indexes)
        ret = set.intersection(*unique_values)

        if ret:
            logger.info(
                f"Found {len(ret)} overlapping values for " f"indexes: {column_indexes}"
            )
            return list(self._discard_filler_values(ret))
        else:
            logger.info(f"No overlap found for indexes: {column_indexes}")
            return []

    def get_differences(self, column_indexes: list[int]) -> list[str]:
        """
        Returns symmetric difference of values in specified columns.

        Args:
            column_indexes (list[int]): List of column indexes
                to compare.

        Returns:
            list[str]: List of unique values that are different
                across the specified columns.
        """
        if not self.validate_indexes(column_indexes, min_=2):
            return []

        unique_values = self.get_unique_values(column_indexes)
        ret = set.symmetric_difference(*unique_values)

        if ret:
            ret = list(self._discard_filler_values(ret))

            logger.info(f"Found {len(ret)} differences for indexes: {column_indexes}")
            return ret
        else:
            logger.info(f"No differences found for indexes: {column_indexes}")
            return []

    def get_scan_overlap(self, column_indexes: list[int]) -> list[str]:
        """
        Gets overlapping values between scan and shipment columns.

        Returns a list of overlapping values between scan and
        shipment columns for the given column indexes.

        Args:
            column_indexes (list[int]): List of column indexes to
                check for overlap.

        Returns:
            list[str]: List of overlapping values between scan and
                shipment columns.
        """
        if not self.validate_indexes(column_indexes, min_=2):
            return []

        scan_cols, shipment_cols = self._get_scan_and_ship_cols(column_indexes)

        if scan_cols and shipment_cols:
            # Get overlap of scan and shipment columns
            intersection = list(
                self._discard_filler_values(set(scan_cols).intersection(shipment_cols))
            )

            logger.info(
                f"Found {len(intersection)} scan overlapping values "
                f"for indexes: {column_indexes}"
            )
            return intersection
        else:
            logger.warning(
                f"No scan or shipment columns found for indexes: {column_indexes}"
            )
            return []

    def get_scan_differences(self, column_indexes: list[int]) -> list[str]:
        """
        Get the differences between the scan and shipment columns.

        Returns a list of strings representing the differences
        between the shipment columns and scan columns for the
        given column indexes.

        All values that exist in the shipment columns that are not
        found in the scan columns are returned.

        Args:
            column_indexes: A `list` of integers representing the
                column indexes to compare.

        Returns:
            list[str]: A `list` of strings representing the
                differences between the shipment columns and scan
                columns.
        """
        if not self.validate_indexes(column_indexes, min_=2):
            return []

        scan_cols, shipment_cols = self._get_scan_and_ship_cols(column_indexes)

        if scan_cols and shipment_cols:
            ret = list(set(shipment_cols).difference(scan_cols))

            logger.info(
                f"Found {len(ret)} scan differences for indexes: {column_indexes}"
            )
            return ret
        else:
            logger.warning(
                f"No scan or shipment columns found using "
                f"get_scan_differences() for indexes: "
                f"{column_indexes}"
            )
            return []

    def validate_indexes(self, column_indexes: list[int], min_: int = 1) -> list[bool]:
        """
        Checks that all indexes in `column_indexes` are valid indexes.

        Looks at indices in column_indexes and verifies that they
        are all within range of the total columns in `df`.

        Returns a `list` of `bool` values indicating whether each
        index in `column_indexes` is invalid.
            `True` = valid
            `False` = invalid

        Args:
            column_indexes (list[int]): list of column indexes to
                check.
            min (int, optional): The minimum number of indexes that
                must be given. Defaults to 1.

        Returns:
            list[bool]: A `list` of `bool` values indicating whether
                each index in `column_indexes` is invalid.
        """
        if not column_indexes:
            logger.error("Index validation failed. No column indexes given.")
            return [True]  # Failed validation
        elif len(column_indexes) < min_:
            logger.error(
                f"Index validation failed, less than 2 column indexes given. "
                f"Indices given: {column_indexes}"
            )
            return [True]  # Failed validation

        # Check that all indexes are valid
        max_ = len(self.df.columns)
        index_check = [(0 <= idx < max_) for idx in column_indexes]

        # Fail validation if any invalid indexes are found
        if not any(index_check):
            # Invalid column indexes found in column_indexes
            logger.warning(
                "Invalid column index given to get_overlap(). "
                "Invalid Index check (True=valid | False=invalid): "
                f"{list(zip(column_indexes, index_check))}"
            )

        return index_check

    def _get_scan_and_ship_cols(
        self, column_indexes: list[int]
    ) -> list[list[int], list[int]]:
        """
        Get scan and shipment column values in the specified columns.

        Verifies that the indices in `column_indexes` are valid
        indices, then looks for scan and shipment columns in the
        headers of `df`. Returns a `list` containing two `list`s,
        the first containing the values in the scan columns and
        the second containing the values in the shipment columns.

        Args:
            column_indexes (list[int]): List of column indexes to
                search for scan and shipment columns.

        Returns:
            list[list[int], list[int]]: A list containing two lists,
                the first containing the values in the scan columns
                and the second containing the values in the
                shipment columns.
        """
        # Look for scan and shipment columns indices in headers
        indices = self.get_header_indices(["scan", "shipment"])

        # Get the intersection of the indices and column_indexes
        scan_indices = list(set(indices.get("scan")).intersection(column_indexes))
        shipment_indices = list(
            set(indices.get("shipment")).intersection(column_indexes)
        )

        if scan_indices:
            # Get values in scan columns
            scan_col_values = list(
                self._discard_filler_values(self.get_values(scan_indices))
            )
        else:
            scan_col_values = []

        if shipment_indices:
            # Get values in shipment columns
            shipment_col_values = list(
                self._discard_filler_values(self.get_values(shipment_indices))
            )
        else:
            shipment_col_values = []

        return [scan_col_values, shipment_col_values]


class RegexTable(Table):
    def __init__(self, filename: str, *args, **kwargs) -> None:
        super().__init__(filename, *args, **kwargs)


def enable_full_pandas_output() -> None:
    """
    Enable full output of pandas DataFrames.

    This method sets the following pandas options:

    - `display.max_columns` to `None`
    - `display.max_rows` to `None`
    - `display.width` to `None`
    - `display.max_colwidth` to `None`
    """
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

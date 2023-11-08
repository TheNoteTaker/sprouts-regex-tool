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

    def __init__(self, filename: str, *args, **kwargs) -> None:
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

        base_data = self._pre_process_file(filename)

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

    def __str__(self) -> str:
        """
        Returns a string representation of the `Table` object.
        """
        return str(self.df)

    def _pre_process_file(
        self, filepath: str, num_scan_col: int = 1
    ) -> list[pd.Series]:
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
        ret.append(
            pd.concat(
                [df[col] for col in df.columns if col.casefold().startswith("scan")],
                axis=1,
            )
        )

        # Get all shipment columns
        ret.append(
            pd.concat(
                [
                    df[col]
                    for col in df.columns
                    if col.casefold().startswith("shipment")
                ],
                axis=1,
            )
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

        logger.debug(f"Column headers generated: {self.headers}")
        self.headers = headers

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
        # Check if the index exists in any 'Scan' or 'Shipment' columns
        in_scan = (self.scan_col_df == df_row.name).any(axis=1)
        in_shipment = (self.shipment_col_df == df_row.name).any(axis=1)

        # Apply the fill logic to the df_row based on the conditions
        for col in df_row.index:
            # Check for NaN value before proceeding (It will not be NaN
            # if it has the value matching the index)
            if pd.isna(df_row[col]):
                # Case 1: Exists in both 'Scan' and 'Shipment' -> "-----"
                if in_scan.loc[df_row.name] and in_shipment.loc[df_row.name]:
                    df_row[col] = "-----"

                # Case 2: Exists in a 'Scan' but not any 'Shipment' -> "/////"
                elif in_scan.loc[df_row.name] and not in_shipment.loc[df_row.name]:
                    df_row[col] = "/////"

                # Case 3: Does not exist in any 'Scan' -> "!!!!!"
                elif not in_scan.loc[df_row.name]:
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

    def _discard_filler_values(self, data: set[str]) -> set[str]:
        """
        Discard filler values from a set of values.

        Args:
            data (set[str]): The set of values to discard filler values
                from.

        Returns:
            set[str]: The set of values with filler values removed.
        """
        return data.difference({"-----", "/////", "!!!!!"})

    # ==========DATA RETRIEVAL METHODS==========

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
        return [set(self.df.iloc[:, idx]) for idx in column_indexes]

    def compare(
        self, column_indexes: list[int], comp_type: str = "overlap"
    ) -> list[str]:
        """
        Get overlapping values between all columns in `column_indexes`.

        Gets the intersection of all values in all columns in
        `column_indexes`.

        Args:
            column_indexes (list[int]): `list` of column indexes to get
                the intersection of.

        Returns:
            list[str]: A `list` of all values that exist in all
                columns in `column_indexes`.
        """
        if not column_indexes:
            raise ValueError("No column indexes given to get_overlap()")
        elif len(column_indexes) < 2:
            raise ValueError(
                "get_overlap() requires at least 2 column indexes to compare"
            )

        # Get all unique values
        unique_values = self.get_unique_values(column_indexes)

        if comp_type == "overlap":
            ret = set.intersection(*unique_values)
        elif comp_type == "difference":
            ret = set.difference(*unique_values)
        elif comp_type == "scan":
            # Get all scan and shipment column indexes
            scan_col_indexes = list(set(self.headers.get("indices")[0]).intersection(
                column_indexes
            ))
            shipment_col_indexes = list(set(self.headers.get("indices")[1]).intersection(
                column_indexes
            ))

            # Compare scan columns with indexes in column_indexes to
            # shipment columns with indexes in column_indexes
            if scan_col_indexes and shipment_col_indexes:

                # Get values in scan columns
                scan_col_values = set(
                    self.df.iloc[:, scan_col_indexes].values.flatten()
                )

                print(scan_col_values)

                # Get values in shipment columns
                shipment_col_values = set(
                    self.df.iloc[:, shipment_col_indexes].values.flatten()
                )

                print(shipment_col_values)

                ret = scan_col_values.difference(shipment_col_values)

            else:
                ret = []

        else:
            raise ValueError(
                f"Invalid comparison type '{comp_type}'. Valid types are 'overlap' and 'difference'."
            )

        # Discard filler values
        if ret:
            ret = list(self._discard_filler_values(ret))

        logger.info(f"Compared columns {column_indexes} with type '{comp_type}'.")
        logger.info(f"Total values found in comparison: {len(ret)}")
        return ret


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

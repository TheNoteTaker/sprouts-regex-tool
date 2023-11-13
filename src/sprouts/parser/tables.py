from .. import utils
import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)


class Table:
    """
    A class for handling and analyzing data tables.

    This class encapsulates a pandas `DataFrame` and provides
    methods for its manipulation and analysis. It facilitates
    operations such as data validation, header management, and
    data retrieval.

    All columns are labeled with an incremental number, starting at 1
    as "Column 1", "Column 2", etc.

    Attributes:
        filepath (str): The path to the file that was parsed.
        filter_values (list[str]): A `list` of strings containing
            values to be filtered out of the data for all retrieval
            methods.
        df (pd.DataFrame): The pandas DataFrame containing the data.

    Methods:
        __init__(filename: str, *args, **kwargs): Initializes the
            `Table` object with data from the specified file.
        __str__(): Returns a string representation of the `DataFrame`.
        _init_table(data: list[pd.Series], *args, **kwargs): Creates
            a `DataFrame` from the given data.
        _pre_process_file(filepath: str):
            Pre-processes a file before loading it into a `DataFrame`.
        _create_series(data: list[str], name: str = "",
            sort: bool = True): Creates a pandas Series from the
                given data.
        _create_series_from_list(data: list[list[str]],
            headers: list[str], sort: bool = True): Creates a
                    dictionary of Series objects.
        _get_values(column_indexes: list[int], unique: bool = False):
            Retrieves all values in specified columns.
        hard_refresh(*args, **kwargs): Updates the table with the
            latest data from the `DataFrame`.
        reindex_df(df: pd.DataFrame, *args, **kwargs): Reindexes and
            aligns `df` so all columns are in order.
        align_series_list(data: list[pd.Series]): Aligns the indexes
            and values of all Series in the list.
        validate_indexes(column_indexes: list[int], min_: int = 1):
            Validates the specified column indexes.
        update_headers(headers: list[str] | dict, *args, **kwargs):
            Updates the column headers of `df` with the given headers.
        filter_list(data: list, remove_values: list[str]): Filters a
            list of values.
        get_header_indices(headers: list[str]): Retrieves indices of
            each header type in the `DataFrame`.
        get_values(column_indexes: list[int], unique: bool = False):
            Retrieves all values in specified columns or batches.
        get_duplicates(column_indexes: list[int]): Identifies
            duplicates in specified columns.
        get_overlap(column_indexes: list[int]): Finds overlapping
            values in specified columns.
        get_differences(column_indexes: list[int]): Determines
            symmetric differences in specified columns.
        set_iloc(row: int | list[int], col: int | list[int],
            value: int): Sets a value in the `DataFrame` at the
                specified row and column.
        set_loc(row: str | list[str], col: str | list[str],
            value: int): Sets a value in the `DataFrame` at the
                specified row and column.
        info(columns: list[str] | list[list[str]]): Prints information
            about the `Table` object.
        dict_to_df_dict(data: dict, key_name: str = "Set",
            fill_na_str: str = "-----"): Converts all values in a
                dictionary to pandas `DataFrames`.
        add_counts_col(df: pd.DataFrame, all_values: list[str]):
            Adds a count column to a `DataFrame`.

    Usage:
        table = Table("path/to/file.txt")
        print(table.df) # Display the DataFrame
        print(table.headers) # Show the column headers"""

    def __init__(
        self, filename: str, filter_values: list[str] = None, *args, **kwargs
    ) -> None:
        """
        Initialize a `Table` object.

        Args:
            filename (str): The path to the file to be parsed.
            filter_values (list[str], optional): A `list` of strings
                containing values to be filtered out of the data.
                Defaults to `None`.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        self.filepath = filename
        self.filter_values = filter_values or []

        base_data = self._pre_process_file(filename)

        # Create a DataFrame from the pre-processed data
        self._init_table(base_data, *args, **kwargs)

    def __str__(self) -> str:
        """
        Returns a string representation of the `Table` object.
        """
        return str(self.df)

    def _init_table(self, data: list[pd.Series], *args, **kwargs) -> None:
        self.df = pd.concat(
            data,
            *args,
            axis=1,
            **kwargs,
        )

    def _pre_process_file(
        self,
        filepath: str,
    ) -> list[pd.Series]:
        """
        Pre-process a file before parsing it with `pd.read_csv`.

        Args:
            filepath (str): Filepath of the file to pre-process.

        Returns:
            list[pd.Series]: A `list` containing the pre-processed data
                from `filepath`.
        """
        section_series = {}
        # Get the contents of the file
        file_contents = utils.read_file_string(filepath)

        # Split the file contents into sections
        sections = utils.split_delimited_string(file_contents)

        if not sections:
            raise ValueError(f"No sections found in file: {filepath}")

        # Convert sections to a Series objects and align them
        if isinstance(sections[0], list):
            # Discard all non-numeric values
            sections = [
                [int(i) for i in section if str(i).isnumeric()] for section in sections
            ]
            section_series = self._create_series_from_list(sections)
        else:
            section_series = self._create_series(sections)

        section_series = self.align_series_list(section_series)

        logger.info(f"Pre-processed file [{filepath}].")
        logger.debug(f"Total series created: {len(section_series)}")

        return section_series

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
                logger.debug(
                    f"Failed to sort series [{name}] numerically. Attempting to "
                    "discard filler and non-numeric values and sort again. "
                    f"Data: {data}"
                )
                # Discard filler values
                values = self.filter_list(data, self.filter_values)

                # Discard non-numeric values
                values = [int(i) for i in values if str(i).isnumeric()]

                # Attempt to sort again
                logger.debug(f"Data after filtering: {values}")
                sorted_list = sorted(set(values))

                logger.debug(f"Successfully sorted the series [{name}].")

            # Convert data back to a list of strings
            data = utils.stringify_list(sorted_list)

        # Create a pandas series from the data
        return pd.Series(data, name=name)

    def _create_series_from_list(
        self,
        data: list[list[str]],
        headers: list[str] = None,
        sort: bool = True,
    ) -> list[pd.Series]:
        """
        Create a `dict` of `Series` objects from a `list` of lists.

        Args:
            data (list[list[str]]): A `list` of lists containing
                the data to be converted to `Series` objects.
            headers (list[str], optional): A `list` of strings containing
                the labels for the `Series` objects.
            sort (bool, optional): Whether to sort the `Series`
                objects by index. Defaults to `True`.

        Returns:
            list[pd.Series]: A `list` of pandas `Series` objects.
        """
        if not headers:
            headers = [f"Column {i + 1}" for i in range(len(data))]

        return [
            self._create_series(list(set(data[i])), name=headers[i], sort=sort)
            for i in range(len(data))
        ]

    def _get_values(
        self, column_indexes: list[int] | int, unique: bool = False
    ) -> list[str]:
        """
        Returns a `list` of all values in the specified columns.

        Will only return unique values if `unique` is `True`. All
        values are filtered by the `filter_values` attribute.

        Args:
            column_indexes (list[int]): List of column indexes to
                retrieve values from.
            unique (bool, optional): Whether to return only unique
                values. Defaults to `False`.

        Returns:
            list[str]: List of all values in the specified columns.
        """
        # Check if column_indexes is a single int
        if isinstance(column_indexes, int):
            column_indexes = [column_indexes]

        # Check if column_indexes is a list of lists
        if not self.validate_indexes(column_indexes):
            return []

        values = self.df.iloc[:, column_indexes].values.flatten()

        if unique:
            values = set(values)

        return self.filter_list(values, self.filter_values)

    def hard_refresh(self, *args, **kwargs) -> None:
        """
        Updates the table with the latest data from the DataFrame.

        This method uses the `reindex_df()` method to reindex the
        DataFrame and update the table with the latest data.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.df = self.reindex_df(self.df, *args, **kwargs)

    def reindex_df(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        """
        Reindexes and aligns `df` so all columns are in order.

        Breaks down the `DataFrame` into a `list` of `Series`
        objects, aligns them so that all series values are the same
        length and contain all unique values, and then reassembles
        them into a new `DataFrame`. This also reindexes the columns
        of the `DataFrame` to ensure that all columns are in
        order.

        Args:
            df (pd.DataFrame): The DataFrame to reindex.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            pd.DataFrame: The reindexed DataFrame.
        """
        series_list = self._create_series_from_list(
            [self.filter_list(df[col].values, self.filter_values) for col in df],
            headers=list(df.columns),
        )
        series_list = self.align_series_list(series_list)

        return pd.concat(series_list, *args, axis=1, **kwargs)

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
        if not isinstance(data, pd.Series) and not isinstance(data[0], pd.Series):
            raise ValueError(f"Invalid data given to align_series_list(): {data}")
        elif isinstance(data, pd.Series):
            # Convert single Series to a list of Series
            data = [data]

        # Get all unique values
        unique_values = list(set().union(*[series.values for series in data]))

        # Discard filler values
        unique_values = self.filter_list(unique_values, self.filter_values)

        # Sort unique values - Convert values to int for sorting, then
        # back to str for reindexing
        unique_values = utils.stringify_list(
            utils.intify_list(unique_values, sort=True)
        )

        # Reindex all series to include all unique values (and put them
        # in order)
        reindexed_series = [
            pd.Series(index=s.values, data=s.values, name=s.name).reindex(unique_values)
            for s in data
        ]

        logger.debug(
            f"Reindexed {len(reindexed_series)} series. All series now contain "
            f"{len(reindexed_series[0])} elements."
        )

        return reindexed_series

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

    def update_headers(self, headers: list[str] | dict, *args, **kwargs) -> None:
        """
        Updates the column headers of `df` with the given headers.

        Args:
            headers (list[str] | dict): A `list` of strings or a
                `dict` containing the new column headers.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if isinstance(headers, list):
            # Convert list of headers to a dict
            headers = {
                self.df.columns[i]: headers[i] for i in range(len(self.df.columns))
            }
        self.df.rename(*args, columns=headers, inplace=True, **kwargs)

    def filter_list(self, data: list | set, remove_values: list[str]) -> list[str]:
        """
        Filters a list of values.

        Filters a `list` of values by removing all values in
        `remove_values`.

        Args:
            data (list): The `list` of values to filter.
            remove_values (list[str]): The `list` of values to
                remove from `data`.

        Returns:
            list[str]: The filtered `list` of values.
        """
        # Convert non-list data to a list
        if not isinstance(data, list):
            data = list(data)

        if not data:
            return []

        regex_pattern = re.compile("|".join([re.escape(val) for val in remove_values]))
        logger.debug(f"Filtering values with regex pattern: {regex_pattern}")

        return [val for val in data if not regex_pattern.match(str(val))]

    def get_header_indices(self, headers: list[str]) -> dict[str, list[int]]:
        """
        Gets indices of each header `str` in `headers` if it's in `df`.

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

        # Logging for header indices
        if ret:
            total_indices = sum([len(ret[key]) for key in ret])
        logger.debug(
            f"Found {total_indices} header indices for headers: {headers}. "
            f"Header indices: {ret}"
        )

        return ret

    def get_values(
        self, column_indexes: list[int] | list[list[int]], unique: bool = False
    ) -> list[str] | list[list[str]]:
        """
        Returns a `list` of all values in the specified columns.

        If a `list` of lists is provided for `column_indexes`, a
        `list` of lists will be returned where each list contains
        values from a batch.

        All values are filtered by the `filter_values` attribute.

        Args:
            column_indexes (list[int] | list[list[int]]): List of
                column indexes to retrieve values from. If a `list`
                of lists is provided, values from each
                batch will be returned.
            unique (bool, optional): Whether to return only unique
                values. Defaults to `False`.

        Returns:
            list[str] | list[list[str]]: List of all values in the specified columns.
            If a list of lists is provided for `column_indexes`, a list of lists will be
            returned where each list contains values from a batch.
        """
        # column_indexes is a list of ints or a single int
        if isinstance(column_indexes, int) or isinstance(column_indexes[0], int):
            return self._get_values(column_indexes, unique=unique)
        else:
            # Check if column_indexes is a list of lists
            # Get values from each batch
            values = []
            for batch in column_indexes:
                values.append(self._get_values(batch, unique=unique))

            return values

    def get_duplicates(self, column_indexes: list[int] | list[list[int]]) -> list[str]:
        """
        Returns all duplicates in the specified columns.

        If `column_indexes` is a list of `int`s, all columns will be
        compared.

        If `column_indexes` is a list of lists, duplicates will be
        counted in each batch as a whole and compared across batches.

        Args:
            column_indexes (list[int] | list[list[int]]): A `list` or
                a `list` of `list`s of column indexes to search for
                duplicates.

        Returns:
            list[str]: A `list` of all values that appear more than
                once in the specified columns or batches.
        """
        if not column_indexes:
            return []

        # If column_indexes is a list of ints, compare all columns
        if not isinstance(column_indexes[0], list):
            # Validate column indexes
            if not self.validate_indexes(column_indexes, min_=2):
                return []

            # Get all values in all columns (in list form)
            all_values_list = self.get_values(column_indexes)

            # Get all values that appear more than once
            duplicate_values = {
                val for val in all_values_list if list(all_values_list).count(val) > 1
            }

        # If column_indexes is a list of lists, count duplicates in each
        # batch as a whole and compare batches
        else:
            batch_values = []
            for batch in column_indexes:
                # Validate column indexes
                if not self.validate_indexes(batch, min_=2):
                    return []

                # Get all values in batch
                batch_values.append(set(self.get_values(batch)))

            # Get all values that appear more than once in all batches
            duplicate_values = set.intersection(*batch_values)

        logger.info(
            f"Found {len(duplicate_values)} duplicates values "
            f"for indexes: {column_indexes}"
        )
        return list(duplicate_values)

    def get_overlap(self, column_indexes: list[int] | list[list[int]]) -> list[str]:
        """
        Returns a `list` of overlapping values in the specified columns.

        If `column_indexes` is a `list` of `int`s, this method
        compares all columns specified by the indexes in
        `column_indexes` and returns the unique intersection of
        all columns.

        If `column_indexes` is a `list` of `list`s, this method
        compares each batch of columns specified by the sublists
        in `column_indexes` and returns the unique intersection of
        all batches.

        Args:
            column_indexes (list[int] | list[list[int]]): A `list`
                of column indexes or a `list` of `list`s of column
                indexes to check for overlap.

        Returns:
            list[str]: A `list` of values that overlap in all
                columns specified by `column_indexes`. If
                `column_indexes` is a `list` of `list`s, a `list`
                of values that overlap in all batches is returned.

                If no overlap is found, an empty `list` is returned.
        """
        # If column_indexes is a list of ints, compare all columns
        if not isinstance(column_indexes[0], list):
            if not self.validate_indexes(column_indexes, min_=2):
                return []

            # Get the unique intersection of all columns in
            # column_indexes
            ret = set.intersection(
                *[set(self.get_values(col)) for col in column_indexes]
            )

        # If column_indexes is a list of lists, compare batches
        else:
            # Get overlap of each batch as a whole
            batch_values = []
            for batch in column_indexes:
                # Validate column indexes
                if not self.validate_indexes(batch, min_=2):
                    return []

                # Get all values in batch
                batch_values.append(set(self.get_values(batch)))

            # Get all values that appear in all batches
            ret = set.intersection(*batch_values)

        if ret:
            # Discard filler values if any overlap values exist
            logger.info(
                f"Found {len(ret)} overlapping values for indexes: {column_indexes}"
            )
            return list(ret)
        else:
            # No overlap found
            logger.info(f"No overlap found for indexes: {column_indexes}")
            return []

    def get_differences(
        self, column_indexes: list[int], symmetric: bool = True
    ) -> list[str]:
        """
        Returns the symmetric or standard difference columns.

        If symmetric is `True`, returns the symmetric difference of
        values in the specified columns.

        If symmetric is `False`, returns the standard difference of
        values in the specified columns. The order of column indexes
        provided is important when calculating the standard
        difference, because the first column in `column_indexes`
        is used as the base for comparison and columns are then
        iterated over in order. Each column is compared to the
        base column, and the difference is returned.

        Args:
            column_indexes (list[int] or list[list[int]]): List of
                column indexes to compare.

                If `column_indexes` is a `list` of `int`s, compare
                all columns.

                If `column_indexes` is a `list` of `list`s, compare
                batches.
            symmetric (bool, optional):
                If `True`, returns the symmetric difference (values
                that are unique to each column).

                If `False`, returns the standard difference (values
                that are unique to the first column in
                `column_indexes`).

                Defaults to `True`.

        Returns:
            list[str]: List of unique values that are different across the specified columns.
        """
        ret = []
        # Set function to use for differences
        if symmetric:
            # Symmetric difference
            diff_func = set.symmetric_difference
        else:
            # Standard difference
            diff_func = set.difference

        # If column_indexes is a list of ints, compare all columns
        if not isinstance(column_indexes[0], list):
            if not self.validate_indexes(column_indexes, min_=2):
                return []

            # Get difference (symmetric or standard) of all columns in
            # column_indexes
            sets = [set(self.get_values(col)) for col in column_indexes]
            ret = sets.pop(0)  # For first comparison
            # Compare all sets (two at a time)
            for s in sets:
                ret = diff_func(ret, s)

        # If column_indexes is a list of lists, compare batches
        else:
            # Get difference of each batch as a whole
            batch_values = []
            for batch in column_indexes:
                # Validate column indexes
                if not self.validate_indexes(batch, min_=2):
                    return []

                # Get all values in batch
                batch_values.append(set(self.get_values(batch)))

            # Get the difference (symmetric or standard) of all batches
            ret = batch_values.pop(0)  # For first comparison
            # Compare all sets (two at a time)
            for s in batch_values:
                ret = diff_func(ret, s)

        # Logging for differences
        if ret:
            logger.info(f"Found {len(ret)} differences for indexes: {column_indexes}")
        else:
            logger.info(f"No differences found for indexes: {column_indexes}")

        return list(ret)

    def set_iloc(self, row: int | list[int], col: int | list[int], value: int) -> None:
        """
        Sets a value in the DataFrame at the specified row and column.

        Performs a hard refresh after setting the value. This will
        update the table with the latest data from the DataFrame,
        reindexing the columns.

        Args:
            row (int | list[int]): The row index or `list` of row
                indices to set.
            col (int | list[int]): The column index or `list` of
                column indices to set.
            value (int): The value to set.
        """
        try:
            self.df.iloc[row, col] = int(value)
            self.hard_refresh()
        except IndexError:
            logger.error(
                f"IndexError: Unable to set value [{value}] at row {row} and column {col}."
            )

    def set_loc(self, row: str | list[str], col: str | list[str], value: int) -> None:
        """
        Sets a value in the DataFrame at the specified row and column.

        Performs a hard refresh after setting the value. This will
        update the table with the latest data from the DataFrame,
        reindexing the columns.

        Args:
            row (str | list[str]): The row label or `list` of row
                labels to set.
            col (str | list[str]): The column label or `list` of
                column labels to set.
            value (int): The value to set.
        """
        try:
            self.df.loc[row, col] = int(value)
            self.hard_refresh()
        except IndexError:
            logger.error(
                f"IndexError: Unable to set value [{value}] at row {row} and column {col}."
            )

    def info(
        self, columns: list[str] | list[list[str]] = None, regex: bool = False
    ) -> tuple[str, dict[str, pd.DataFrame], dict[str, list[str]]]:
        """
        Gets information about the `Table` object.

        Passing a list of column indices (or a list of lists of column
        indices) to `columns` will perform additional analysis on the
        specified columns. Additionally, setting `regex` to `True` will
        add a regex pattern for all values in the specified columns.

        Args:
            columns (list[str], optional): List of column names to
                perform additional analysis on. Defaults to `None`.
            regex (bool, optional): Whether to print a regex pattern
                for all analyzed values. Defaults to `False`.

        Returns:
            tuple(str, dict[str, pd.DataFrame], dict[str, list[str]]):
                A `tuple` containing:
                    - A string containing information about the
                      `Table` object.
                    - A `dict` containing a `list` of values for each
                      type of analysis performed on the specified
                      columns.
                    - A `dict` containing a pandas `DataFrame` for
                      each type of analysis performed on the specified
                      columns.
        """
        output = "\n====================MAIN TABLE====================\n"
        output += f"{self.df}\n"
        output += f"Filepath: {self.filepath}\n"
        output += "Filter values: " + ", ".join(self.filter_values) + "\n"
        output += "Column headers: " + ", ".join(list(self.df.columns)) + "\n"
        output += f"Total columns: {len(self.df.columns)}\n"
        output += f"Total rows: {len(self.df.index)}\n"

        # Perform additional analysis on specified columns
        if columns:
            df_analysis_values = {
                "all_values": self.get_values(columns),
                "unique_values": self.get_values(columns, unique=True),
                "duplicate_values": [self.get_duplicates(columns)],
                "overlap_values": self.get_overlap(columns),
                "differences_symmetric": self.get_differences(columns, symmetric=True),
                "differences_asymmetric": self.get_differences(
                    columns, symmetric=False
                ),
            }
            # Create a pandas DataFrame per analysis type
            df_comparisons_dict = self.dict_to_df_dict(df_analysis_values)

            # Add count columns

            # Print analysis results
            output += "\n"
            for key, df in df_comparisons_dict.items():
                formatted_key = key.replace("_", " ").title()
                output += f"===================={formatted_key}====================\n"

                # No values found for comparison
                if df is None:
                    output += "\nNo values found.\n\n"
                    continue

                # Add count column to duplicates and overlap dataframes
                if key in ["duplicate_values", "overlap_values"]:
                    df = self.add_counts_col(df, df_analysis_values["all_values"])

                # When listing sets of columns, include index and
                # headers
                if key in ["all_values", "unique_values"]:
                    output += df.to_string() + "\n"
                elif len(df.columns) > 1:
                    output += df.to_string(index=False) + "\n"
                else:
                    output += df.to_string(index=False, header=False) + "\n"

                # Print additional info (and separator)
                output += "........................\n"
                output += f"Total values: {len(df.index)}\n"

                # Get all values in df for printing
                all_values = self.filter_list(
                    utils.stringify_list(set(df.values.flatten())), self.filter_values
                )

                # Sort values - (Convert to int for accurate numeric
                # sorting, then back to str for `join` method)
                all_values = utils.stringify_list(
                    utils.intify_list(all_values, sort=True)
                )

                output += "All values: " + ", ".join(all_values) + "\n"
                if regex:
                    output += f"Regex Pattern: {utils.Regex.create_regex_patern(all_values)}\n"

                output += "\n"  # Spacing separator

        return output, df_analysis_values, df_comparisons_dict

    def dict_to_df_dict(
        self,
        data: dict,
        key_name: str = "Set",
        fill_na_str: str = "-----",
    ) -> dict[str, pd.DataFrame]:
        """
        Converts all values in a dictionary to pandas `DataFrames`.

        Either a `list` or nested `list` can be used with each key.
        dictionary of pandas DataFrames.

        For nested lists, the resulting `DataFrame` will contain
        monotonically increasing headers for each value in the nested
        list. The name of each header is determined by `key_name`. The
        index is also aligned using the `_align_series_list()` method.

        For single lists, the resulting `DataFrame` will contain a
        single column with the name of the existing key.

        Args:
            data (dict): A `dict` where each key represents a
                column name and each value is a nested or unnested
                `list` of values.
            key_name (str, optional): The name of the key to use
                when creating headers for nested lists. Defaults
                to "Set".
            fill_na_str (str, optional): The string to use to fill
                NaN values. Defaults to "-----".

        Returns:
            dict[str, pd.DataFrame]: A `dict` where each key represents
                a column name and each value is a pandas `DataFrame`.
        """
        retdict = {}
        for k, v in data.items():
            # Empty values
            if not v or not any(v):
                retdict[k] = None
                continue

            if isinstance(v[0], list):
                # Create headers and series from list
                headers = [f"{key_name} {idx + 1}" for idx in range(len(v))]
                series_list = self._create_series_from_list(v, headers=headers)

                # Align all series
                series_list = self.align_series_list(series_list)
            else:
                # For single column analysis, create a single Series
                series_list = [self._create_series(v, name=k)]

            df = pd.concat(series_list, axis=1)
            retdict[k] = self.reindex_df(df).fillna(fill_na_str)

        return retdict

    def add_counts_col(self, df: pd.DataFrame, data: list[str | int]) -> pd.DataFrame:
        """
        Adds a count column to `df` for value occurrences in `data`.

        Creates a new column in `df` containing the number of
        occurrences of each value in `data`.

        Args:
            df1 (pd.DataFrame): The DataFrame to add the counts to.
            data (list[str|int]): The data to count occurrences of.

        Returns:
            pd.DataFrame: The DataFrame with the counts column added.
        """
        if not data:
            return df

        # Create counts column for nested lists
        if isinstance(data[0], list):
            # Flatten and deduplicate each set of columns
            data = [item for sublist in data for item in set(sublist)]

            # Create counts column
            counts = [
                data.count(item)
                for sublist in df.values.tolist()
                for item in self.filter_list(sublist, self.filter_values)
            ]
        # Create counts column for single lists
        else:
            counts = [data.count(item) for item in df.values.flatten()]

        df["Count"] = counts

        return df


class SproutsTable(Table):
    """
    A class representing a Sprouts table.

    This class extends the `Table` class and provides additional
    functionality specific to Sprouts tables.

    Attributes:
        num_scan_col (int): The number of scan columns in the table.
        scan_label (str): The label for scan columns.
        shipment_label (str): The label for shipment columns.
        scan_df (pd.DataFrame): A `pd.DataFrame` containing all
            scan columns in the table.
        shipment_df (pd.DataFrame): A `pd.DataFrame` containing
            all shipment columns in the table.

    Methods:
        _get_scan_and_ship_cols(column_indexes: list[int])
            -> list[list[int], list[int]]:
                Get scan and shipment column values in the
                specified columns.
        _update_sub_dfs(df: pd.DataFrame) -> list[pd.DataFrame,
            pd.DataFrame]:
                Identifies "Scan" columns and "Shipment" columns in
                `df`.
        _update_values(df_row: pd.Series) -> None:
            Conditionally fills values in a `pd.Series` object based on
            their relations to other columns.
        get_scan_overlap(column_indexes: list[int]) -> list[str]:
            Gets overlapping values between scan and shipment columns.
        get_scan_differences(column_indexes: list[int]) -> list[str]:
            Get the differences between the scan and shipment columns.
        refresh_headers() -> None:
            Updates the column headers to scan and shipment columns.
        update_scan_label(new_label: str) -> None:
            Updates `scan_label` and refreshes headers.
        update_shipment_label(new_label: str) -> None:
            Updates `shipment_label` and refreshes headers.
        update_scan_col_count(new_count: int) -> None:
            Updates `num_scan_col` and refreshes headers and columns.
        update_table(hard: bool = False) -> None:
            Refreshes headers, columns, and fills missing values.
            If `hard` is `True`, the table will be updated with the
            latest data from the DataFrame.
    """

    def __init__(
        self,
        filename: str,
        num_scan_col: int = 0,
        filter_values: list[str] = None,
        scan_label: str = "Scan",
        shipment_label: str = "Shipment",
        *args,
        **kwargs,
    ) -> None:
        """
        Initializes a SproutsTable object.

        Args:
            filename (str): The path to the file containing the table.
            num_scan_col (int, optional): The number of scan columns in
                the table. Defaults to 0.
            filter_values (list[str], optional): A list of values to
                filter out of the table. Defaults to None.
            scan_label (str, optional): The label for scan columns.
                Defaults to "Scan".
            shipment_label (str, optional): The label for shipment
                columns. Defaults to "Shipment".
            *args: Additional arguments to pass to the parent class.
            **kwargs: Additional keyword arguments to pass to the
                parent class.
        """
        super().__init__(filename, filter_values, *args, **kwargs)
        # Ensure num_scan_col is within range
        if num_scan_col < 0:
            self.num_scan_col = 0
        elif num_scan_col > len(self.df.columns):
            self.num_scan_col = len(self.df.columns)
        else:
            self.num_scan_col = num_scan_col

        self.scan_label = scan_label.casefold().title()
        self.shipment_label = shipment_label.casefold().title()

        # Create scan_columns and shipment_columns attributes
        self.scan_df, self.shipment_df = None, None

        # Update headers, scan_col_df, shipment_col_df, and fill missing values
        self.update_table()

    def _gen_header_labels(self) -> list[str]:
        """
        Creates a `dict` containing scan and shipment column labels.

        Generates a `dict` containing the labels for the scan and
        shipment columns. The scan column labels are generated first,
        followed by the shipment column labels.

        The number of scan column labels generated is determined by
        `num_scan_col`. The number of shipment column labels generated
        is determined by the difference between `num_scan_col` and
        `max_`.

        Labels are taken from the `scan_label` and `shipment_label`
        attributes.

        Example:

        - `max_ = 6`
        - `scan_col_count = 3`
        - `scan_col_label = "Scan"`
        - `ship_col_label = "Shipment"`

        The following headers will be created:

        `[Scan 1, Scan 2, Scan 3, Shipment 4, Shipment 5, Shipment 6]`

        Returns:
            A `list` containing the labels for the scan and shipment
            columns.
        """
        logger.debug("Generating column headers...")
        headers = []

        # Create scan column headers
        for i in range(self.num_scan_col):
            headers.append(f"{self.scan_label.title()} {i + 1}")

        # Create shipment column headers
        for i in range(self.num_scan_col, len(self.df.columns)):
            headers.append(f"{self.shipment_label.title()} {i + 1}")

        logger.debug(f"Generated {len(headers)} headers: {headers}")
        return headers

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
            list[list[int], list[int]]: A `list` containing two `list`s.
                Format: `[[scan_col_values], [shipment_col_values]]`
        """
        # Look for scan and shipment columns indices in headers
        indices = self.get_header_indices([self.scan_label, self.shipment_label])

        # Get scan column indices
        scan_indices = list(
            set(indices.get(self.scan_label)).intersection(column_indexes)
        )

        # Get shipment column indices
        shipment_indices = list(
            set(indices.get(self.shipment_label)).intersection(column_indexes)
        )

        if scan_indices:
            # Get values in scan columns
            scan_col_values = self.get_values(scan_indices)
        else:
            scan_col_values = []

        if shipment_indices:
            # Get values in shipment columns
            shipment_col_values = self.get_values(shipment_indices)
        else:
            shipment_col_values = []

        return [scan_col_values, shipment_col_values]

    def _update_sub_dfs(self, df: pd.DataFrame) -> list[pd.DataFrame, pd.DataFrame]:
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

        indices = self.get_header_indices([self.scan_label, self.shipment_label])

        # Check if any scan columns exist
        if not indices.get(self.scan_label):
            logger.debug(
                "No scan columns found in DataFrame passed to _update_sub_dfs()"
            )

            # Add empty DataFrame to ret
            ret.append(pd.DataFrame())

        # Get all scan columns
        else:
            scan_columns = [df.iloc[:, idx] for idx in indices.get(self.scan_label)]

            # Create a DataFrame from the scan columns
            ret.append(
                pd.concat(
                    scan_columns,
                    axis=1,
                )
            )

        # Check if any shipment columns exist
        if not indices.get(self.shipment_label):
            logger.warning(
                "No shipment columns found in DataFrame passed to _Update_sub_dfs()"
            )

            # Add empty DataFrame to ret
            ret.append(pd.DataFrame())

        # Get all shipment columns
        else:
            shipment_columns = [
                df.iloc[:, idx] for idx in indices.get(self.shipment_label)
            ]

            # Create a DataFrame from the shipment columns
            ret.append(
                pd.concat(
                    shipment_columns,
                    axis=1,
                )
            )

        return ret

    def _update_values(self, df_row: pd.Series) -> None:
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
        if self.num_scan_col <= 0 or self.num_scan_col >= len(self.df.columns):
            for col in df_row.index:
                if df_row[col] != df_row.name:
                    df_row[col] = "-----"

            return df_row

        # Check if the index exists in any 'Scan' or 'Shipment' columns
        try:
            in_scan = (self.scan_df == df_row.name).any(axis=1)
        except KeyError as e:
            logger.error(
                "KeyError occurred while trying to check if index "
                f"'{df_row.name}' exists in any 'Scan' columns. "
            )
            in_scan = pd.Series(False)

        try:
            in_shipment = (self.shipment_df == df_row.name).any(axis=1)
        except KeyError as e:
            logger.error(
                "KeyError occurred while trying to check if index "
                f"'{df_row.name}' exists in any 'Shipment' columns. "
            )
            in_shipment = pd.Series(False)

        # Apply the fill logic to the df_row based on the conditions
        for col in df_row.index:
            # Case 1: Value already exists -> leave it alone
            try:
                # Check if value is a number. Continue if it is.
                int(df_row[col])
                continue
            except ValueError:
                pass
            # Case 2: Exists in both 'Scan' and 'Shipment' -> "-----"
            if in_scan.any() and in_shipment.any():
                # Scan column
                if col in self.scan_df.columns:
                    df_row[col] = "....."
                else:
                    df_row[col] = "-----"

            # Case 3: Exists in a 'Scan' but not any 'Shipment' -> "/////"
            elif in_scan.any() and not in_shipment.any():
                # Scan column
                if col in self.scan_df.columns:
                    df_row[col] = "....."

                # Shipment column
                else:
                    df_row[col] = "/////"

            # Case 4: Does not exist in any 'Scan' -> "!!!!!"
            elif not in_scan.any():
                # Scan column
                df_row[col] = "!!!!!"

        return df_row

    def update_scan_label(self, new_label: str) -> None:
        """Updates `scan_label` and refreshes headers."""
        self.scan_label = new_label.casefold().title()
        self.refresh_headers()

    def update_shipment_label(self, new_label: str) -> None:
        """Updates `shipment_label` and refreshes headers."""
        self.shipment_label = new_label.casefold().title()
        self.refresh_headers()

    def update_scan_col_count(self, new_count: int) -> None:
        """Updates `num_scan_col` and refreshes headers and columns."""
        self.num_scan_col = new_count
        self.update_table(hard=True)

    def update_table(self, hard: bool = False) -> None:
        """Refreshes headers, columns, and fills missing values."""
        logger.debug("Refreshing table...")
        # Reindex all series to include all unique values (and put them
        # in order) if hard is True
        if hard:
            self.hard_refresh()

        self.refresh_headers()
        self.scan_df, self.shipment_df = self._update_sub_dfs(self.df)
        self.df.apply(self._update_values, axis=1)
        logger.debug("Table refreshed.")

    def refresh_headers(self) -> None:
        """Updates the column headers to scan and shipment columns."""
        new_headers = self._gen_header_labels()
        super().update_headers(new_headers)

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
            intersection = list(set(scan_cols).intersection(shipment_cols))

            logger.info(
                f"Found {len(intersection)} scan overlapping values "
                f"for indexes: {column_indexes}"
            )
            return intersection
        else:
            if not scan_cols:
                logger.info(
                    f"No scan columns found using get_scan_overlap() "
                    f"for indexes: {column_indexes}"
                )
            else:
                logger.warning(
                    "No shipment columns found using get_scan_overlap() "
                    f"for indexes: {column_indexes}"
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
            if not scan_cols:
                logger.info(
                    f"No scan columns found using get_scan_differences() "
                    f"for indexes: {column_indexes}"
                )
            else:
                logger.warning(
                    f"No shipment columns found using get_scan_differences() "
                    f"for indexes: {column_indexes}"
                )

            return []

    def set_iloc(self, row: int | list[int], col: int | list[int], value: int) -> None:
        super().set_iloc(row, col, value)
        self.update_table(hard=True)

    def set_loc(self, row: str | list[str], col: str | list[str], value: int) -> None:
        super().set_loc(row, col, value)
        self.update_table(hard=True)


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

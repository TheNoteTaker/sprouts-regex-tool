from .parser import SproutsTable
import pandas as pd
from . import utils
import logging
import re
import os
import shutil

logger = logging.getLogger(__name__)

INPUT_FP = os.environ["INPUT_PATH"]
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", utils.get_file_dir(__file__) + "/data/report")


def init_table() -> SproutsTable:
    """Initialize script with user input."""
    # Program info
    print(
        "First, we need to create a table from the input file containing your data..."
    )
    print("How many columns are scan columns?")
    print(
        "(A scan column is a set of data that is directly entered from an "
        "invoice scan and not our systems)\n"
    )

    # Get number of scan columns from user input
    num_scan_col = utils.input_(
        message="Enter number of scan columns:\n>",
        constraint="^\s*?\d+\s*?$",
        regex=True,
    )

    # Convert to int
    num_scan_col = int(num_scan_col)

    # Create table
    print("Creating table...\n")
    table = SproutsTable(
        INPUT_FP,
        num_scan_col=num_scan_col,
        filter_values=["-----", "/////", "!!!!!", "....."],
    )
    logger.info(
        f"Generating table with {num_scan_col} scan columns and "
        f"{len(table.df.columns) - table.num_scan_col} shipment "
        f"columns from file: {INPUT_FP}"
    )

    return table


def print_menu(menu_options: list[str], zero_start: bool = False) -> None:
    """Print a menu with the given options."""
    for i, option in enumerate(menu_options):
        print(f"{i if zero_start else i + 1}. {option}")


def get_choice_from_menu(
    menu_options: list[str], multi: bool = False, zero_start: bool = False
) -> int | list[int]:
    """
    Prompts the user to select an option from a menu.

    Uses the `input_` function to get user input and validates it
    against the given `menu_options`. If the input is invalid, then
    the user will be prompted to enter a valid input.

    Setting `multi` to `True` will allow the user to select multiple
    options from the menu delimited by any of the following characters:
    `-`,`_`,` `,`,`.

    Args:
        menu_options (list[str]): A `list` of strings representing the
            menu options.
        multi (bool, optional): Whether to allow multiple choices.
            Defaults to `False`.

    Returns:
        int | list[int]: The index(es) of the selected option(s) in
            the `menu_options` list.
    """
    # Create a list of valid indices for the menu
    menu_index = list(range(len(menu_options) + 1))

    if multi:
        # Multi mode (accepts multiple choices)
        # Create a regex pattern for all values in the menu

        # Get user input
        valid_input_regex = r"^(?:[\s\-,_]*?\d+[\s\-,_]*?)+?$"
        user_input = utils.input_(constraint=valid_input_regex, regex=True)

        # Extract all numbers from the user input (as strings)
        user_input = re.findall(r"\d+", user_input)

        try:
            retval = []
            # Convert all numbers to ints and discard non-menu values.
            for val in user_input:
                val = int(val)
                if val in menu_index:
                    retval.append(val - 1)  # Subtract 1 for offset

            return retval

        except ValueError as e:
            logger.error(e)
            logger.error(
                f"Invalid input given for multi-choice menu: {user_input}. "
                f"Possible options: {menu_options}"
            )
            print("Invalid input given. Please try again.")
            return get_choice_from_menu(menu_options, multi=True, zero_start=zero_start)
    else:
        # Non-multi mode (accepts only one choice)
        return int(utils.input_(constraint=menu_index)) - 1


def get_df_columns(table: pd.DataFrame) -> list[str]:
    """Get all columns from the table."""
    return list(table.df.columns)


def save(
    info_str: str,
    df_analysis_values: list[str] | list[list[str]],
    df_comparisons_dict: dict[pd.DataFrame],
    table: SproutsTable,
) -> None:
    """Save the given data to the output directory."""
    # Create output directories if they doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # Remove and recreate report folder if it already exists
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)

    with open(OUTPUT_DIR + "/full_table_report.txt", "w") as f:
        f.write(info_str)

    # Save analysis values
    with open(OUTPUT_DIR + "/table_values.txt", "a") as f:
        for k, v in df_analysis_values.items():
            f.write(f"{k}:\n")
            f.write(f"{v}\n\n")

    # Save comparisons
    for key, df in df_comparisons_dict.items():
        if df is not None:
            os.makedirs(f"{OUTPUT_DIR}/individual_tables/{key}")
            df.to_csv(f"{OUTPUT_DIR}/individual_tables/{key}/table_report.csv")
            df.to_excel(f"{OUTPUT_DIR}/individual_tables/{key}/table_report.xlsx")
            df.to_markdown(f"{OUTPUT_DIR}/individual_tables/{key}/table_report.md")
            df.to_string(f"{OUTPUT_DIR}/individual_tables/{key}/table_report.txt")

    # Save original table
    output_dir = f"{OUTPUT_DIR}/original_table"
    os.mkdir(output_dir)
    table.df.to_csv(f"{output_dir}/table_report.csv")
    table.df.to_excel(f"{output_dir}/table_report.xlsx")
    table.df.to_markdown(f"{output_dir}/table_report.md")
    table.df.to_string(f"{output_dir}/table_report.txt")

    print(f"Generated reports at {OUTPUT_DIR}")


# ====================COLUMN MENUS====================


def columns_menu(table: pd.DataFrame, zero_start: bool = False):
    """Display compare menu options to the user and get their choice."""
    print("Please enter all columns separated by spaces or commas (0 to exit)")
    print("Example: 1, 2, 3\n")
    options = ["All Columns"]
    options += get_df_columns(table)

    print_menu(options, zero_start=zero_start)
    return get_choice_from_menu(options, multi=True, zero_start=zero_start)


def multi_columns_menu(table: pd.DataFrame, zero_start: bool = False):
    """Display compare menu options to the user and get their choice."""
    # Menu info
    print("This mode compares multiple sets of columns, treating each set as a group")
    print("Please enter all columns separated by spaces or commas (example: 1, 2, 3)\n")

    # Get columns options and indices
    logger.debug("Getting batch column options")
    column_options = {i: col for i, col in enumerate(get_df_columns(table))}

    # Get number of sets to compare
    print("How many sets of columns would you like to compare?")
    num_sets = int(
        utils.input_(
            message=f"Select from from 1 to {len(column_options)} or '0' to exit:\n>",
            constraint=[0] + list(column_options.keys()),  # Add 0 for exit option
            regex=True,
        )
    )

    # Exit if user enters 0
    if num_sets == 0:
        print("Exiting...")
        return

    print(f"The program will attempt to create {num_sets} sets.")
    print(
        "If you select more columns than are available, only the available "
        "columns will be used."
    )
    sets_to_compare = []

    logger.debug(
        f"User selected {num_sets} sets. Current column options: {column_options}"
    )
    # Create sets of columns until no more columns are left
    while (len(sets_to_compare) < num_sets) and column_options:
        print(f"Please select columns for Set {len(sets_to_compare) + 1}:")

        # Print menu options and get user choice
        print_menu(list(column_options.values()), zero_start=zero_start)

        user_choice = get_choice_from_menu(
            list(column_options.values()), multi=True, zero_start=zero_start
        )

        # Use 0 as a sentinel value to exit. User input is shifted by -1.
        if user_choice and -1 in user_choice:
            break

        # Get corresponding columns from column_options based on user choice
        selected_cols = [v for k, v in enumerate(column_options) if k in user_choice]

        # Log and collumn options
        logger.debug(f"User selected columns: {selected_cols}")
        logger.debug(
            f"There are {len(column_options)} column options remaining: {column_options}"
        )

        # Add selected columns to sets_to_compare
        sets_to_compare.append(sorted(selected_cols))

        # Discard user selected columns from options
        column_options = {
            i: col for i, col in column_options.items() if i not in sets_to_compare[-1]
        }

    logger.debug(f"Sets to compare: {sets_to_compare}")

    return sets_to_compare


# ====================MENUS====================


def main_menu(table: pd.DataFrame, zero_start: bool = False):
    """Display main menu options to the user and get their choice."""
    print("====================MAIN MENU====================")
    print(table)
    print()
    print("Please select an option (0 to exit):")
    options = ["Compare Individual Columns", "Compare Sets of Columns", "Help"]

    # Print menu options and return user's choice
    print_menu(options, zero_start=zero_start)
    # Add 0 for exit option
    return get_choice_from_menu(options) + 1


def compare_sets_menu(table: SproutsTable):
    """Display compare menu options to the user and get their choice."""
    print("====================MULTI COLUMN COMPARISON MODE====================")
    print(table)
    print()
    compare_sets = multi_columns_menu(table)
    if compare_sets:
        print("========================================")
        # Print info about the sets being compared
        print(f"Comparing {len(compare_sets)} sets:")
        for i, set_indices in enumerate(compare_sets):
            set_values = ", ".join([table.df.columns[i] for i in set_indices])
            print(f"  - Set {i + 1}:", set_values)

        print("========================================")
        # Print info about the sets themselves
        report, df_analysis_values, df_comparisons_dict = table.info(
            compare_sets, regex=True
        )
        print(report)

        # Save data
        save(report, df_analysis_values, df_comparisons_dict)


def compare_individual_columns_menu(table: SproutsTable) -> None:
    """Display compare menu options to the user and get their choice."""
    print("====================SINGLE COLUMN COMPARISON MODE====================")
    print(table)
    print()
    columns = columns_menu(table)
    if columns:
        # Use 0 as a sentinel value to exit. User input is shifted by -1.
        if -1 in columns:
            print("Exiting...")
            return
        # If user selected 1 (all columns), then set columns to all columns
        elif 0 in columns:
            columns = list(range(len(table.df.columns)))

        print("========================================")
        # Print info about the sets being compared
        print(f"Comparing {len(columns)} columns:")
        for i, j in enumerate(columns):
            print(f"  - Column {i + 1}:", table.df.columns[j])

        print("========================================")
        # Print info about the sets themselves
        report, df_analysis_values, df_comparisons_dict = table.info(
            columns, regex=True
        )
        print(report)

        # Save data
        save(report, df_analysis_values, df_comparisons_dict, table)
    else:
        print("No columns selected. Exiting...")


def help_menu():
    """Display help menu options to the user and get their choice."""
    print("====================HELP MENU====================")
    print("Meanings of different comparison values:")
    print(
        "  - `Unique`: All unique (non-duplicate) values in all columns or "
        "sets of columns."
    )
    print(
        "  - `Duplicates`: All duplicate values in all columns or sets of "
        "columns. These are values that appear more than once. When comparing "
        "sets of columns, this is the intersection of all sets (instead of the "
        " intersection of each individual column)."
    )
    print(
        "  - `Overlap`: All values that appear in more than one column or set "
        "of columns. When comparing sets of columns, this is the intersection "
        "of each set (instead of the inersection of each column)."
    )
    print(
        "  - `Differences (Symmetric)`: All values that appear in only one "
        "column or set of columns that are being compared (no duplicate values). When comparing sets "
        "of columns, this is the symmetric difference of each set (instead of "
        "the symmetric difference of each column)."
    )
    print(
        "  - `Differences (Asymmetric)`: All values that do not appear in the "
        "other column(s) or set of columns that are being compared to the first "
        "provided column(s) (or set). When comparing sets of columns, this is "
        "the asymmetric difference of each set (instead of the asymmetric "
        "difference of each column)."
    )

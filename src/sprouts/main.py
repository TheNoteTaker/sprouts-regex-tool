from . import logger_init  # Initialize logging module and configuration
from dotenv import load_dotenv
from .parser import SproutsTable, enable_full_pandas_output
from . import cli
from . import utils
import logging
import re


# Init settings
load_dotenv()
logger = logging.getLogger(__name__)


def main():
    enable_full_pandas_output()

    print("Welcome to the Sprouts CLI!\n")
    # Get table from CLI initialization
    table = cli.init_table()

    while True:
        menu_choice = int(cli.main_menu(table))
        print()

        match menu_choice:
            case 0:
                print("Exiting...")
                exit(0)
            case 1:
                cli.compare_individual_columns_menu(table)
            case 2:
                cli.compare_sets_menu(table)
            case 3:
                cli.help_menu()
            case default:
                continue
        
        print()  # Spacer



if __name__ == "__main__":
    main()

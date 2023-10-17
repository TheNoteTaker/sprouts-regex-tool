from .tables import TableSegmentor
from .sprouts_session.sprouts_parser import ShipmentList, ShipmentParser
from .menu import InteractiveMenu

empty_tables_message = "No tables exist yet!\n\n"
invalid_option_message = "Invalid option selected!\n\n"


def main():
    # Initialize objects
    table_maker = TableSegmentor()
    menu = InteractiveMenu()

    user_input = "-1"  # TODO delete this line
    program_exit_strings = ["exit", ""]
    while user_input not in program_exit_strings:
        print("==========Main Menu==========")
        user_input = menu.main_menu()
        # Test data for debugging
        # rows = [
        #     # five lists of random 4-digit numbers
        #     ["1234", "5678", "9012", "3456"],
        #     ["7890", "1234", "5678", "9012"],
        #     ["3456", "7890", "1234", "5678"],
        #     ["9012", "3456", "7890", "1234"],
        #     ["5678", "9012", "3456", "7890"],
        # ]
        # scan_column_amount = 2
        match user_input:
            case "1":  # Create table
                # Get shipment data for creating table
                (
                    rows,
                    _,
                    scan_column_amount,
                ) = menu.shipments_menu()

                shipments = ShipmentList(rows)

                # Create table
                table_maker.create_table(
                    rows=shipments.get_shipments(),
                    invoice_scan=scan_column_amount,
                )

                # Ask user if they want to use grid tables
                grid = menu.grid_table_input()

                # Print table
                table_maker.print_table(grid=grid)
            case "2" | "4" | "5":  # Select, edit, or get patterns from table
                # Get table index from user and table
                table_index = menu.table_menu(table_maker.tables)
                table = table_maker.get_table(table_index)

                # Check if table exists
                if not table:
                    print(empty_tables_message)
                    continue

                if user_input == "2":  # Print table
                    # Ask user if they want to use grid tables
                    grid = menu.grid_table_input()

                    # Print selected table
                    table_maker.print_table(table_index, grid=grid)

                elif user_input == "4":  # Edit table
                    while True:
                        table_maker.print_table(table_index, grid=True)
                        results = menu.edit_menu(table)
                        
                        # Exit if user wants to exit
                        if not results:
                            print("Exiting edit menu...\n")
                            break
                        else:
                            row_index, column_index, replace = results

                        # Replace value in table
                        table_maker.edit_table(
                            row_index, column_index, replace, table_index
                        )

                elif user_input == "5":  # Get Regex Patterns
                    if table:
                        table_maker.print_table(table_index, grid=grid)

                        # Print all patterns in table
                        print("--------------------------------------------------")
                        for k, v in table.get_patterns().items():
                            # Flatten sublist
                            if isinstance(v, list):
                                v = ", ".join(v)

                            print(f"{k:16}: {v}")
                        print("--------------------------------------------------\n")

                else:  # Invalid option
                    print(invalid_option_message)

            case "3":  # Print all tables
                if table_maker.tables:
                    # Ask user if they want to use grid tables
                    grid = menu.grid_table_input()

                    # Print all tables
                    table_maker.print_tables(grid=grid)
                else:
                    print(empty_tables_message)

            case _:
                print(invalid_option_message)


if __name__ == "__main__":
    main()

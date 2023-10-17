from .tables import TableSegmentor
from .sprouts_session.sprouts_parser import ShipmentList, ShipmentParser
from .menu import InteractiveMenu
from .utils import input_


def main():
    # Initialize objects
    table_segmentor = TableSegmentor()
    menu = InteractiveMenu()

    user_input = "1"  # TODO delete this line
    while True:
        print("==========Main Menu==========")
        user_input = menu.main_menu()
        rows = [
            # five lists of random 4-digit numbers
            ["1234", "5678", "9012", "3456"],
            ["7890", "1234", "5678", "9012"],
            ["3456", "7890", "1234", "5678"],
            ["9012", "3456", "7890", "1234"],
            ["5678", "9012", "3456", "7890"],
        ]
        scan_column_amount = 2
        print()  # Newline separator
        match user_input:
            case "1":  # Create table
                # Get shipment data for creating table
                #  TODO uncomment this part
                # (
                #     rows,
                #     _,
                #     scan_column_amount,
                # ) = menu.shipments_menu()

                shipments = ShipmentList(rows)

                # Create table
                table_segmentor.create_table(
                    rows=shipments.get_shipments(),
                    invoice_scan=scan_column_amount,
                )

                # Ask user if they want to use grid tables
                grid = menu.grid_table_input()
                print()

                # Print table
                table_segmentor.print_table(grid=grid)
            case "2" | "4" | "5":  # Select a table
                # Get table index from user and table
                table_index = menu.table_menu(table_segmentor.tables)
                table = table_segmentor.get_table(table_index)

                if table:
                    match user_input:

                        case "2":  # Print table
                            # Ask user if they want to use grid tables
                            print()
                            grid = menu.grid_table_input()

                            # Print selected table
                            table_segmentor.print_table(table_index, grid=grid)
                        case "4":  # Edit table
                            exit_strings = ["exit", ""]
                            while user_input not in ["exit", ""]:
                                table_segmentor.print_table(table_index, grid=True)

                                print("\n==========Edit Menu==========")
                                try:
                                    row = input_(
                                            message="1. Select row to edit (left/right numbers):",
                                            valid_input=[
                                                str(i) for i in range(table.num_rows)
                                            ] + exit_strings,
                                        )
                                    # Check if user wants to exit
                                    if row in exit_strings:
                                        break
                                    else:
                                        row = int(row)
                                    # Adjust indexing for before/after separator
                                    if row > 0:
                                        row = row
                                    else:
                                        row = int(row)
                                except ValueError:
                                    print(f"ERROR: Invalid input!: {row}")
                                    print()
                                    continue

                                try:
                                    # Get column number to edit
                                    column = input_(
                                            message="2. Select column to edit (top/bottom numbers):",
                                            valid_input=[
                                                str(i) for i in range(table.num_columns)
                                            ] + exit_strings,
                                        )
                                    # Check if user wants to exit
                                    if column in exit_strings:
                                        break
                                    else:
                                        column = int(column)
                                except ValueError:
                                    print(f"ERROR: Invalid input!: {column}")
                                    print()
                                    continue
                                
                                replace = input_(
                                    message="3. Replace cell with:",
                                    # First pattern is for rows, second is
                                    # for headers
                                    valid_input="^(?:\d+|exit|)$" if row > 0 else "^(?:[\d\w]+|exit|)$",
                                )
                                # Check if user wants to exit
                                if replace in exit_strings:
                                    break

                                # Edit table
                                print(f"row: {row}, column: {column}, replace: {replace} table_index: {table_index}")  # TODO delete this line
                                table_segmentor.edit_table(
                                    row, column, replace, table_index
                                )
                        case "5": # Get Regex Patterns
                            if table:
                                print()
                                table_segmentor.print_table(table_index, grid=grid)
                                for k, v in table.get_patterns().items():
                                    print(f"{k}: {v}")

                        case _:
                            print("Invalid option selected!")
                            print()

                print()
            case "3":  # Print all tables
                if table_segmentor.tables:
                    # Ask user if they want to use grid tables
                    grid = menu.grid_table_input()
                    print()

                    # Print all tables
                    table_segmentor.print_tables(grid=grid)
                else:
                    print("No tables exist yet!")
                    print()

            case _:
                print("Invalid option selected!")
                print()


if __name__ == "__main__":
    main()

from .tables import TableSegmentor
from .sprouts_session.sprouts_parser import ShipmentList, ShipmentParser
from .menu import InteractiveMenu


def main():
    # Initialize objects
    table_segmentor = TableSegmentor()
    menu = InteractiveMenu()

    while True:
        print("==========Main Menu==========")
        user_input = menu.main_menu()
        print()  # Newline separator
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
                table_segmentor.create_table(
                    rows=shipments.get_shipments(),
                    invoice_scan=scan_column_amount,
                )

                # Print table
                table_segmentor.print_table()
            case "2":  # Select a table
                # Get table index from user
                table_index = menu.table_menu(table_segmentor.tables)

                # Print selected table
                table = table_segmentor.get_table(table_index)
                if table:
                    print()
                    table_segmentor.print_table(table_index)

                print()
            case "3":  # Print all tables
                if table_segmentor.tables:
                    table_segmentor.print_tables()
                else:
                    print("No tables exist yet!")
                    print()

            case _:
                print("Invalid option selected!")
                print()

    print("====================DRIVER====================")


if __name__ == "__main__":
    main()

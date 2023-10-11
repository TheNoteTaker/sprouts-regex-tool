from sprouts import utils
from sprouts.tables import TableSegmentor


def main():
    # Driver code
    sprouts_parser = TableSegmentor()

    # Determine if config file exists

    # Load patterns from config file if they exist

    # Prompt user to use data file or input data
    print("System will try to parse your data. Shipments should be separated "
          "by a blank line if you select data utils.\n")
    print(f"1. Use data file")
    print("2. Input data")
    user_choice = utils.input_(["1", "2"])

    # If user chooses to use data file, load data from file
    filename = utils.exists("data.txt")
    if user_choice == "1":
        while not filename:
            # Prompt user to enter a valid filename until one is entered or
            # the user chooses to exit
            print(f"File does not exist. Please enter valid "
                  "filename (0 to exit):")

            # Get user input for filename
            filename = utils.exists(input("Filename: "))

            if filename in ["exit", "0", "e"]:
                # User chooses to exit
                print("Exiting...")
                exit(0)

        # Get row data from file
        rows = utils.read_file_lines(filename)
    else:
        # Prompt user to input data since they chose not to use a file
        # Get total number of shipments
        shipment_amount = int(utils.input_(
            valid_input="^[1-9][0-9]*$",
            message="Enter Total Shipments: "
        ))
        rows = []
        # for shipment in range(shipment_amount):
        #     # Get data for each shipment
        #     print(f"\nShipment {shipment + 1} "
        #           f"(Type each vendor item on a new line):")
        #     rows.append(utils.read_input_lines())
        #     # Separate shipments with a dashed line
        #     rows.append("|")
        rows = [["000001", "0324", "17842", "001", "7131", "3281"],
                ["|"],
                ["0002", "9243", "7131", "9942", "9999"],
                ["|"],
                ]

    # Create a table
    sprouts_parser.create_table(rows=rows[:-1], invoice_scan=0)

    # Print the table
    table = sprouts_parser.get_table(-1)
    print(table)


if __name__ == "__main__":
    main()

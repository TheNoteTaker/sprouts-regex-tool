from .tables import TableSegmentor
from .sprouts_session.sprouts_parser import ShipmentManager, ShipmentParser


def main():
    # TODO: Remove below
    print("====================DRIVER====================")
    test_data = [["000001", "0324", "17842", "001", "7131", "3281"],
            ["0002", "9243", "7131", "9942", "9999"],
            ]

    # Initialize objects
    table_segmentor = TableSegmentor()
    shipments = ShipmentManager()
    parser = ShipmentParser()

    # Add and parse shipments
    rows = []
    shipments.shipments_menu()
    for shipment in shipments:
        pass


    # Print shipments
    print("Shipments:", shipments.get_shipments())



    # Create a table
    table_segmentor.create_table(rows=shipments.get_shipments(), invoice_scan=1)

    # Print the table
    table = table_segmentor.get_table(-1)
    print(table)

    # Print attributes
    for k, v in table.__dict__.items():
        print(f"{k}: {v}")

    for item in table.get_pattern("rows"):
        print(item)

    for item in table.get_pattern("columns"):
        print(item)
    print("====================DRIVER====================")


if __name__ == "__main__":
    main()

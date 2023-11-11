from . import logger_init  # Initialize logging module and configuration
from . import utils
from .parser import SproutsTable, enable_full_pandas_output
import logging

logger = logging.getLogger(__name__)


def main():
    enable_full_pandas_output()
    data_fp = utils.join(utils.get_parent_dir(__file__, 2), "data", "sample2.txt")
    data = utils.read_file_lines(data_fp)
    table = SproutsTable(data_fp, num_scan_col=3, filter_values=["-----", "/////", "!!!!!", "....."])
    print("Header indices:", table.get_header_indices(["scan", "shipment", "batch"]))
    print("Validate indexes:", table.validate_indexes([0, 1, 2, 3, 4, 5]))
    print("get_scan_and_ship_cols([0, 1, 2, 3]):", table._get_scan_and_ship_cols([0, 1, 2, 3]))
    # print('Scan differences:', table.get_scan_differences([0, 1, 2, 3]))
    # print("Scan overlap:", table.get_scan_overlap([0, 1, 2, 3]))
    # print("Scan differences:", table.get_scan_differences([0, 1, 2, 3]))
    print("Unique values (0, 1, 2, 3):", table.get_values([0, 1, 2, 3], unique=True))
    print("Unique values [Batch] ((0, 1), (2, 3)):", table.get_values([[0, 1], [2, 3]], unique=True))
    print("Values (0, 1, 2, 3):", table.get_values([0, 1, 2, 3]))
    print("Values [Batch] ((0, 1), (2, 3)):", table.get_values([[0, 1], [2, 3]]))
    print("Duplicates (0, 1, 2, 3):", table.get_duplicates([0, 1, 2, 3]))
    print("Duplicates [Batch] ((0, 1), (2, 3)):", table.get_duplicates([[0, 1], [2, 3]]))
    print("Overlap (0, 1, 2, 3):", table.get_overlap([0, 1, 2, 3]))
    print("Overlap [Batch] ((0, 1), (2, 3)):", table.get_overlap([[0, 1], [2, 3]]))
    print("Differences [Symmetric] (0, 1, 2, 3):", table.get_differences([0, 1, 2, 3]))
    print("Differences [Symmetric] [Batch] ((0, 1), (2, 3)):", table.get_differences([[0, 1], [2, 3]]))
    print("Differences [Standard] (0, 1, 2, 3):", table.get_differences([0, 1, 2, 3], symmetric=False))
    print("Differences [Standard] [Batch] ((0, 1), (2, 3)):", table.get_differences([[0, 1], [2, 3]], symmetric=False))
    print("Scan_df:", table.scan_df.info())
    print("Ship_df:", table.shipment_df.info())


    print(table)
    # Change a value in table
    table.df.iloc[0, 0] = "11"
    print(table)
    table.update_table(hard=True)
    print(table)
    

if __name__ == "__main__":
    main()

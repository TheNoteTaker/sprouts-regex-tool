from . import logger_init  # Initialize logging module and configuration
from . import utils
from .parser import Table, enable_full_pandas_output
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def main():
    enable_full_pandas_output()
    data_fp = utils.join(utils.get_parent_dir(__file__, 2), "data", "sample2.txt")
    data = utils.read_file_lines(data_fp)
    table = Table(data_fp, 1)
    print("Header indices:", table.compare.get_header_indices(["scan", "shipment"]))
    print("Validate indexes:", table.compare.validate_indexes([0, 1, 2, 3, 4, 5]))
    print("get_scan_and_ship_cols([0, 1, 2]):", table.compare._get_scan_and_ship_cols([0, 1, 2]))
    print('Scan differences:', table.compare.get_scan_differences([0, 1]))
    print("Differences:", table.compare.get_differences([0, 1]))
    print("Overlap:", table.compare.get_overlap([0, 1]))
    print("Scan overlap:", table.compare.get_scan_overlap([0, 1]))
    print("Duplicates:", table.compare.get_duplicates([0, 1]))
    print(table)
    

if __name__ == "__main__":
    main()

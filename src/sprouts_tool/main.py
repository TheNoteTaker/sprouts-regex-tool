from . import logger_init  # Initialize logging module and configuration
from . import utils
from .parser import Table, enable_full_pandas_output
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def main():
    enable_full_pandas_output()
    data_fp = utils.join(utils.get_parent_dir(__file__, 2), "data", "sample.txt")
    data = utils.read_file_lines(data_fp)
    table = Table(data_fp)
    


if __name__ == "__main__":
    main()

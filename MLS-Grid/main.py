# import functions_framework
from get_notes import write_to_bq
from update_writeback import call_sproc, write_df_to_sheet
from mls_grid import main as mls_main
import logging
from config import config

# @functions_framework.http
def main() -> str:
    try:
        write_to_bq()
    except Exception as e:
        logging.error(f"Error writing to BigQuery: {e}")
        raise
    mls_main()
    call_sproc(config.bq_client())
    write_df_to_sheet()

    return "OK"

main()
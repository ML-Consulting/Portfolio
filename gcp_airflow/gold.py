import logging
import os
from config import config



def run_gold(project_id: str, dataset_id: str, bucket_name: str):

    client = config.bq_client()

    params = {
        "project": project_id,
        "dataset": dataset_id,
        "table": "movies_gold",
        "bucket_name": bucket_name
    }

    try:
        client.get_dataset(dataset_id)
        sql_path = os.path.join(os.path.dirname(__file__), "gold.sql")

        with open(sql_path, 'r') as f:
            raw_sql = f.read()

        formatted_sql = raw_sql.format(**params)
    except Exception as e:
        logging.error(f"Error preparing gold transformation: {e}")
        raise

    try:
        query_job = client.query(formatted_sql)
        query_job.result() # Wait for the job to complete
    except Exception as e:
        logging.error(f"Error executing gold transformation: {e}")
        raise
    
# if __name__ == "__main__": 
def gold_main(project_id: str, dataset_id: str, bucket_name: str):
    run_gold(project_id, dataset_id, bucket_name)
    return 'Gold Layer transformation complete'
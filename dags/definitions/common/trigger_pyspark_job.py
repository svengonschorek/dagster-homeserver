import requests, json, time
import traceback
from typing import Optional

from dagster import get_dagster_logger

# trigger extract_load.py in spark cluster
# -------------------------------------------------------
def trigger_pyspark(file_path: str, args: str = None) -> Optional[str]:
    """
    Submit a PySpark job to a Spark cluster and monitor its execution.
    
    Args:
        file_path: Path to the Python script to execute
        args: Arguments to pass to the script
        
    Returns:
        Optional[str]: Submission ID if successful, None if failed
    """
    logger = get_dagster_logger()
    logger.info(f"Triggering PySpark job with file: {file_path}, args: {args}")
    
    url = "http://spark-master:7078/v1/submissions/create"
    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8'}
    data = {
        "appResource": "",
        "sparkProperties": {
            "spark.master": "spark://spark-master:7077",
            "spark.app.name": "Spark Job " + (args if args else "")
        },
        "clientSparkVersion": "",
        "mainClass": "org.apache.spark.deploy.SparkSubmit",
        "environmentVariables": { },
        "action": "CreateSubmissionRequest",
        "appArgs": [ file_path, args ]
    }

    try:
        logger.debug(f"Sending request to {url} with data: {json.dumps(data)}")
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Spark job submitted successfully! --> {args}")
        submission_id = response.json().get('submissionId')
        
        if not submission_id:
            logger.error(f"No submission ID returned in response: {response.text}")
            raise Exception(f"PySpark job submission failed: No submission ID returned")
            
        logger.debug(f"Received submission ID: {submission_id}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to submit job. Error: {str(e)}")
        logger.error(f"Request details: URL={url}, Headers={headers}")
        raise Exception(f"Failed to submit PySpark job: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error submitting job: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Unexpected error submitting PySpark job: {str(e)}")

    time.sleep(1)
    status_url = f'http://spark-master:7078/v1/submissions/status/{submission_id}'
    logger.debug(f"Monitoring job status at: {status_url}")

    while True:
        try:
            status_response = requests.get(status_url, timeout=10)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            driver_state = status_data.get('driverState')
            success_state = status_data.get('success')
            
            logger.debug(f"Current status: driverState={driver_state}, success={success_state}")

            if success_state == "false" or driver_state == "FAILED":
                logger.error(f"Job failed during execution. Driver state: {driver_state}")
                if 'message' in status_data:
                    logger.error(f"Error message: {status_data['message']}")
                raise Exception(f"PySpark job failed. Driver state: {driver_state}")
                
            elif driver_state in ["RUNNING", "SUBMITTED"]:
                logger.debug(f"Job still running in state: {driver_state}")
                time.sleep(1)
                
            elif driver_state == "FINISHED":
                logger.info(f"Spark job finished successfully! --> {args}")
                return submission_id
                
            else:
                logger.error(f"Unknown driver state: {driver_state}, full response: {status_data}")
                raise Exception(f"PySpark job failed with unknown driver state: {driver_state}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking job status: {str(e)}")
            raise Exception(f"Failed to check PySpark job status: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error monitoring job: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Unexpected error while monitoring PySpark job: {str(e)}")

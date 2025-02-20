import requests, json, time

from dagster import get_dagster_logger

# trigger extract_load.py in spark cluster
# -------------------------------------------------------
def trigger_pyspark(file_path: str, args: str = None):
    
    url = "http://spark-master:7078/v1/submissions/create"
    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8'}
    data = {
        "appResource": "",
        "sparkProperties": {
            "spark.master": "spark://spark-master:7077",
            "spark.app.name": "Spark Test"
        },
        "clientSparkVersion": "",
        "mainClass": "org.apache.spark.deploy.SparkSubmit",
        "environmentVariables": { },
        "action": "CreateSubmissionRequest",
        "appArgs": [ file_path, args ]
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    logger = get_dagster_logger()

    if response.status_code == 200:
        logger.info("Spark job submitted successfully!")
    else:
        logger.error(f"Failed to submit job. Status code: {response.status_code}")
        logger.error(response.text)
        return None

    time.sleep(1)

    submission_id = response.json()['submissionId']
    status_url = 'http://spark-master:7078/v1/submissions/status/' + submission_id

    while True:
        status_response = requests.get(status_url)
        driver_state = status_response.json()['driverState']
        success_state = status_response.json()['success']

        if success_state == "false" or driver_state == "FAILED":
            logger.error("Job failed during execution. Please check Spark logs.")
            return None
        elif driver_state in ["RUNNING", "SUBMITTED"]:
            time.sleep(1)
        elif driver_state == "FINISHED":
            logger.info("Spark job finished successfully!")
            return None
        else:
            logger.info(f"Unknown driver state: {driver_state}")
            return None

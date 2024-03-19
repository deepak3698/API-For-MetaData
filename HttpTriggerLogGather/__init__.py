import logging
from azure.loganalytics import LogAnalyticsDataClient
from azure.identity import DefaultAzureCredential
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        app_id=req_body.get("app_id")
        log_query=req_body.get("log_query")
        
        # Get logs from Log Analytics
        logs = get_logs(app_id, log_query)

        logging.info(f"Logs data {logs}")
        
        # Process logs as needed
        for table in logs:
            for row in table['rows']:
                # Process each row of logs
                logging.info(f"{row}")

        return func.HttpResponse(
             "Log gather successfully",
             status_code=200
        )
    except Exception as error:
        logging.error(f"Error {error}")
        return func.HttpResponse(
             f"Failed to run {error}",
             status_code=400
        )



def get_logs(workspace_id, query):
    # Set up Log Analytics client
    credential = DefaultAzureCredential()
    client = LogAnalyticsDataClient(credential)

    # Execute the query
    response = client.query(workspace_id, query)

    logging.info(f"Get response {response}")
    # Return the logs
    return response.tables
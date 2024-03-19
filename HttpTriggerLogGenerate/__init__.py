import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        list_of_error=req_body.get("list_of_error")

        logging.info("Logging the errors")
        for error_message in list_of_error:
            logging.error(f"{error_message}")

        return func.HttpResponse(
             "Error has been logged successfully",
             status_code=200
        )
    except Exception as error:
        logging.error(f"Error {error}")
        return func.HttpResponse(
             f"Failed to run {error}",
             status_code=400
        )

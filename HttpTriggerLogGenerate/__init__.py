import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    # Type 1 : NameError
    try:
        print(request_variable)
    except Exception as error:
        logging.error(f"{error}")
    
    # Type 2 : TypeError
    try:
        test_data=len(10)
    except Exception as error:
        logging.error(f"{error}")

    # Type 3 : ValueError
    try:
        int_val=int("test")
    except Exception as error:
        logging.error(f"{error}")

    # Type 4 : KeyError
    try:
        my_dict = {'a': 1, 'b': 2}
        print(my_dict['c'])
    except Exception as error:
        logging.error(f"{error}")

    # Type 5 : IndexError
    try:
        my_list = [1, 2, 3]
        print(my_list[3])
    except Exception as error:
        logging.error(f"{error}")

    # Type 6 : FileNotFoundError
    try:
        with open('file_not_available.txt', 'r') as file:
            content = file.read()
    except Exception as error:
        logging.error(f"{error}")

    # Type 7 : ZeroDivisionError
    try:
        test_value=10/0
    except Exception as error:
        logging.error(f"{error}")

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

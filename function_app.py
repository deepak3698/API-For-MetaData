## important libraries 
import pandas as pd
import os
import json
from datetime import datetime
import ssl
from openai import OpenAI  ##importing openai from OpenAI
## SendGrid API to send mail....SMTP SERVER
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import azure.functions as func
import logging

# Disable SSL certificate verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="logcontainer",
                               connection="logparserpoc_STORAGE") 
def blob_trigger(myblob: func.InputStream):
    try:
        # Read the content of the blob
        logs_from_text_file = myblob.read().decode('utf-8')  # Assuming it's a text file, adjust encoding if necessary
        
        # Process logs through AI
        process_logs_through_ai(log_content=logs_from_text_file)
        
    except Exception as e:
        # Log the exception
        logging.error(f"An error occurred while processing the blob: {e}")
        # You can handle the exception further based on your requirements


# Email details
sender_email = 'sakshamverma326@gmail.com'
sendgrid_api_key = os.environ.get('sendgrid_api_key')
open_ai_api_key = os.environ.get('open_ai_api_key')
recipients = ["sakshamverma326@gmail.com"]


def get_openai_response(filtered_log_content):
    # Initialize the OpenAI client
    client = OpenAI(api_key=open_ai_api_key)

    # Define the system and user messages
    system_message = {
        "role": "system",
        "content": "You are an Azure Function App expert developer and debug logs encountered in any function built."
    }

    user_message = {
        "role": "user",
        "content": f"Below are the error logs encountered in various azure function apps on Azure. List out all the errors or exceptions occurred and provide resolutions to resolve each of these errors effectively. The error and resolution in response must be comprehensive and explanatory. Provide response in the following json format:\n\n{{azure_function_app:azure_function_app, datetime_error:datetime_error ,error: error, resolutions: resolution}}\n\nlogs:\n{filtered_log_content}"
    }

    try:
        # Send a request to OpenAI's chat completions API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={ "type": "json_object" },
            messages=[system_message, user_message],
            temperature=0.2,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the generated message content from the OpenAI response
        generated_message = response.choices[0].message.content
        return generated_message
    
    except Exception as e:
        print(f"An error occurred while making a request to OpenAI: {e}")
        return None

def filter_error_logs(log_content):
    # Split the log content into lines
    log_lines = log_content.split('\n')

    # Filter out lines containing [Information] or [Warning]
    filtered_lines = [line for line in log_lines if all(tag not in line for tag in ('[Information]', '[Warning]'))]

    # Join the filtered lines back into a string
    filtered_log_content = '\n'.join(filtered_lines)

    return filtered_log_content

def convert_to_json(data):
    # Check if the input is already a dictionary
    if isinstance(data, dict):
        return data
    # If it's a string, try to load it as JSON
    elif isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            print("Error: Input string is not valid JSON.")
            return None
    else:
        print("Error: Input is neither a string nor a dictionary.")
        return None

# Function to format the DataFrame as an HTML table with better styling
def format_dataframe(df):
    # Replace newline characters with HTML line breaks
    df = df.replace('\n', '<br>', regex=True)

    # Set the table attributes to add borders
    table_attributes = 'border="1" style="border-collapse: collapse; width: 100%;"'

    # Apply the styles to the DataFrame
    styler = df.style.hide(axis='index').set_table_attributes(table_attributes)

    # Set header styles
    styler = styler.set_table_styles([{
        'selector': 'th',
        'props': [
            ('background-color', '#f4f4f4'),
            ('font-weight', 'bold'),
            ('text-align', 'center')
        ]
    }])

    # Get the HTML representation of the Styler object
    html_output = styler.to_html(escape=False)

    # Return the HTML output
    return html_output


# Function to send an email with the formatted DataFrame using SendGrid API
def send_email(subject, body, recipients, sender_email, sendgrid_api_key):
    message = Mail(
        from_email=sender_email,
        to_emails=recipients,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent with status code {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def process_logs_through_ai(log_content):
    filtered_log_content = filter_error_logs(log_content) ##Filtering out the logs keeping errors and exceptions only
    response_from_openai = get_openai_response(filtered_log_content) 

    final_genai_output = convert_to_json(data=response_from_openai)
    
    # Find the key containing the list of errors
    errors_key = None
    for key, value in final_genai_output.items():
        if isinstance(value, list):
            errors_key = key
            break


    # If the key is found, convert to DataFrame and rename columns
    if errors_key:
        output_table = pd.DataFrame(final_genai_output[errors_key]).rename(columns={
            "azure_function_app": "Azure Function",
            "datetime_error": "Timestamp",
            "error": "Error",
            "resolutions": "Resolution"
        })
    else:
        print("No list of errors found in the dictionary.")


    
    ## Send the final output from GenAI through mail.
        
    # Format the DataFrame in a better way (customize this as needed)
    formatted_report_table = format_dataframe(output_table)
    
    # Get the current datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
    
    subject = f"Error report {formatted_datetime}"
    body = f"Error Report {formatted_datetime}<br><br>{formatted_report_table}"

    # Send the email
    if send_email(subject, body, recipients, sender_email, sendgrid_api_key):
        return "Email sent successfully!"



# ##invocation of our main function
# if __name__=='__main__':
#     process_logs_through_ai(log_content = logs_from_text_file)







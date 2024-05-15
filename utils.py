import re
from prompt_collection import COMMAND_DETECTION
from OpenAI_API import openai_api_email
import streamlit as st

def extract_command_from_natural_response(user_input):

    action_list = ["CREATE" , "READ"]
    messages=[{
                
                "role": "assistant" ,
                "content" : f"{COMMAND_DETECTION}\ncontent:{user_input}" ,  
            } ]
    # print(messages)
    email_response = openai_api_email(messages=messages)
    print("this is the email response" , email_response)
    if email_response in action_list:
        return email_response
    else:
        return None 



def is_valid_email(email):
    # Regular expression for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Match the pattern with the email string
    match = re.match(pattern, email)
    
    # If match is found, return True, otherwise return False
    return bool(match)


def truncate_string(string, max_length):
    if len(string) > max_length:
        return string[:max_length - 10]  # Remove the last 10 characters if the string exceeds max length
    else:
        return string


def modify_file_name(original_name):
    # Remove leading and trailing whitespaces
    original_name = original_name.strip()

    # Replace spaces with underscores
    modified_name = original_name.replace(" ", "_")

    # Replace hyphens with underscores
    modified_name = modified_name.replace("-", "_")
    modified_name = modified_name.replace("." ,"_")
    # Remove special characters other than underscores and hyphens
    modified_name = re.sub(r'[^\w\s-]', '', modified_name)

    # Ensure the name starts and ends with an alphanumeric character
    modified_name = re.sub(r'^[^a-zA-Z0-9]*|[^a-zA-Z0-9]*$', '', modified_name)

    # Eliminate consecutive periods
    modified_name = re.sub(r'\.{2,}', '.', modified_name)

    # Ensure the name length is between 3 and 63 characters
    modified_name = truncate_string(string=modified_name , max_length=50)

    return modified_name




def extract_command(user_input):
    # Define the regex pattern to match any action word at the beginning of the sentence followed by a colon
    pattern = r'^([A-Za-z]+):'
    
    
    match = re.search(pattern, user_input)
    
    if match:
        
        action_word = match.group(1)
        return action_word
    else:
        return None





def extract_email_info(email_text):
    # Regular expression patterns for subject, to, and email body
    subject_pattern = r"SUBJECT:\s*(.*?)\s*TO:\s*(.*?)\s*FROM:\s*(.*?)\s*EMAIL_BODY:\s*(.*)"
    
    # Extracting subject, to, and email body
    email_text = str(email_text)
    match = re.match(subject_pattern, email_text, re.DOTALL)
    if match:
        subject = match.group(1).strip()
        to = match.group(2).strip()
        email_body = match.group(4).strip()
        if is_valid_email(email=to):
            print("No valid email address provided")
        return subject, to, email_body
    else:
        return None, None, None


#### TEST CODE ######
# print(modify_file_name("Research Guidance Document - Initial Draft Version.pdf"))
# print(extract_command(user_input="SAVE:Hello, how are you?"))
#### END CODE ######





# Extracting email information
# subject, to, email_body = extract_email_info(email_text)

# # Printing extracted information
# print("Subject:", subject)
# print("To:", to)



# print(extract_command_from_natural_response(user_input="what are the main promotion polices of this company ?"))

# Example usage:


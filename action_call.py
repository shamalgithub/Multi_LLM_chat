
from tool_gmail import create_creds
from tool_gmail import send_email
import ollama 
from prompt_collection import EMAIL_PROMPT
from OpenAI_API import openai_api_email


  
creds = create_creds()

ACTION_LIST = ["SEND" , "SAVE" , "VIEW" , "CREATE"]

def call_ollama(content , system_prompt , action):
    response = ollama.generate(
        model="llama3:instruct" ,
        prompt = f"{system_prompt} , {content} , {action}"
    )
    return response


def call_openai(content , system_prompt , action):
    messages=[{
            
            "role": "assistant" ,
            "content" : f"system: {system_prompt} , content:{content} , prompt:{action}" ,  
        } ]
    print("this is call openai " , messages)
    email_response = openai_api_email(messages=messages)
    return email_response
    


def save_file_as_excel_call():
    pass

def send_email_call(email_address , email_content , email_subject):
    
    if email_content:
        send_status = send_email(auth_creds=creds , email_content=email_content , 
                email_address=email_address , email_subject=email_subject ,
                email_from="airesearchtesting@gmail.com")
    else:
        print("empty email content")

def create_email_conent(user_message):
    pass 



def view_email_call():
    pass 


def action_selection(command , pervious_context , user_input):

    if command in ACTION_LIST:
        if command == "CREATE":
            # email_response = call_ollama(content=pervious_context , system_prompt=EMAIL_PROMPT , action=user_input)
            
            email_response = call_openai(content=pervious_context , system_prompt=EMAIL_PROMPT , action=user_input)
            return email_response
        else:
            return None



# action_selection(command="CREATE")



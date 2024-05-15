from openai import OpenAI

client = OpenAI(api_key="YOUR API KEY")

def openai_api(messages):
   
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield (chunk.choices[0].delta.content)





def openai_api_email(messages):
    email_response = client.chat.completions.create(
       model="gpt-3.5-turbo-1106",
        messages=messages,
        stream=False
    )

    if email_response.choices:
        first_choice = email_response.choices[0]
        chat_response = first_choice.message.content
        return chat_response



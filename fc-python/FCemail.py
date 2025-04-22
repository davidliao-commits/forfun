from openai import OpenAI
import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-wosxiisuzqcpwbnmaobpgflmgxzpumvxsuvusoduscvhcdoc"
)

def send_email(to: str, subject:str, body:str):

    try:
        # Use 163.com SMTP server instead of Gmail
        smtp = smtplib.SMTP('smtp.163.com', 25)
        smtp.ehlo()
        smtp.starttls()  # Fixed: added parentheses
        smtp.login('davidliao2005@163.com', 'david134679')

        msg = MIMEMultipart()
        msg['From'] = 'davidliao2005@163.com'  # Added From field
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        smtp.sendmail(from_addr='davidliao2005@163.com', to_addrs=to, msg=msg.as_string())
        smtp.quit()
        return "Email sent successfully"
    
    except Exception as e:
        return f"Failed to send email: {str(e)}"

tools=[{
        "type": "function",
        "function":{
            "name": "send_email",
            "description":"send email to a given address with a given subject and body",
            "parameters":{
                "type":"object",
                "properties":{
                    "to":{
                        "type":"string",
                        "description":"the email address of the recipient"
                    },
                    "subject":{
                        "type":"string",
                        "description":"the subject of the email"
                    },
                    "body":{
                        "type":"string",
                        "description":"the body of the email"
                    }
                },
                "required":["to","subject","body"],
                "additionalProperties":False
            }
        }
}]

def function_call_playground(prompt:str):
    messages=[
        {"role":"system","content":prompt}
    ]


    response=client.chat.completions.create(
         model="THUDM/glm-4-9b-chat",
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

    func1_name=response.choices[0].message.tool_calls[0].function.name
    func1_args=response.choices[0].message.tool_calls[0].function.arguments
    func1_out=eval(f'{func1_name}(**{func1_args})')
    # breakpoint()
    messages.append(response.choices[0].message)
    messages.append({
        "role":"tool",
        "content":f"{func1_out}",
        "tool_call_id":response.choices[0].message.tool_calls[0].id
    })

    response=client.chat.completions.create(
        model="THUDM/glm-4-9b-chat",
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

    return response.choices[0].message.content

prompt="send an email to chenyitong2024@nsd.pku.edu.cn with subject 'test' and body 'this is a test'"

print(function_call_playground(prompt))
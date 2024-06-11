import os
import sys
import requests
import json
import time
from datetime import datetime

local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True


def send_wechat_message(input_obj):
    response = requests.Response()

    url = 'https://renewal.deepspace.org.cn/api/v1/work-tool/send-message'
    if local_mode:
        url = 'http://localhost:8118/v1/work-tool/send-message'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'API gzWGFkOzdPqrr8DiNYbWJjNGExMDczNmVlNzU3NzoXOTeJDYyz'
    }

    # Construct the text with values from input_obj
    if 'cn' in input_obj.get("preferred_language", ""):
        text = "{}， {}\n\n捐款者：{}\n捐款日期：{}\n捐款金额：{}\n捐款描述：{}\n捐款方式：{}\n捐款编号：{}".format(
            input_obj.get("salutation", ""),
            input_obj.get("message", ""),
            input_obj.get("contributor", ""),
            input_obj.get("date", ""),
            input_obj.get("amount", ""),
            input_obj.get("description", "For most urgent needs"),
            input_obj.get("method", ""),
            input_obj.get("reference", "")
        )
    else:
        text = "{}, {}\n\nContributor: {}\nDate of gift: {}\nAmount: {}\nDescription: {}\nMethod: {}\nReference: {}".format(
            input_obj.get("salutation", ""),
            input_obj.get("message", ""),
            input_obj.get("contributor", ""),
            input_obj.get("date", ""),
            input_obj.get("amount", ""),
            input_obj.get("description", ""),
            input_obj.get("method", ""),
            input_obj.get("reference", "")
        )

    data = json.dumps({
        "phoneNumber": input_obj.get("phone_number", ""),
        "wechatNickname": input_obj.get("wechat_nickname", ""),
        "preferredLanguage": input_obj.get("preferred_language", ""),
        "text": text
    })

    # Try to send the request up to 10 times
    retry_times = 25
    error_message = ""
    for attempt in range(retry_times):
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                # If the request is successful, return the response
                return {
                    "command_id": str(response.json().get("command_id", "")),
                    "message": response.json().get("message", ""),
                    "code": response.status_code
                }
            else:
                print(f"Attempt {attempt + 1} failed with status code {response.status_code}.")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with exception: {str(e)}.")
            error_message = f"Attempt {attempt + 1} failed with exception: {str(e)}."

        # Wait for 1 seconds before retrying
        time.sleep(1)

    # If all attempts fail, return an error message
    return {"command_id": "", "message": error_message, "code": response.status_code}


#
# main code
#        "wechat_nickname": "Edward 2865",
if local_mode:
    input_data = {
        "phone_number": "+86 15250982865",
        "preferred_language": "en-us",
        "contributor": "陶小姐",
        "amount": "2.23 CNY",
        "method": "WeChat",
        "reference": "REL-808122",
        "salutation": "Edward",
        "description": "测试中文网站",
        "message": "thank you so much for your recent gift of 2.23 RMB. Your support is amazing, and I really appreciate you. The people at the Renewal Center feel the same way. They are simply amazed when they learn that friends like you care enough to provide, food, warm clothes, training and support to help them start a new life!",
        "date": "2024-06-05"
    }

output = send_wechat_message(input_data)
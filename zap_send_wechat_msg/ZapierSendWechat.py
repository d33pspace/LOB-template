import os
import sys
import requests
import json
from datetime import datetime

local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True


def format_date_of_gift():
    today_date = datetime.now()
    formatted_date = today_date.strftime("%Y-%m-%d")
    return formatted_date


def send_wechat_messsage(input_obj):
    response = {"status_code": -999}

    url = 'https://renewal.deepspace.org.cn/api/v1/work-tool/send-message'
    if local_mode:
        url = 'http://localhost:8118/v1/work-tool/send-message'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'API gzWGFkOzdPqrr8DiNYbWJjNGExMDczNmVlNzU3NzoXOTeJDYyz'
    }
    try:
        # Construct the text with values from input_obj
        text = "Contributor: {}\nDate of gift: {}\nAmount: {}\nMethod: {}\nReference: {}".format(
            input_obj.get("contributor", ""),
            format_date_of_gift(),
            input_obj.get("amount", ""),
            input_obj.get("method", ""),
            input_obj.get("reference", "")
        )

        data = json.dumps({
            "phoneNumber": input_obj.get("phone_number", ""),
            "wechatNickname": input_obj.get("wechat_nickname", ""),
            "preferredLanguage": input_obj.get("preferred_language", ""),
            "text": text
        })

        # Make a POST request to the API endpoint with the defined headers and data
        # print(data)
        response = requests.post(url, headers=headers, data=data)
        # print(response.json())
    except Exception as e:
        print("Error occurred: {}".format(str(e)))

    return {"command_id": response.json().get("command_id", ""), "message": response.json().get("message", ""),
            "code": response.status_code}


#
# main code
#
if local_mode:
    input_data = {
        "phone_number": "15250982865",
        "wechat_nickname": "名称12865",
        "preferred_language": "en-us",
        "contributor": "James Edward McWhinney (0484)",
        "amount": "13.12",
        "method": "Alipay",
        "reference": "REL-808111"
    }

output = send_wechat_messsage(input_data)
print(output)

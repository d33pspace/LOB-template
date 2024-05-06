import os
import sys
import requests
import json
from datetime import datetime

local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True

def send_wechat_message(input_obj):
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
        if 'cn' in input_obj.get("preferred_language", ""):
            text = "{}\n\n捐款者: {}\n捐款日期: {}\n捐款金额: {}\n捐款方式: {}\n捐款编号: {}".format(
                input_obj.get("text", ""),
                input_obj.get("contributor", ""),
                input_obj.get("date", ""),
                input_obj.get("amount", ""),
                input_obj.get("method", ""),
                input_obj.get("reference", "")
            )
        else:
            text = "{}\n\nContributor: {}\nDate of gift: {}\nAmount: {}\nMethod: {}\nReference: {}".format(
                input_obj.get("text", ""),
                input_obj.get("contributor", ""),
                input_obj.get("date", ""),
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

    return {"command_id": str(response.json().get("command_id", "")), "message": response.json().get("message", ""),
            "code": response.status_code}


#
# main code
#
if local_mode:
    input_data = {
        "phone_number": "15250982865",
        "wechat_nickname": "名称2865",
        "preferred_language": "zh-cn",
        "contributor": "James (0484)",
        "amount": "10.12",
        "method": "Alipay",
        "reference": "REL-808122",
        "text": "Eddie, thank you for your support.",
        "date": "2024-05-01"
    }

output = send_wechat_message(input_data)
print(output)

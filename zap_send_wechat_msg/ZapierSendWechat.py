##############
# V2024-10-05 separate contact_owner and prefer language
# V2024-09-30 set to English group if missing contact_owner
##############

# https://zapier.com/editor/144538426/draft/144538432/fields
# https://zapier.com/editor/159365690/published
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

    validation_message = ""
    retry_times = 25
    url = 'https://renewal.deepspace.org.cn/api/v1/work-tool/send-message'
    if local_mode:
        validation_message += "enable test mode; "
        url = 'http://localhost:8118/v1/work-tool/send-message'
        retry_times = 2

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'API gzWGFkOzdPqrr8DiNYbWJjNGExMDczNmVlNzU3NzoXOTeJDYyz'
    }

    # Construct the text with values from input_obj
    is_contact_owner_cn = False
    # Check if 'contact_owner' exists in input_obj
    if "contact_owner" not in input_obj:
        validation_message += 'missing contact_owner as input; '
    else:
        # Set is_contact_owner_cn based on contact_owner's value
        is_contact_owner_cn = input_obj.get("contact_owner") == "33083949"

    preferred_language = 'zh-cn' if 'cn' in input_obj.get("preferred_language", "") else 'en-us'
    if preferred_language == 'zh-cn':
        text = "{}：{}\n\n捐款者：{}\n捐款日期：{}\n捐款金额：{}\n捐款描述：{}\n捐款方式：{}\n捐款编号：{}".format(
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
            input_obj.get("description", "For most urgent needs"),
            input_obj.get("method", ""),
            input_obj.get("reference", "")
        )

    data = json.dumps({
        "phoneNumber": input_obj.get("phone_number", ""),
        "wechatNickname": input_obj.get("wechat_nickname", ""),
        "contributor": input_obj.get("contributor", ""),
        "preferredLanguage": preferred_language,
        "reference": input_obj.get("reference", ""),
        "contactOwnerCn": is_contact_owner_cn,
        "text": text
    })

    # Try to send the request up to 10 times
    error_message = ""
    for attempt in range(retry_times):
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                # If the request is successful, return the response
                return {
                    "command_id": str(response.json().get("command_id", "")),
                    "message": response.json().get("message", ""),
                    "code": response.status_code,
                    "validation_message": validation_message,
                    "data_to_website": data
                }
            else:
                print(f"Attempt {attempt + 1} failed with status code {response.status_code}.")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with exception: {str(e)}.")
            error_message = f"Attempt {attempt + 1} failed with exception: {str(e)}."

        # Wait for 1 seconds before retrying
        time.sleep(1)

    # If all attempts fail, return an error message
    return {"command_id": "", "message": error_message, "code": response.status_code,
            "validation_message": validation_message, "data_to_website": data}


#
# main code
#        "wechat_nickname": "Edward 2865",
#        "contact_owner": "33083949" is hanson
if local_mode:
    input_data = {
        "phone_number": "+86 15250982865",
        "preferred_language": "en-us",
        "contact_owner": "33083949342",
        "contributor": "Edward Test",
        "amount": "1.02 CNY",
        "method": "WeChat",
        "reference": "TEST-9999",
        "salutation": "Edward",
        "description": "When people are struggling, your gift offers real help",
        "message": "您捐赠的1.02元为人们提供了紧急援助，帮助他们获得重建人生的技能与机会。您的支持至关重要，因此衷心地感谢您！",
        "date": "2024-08-31"
    }

output = send_wechat_message(input_data)

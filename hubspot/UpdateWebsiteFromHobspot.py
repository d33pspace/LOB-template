import os
import sys
import requests
import json
from datetime import datetime

local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True


def update_website(input_obj):

    if input_obj.get("email", "") == "":
        return {"update_count": 0, "message": "update failed because empty email"}

    if input_obj.get("email", "").endswith("@alt.renewal.org.cn"):
        url = 'https://renewal.deepspace.org.cn/api/v1/user/update-from-hubspot'
    else:
        url = 'https://www.renewal.org.cn/api/v1/user/update-from-hubspot'

    if local_mode:
        url = 'http://localhost:8118/v1/user/update-from-hubspot'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'API gzWGFkOzdPqrr8DiNYbWJjNGExMDczNmVlNzU3NzoXOTeJDYyz'
    }
    try:
        receipt_preference = input_obj.get("receipt_preference", "")
        wechat_preference = input_obj.get("wechat_preference", "")
        email_preference = input_obj.get("email_preference", "")

        if receipt_preference.lower() == "wechat" or receipt_preference.lower() == "email":
            if wechat_preference.lower() in ("n", "no", "f", "false"):
                approach_preference = "ALL"
            elif email_preference.lower() in ("n", "no", "f", "false"):
                approach_preference = "ALL"
            else:
                approach_preference = "RECEIPT_ONLY"
        else:
            approach_preference = "None"

        # Construct the new JSON object
        data = json.dumps({
            "email": input_obj.get("email", ""),
            "fullName": input_obj.get("receipt_name", ""),
            "nickname": input_obj.get("salutation", ""),
            "preferredLanguage": input_obj.get("preferred_language", ""),
            "approachPreference": approach_preference,
            "zapierInputData": json.dumps(input_obj)
        })

        print("Post to url {} with data: {}".format(url, str(data)))
        # Make a POST request to the API endpoint with the defined headers and data
        response = requests.post(url, headers=headers, data=data)
        result_json = {"update_count": response.json().get("update_count", 0), "message": "website processed"}
    except Exception as e:
        print("Error occurred: {}".format(str(e)))
        result_json = {"update_count": 0, "message": "update failed with exception, because " + str(e)}

    return result_json


#
# main code
#
if local_mode:
    input_data = {
        "email": "12323534522.yoopay@alt.renewal.org.cn",
        "receipt_preference": "WeChat", # WeChat, email, manual
        "wechat_preference": "false",   # No or N means accept WeChat stories
        "email_preference": "true",   # No or N means accept email stories
        "preferred_language": "zh-cn",
        "receipt_name": "Test Z1",
        "salutation": "et1"
    }

output = update_website(input_data)
print(output)

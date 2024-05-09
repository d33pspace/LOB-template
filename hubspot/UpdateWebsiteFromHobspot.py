import os
import sys
import requests
import json
from datetime import datetime

local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True


def update_website(input_obj):
    url = 'https://renewal.deepspace.org.cn/api/v1/user/update-from-hubspot'
    if local_mode:
        url = 'http://localhost:8118/v1/user/update-from-hubspot'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'API gzWGFkOzdPqrr8DiNYbWJjNGExMDczNmVlNzU3NzoXOTeJDYyz'
    }
    try:
        if input_data["receipt_preference"] == "N":
            approach_preference = "None"
        elif input_data["wechat_preference"] == "Y" or input_data["email_preference"] == "Y":
            approach_preference = "ALL"
        else:
            approach_preference = "RECEIPT_ONLY"

        # Construct the new JSON object
        data = json.dumps({
            "email": input_obj.get("email", ""),
            "fullName": input_obj.get("receipt_name", ""),
            "nickname": input_obj.get("salutation", ""),
            "preferredLanguage": input_obj.get("preferred_language", ""),
            "approachPreference": approach_preference
        })

        # Make a POST request to the API endpoint with the defined headers and data
        if "email" not in input_data or not input_data["email"]:
            result_json = {"update_count": 0, "message": "update failed because empty email"}
        else:
            response = requests.post(url, headers=headers, data=data)
            result_json = {"update_count": response.json().get("update_count", 0), "message": "website processed"}
    except Exception as e:
        print("Error occurred: {}".format(str(e)))
        result_json = {"update_count": 0, "message": "update failed because " + str(e)}

    return result_json


#
# main code
#
if local_mode:
    input_data = {
        "email": "12323534522.yoopay@alt.renewal.org.cn",
        "receipt_preference": "Y",
        "wechat_preference": "Y",
        "email_preference": "N",
        "preferred_language": "zh-cn",
        "receipt_name": "Test Z",
        "salutation": "et"
    }

output = update_website(input_data)
print(output)

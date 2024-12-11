##############
# V2024-12-08 init version of WeChat giving report
##############
import os
import sys
import requests
import json
import uuid
from ftplib import FTP, error_perm
from datetime import datetime
from io import BytesIO
import unicodedata
import time


local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True


def translate_description(description):
    lower_cased_description = description.lower()
    if preferred_language != 'en' and lower_cased_description == 'for most urgent needs':
        description = '为最急需帮助的人们'
    return description


def format_date_of_gift(date_string):
    parsed_date = datetime.strptime(date_string, "%m/%d/%Y")

    # Format the date based on preferred_language
    if preferred_language != 'en':
        formatted_date = parsed_date.strftime("%Y-%m-%d")
    else:
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        # ("%m/%d/%Y")
    return formatted_date

def contains_only_halfwidth_characters(input_string):
    for char in input_string:
        # Check if the character is a half-width character
        if unicodedata.east_asian_width(char) != 'Na' and unicodedata.east_asian_width(char) != 'F':
            return ""
    return input_string


def translate_payment_method(payment_method, reference=None):
    lower_cased_payment_method = payment_method.lower()
    if preferred_language != 'en':
        translation_dict = {
            'alipay': '支付宝',
            'wire': '电汇',
            'bank transfer': '银行转账',
            'paypal': '贝宝',
            'wechat': '微信',
            'stripe': '信用卡',
            'check': '支票',
            'yoopay': '友付'
        }
        payment_method = translation_dict.get(lower_cased_payment_method, payment_method)

    if lower_cased_payment_method == 'check':
        payment_method = f'{payment_method} #{reference}'
    return payment_method


def translate_currency(currency_set, currency=None):

    if len(currency_set) > 1:
        return 'USD' if preferred_language == 'en' else '美元'

    if currency is None and len(currency_set) == 1:
        # If currency is not provided, pop the single currency from the set
        currency = next(iter(currency_set), None)

    if currency == 'USD':
        return 'USD' if preferred_language == 'en' else '美元'
    elif currency == 'CNY':
        return 'CNY' if preferred_language == 'en' else '人民币'
    else:
        return currency


def read_resource(url):
    if local_mode:
        # If local mode is enabled, assume the resource is a local filename
        filename = os.path.basename(url)
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    else:
        # Otherwise, read the resource from the provided URL
        response = requests.get(url)
        content = response.text

    # Check if the resource is a JSON file based on the file extension
    # if url.endswith(".json") or (local_mode and filename.endswith(".json")):
    #     return json.loads(content)
    # else:
    return content


def compose_html():
    from_email = 'connect@renewal.org.cn'
    mailTo = input_data["mail_to"]
    contactName = jsonObject["contactName"]
    salutation = input_data["salutation"]
    salutation = contactName if salutation is None or salutation == "" else salutation

    public_page_url = "https://d33pspace.github.io/LOB-template"
    main_template_url = f'{public_page_url}/2025_giving_reports/wechat/wechat_report_{preferred_language}.html'
    email_report_en_line_item_multi_currency_url = f'{public_page_url}/2025_giving_reports/wechat/wechat_report_{preferred_language}_line_item_multi_currency_template.html'
    email_report_en_line_item_single_currency_url = f'{public_page_url}/2025_giving_reports/wechat/wechat_report_{preferred_language}_line_item_single_currency_template.html'

    main_html_template = read_resource(main_template_url)
    email_report_en_line_item_multi_currency_template = read_resource(email_report_en_line_item_multi_currency_url)
    email_report_en_line_item_single_currency_url = read_resource(email_report_en_line_item_single_currency_url)

    unique_currencies = set()
    invoiceTotalUSD_Count = 0
    unitPriceSource_Count = 0
    for line_item in jsonObject['lineItems']:
        unique_currencies.add(line_item['originalCurrency'])
        invoiceTotalUSD_Count += float(line_item['invoiceTotalUSD'])
        unitPriceSource_Count += float(line_item['unitPriceSource'])

    line_item_template_to_use = email_report_en_line_item_single_currency_url if len(unique_currencies) == 1 \
        else email_report_en_line_item_multi_currency_template

    amount_format = "{:,.2f}"
    total_giving = "{:,.2f} {}"
    if len(unique_currencies) == 1:
        total_giving = total_giving.format(unitPriceSource_Count, translate_currency(unique_currencies))
    else:
        total_giving = total_giving.format(invoiceTotalUSD_Count, translate_currency(unique_currencies))

    # List to store generated HTML content
    line_items_content_array = []
    # Iterate through each line item in the JSON object
    for line_item in jsonObject['lineItems']:
        # Replace placeholders in the HTML template with values from the JSON object
        html_content = line_item_template_to_use.replace('{{ 202401_report_date }}',
                                                         format_date_of_gift(line_item['invoiceDate']))
        html_content = html_content.replace('{{ 202401_report_transaction_reference }}',
                                            line_item['invoiceNumber'].replace("INV", "RWL"))
        html_content = html_content.replace('{{ 202401_report_amount }}',
                                            amount_format.format(float(line_item['unitPriceSource'])))
        html_content = html_content.replace('{{ 202401_report_currency }}',
                                            translate_currency({}, line_item['originalCurrency']))
        html_content = html_content.replace('{{ 202401_report_exchange_rate }}',
                                            '1' if line_item['originalCurrency'] == 'USD' else str(
                                                line_item['currencyRate']))
        html_content = html_content.replace('{{ 202401_report_usd_amount }}',
                                            amount_format.format(float(line_item['invoiceTotalUSD'])))
        html_content = html_content.replace('{{ 202401_report_description }}',
                                            translate_description(line_item['description']))
        html_content = html_content.replace('{{ 202401_report_method }}',
                                            translate_payment_method(line_item['method'], line_item['reference']))

        # Append the generated HTML content to the list
        line_items_content_array.append(html_content)

    # Concatenate all HTML contents into one string
    line_items_html_content = "\n".join(line_items_content_array)

    main_html_content = main_html_template.replace('{{ 202401_report_salutation }}', salutation)
    main_html_content = main_html_content.replace('{{ 202401_report_donor_name }}', contactName)
    main_html_content = main_html_content.replace('{{ 202401_report_line_items }}', line_items_html_content)
    main_html_content = main_html_content.replace('{{ 202401_report_total_giving }}', total_giving)
    main_html_content = main_html_content.replace('{{ from_email }}', from_email)
    main_html_content = main_html_content.replace('{{ subscriber.email }}', mailTo)
    main_html_content = main_html_content.replace('{{ subscriber.salutation }}', salutation)
    main_html_content = main_html_content.replace('{{ inline_postal_address }}',
                                                  '548 Market St # 54802, San Francisco CA, 94104, USA')

    email_subject = '您的2023捐赠报告' if preferred_language == 'zh' else 'Your 2023 giving report'

    if local_mode:
        output_file_name = f'test_{preferred_language}_{salutation}_{len(unique_currencies)}.html'
        with open(output_file_name, 'w', encoding='utf-8') as output_file:
            output_file.write(main_html_content)
        print(f'The final HTML content has been written to {output_file_name}')

    return main_html_content, len(line_items_content_array)

def upload_string_to_ftp(host, username, password, html_string, remote_file_path):
    ftp_error = ""
    try:
        # Connect to the FTP server
        with FTP(host) as ftp:
            # Login to the FTP server
            ftp.login(username, password)

            # Split the path into directory and filename
            *dirs, filename = remote_file_path.split('/')

            # Navigate to or create the remote directories
            for dir_part in dirs:
                try:
                    ftp.cwd(dir_part)  # Try to navigate into the directory
                except error_perm:
                    # Directory does not exist; create it
                    ftp.mkd(dir_part)
                    ftp.cwd(dir_part)

            # Convert the string to bytes
            html_bytes = html_string.encode('utf-8')

            # Open a BytesIO object as a file-like object
            html_file = BytesIO(html_bytes)

            # Upload the file to the FTP server
            ftp.storbinary(f'STOR {remote_file_path}', html_file)

        print(f"Uploaded to '{remote_file_path}' on FTP server.")
    except Exception as ftp_ex:
        print(f"FTP Error: {ftp_ex}")
        ftp_error = f"FTP Error: {ftp_ex}"

    return ftp_error


def send_wechat_message(input_obj):
    response = requests.Response()

    validation_message = ""
    retry_times = 20
    domain = 'https://renewal.deepspace.org.cn/api'
    if local_mode:
        validation_message += "enable test mode; "
        domain = 'http://localhost:8118'
        retry_times = 2

    url = domain + "/v1/work-tool/send-message?wechatRequestType=GIVING_REPORT"
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

    language_in_method = 'zh-cn' if 'cn' in input_obj.get("preferred_language", "") else 'en-us'
    if language_in_method == 'zh-cn':
        text = "{}：感谢您2024年对日新中心慷慨的捐赠，请查看您这一年的捐赠记录 {}".format(
            input_obj.get("salutation", ""),
            input_obj.get("ftp_html_path", "")
        )
    else:
        text = "{}, thank you for your generous donation to Renewal in 2024, here is the records {}".format(
            input_obj.get("salutation", ""),
            input_obj.get("ftp_html_path", "")
        )

    data = json.dumps({
        "phoneNumber": input_obj.get("phone_number", ""),
        "wechatNickname": input_obj.get("wechat_nickname", ""),
        "contributor": input_obj.get("contributor", ""),
        "preferredLanguage": language_in_method,
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

        # Wait for 1 second before retrying
        time.sleep(1)

    # If all attempts fail, return an error message
    return {"command_id": "", "message": error_message, "code": response.status_code,
            "validation_message": validation_message, "data_to_website": data}


#
# main code
#
ftp_host = 'renewal365.org'
ftp_username = 'connect@renewal365.org'
ftp_password = 'A6%hJ!xGea'
remote_html_directory = '/donorreport/templates/2025_wechat_reports/'
if local_mode:
    read_json_object = read_resource("input.json")
    # read_json_object = json.dumps(read_resource("input.json"))
    input_data = {
        ##### new starts
        "phone_number": "+86 15250982865",
        "contact_owner": "33083949342",
        "contributor": "Edward Test", # full name
        #### new ends
        "json_object": read_json_object,
        "preferred_language": "en-us",
        "mail_to": "edwazhao@hotmail.com",
        "salutation": "xxx"
    }

preferred_language = 'zh' if "preferred_language" in input_data and 'zh' in input_data["preferred_language"] else 'en'
jsonObject = {}
output_error = ''
try:
    # Try to parse the JSON string
    jsonObject = json.loads(input_data["json_object"])
except ValueError as e:
    # Handle the exception when the JSON string is not valid
    output_error = f"Error decoding JSON: {e}"

output = {}
if "contactName" in jsonObject:
    html_content, count_of_line_items = compose_html()

    # https://renewal365.org/images/donorreport/templates/2025_wechat_reports/0116_contactName.html
    random_chars = str(uuid.uuid4())[:6]
    html_file_name = datetime.now().strftime("%m%d") + "_" + random_chars + "_" + contains_only_halfwidth_characters(input_data["salutation"]) + ".html"
    remote_html_file_path = f"{remote_html_directory}{html_file_name}"
    error = upload_string_to_ftp(ftp_host, ftp_username, ftp_password, html_content, remote_html_file_path)
    ftp_html_path = f"https://renewal365.org/images/donorreport/templates/2025_wechat_reports/{html_file_name}"

    info = f"count_of_line_items is {count_of_line_items} for {input_data['salutation']}"

    input_obj = {**input_data, "ftp_html_path": ftp_html_path}
    wechat_response = send_wechat_message(input_obj)

    output = {**wechat_response, "ftp_html_path": ftp_html_path, "error": error, "info": info}
else:
    output = {"error": output_error}

output = {**output, **input_data}
if local_mode:
    print(output)

import os
import sys
import requests
import json
from datetime import datetime

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


# Method to generate the full giving report in English
def generate_giving_report_english(contact_name, line_items):
    # Extract the contact name for salutation (first name)
    salutation = contact_name.split()[0]

    # Define the letter body text in English
    letter_body = "We are pleased to provide you with a summary of your 2024 giving record below."

    # Initialize the full report content
    full_report = f"Dear {salutation},\n\n{letter_body}\n\nYour 2024 giving record:\n"

    # Iterate over the sorted line items and format them into the desired template
    for item in line_items:
        invoice_date = format_date_of_gift(item['invoiceDate'])
        amount = f"${float(item['invoiceTotalUSD']):,.2f}"
        reference = item['reference'] if item['reference'] else None  # Reference is None if not available
        description = item['description']

        # Append each gift to the report content
        full_report += f"\nDate of gift: {invoice_date}\nAmount: {amount}\n"

        # Only include the reference if it's not None or "N/A"
        if reference and reference != "N/A":
            full_report += f"Reference: {reference}\n"

        # Append the description regardless of reference presence
        full_report += f"Description: {description}\n"

    return full_report


# Method to generate the full giving report in Chinese
def generate_giving_report_chinese(contact_name, line_items):
    # Extract the contact name for salutation (first name)
    salutation = contact_name.split()[0]

    # Define the letter body text in Chinese
    letter_body = "我们很高兴为您提供2024年度的捐赠记录。"

    # Initialize the full report content
    full_report = f"亲爱的 {salutation},\n\n{letter_body}\n\n您的2024年度捐赠记录如下：\n"

    # Iterate over the sorted line items and format them into the desired template
    for item in line_items:
        invoice_date = format_date_of_gift(item['invoiceDate'])
        amount = f"¥{float(item['invoiceTotalUSD']):,.2f}"  # Convert USD to CNY symbol
        reference = item['reference'] if item['reference'] else None
        description = item['description']

        # Append each gift to the report content
        full_report += f"\n捐赠日期: {invoice_date}\n捐赠金额: {amount}\n"

        # Only include the reference if it's not None or "N/A"
        if reference and reference != "N/A":
            full_report += f"参考: {reference}\n"

        # Append the description regardless of reference presence
        full_report += f"描述: {description}\n"

    return full_report


# Main logic to load JSON and generate the appropriate report
def generate_report():
    # Read the JSON object from input_data
    read_json_object = json.loads(input_data["json_object"])
    salutation = input_data["salutation"] or read_json_object.get("contactName", "").split()[
        0]  # Use input salutation or first name from contactName

    # Sort the line items by invoice date before passing them to the method
    line_items_sorted = sorted(read_json_object['lineItems'],
                               key=lambda x: datetime.strptime(x['invoiceDate'], '%m/%d/%Y'))

    # Generate the report based on the preferred language
    if preferred_language == "en":
        # Generate report in English
        # print("Generate report in English")
        full_report = generate_giving_report_english(salutation, line_items_sorted)
    else:
        # Generate report in Chinese
        # print("Generate report in Chinese")
        full_report = generate_giving_report_chinese(salutation, line_items_sorted)

    return full_report


#
# main code
#
if local_mode:
    local_read_json_object = read_resource("input.json")
    # read_json_object = json.dumps(read_resource("input.json"))
    input_data = {
        "json_object": local_read_json_object,
        "preferred_language": "en-us",
        "phone": "1555550000",
        "salutation": "salu123"
    }

preferred_language = 'zh' if "preferred_language" in input_data and 'zh' in input_data["preferred_language"] else 'en'
jsonObject = {}
final_text_report = ''
json_error = ''
# try:
final_text_report = generate_report()
print(final_text_report)
# except ValueError as e:
#     # Handle the exception when the JSON string is not valid
#     json_error = f"Error decoding JSON: {e}"
#     print(json_error)

output = {}
if "contactName" in jsonObject:
    output = {"wechat_report": final_text_report, "contactName": jsonObject['contactName']}
else:
    output = {"error": json_error}

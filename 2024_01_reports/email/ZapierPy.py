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
        formatted_date = parsed_date.strftime("%m/%d/%Y")
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
    if currency is None:
        # If currency is not provided, pop the single currency from the set
        currency = currency_set.pop()

    if len(currency_set) != 1:
        return 'USD' if preferred_language == 'en' else '美元'
    else:
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
    if url.endswith(".json") or (local_mode and filename.endswith(".json")):
        return json.loads(content)
    else:
        return content


public_page_url="https://d33pspace.github.io/LOB-template"
json_input_url = f'{public_page_url}/2024_01_reports/email/input.json'

jsonObject = read_resource(json_input_url) if local_mode else json.loads(input_data["json_object"])
preferred_language = 'en' if local_mode else input_data["preferred_language"]
preferred_language = 'en' if 'en' in preferred_language else 'zh'
from_email = 'connect@renewal.org.cn'
mailTo = 'connect@renewal.org.cn' if local_mode else input_data["mail_to"]
contactName = jsonObject["contactName"]
salutation = contactName if local_mode else input_data["salutation"]
salutation = contactName if salutation is None or salutation == "" else salutation

main_template_url = f'{public_page_url}/2024_01_reports/email/email_report_{preferred_language}.html'
email_report_en_line_item_multi_currency_url = f'{public_page_url}/2024_01_reports/email/email_report_{preferred_language}_line_item_multi_currency_template.html'
email_report_en_line_item_single_currency_url = f'{public_page_url}/2024_01_reports/email/email_report_{preferred_language}_line_item_single_currency_template.html'

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
    html_content = line_item_template_to_use.replace('{{ 202401_report_date }}', format_date_of_gift(line_item['invoiceDate']))
    html_content = html_content.replace('{{ 202401_report_transaction_reference }}', line_item['invoiceNumber'].replace("INV", "RWL"))
    html_content = html_content.replace('{{ 202401_report_amount }}', amount_format.format(float(line_item['unitPriceSource'])))
    html_content = html_content.replace('{{ 202401_report_currency }}', translate_currency(unique_currencies, line_item['originalCurrency']))
    html_content = html_content.replace('{{ 202401_report_exchange_rate }}', '1' if line_item['originalCurrency'] == 'USD' else str(line_item['currencyRate']))
    html_content = html_content.replace('{{ 202401_report_usd_amount }}', amount_format.format(float(line_item['invoiceTotalUSD'])))
    html_content = html_content.replace('{{ 202401_report_description }}', translate_description(line_item['description']))
    html_content = html_content.replace('{{ 202401_report_method }}', translate_payment_method(line_item['method'], line_item['reference']))

    # Append the generated HTML content to the list
    line_items_content_array.append(html_content)

# Concatenate all HTML contents into one string
line_items_html_content = "\n".join(line_items_content_array)

main_html_content = main_html_template.replace('{{ 202401_report_donor_name }}', salutation)
main_html_content = main_html_content.replace('{{ 202401_report_line_items }}', line_items_html_content)
main_html_content = main_html_content.replace('{{ 202401_report_total_giving }}', total_giving)
main_html_content = main_html_content.replace('{{ from_email }}', from_email)
main_html_content = main_html_content.replace('{{ subscriber.email }}', mailTo)
main_html_content = main_html_content.replace('{{ subscriber.salutation }}', salutation)
main_html_content = main_html_content.replace('{{ inline_postal_address }}', '548 Market St # 54802, San Francisco CA, 94104')

output = {"output": main_html_content}

if local_mode:
    output_file_name = 'test.html'
    with open(output_file_name, 'w', encoding='utf-8') as output_file:
        output_file.write(main_html_content)
    print(f'The final HTML content has been written to {output_file_name}')


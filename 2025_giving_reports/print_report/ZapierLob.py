import os
import sys
import requests
import json
import uuid
from ftplib import FTP
from datetime import datetime
from io import BytesIO
import unicodedata


preferred_language = 'en'
local_mode = False  # True or False
if "local_mode=true" in sys.argv:
    local_mode = True


def contains_only_halfwidth_characters(input_string):
    for char in input_string:
        # Check if the character is a half-width character
        if unicodedata.east_asian_width(char) != 'Na' and unicodedata.east_asian_width(char) != 'F':
            return ""
    return input_string


def format_date_of_gift(date_string):
    parsed_date = datetime.strptime(date_string, "%m/%d/%Y")

    # Format the date based on preferred_language
    if preferred_language != 'en':
        formatted_date = parsed_date.strftime("%Y-%m-%d")
    else:
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        # ("%m/%d/%Y")
    return formatted_date


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
    contactName = jsonObject["contactName"]
    salutation = input_data["salutation"]
    salutation = contactName if salutation is None or salutation == "" else salutation

    public_page_url = "https://d33pspace.github.io/LOB-template"
    main_template_url = f'{public_page_url}/2024_01_reports/print_report/print_report_no_photo.html'

    main_html_template = read_resource(main_template_url)

    unique_currencies = set()
    invoiceTotalUSD_Count = 0
    unitPriceSource_Count = 0
    for line_item in jsonObject['lineItems']:
        unique_currencies.add(line_item['originalCurrency'])
        invoiceTotalUSD_Count += float(line_item['invoiceTotalUSD'])
        unitPriceSource_Count += float(line_item['unitPriceSource'])

    line_item_template_to_use = "<tr><td><p>{{date}}</p></td><td><p>{{reference}}</p></td>" \
                                "<td><p>{{amount}}</p></td><td><p>{{currency}}</p></td></tr>"

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
        temp_html_content = line_item_template_to_use.replace('{{date}}',
                                                              format_date_of_gift(line_item['invoiceDate']))
        temp_html_content = temp_html_content.replace('{{reference}}',
                                                      line_item['invoiceNumber'].replace("INV", "RWL"))
        temp_html_content = temp_html_content.replace('{{amount}}',
                                                      amount_format.format(float(line_item['unitPriceSource'])))
        temp_html_content = temp_html_content.replace('{{currency}}',
                                                      translate_currency({}, line_item['originalCurrency']))

        # Append the generated HTML content to the list
        line_items_content_array.append(temp_html_content)

    # Concatenate all HTML contents into one string
    line_items_html_content = "\n".join(line_items_content_array)

    main_html_content = main_html_template.replace('{{202401_report_salutation}}', salutation)
    main_html_content = main_html_content.replace('{{202401_report_line_items}}', line_items_html_content)
    main_html_content = main_html_content.replace('{{202401_report_total_giving}}', total_giving)

    if local_mode:
        output_file_name = f'test_email.html'
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


#
# main code
#
ftp_host = 'renewal365.org'
ftp_username = 'connect@renewal365.org'
ftp_password = 'A6%hJ!xGea'
remote_html_directory = '/donorreport/templates/2024_lob_reports/'

if local_mode:
    read_json_object = read_resource("input.json")
    # read_json_object = json.dumps(read_resource("input.json"))
    input_data = {
        "json_object": read_json_object,
        "salutation": "Amadeus"
    }

jsonObject = {}
json_error = ''
try:
    # Try to parse the JSON string
    jsonObject = json.loads(input_data["json_object"])
except ValueError as e:
    # Handle the exception when the JSON string is not valid
    json_error = f"Error decoding JSON: {e}"

output = {}
if "contactName" in jsonObject:
    html_content, count_of_line_items = compose_html()

    # https://renewal365.org/images/donorreport/templates/2024_lob_reports/0116_contactName.html
    random_chars = str(uuid.uuid4())[:6]
    html_file_name = datetime.now().strftime("%m%d") + "_" + contains_only_halfwidth_characters(input_data["salutation"]) + "_" + random_chars + ".html"
    remote_html_file_path = f"{remote_html_directory}{html_file_name}"
    error = upload_string_to_ftp(ftp_host, ftp_username, ftp_password, html_content, remote_html_file_path)
    ftp_html_path = f"https://renewal365.org/images/donorreport/templates/2024_lob_reports/{html_file_name}"

    if (error is None or error == '') and count_of_line_items > 15:
        error = f"count_of_line_items is {count_of_line_items} which exceed the frame"

    output = {"ftp_html_path": ftp_html_path, "error": error}
else:
    output = {"error": json_error}

if local_mode:
    print(output)
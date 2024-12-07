import requests

response = requests.post(
    'https://api.pdfshift.io/v3/convert/pdf',
    auth=('api', 'sk_0a19d4e4c2917705952d348c84190fdbd4841348'),
    json={
        "source": "https://renewal365.org/images/donorreport/templates/2025_wechat_reports/1207_Amadeus_dff1e4.html",
        "sandbox": True,
        "landscape": False,
        "use_print": False
    }
)

response.raise_for_status()

with open('abc_use_print.pdf', 'wb') as f:
    f.write(response.content)

# curl \
#     -u 'api:sk_0a19d4e4c2917705952d348c84190fdbd4841348' \
#     -H 'Content-Type: application/json' \
#     -d '{"source":"https://renewal365.org/images/donorreport/templates/2025_wechat_reports/1207_Amadeus_dff1e4.html","landscape": false, "use_print": false, "sandbox": true}' \
#     "https://api.pdfshift.io/v3/convert/pdf" \
#     -o 1207_Amadeus_2_pages_2.pdf
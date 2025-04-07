import requests
import json
import re
# Confluence API URL
url = "https://confluence.fkinternal.com/rest/searchv3/1.0/cqlSearch?user=padala.t&sessionUuid=11006a06-199b-436f-af51-2d9d96661d20&cql=space+in+(%22TNS%22%2C%22TRUS%22%2C%22tnsds%22%2C%22TMOS%22%2C%22TNSBIZ%22)&start="

# Headers from your browser request
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "confluence.fkinternal.com",
    "Pragma": "no-cache",
    "Referer": "https://confluence.fkinternal.com/dosearchsite.action?cql=space+in+(%22TNS%22%2C%22TRUS%22%2C%22tnsds%22%2C%22TMOS%22%2C%22TNSBIZ%22%2C%223PS%22)",
    "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# Include authentication cookies
cookies = {
    "_ga": "GA1.1.1233615838.1742792249",
    "_ga_N8V65JFHVX": "GS1.1.1742794407.2.1.1742794526.0.0.0",
    "seraph.confluence": "446434323%3A79066bcf1dc6d96221c5f8a44f7a9fd11dc451bb",
    "ROUTEID": "0dd6cd7f1116891a",
    "JSESSIONID": "7AD686601A66CD3BF1F9AF96CA4B1E2B"
}

# Send GET request wit
cache = {}

# Send request

for start_index in range(0,5190,10):
    response = requests.get(url+str(start_index)+"&limit=10&excerpt=highlight&includeArchivedSpaces=false&_=1743140221149", headers=headers, cookies=cookies)

    if response.status_code == 200:
        data = response.json()
        
        # Save full JSON response
        with open("confluence_response.json", "w") as f:
            json.dump(data, f, indent=4)
        
        print("Response saved successfully.")
        
        # Regex patterns
        pageid_pattern = re.compile(r"(.*?pageId=\d+)")  # Extracts up to pageId=...
        display_pattern = re.compile(r"(https://confluence\.fkinternal\.com/display/[^?]+)")  # Extracts up to /display/...
        preview_pattern = re.compile(r"(.*?)(\?preview=.*)")  # Removes preview=... from the URL

        # Lists to store categorized URLs
        pageid_urls = []
        full_urls = []

        # Extract URLs from the response
        for result in data.get("results", []):
            e_url = result.get("url", "")
            
            # Remove preview if present
            match_preview = preview_pattern.search(e_url)  
            match_pageid = pageid_pattern.search(e_url)
            match_display = display_pattern.search(e_url)

            extracted_url = None  # Default case

            if match_pageid:
                extracted_url = match_pageid.group(1)  # Store only up to pageId
            elif match_display:
                extracted_url = match_display.group(1)  # Store only up to /display/...
            elif match_preview:
                extracted_url = match_preview.group(1)  # Store only up to before preview
            
            if extracted_url:
                # Check if URL is already in cache
                if extracted_url not in cache:
                    cache[extracted_url] = True  # Mark URL as processed
                    pageid_urls.append(extracted_url)
            else:
                if e_url not in cache:
                    cache[e_url] = True  # Mark URL as processed
                    full_urls.append(e_url)  # Store full URL

        # Save to files
        with open("pageid_urls.txt", "a") as f:
            f.write("\n".join(pageid_urls))

        with open("full_urls.txt", "a") as f:
            f.write("\n".join(full_urls))

        print(f"Extracted {len(pageid_urls)} pageId/display URLs and {len(full_urls)} full URLs.")

    else:
        print(f"Error: {response.status_code}, {response.text}")
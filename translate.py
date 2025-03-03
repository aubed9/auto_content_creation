import time
import requests
import re
api_key = "268976:66f4f58a2a905"


def read_srt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            srt_content = file.read()
            return srt_content
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def clean_text(text):
    # Remove 'srt ' from the start of each line
    # Remove ''' from the start and end
    text = re.sub(r"^```|```$", '', text)
    text = re.sub(r'^srt', '', text, flags=re.MULTILINE)
    return text

def translate_text(api_key, text, source_language = "en", target_language = "fa"):
    url = "https://api.one-api.ir/translate/v1/google/"
    request_body = {"source": source_language, "target": target_language, "text": text}
    headers = {"one-api-token": api_key, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=request_body)
    if response.status_code == 200:
        result = response.json()
        return result['result']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def enhance_text(api_key, text):
    url = "https://api.one-api.ir/chatbot/v1/gpt4o/"

    # Prepare the request body
    request_body = [{
        "role": "user",
        "content":  f"Please take the following SRT subtitle text in English and translate only the subtitle text into Persian. Ensure that all numbering and time codes remain unchanged. convert English terms in to common persian terms. The output should be a new SRT file with the subtitles in Persian, preserving the original formatting and timings and exept for the subtitle dont return anything in response. the subtitle will be provided in the following message"
    },
    {
    "role": "assistant",
    "content": "okay"
    },
    {
    "role": "user",
    "content": text
    }
    ]

    # Add the API key to the request
    headers = {
        "one-api-token": api_key,
        "Content-Type": "application/json"
    }

    # Make the POST request
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        response = requests.post(url, headers=headers, json=request_body)
        if response.status_code == 200:
            result = response.json()
            if result["status"] == 200:
                print("status: ", result["status"])
                te = clean_text(result["result"][0])
                print("result: ", te)
                return te
            else:
                print(f"Error: status {result['status']}, retrying in 30 seconds...")
        else:
            print(f"Error: {response.status_code}, {response.text}, retrying in 30 seconds...")
        attempts += 1
        time.sleep(10)
    print("Error Max attempts reached. Could not retrieve a successful response.")
    te = translate_text(api_key, text)
    return te


def generate_translated_subtitle(language, segments, input_video_name):
    input_video_name=input_video_name.split('/')[-1]
    subtitle_file = f"{input_video_name}.srt"
    text = ""
    lines = segments.split('\n')
    new_list = [item for item in lines if item != '']
    segment_number = 1

    for index, segment in enumerate(new_list):
        if (index+1) % 3 == 1 or (index+1)==1:
            text += f"{segment}\n"
            segment_number += 1
        if (index+1) % 3 == 2 or (index+1)==2:
            text += segment + "\n"
        if (index+1) % 3 == 0:
            text += f"\u200F{segment}\n\n"

    with open(subtitle_file, "a", encoding='utf8') as f:
        f.write(text)
    return subtitle_file

def translate(srt_files):
    print("translate")
    for srt_file in srt_files:
        srt = read_srt_file(srt_file)
        srt_string = enhance_text(api_key, srt)
        print(srt_string)
        subtitle_file = generate_translated_subtitle('fa', srt_string, 'video_subtitled')
        time.sleep(10)

    return subtitle_file

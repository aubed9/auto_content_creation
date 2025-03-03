import os
import requests
import subprocess
from pydub import AudioSegment
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from pydub import effects
import os
import pysrt
import json
import time
from moviepy import VideoFileClip, AudioFileClip, AudioClip
import os
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzeXN0ZW0iOiJzYWhhYiIsImNyZWF0ZVRpbWUiOiIxNDAzMTIwNTE0MTgzMDM2MyIsInVuaXF1ZUZpZWxkcyI6eyJ1c2VybmFtZSI6IjFlZDZjN2M1LWVjNTktNGI4Yi1iYThkLTk1NTk1ZWQ0MmNhMCJ9LCJkYXRhIjp7InNlcnZpY2VJRCI6ImRmNTNhNzgwLTIxNTgtNDUyNC05MjQ3LWM2ZjBiYWQzZTc3MCIsInJhbmRvbVRleHQiOiJvYlNXciJ9LCJncm91cE5hbWUiOiIwMmYzMWRmM2IyMjczMmJkMDNmYjBlYjU2ZjE1MGEzZCJ9.QakcV3rPn7bji7ur0VPmCzHLWiOs2NXEGw9ILyhpgOw"



def generate_tts_audio(persian_text, output_file):
    api_url = "https://partai.gw.isahab.ir/TextToSpeech/v1/speech-synthesys"
    proxies = { 
              "https"  : "https://free.shecan.ir/dns-query"
            }
    headers = {
    'Content-Type': 'application/json',
    'gateway-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzeXN0ZW0iOiJzYWhhYiIsImNyZWF0ZVRpbWUiOiIxNDAzMTIwNTE0MTgzMDM2MyIsInVuaXF1ZUZpZWxkcyI6eyJ1c2VybmFtZSI6IjFlZDZjN2M1LWVjNTktNGI4Yi1iYThkLTk1NTk1ZWQ0MmNhMCJ9LCJkYXRhIjp7InNlcnZpY2VJRCI6ImRmNTNhNzgwLTIxNTgtNDUyNC05MjQ3LWM2ZjBiYWQzZTc3MCIsInJhbmRvbVRleHQiOiJvYlNXciJ9LCJncm91cE5hbWUiOiIwMmYzMWRmM2IyMjczMmJkMDNmYjBlYjU2ZjE1MGEzZCJ9.QakcV3rPn7bji7ur0VPmCzHLWiOs2NXEGw9ILyhpgOw'
    }
    payload = json.dumps({
    "data": persian_text,
    "filePath": "true",
    "base64": "0",
    "checksum": "1",
    "speaker": "2"
    })
    response = requests.request("POST", api_url, headers=headers, data=payload, proxies=proxies)
    link = response.text.split('"')[11]
    link = "https://"+link
    print(link)
    responseD = requests.get(link, stream=True)
    responseD.raise_for_status()
    if responseD:
        with open(output_file, 'wb') as file:
            for chunk in responseD.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
            file.close()
        print(f"Downloaded successfully")
        time.sleep(10)
        return "video.mp4"
    else:
        print(f"Failed to generate TTS audio: {response.status_code} - {response.text}")
        return False

def generate_audio_segments(segments, output_dir):
    audio_files = []
    for index, segment in enumerate(segments):
        audio_file = os.path.join(output_dir, f"segment_{index}.mp3")
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                if generate_tts_audio(segment.text, audio_file):  # Assuming this returns True/False based on success
                    audio_files.append(((f"{segment.start} --> {segment.end}"), audio_file))
                    break  # If successful, move to the next segment
                # If the above fails (returns False or raises an exception), wait and retry
                retries += 1
                if retries < max_retries:
                    time.sleep(30)  # Wait for 30 seconds before retrying
            except Exception as e:
                if retries == max_retries - 1:  # Last retry attempt
                    raise RuntimeError(f"Failed to generate audio after {max_retries} attempts for segment: {segment.text}") from e
        else:
            # If all retries failed (loop completed without breaking)
            raise RuntimeError(f"Failed to generate audio after {max_retries} attempts for segment: {segment.text}")
    return audio_files

def srt_time_to_seconds(srt_time):
    hours, minutes, seconds = srt_time.split(':')
    seconds, milliseconds = seconds.split(',')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    return total_seconds

def render_dubbed_video(input_video, audio_files, output_video):
    # Load the input video and remove its audio
    video = VideoFileClip(input_video)
    video_no_audio = video.without_audio()
    print("Video duration (ms):")
    print(video_no_audio.duration * 1000)
    # Get total video duration in milliseconds
    video_duration_in_seconds = video_no_audio.duration
    video_duration_in_ms = video_duration_in_seconds * 1000
    audio_canva = AudioSegment.silent(duration=video_duration_in_ms)
    for timestamp, audio_file in audio_files:
        start_str, end_str = timestamp.split(' --> ')
        start_sec = srt_time_to_seconds(start_str) * 1000
        end_sec = srt_time_to_seconds(end_str) * 1000
        # Load the audio file
        audio = AudioSegment.from_file(audio_file)
        original_duration_ms = len(audio)
        available_slot = end_sec - start_sec
        if available_slot <= 0:
            print(f"Invalid timestamp for {audio_file}. Skipping.")
            continue
        elif original_duration_ms > available_slot:
            speed_factor = min(original_duration_ms / available_slot, 1.2)
            audio = audio.speedup(speed_factor)
        # Append the processed audio to the canvas
        audio_canva = audio_canva.overlay(audio, position=start_sec)
    # Export the combined audio to a temporary file
    combined_audio_file = "combined_audio.mp3"
    audio_canva.export(combined_audio_file, format="mp3")
    # Load the combined audio using MoviePy
    new_audio = AudioFileClip(combined_audio_file)
    # Set the new audio to the video
    final_video = video_no_audio.with_audio(new_audio)
    # Write the output video file
    final_video.write_videofile(output_video, codec="libx264", audio_codec="aac")
    # Clean up temporary files
    video.close()
    new_audio.close()
    final_video.close()

def dub(srt, input_video):
    # Step 1: Parse the SRT-like text
    output_video = "video_out.mp4"
    subtitles = pysrt.open(srt, encoding="utf-8")
    print("Parsed segments:", subtitles)
    # Step 2: Translation (commented out as input is already Persian)
    # Step 3: Generate audio for each Persian segment
    output_dir = "audio_segments"
    os.makedirs(output_dir, exist_ok=True)
    audio_files = generate_audio_segments(subtitles, output_dir)
    # Step 4: Render the dubbed video
    render_dubbed_video(input_video, audio_files, output_video)
    # Clean up audio segments directory
    for _, audio_file in audio_files:
        os.remove(audio_file)
    os.rmdir(output_dir)
    
    return output_video
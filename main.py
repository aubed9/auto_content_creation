from transcribe import transcribe
from moviepy import *
from translate import translate  
from edite_video import video_edit
import gradio as gr
import requests
import os
from dub import dub


def extract_audio(input_video_name):
    # Define the input video file and output audio file
    mp3_file = "audio.mp3"
    # Load the video clip
    video_clip = VideoFileClip(input_video_name)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio
    duration = audio_clip.duration
    print(duration)
    # Write the audio to a separate file
    audio_clip.write_audiofile(mp3_file)

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()

    print("Audio extraction successful!")
    return mp3_file, duration

def download_video(url):

    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open("video.mp4", 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
        file.close()
    print(f"Downloaded successfully")
    return "video.mp4"

def main(url, clip_type, parameters,  progress=gr.Progress()):

    if clip_type == "dub":
        progress(0, desc="Starting")
        video = download_video(url)
        progress(5, desc="downloaded")
        mp3_file, duration = extract_audio(video)
        progress(10, desc="extract audio")
        srt_list = transcribe(mp3_file)
        progress(35, desc="transcribe")
        subtitle_file = translate(srt_list)
        progress(55, desc="translate")
        output_video_file = dub(subtitle_file, video)
        progress(100, desc="finish")
        os.remove(subtitle_file)
    else:
        color, font = parameters.split(",")
        progress(0, desc="Starting")
        video = download_video(url)
        progress(5, desc="downloaded")
        mp3_file, duration = extract_audio(video)
        progress(10, desc="extract audio")
        srt_list = transcribe(mp3_file)
        progress(35, desc="transcribe")
        subtitle_file = translate(srt_list)
        progress(55, desc="translate")
        print(parameters)
        output_video_file = video_edit(subtitle_file, video, color, font, input_audio= "audio.mp3")
        progress(100, desc="finish")
        os.remove(subtitle_file)
    return output_video_file

with gr.Blocks() as demo:
    gr.Markdown("Start typing below and then click **Run** to see the output.")
    with gr.Column():
        video_file_input = gr.Text(label="Upload Video url")
        clip_type = gr.Dropdown(["dub", "sub"], label="Clip Type")
        parameters = gr.Text()
        btn = gr.Button("create")
        video_file_output = gr.Video(label="result: ")
        btn.click(fn=main, inputs=[video_file_input, clip_type, parameters], outputs=video_file_output, server_name="0.0.0.0")
"""    with gr.Row():
        vid_out = gr.Video()
        srt_file = gr.File()
        btn2 = gr.Button("transcribe")
        gr.on(
            triggers=[btn2.click],
            fn=write_google,
            inputs=out,
        ).then(video_edit, [out, video_path_output, audio_path_output], outputs=[vid_out, srt_file])"""


demo.launch(debug=True)
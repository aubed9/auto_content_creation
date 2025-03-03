from moviepy import *
import pysrt



def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

def create_subtitle_clips(subtitles, videosize, fontsize, font, color, debug):
    subtitle_clips = []
    color_clips=[]
    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start) # Add 2 seconds offset
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time
        video_width, video_height = videosize
        max_width = video_width * 0.8
        max_height = video_height * 0.2
        #reshaped_text = arabic_reshaper.reshape(subtitle.text)
        #bidi_text = get_display(reshaped_text)
        text_clip = TextClip(font, subtitle.text, font_size=fontsize, size=(int(video_width * 0.8), int(video_height * 0.2)) ,text_align="right" ,color=color, method='caption').with_start(start_time).with_duration(duration)
        #myclip = ColorClip(size=(int(video_width * 0.8), int(video_height * 0.2)) , color=(225, 0, 0)).with_opacity(0.2).with_start(start_time).with_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height * 0.68
        text_position = (subtitle_x_position, subtitle_y_position)
        subtitle_clips.append(text_clip.with_position(text_position))
        #color_clips.append(myclip.with_position(text_position))
    return subtitle_clips

def video_edit(srt, input_video, color, font, input_audio= "audio.mp3"):
    print(input_video)
    input_video_name = input_video.split(".mp4")[0]
    video = VideoFileClip(input_video)
    audio = AudioFileClip(input_audio)
    video = video.with_audio(audio)
    print(video)
    output_video_file = input_video_name + '_subtitled' + ".mp4"
    subtitles = pysrt.open(srt, encoding="utf-8")
    subtitle_clips = create_subtitle_clips(subtitles, video.size, 32, f'{font}.ttf', color, False)
    final_video = CompositeVideoClip([video]+ subtitle_clips)
    final_video.write_videofile(output_video_file, codec="libx264", audio_codec="aac", logger=None, preset = "faster", fps=24)
    print('final')
    video.close()
    audio.close()
    return output_video_file

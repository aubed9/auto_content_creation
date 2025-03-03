from faster_whisper import WhisperModel
import math


def word_level_transcribe(audio, max_segment_duration=2.0):  # Set your desired max duration here
    model = WhisperModel("tiny", device="cpu")
    segments, info = model.transcribe(audio, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=1500), word_timestamps=True, log_progress=True)
    segments = list(segments)  # The transcription will actually run here.
    wordlevel_info = []
    for segment in segments:
        for word in segment.words:
          print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
          wordlevel_info.append({'word':word.word,'start':word.start,'end':word.end})
    return wordlevel_info

def create_subtitles(wordlevel_info):
    punctuation_marks = {'.', '!', '?', ',', ';', ':', '—', '-', '。', '！', '？'}  # Add/remove punctuation as needed
    subtitles = []
    line = []

    for word_data in wordlevel_info:
        line.append(word_data)
        current_word = word_data['word']

        # Check if current word ends with punctuation or line reached 5 words
        ends_with_punct = current_word and (current_word[-1] in punctuation_marks)

        if ends_with_punct or len(line) == 5:
            # Create a new subtitle segment
            subtitle = {
                "word": " ".join(item["word"] for item in line),
                "start": line[0]["start"],
                "end": line[-1]["end"],
                "textcontents": line.copy()
            }
            subtitles.append(subtitle)
            line = []

    # Add remaining words if any
    if line:
        subtitle = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line.copy()
        }
        subtitles.append(subtitle)

    # Remove gaps between segments by extending the previous segment's end time
    for i in range(1, len(subtitles)):
        prev_subtitle = subtitles[i - 1]
        current_subtitle = subtitles[i]

        # Extend the previous segment's end time to the start of the current segment
        prev_subtitle["end"] = current_subtitle["start"]

    return subtitles

def format_time(seconds):
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"
    return formatted_time

def generate_subtitle_file(language, segments, input_video_name):
    subtitle_file = f"sub-{input_video_name}.{language}.srt"
    text = ""
    for index, segment in enumerate(segments):
        segment_start = format_time(segment['start'])
        segment_end = format_time(segment['end'])
        text += f"{str(index+1)} \n"
        text += f"{segment_start} --> {segment_end} \n"
        text += f"{segment['word']} \n"
        text += "\n"
    f = open(subtitle_file, "w", encoding='utf8')
    f.write(text)
    f.close()
    return subtitle_file

def split_srt_file(input_file, max_chars=3000):
    # Read the contents of the SRT file
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
    file.close()

    # Split the content into individual subtitles
    subtitles = content.strip().split('\n\n')

    # Prepare to write the split files
    output_files = []
    current_file_content = ''
    current_file_index = 1

    for subtitle in subtitles:
        # Check if adding this subtitle would exceed the character limit
        if len(current_file_content) + len(subtitle) + 2 > max_chars:  # +2 for \n\n
            # Write the current file
            output_file_name = f'split_{current_file_index}.srt'
            with open(output_file_name, 'w', encoding='utf-8') as output_file:
                output_file.write(current_file_content.strip())
            output_files.append(output_file_name)

            # Prepare for the next file
            current_file_index += 1
            current_file_content = subtitle + '\n\n'
        else:
            # If it fits, add the subtitle
            current_file_content += subtitle + '\n\n'

    # Write any remaining content to a new SRT file
    if current_file_content:
        output_file_name = f'split_{current_file_index}.srt'
        with open(output_file_name, 'w', encoding='utf-8') as output_file:
            output_file.write(current_file_content.strip())
        output_files.append(output_file_name)

    return output_files

def transcribe(mp3_file):

    print("transcribe")
    wordlevel_info=word_level_transcribe(mp3_file)
    subtitles = create_subtitles(wordlevel_info)
    subtitle_file = generate_subtitle_file('fa', subtitles, 'video_subtitled')
    srt_list = split_srt_file(subtitle_file)
    return srt_list
import os

import docx
from PyPDF2 import PdfReader
from moviepy.video.io.VideoFileClip import VideoFileClip
import speech_recognition as sr


async def save_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = 'extracted_audio.mp3'
    video.audio.write_audiofile(audio_path)
    video.close()
    os.remove(video_path)
    return audio_path


def pdf_reader(file):
    reader = PdfReader(file)
    page = reader.pages[0]
    text = page.extract_text()
    return text


def word_writer(dock_file, pdf_file):
    doc = docx.Document()
    doc.add_paragraph(pdf_reader(pdf_file))
    doc.save(dock_file)
    return doc


def recognize_speech(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language='uz-UZ')
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Sorry, there was an error while processing the audio."



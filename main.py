import os

import pytesseract
import requests
from PIL import Image
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor

from removeBackground import remove_background
from utils import save_audio, word_writer, recognize_speech

API_TOKEN = '5915305402:AAEepx05lktT-dotxZ1Rx1V5jB9XAlJCCxg'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    msg = "Botimizga xush kelibsiz! \n" \
          "bizning botimiz funksiyalarini bilish \n" \
          "uchun /help buyrug'ini bering \n" \
          "admin: @developer2006"
    await message.answer(msg)


@dp.message_handler(commands=['help'])
async def start_handler(message: types.Message):
    msg = "Botga telegramdagi yumaloq videoni tashlang va sizga 'mp4' ya'ni tortburchak video qilib qaytaradi. \n\n" \
          "Botga ozingiz yoqtirgan videoni tashlang, sizga shu videoni musiqasini qaytaradi. \n\n" \
          "Botga ovozli xabar yuboring va sizga matn formatta qaytaradi. \n\n" \
          "Botga 'PDF' file yuboring, sizga word (docx) formatda qaytaradi. \n\n" \
          "Botga rasm yuboring va u sizga rasmdagi matnlarni qaytaradi. \n\n" \
          "Botga rasm yuboring va u sizga rasmning orqa fonini olib tashlaydi. \n\n" \
          "Botga instagram yoki tiktokdan video silkasini tashlang, sizga yuqori formatda video qaytaradi, \n\n" \
          "Botni ishlatish uchun shunchaki tapadagi narsalarni tashlang."
    await message.answer(msg)


@dp.message_handler(content_types=types.ContentTypes.VIDEO_NOTE)
async def video_note(message: types.Message):
    video = message.video_note
    file_path = await bot.get_file(video.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)
    local_file = f"{video.file_id}.mp4"
    with open(local_file, "wb") as f:
        f.write(downloaded_file.read())
    with open(local_file, "rb") as video_file:
        await message.answer_video(video=video_file)
    os.remove(local_file)


@dp.message_handler(content_types=types.ContentTypes.VIDEO)
async def handle_video(message: types.Message):
    video = message.video
    file_path = await bot.get_file(video.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)
    local_file_path = f"{video.file_id}.mp4"

    with open(local_file_path, "wb") as f:
        f.write(downloaded_file.read())

    if local_file_path:
        audio_path = await save_audio(local_file_path)
        with open(audio_path, "rb") as audio_file:
            await message.answer_audio(audio=audio_file)
            os.remove(audio_path)

    await message.answer("Video downloaded and deleted successfully.")


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def handle_voice_message(message: types.Message):
    file_id = message.voice.file_id

    voice_message = await bot.get_file(file_id)
    voice_path = os.path.join(f"voice_{file_id}.wav")
    await voice_message.download(voice_path)
    try:
        recognized_text = recognize_speech(voice_path)

        await message.reply(f"Recognized Text: {recognized_text}")
    except Exception as e:
        await message.reply(e)
    os.remove(voice_path)


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def download_document(message: types.Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_extension = os.path.splitext(file_path)[-1].lower()

    if file_extension != ".pdf":
        await message.reply("Iltimos, faqat PDF formatidagi fayllarni yuboring.")
        return
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    local_pdf_file_path = f"{file_id}.pdf"
    local_docx_file_path = f"{file_id}.docx"

    with open(local_pdf_file_path, 'wb') as f:
        response = requests.get(file_url)
        f.write(response.content)
    await message.reply("Document downloaded successfully!")
    word_writer(local_docx_file_path, local_pdf_file_path)

    with open(local_docx_file_path, 'rb') as f:
        await message.answer_document(document=f, caption=message.caption)

    os.remove(local_pdf_file_path)
    os.remove(local_docx_file_path)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def photo(message: types.Message):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(f'{file_id}.jpg', 'wb') as f:
        f.write(downloaded_file.read())
    img = Image.open(f"{file_id}.jpg")
    pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract'
    text = pytesseract.image_to_string(img)
    if text.strip():
        await message.reply(text)
    else:
        await message.reply("No text found in the image.")
    if os.path.exists(f'{file_id}.jpg'):
        os.remove(f'{file_id}.jpg')

    image_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"

    await message.answer(image_url)
    new_photo = await remove_background(image_url)
    await message.reply_photo(new_photo)


@dp.message_handler(Text(startswith="https://www.instagram.com/"))
async def get_insta_video(message: types.Message):
    await message.answer("yuklanmoqda..")
    url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"

    querystring = {"url": f"{message.text}"}

    headers = {
        "X-RapidAPI-Key": "6f01dc13e8msh46da8b6a8249169p1b5857jsn3dfb408ca3e5",
        "X-RapidAPI-Host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    down_video = response.json()['media']
    await message.answer("Uzatilmoqda..")
    await message.answer_video(video=down_video)


@dp.message_handler(Text(startswith="https://www.tiktok.com"))
async def get_insta_video(message: types.Message):
    await message.answer("yuklanmoqda..")
    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/vid/index"

    querystring = {
        "url": f"{message.text}"}

    headers = {
        "X-RapidAPI-Key": "6f01dc13e8msh46da8b6a8249169p1b5857jsn3dfb408ca3e5",
        "X-RapidAPI-Host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    down_video = response.json()['video'][0]
    await message.answer("uzatilmoqda..")
    await message.answer_video(video=down_video)


@dp.message_handler()
async def all_message(message: types.Message):
    await message.reply("/help tugmasini bosing va botni ishlating")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

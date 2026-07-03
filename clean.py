import os
import sys
import asyncio
from telethon import TelegramClient

# جلب الإعدادات السرية
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = int(os.environ['CHAT_ID'])
VIDEO_URL = os.environ['VIDEO_URL']
YT_COOKIES = os.environ.get('YT_COOKIES', '')

async def main():
    # 🍪 إعداد الكوكيز
    if YT_COOKIES.strip():
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            f.write(YT_COOKIES)
        cookie_arg = "--cookies cookies.txt"
    else:
        cookie_arg = ""

    print("📥 جاري تحميل الفيديو بجودة 720p...")
    dl_cmd = (
        f'yt-dlp {cookie_arg} --rm-cache-dir --force-ipv4 '
        f'--extractor-args "youtube:player_client=android,ios,web" '
        f'--js-runtimes node --remote-components ejs:github '
        f'-f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best" '
        f'--merge-output-format mp4 "{VIDEO_URL}" -o input_video.mp4'
    )
    os.system(dl_cmd)
    
    # نقطة فحص 1
    if not os.path.exists('input_video.mp4'):
        print("❌ فشل التحميل! لم يتم العثور على ملف الفيديو.")
        return

    print("🧠 جاري عزل الموسيقى (باستخدام نموذج mdx_extra_q الخفيف والسريع)...")
    # استخدام النموذج المخفف لتفادي انهيار الرام في سيرفرات غيت هاب
    os.system('python -m demucs.separate -n mdx_extra_q --two-stems=vocals input_video.mp4')
    
    # مسار النموذج المخفف يختلف عن القديم
    vocals_path = 'separated/mdx_extra_q/input_video/vocals.wav'
    
    # نقطة فحص 2
    if not os.path.exists(vocals_path):
        print("❌ فشل عزل الصوت! (إما أن السيرفر أوقف العملية أو لا يوجد صوت بشري في الفيديو).")
        return

    print("🎬 جاري دمج الصوت النظيف...")
    os.system(f'ffmpeg -y -i input_video.mp4 -i {vocals_path} -c:v copy -map 0:v:0 -map 1:a:0 output_clean.mp4')
    
    # نقطة فحص 3
    if not os.path.exists('output_clean.mp4'):
        print("❌ فشل دمج الفيديو النهائي!")
        return

    print("📤 جاري إرسال الفيديو إلى تليجرام...")
    client = TelegramClient('github_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    await client.send_file(CHAT_ID, 'output_clean.mp4', caption="✨ تم تنظيف الفيديو بنجاح عبر GitHub Actions!")
    await client.disconnect()
    print("✅ تم كل شيء بنجاح!")

if __name__ == '__main__':
    asyncio.run(main())

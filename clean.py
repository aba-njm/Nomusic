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
    # 🍪 إنشاء ملف الكوكيز بأمان
    if YT_COOKIES.strip():
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            f.write(YT_COOKIES)
        print("🍪 تم حفظ ملف الكوكيز بأمان.")
        cookie_arg = "--cookies cookies.txt"
    else:
        cookie_arg = ""

    print("📥 جاري تحميل الفيديو بجودة 720p...")
    
    # ⚡ تحديث: إضافة أوامر التمويه (أندرويد/آيفون) وفرض IPv4 لتجاوز الخطأ 403
    dl_cmd = (
        f'yt-dlp {cookie_arg} --rm-cache-dir --force-ipv4 '
        f'--extractor-args "youtube:player_client=android,ios,web" '
        f'--js-runtimes node --remote-components ejs:github '
        f'-f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best" '
        f'--merge-output-format mp4 "{VIDEO_URL}" -o input_video.mp4'
    )
    os.system(dl_cmd)
    
    if not os.path.exists('input_video.mp4'):
        print("❌ فشل التحميل!")
        return

    print("🧠 جاري عزل الموسيقى عبر Demucs...")
    os.system('python -m demucs.separate --two-stems=vocals input_video.mp4')
    
    print("🎬 جاري دمج الصوت النظيف...")
    os.system('ffmpeg -y -i input_video.mp4 -i separated/htdemucs/input_video/vocals.wav -c:v copy -map 0:v:0 -map 1:a:0 output_clean.mp4')
    
    print("📤 جاري إرسال الفيديو إلى تليجرام...")
    client = TelegramClient('github_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    await client.send_file(CHAT_ID, 'output_clean.mp4', caption="✨ تم تنظيف الفيديو بنجاح عبر GitHub Actions!")
    await client.disconnect()
    print("✅ تم كل شيء بنجاح!")

if __name__ == '__main__':
    asyncio.run(main())

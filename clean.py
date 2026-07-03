import os
import sys
import asyncio
from telethon import TelegramClient

# جلب الإعدادات السرية من بيئة التشغيل لضمان الأمان
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = int(os.environ['CHAT_ID'])  # معرف حسابك الشخصي على تليجرام لتستلم الفيديو عليه
VIDEO_URL = os.environ['VIDEO_URL']

async def main():
    print("📥 جاري تحميل الفيديو بجودة 720p...")
    os.system(f'yt-dlp -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best" --merge-output-format mp4 "{VIDEO_URL}" -o input_video.mp4')
    
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
    
    # إرسال الملف مباشرة إلى حسابك الشخصي
    await client.send_file(CHAT_ID, 'output_clean.mp4', caption="✨ تم تنظيف الفيديو بنجاح عبر GitHub Actions!")
    await client.disconnect()
    print("✅ تم كل شيء بنجاح!")

if __name__ == '__main__':
    asyncio.run(main())

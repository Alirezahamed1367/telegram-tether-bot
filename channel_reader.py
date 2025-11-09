"""
اسکریپت کمکی برای خواندن کانال عمومی تلگرام
این اسکریپت از Telethon استفاده می‌کند که می‌تواند از کانال‌های عمومی بخواند
"""

# نیاز به نصب: pip install telethon

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import os
from dotenv import load_dotenv

load_dotenv()

# باید از https://my.telegram.org دریافت کنید
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

def read_channel_message(channel_username='tetherprice_toman'):
    """
    خواندن آخرین پیام از کانال عمومی
    """
    with TelegramClient('session', API_ID, API_HASH) as client:
        # دریافت کانال
        channel = client.get_entity(channel_username)
        
        # دریافت آخرین پیام‌ها
        messages = client(GetHistoryRequest(
            peer=channel,
            limit=1,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        
        if messages.messages:
            return messages.messages[0].message
        
        return None

if __name__ == '__main__':
    # تست
    message = read_channel_message()
    print("آخرین پیام کانال:")
    print(message)

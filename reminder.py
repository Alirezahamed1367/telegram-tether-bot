#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت یادآوری برای درخواست نرخ یوآن
این اسکریپت از ساعت 10:45 صبح شروع به ارسال یادآوری می‌کند
"""

import os
import asyncio
import logging
from datetime import datetime

import pytz
from dotenv import load_dotenv
from telegram import Bot

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Tehran'))


async def send_reminder():
    """
    ارسال پیام یادآوری برای دریافت نرخ یوآن
    """
    try:
        if not all([BOT_TOKEN, TARGET_GROUP_ID]):
            logger.error("❌ تنظیمات ناقص است!")
            return
        
        # زمان فعلی
        current_time = datetime.now(TIMEZONE).strftime("%H:%M")
        
        # ایجاد پیام یادآوری
        message = f"""
🔔 **یادآوری: ارسال نرخ یوآن**

⏰ زمان: {current_time}

لطفاً نرخ تبدیل تتر به یوآن را از طریق دستور /setrate ارسال کنید.

مثال:
`/setrate 71.2`

⚠️ این یادآوری تا دریافت نرخ جدید ادامه خواهد داشت.
"""
        
        # ارسال به گروه
        bot = Bot(BOT_TOKEN)
        await bot.send_message(
            chat_id=TARGET_GROUP_ID, 
            text=message,
            parse_mode='Markdown'
        )
        
        logger.info("✅ یادآوری ارسال شد!")
        print("\n" + "="*50)
        print("✅ یادآوری ارسال شد!")
        print("="*50)
        print(message)
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ خطا در ارسال یادآوری: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(send_reminder())

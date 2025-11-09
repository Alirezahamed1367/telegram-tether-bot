#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت خودکار برای خواندن کانال عمومی با استفاده از Telethon
این اسکریپت با حساب کاربری شما وارد می‌شود و می‌تواند از کانال‌های عمومی بخواند
"""

import os
import asyncio
import logging
from datetime import datetime

import pytz
from dotenv import load_dotenv
from telethon import TelegramClient
from telegram import Bot
from telegram.ext import Application

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات Telethon (برای خواندن کانال عمومی)
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

# تنظیمات Bot (برای ارسال پیام)
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL', 'tetherprice_toman')
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Tehran'))

# Import از bot.py
try:
    from bot import bot_instance, TetherBot
except ImportError:
    logger.error("نمی‌توان bot.py را import کرد")
    bot_instance = None


async def read_channel_with_telethon(channel_username: str) -> str:
    """
    خواندن آخرین پیام از کانال عمومی با استفاده از Telethon
    """
    try:
        # ایجاد کلاینت Telethon
        client = TelegramClient('user_session', API_ID, API_HASH)
        await client.start(phone=PHONE)
        
        logger.info(f"وارد شدن با حساب کاربری و خواندن از @{channel_username}...")
        
        # دریافت کانال
        channel = await client.get_entity(channel_username)
        
        # دریافت آخرین پیام
        messages = await client.get_messages(channel, limit=1)
        
        if messages and messages[0].text:
            text = messages[0].text
            logger.info(f"پیام دریافت شد از @{channel_username}")
            await client.disconnect()
            return text
        
        await client.disconnect()
        logger.warning("پیامی یافت نشد")
        return None
        
    except Exception as e:
        logger.error(f"خطا در خواندن کانال با Telethon: {e}")
        return None


async def main():
    """
    تابع اصلی: خواندن از کانال و ارسال به گروه
    """
    try:
        # بررسی تنظیمات
        if not all([API_ID, API_HASH, PHONE, BOT_TOKEN, TARGET_GROUP_ID]):
            logger.error("❌ تنظیمات ناقص است! لطفاً .env را کامل کنید")
            return
        
        # بررسی نرخ یوآن
        if not bot_instance or not bot_instance.yuan_rate:
            logger.error("❌ نرخ یوآن تنظیم نشده است!")
            return
        
        logger.info("🔄 شروع فرآیند خودکار...")
        
        # خواندن از کانال عمومی با Telethon
        text = await read_channel_with_telethon(SOURCE_CHANNEL)
        
        if not text:
            logger.error("❌ نتوانستیم از کانال بخوانیم")
            return
        
        # استخراج قیمت تتر
        tether_price = bot_instance.extract_tether_price(text)
        if not tether_price:
            logger.error("❌ قیمت تتر در پیام یافت نشد")
            return
        
        logger.info(f"✅ قیمت تتر: {tether_price:,} ریال")
        
        # محاسبه نرخ مبنا
        base_rate = bot_instance.calculate_base_rate(tether_price)
        if not base_rate:
            logger.error("❌ خطا در محاسبه نرخ")
            return
        
        # بررسی شرط کاهش نرخ
        if bot_instance.last_calculated_rate and base_rate < bot_instance.last_calculated_rate:
            logger.warning(
                f"⚠️ نرخ جدید ({base_rate:,.0f}) کمتر از نرخ قبلی "
                f"({bot_instance.last_calculated_rate:,.0f}) است. "
                f"از نرخ قبلی استفاده می‌شود."
            )
            base_rate = bot_instance.last_calculated_rate
        else:
            bot_instance.last_calculated_rate = base_rate
            bot_instance.save_data()
        
        logger.info(f"✅ نرخ مبنا: {base_rate:,.0f} تومان")
        
        # ایجاد پیام نهایی
        message = bot_instance.format_message(base_rate)
        
        # ارسال به گروه
        bot = Bot(BOT_TOKEN)
        await bot.send_message(chat_id=TARGET_GROUP_ID, text=message)
        
        logger.info("✅ پیام با موفقیت ارسال شد!")
        print("\n" + "="*50)
        print("✅ عملیات موفق بود!")
        print("="*50)
        print(message)
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ خطا در فرآیند: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())

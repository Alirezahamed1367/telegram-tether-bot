#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات تلگرام برای محاسبه و ارسال نرخ یوآن
این ربات هر ساعت از 11 صبح تا 7 شب نرخ تتر را از کانال عمومی دریافت کرده
و با استفاده از نرخ یوآن، قیمت نهایی را محاسبه و ارسال می‌کند.
"""

import os
import re
import json
import math
import logging
from datetime import datetime
from typing import Optional

# تنظیم timezone برای سازگاری با Python 3.13
os.environ.setdefault('TZ', 'UTC')

import pytz
import jdatetime  # type: ignore
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL', 'tetherprice_toman')
PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID')  # کانال میانی برای خواندن
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Tehran'))
DATA_FILE = 'data.json'


class TetherBot:
    """کلاس اصلی ربات محاسبه نرخ یوآن"""
    
    def __init__(self):
        self.yuan_rate: Optional[float] = None
        self.last_calculated_rate: Optional[float] = None
        self.load_data()
    
    def load_data(self):
        """بارگذاری داده‌های ذخیره شده"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.yuan_rate = data.get('yuan_rate')
                    self.last_calculated_rate = data.get('last_calculated_rate')
                    logger.info(f"داده‌ها بارگذاری شد - نرخ یوآن: {self.yuan_rate}")
        except Exception as e:
            logger.error(f"خطا در بارگذاری داده‌ها: {e}")
    
    def save_data(self):
        """ذخیره داده‌ها"""
        try:
            data = {
                'yuan_rate': self.yuan_rate,
                'last_calculated_rate': self.last_calculated_rate,
                'last_update': datetime.now(TIMEZONE).isoformat()
            }
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("داده‌ها ذخیره شد")
        except Exception as e:
            logger.error(f"خطا در ذخیره داده‌ها: {e}")
    
    def extract_tether_price(self, text: str) -> Optional[int]:
        """
        استخراج قیمت فروش تتر از متن کانال
        
        نمونه متن:
        💵 قیمت لحظه‌ای تتر
        🟢 خرید تتر : 1084970 ریال
        🔴 فروش تتر : 1084980 ریال
        """
        try:
            # جستجوی الگوی "فروش تتر : عدد ریال"
            pattern = r'فروش تتر\s*[:：]\s*([\d,]+)\s*ریال'
            match = re.search(pattern, text)
            
            if match:
                price_str = match.group(1).replace(',', '')
                price = int(price_str)
                logger.info(f"قیمت تتر استخراج شد: {price:,} ریال")
                return price
            
            logger.warning("قیمت فروش تتر در متن یافت نشد")
            return None
        except Exception as e:
            logger.error(f"خطا در استخراج قیمت تتر: {e}")
            return None
    
    def calculate_base_rate(self, tether_price_rial: int) -> Optional[float]:
        """
        محاسبه نرخ مبنا
        
        مراحل:
        1. تبدیل ریال به تومان (تقسیم بر 10)
        2. تقسیم بر نرخ یوآن
        3. رند کردن به بالا (به نزدیکترین 10)
        """
        if not self.yuan_rate:
            logger.error("نرخ یوآن تنظیم نشده است!")
            return None
        
        try:
            # تبدیل ریال به تومان
            tether_price_toman = tether_price_rial / 10
            
            # محاسبه نرخ پایه
            base_rate = tether_price_toman / self.yuan_rate
            
            # رند کردن به بالا (به نزدیکترین 10)
            rounded_rate = math.ceil(base_rate / 10) * 10
            
            logger.info(
                f"محاسبه: {tether_price_toman:,.0f} تومان ÷ {self.yuan_rate} = "
                f"{base_rate:,.2f} → رند شده: {rounded_rate:,.0f}"
            )
            
            return float(rounded_rate)
        except Exception as e:
            logger.error(f"خطا در محاسبه نرخ مبنا: {e}")
            return None
    
    def format_message(self, base_rate: float) -> str:
        """
        ایجاد متن پیام نهایی با تاریخ شمسی و میلادی
        """
        # زمان فعلی
        now = datetime.now(TIMEZONE)
        current_time = now.strftime('%H:%M')
        
        # تاریخ شمسی
        j_date = jdatetime.datetime.now()
        persian_date = j_date.strftime('%Y/%m/%d')
        persian_day_name = j_date.strftime('%A')  # نام روز به فارسی
        
        # تاریخ میلادی
        gregorian_date = now.strftime('%Y/%m/%d')
        gregorian_day_name = now.strftime('%A')  # نام روز
        
        # ترجمه نام روزهای میلادی به فارسی
        day_translation = {
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج‌شنبه',
            'Friday': 'جمعه'
        }
        gregorian_day_name_fa = day_translation.get(gregorian_day_name, gregorian_day_name)
        
        return f"""⏳ به‌روزرسانی نرخ یوآن
📅 تاریخ شمسی: {persian_date} ({persian_day_name})
📆 تاریخ میلادی: {gregorian_date} ({gregorian_day_name_fa})
🕐 ساعت: {current_time}

1️⃣ خرید تا 5 هزار یوآن : {base_rate + 80:,.0f}
2️⃣ خرید تا 10 هزار یوآن : {base_rate + 70:,.0f}
3️⃣ خرید بالای 10 هزار یوآن : {base_rate + 60:,.0f}"""


# ایجاد نمونه از ربات
bot_instance = TetherBot()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    await update.message.reply_text(
        "سلام! 👋\n\n"
        "من ربات محاسبه نرخ یوآن هستم.\n\n"
        "دستورات موجود:\n"
        "/start - شروع و راهنما\n"
        "/setrate <نرخ> - تنظیم نرخ یوآن (مثال: /setrate 7.12)\n"
        "/getrate - نمایش نرخ فعلی یوآن\n"
        "/update - به‌روزرسانی دستی نرخ\n"
        "/status - نمایش وضعیت ربات"
    )


async def set_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم نرخ یوآن - دستور /setrate"""
    try:
        if not context.args or len(context.args) != 1:
            await update.message.reply_text(
                "❌ فرمت نادرست!\n"
                "مثال: /setrate 7.12"
            )
            return
        
        rate = float(context.args[0])
        
        if rate <= 0:
            await update.message.reply_text("❌ نرخ باید عددی مثبت باشد!")
            return
        
        bot_instance.yuan_rate = rate
        bot_instance.save_data()
        
        await update.message.reply_text(
            f"✅ نرخ یوآن به {rate} تنظیم شد.\n"
            f"🕐 زمان: {datetime.now(TIMEZONE).strftime('%Y/%m/%d - %H:%M')}"
        )
        
        logger.info(f"نرخ یوآن توسط کاربر به {rate} تنظیم شد")
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
    except Exception as e:
        logger.error(f"خطا در تنظیم نرخ: {e}")
        await update.message.reply_text(f"❌ خطا در تنظیم نرخ: {str(e)}")


async def get_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش نرخ فعلی یوآن - دستور /getrate"""
    if bot_instance.yuan_rate:
        await update.message.reply_text(
            f"💱 نرخ فعلی یوآن: {bot_instance.yuan_rate}\n"
            f"📊 آخرین نرخ محاسبه شده: "
            f"{bot_instance.last_calculated_rate:,.0f} تومان"
            if bot_instance.last_calculated_rate else ""
        )
    else:
        await update.message.reply_text(
            "❌ نرخ یوآن هنوز تنظیم نشده است.\n"
            "لطفاً با دستور /setrate نرخ را تنظیم کنید."
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش وضعیت ربات - دستور /status"""
    status_msg = f"""📊 وضعیت ربات:

💱 نرخ یوآن: {bot_instance.yuan_rate if bot_instance.yuan_rate else '❌ تنظیم نشده'}
📈 آخرین نرخ محاسبه شده: {f"{bot_instance.last_calculated_rate:,.0f} تومان" if bot_instance.last_calculated_rate else '❌ محاسبه نشده'}
📢 کانال منبع: @{SOURCE_CHANNEL}
🎯 گروه مقصد: {TARGET_GROUP_ID if TARGET_GROUP_ID else '❌ تنظیم نشده'}
🕐 زمان فعلی: {datetime.now(TIMEZONE).strftime('%Y/%m/%d - %H:%M:%S')}
"""
    await update.message.reply_text(status_msg)


async def update_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """به‌روزرسانی دستی نرخ - دستور /update"""
    await update.message.reply_text("🔄 در حال به‌روزرسانی نرخ...")
    
    try:
        result = await fetch_and_calculate(context.application)
        await update.message.reply_text(result)
    except Exception as e:
        logger.error(f"خطا در به‌روزرسانی دستی: {e}")
        await update.message.reply_text(f"❌ خطا در به‌روزرسانی: {str(e)}")


async def fetch_and_calculate(application: Application) -> str:
    """
    دریافت قیمت از کانال، محاسبه و ارسال پیام
    این تابع توسط scheduler هر ساعت فراخوانی می‌شود
    """
    try:
        # بررسی تنظیم نرخ یوآن
        if not bot_instance.yuan_rate:
            error_msg = "❌ نرخ یوآن تنظیم نشده است! لطفاً با دستور /setrate نرخ را تنظیم کنید."
            logger.error(error_msg)
            return error_msg
        
        text = None
        
        # اگر کانال میانی تنظیم شده، از آن استفاده کن
        if PRIVATE_CHANNEL_ID:
            logger.info(f"در حال دریافت پیام از کانال میانی {PRIVATE_CHANNEL_ID}...")
            try:
                # دریافت آخرین پیام از کانال میانی
                chat = await application.bot.get_chat(PRIVATE_CHANNEL_ID)
                
                # دریافت updates و پیدا کردن آخرین پیام
                updates = await application.bot.get_updates(limit=100)
                
                for upd in reversed(updates):
                    if (upd.channel_post and 
                        str(upd.channel_post.chat.id) == str(PRIVATE_CHANNEL_ID)):
                        text = upd.channel_post.text
                        logger.info("پیام از کانال میانی دریافت شد")
                        break
                
                if not text:
                    error_msg = f"❌ پیامی در کانال میانی {PRIVATE_CHANNEL_ID} یافت نشد."
                    logger.error(error_msg)
                    return error_msg
                    
            except Exception as e:
                logger.error(f"خطا در دریافت از کانال میانی: {e}")
                error_msg = (
                    f"❌ خطا در دریافت از کانال میانی.\n"
                    f"مطمئن شوید:\n"
                    f"1. ربات عضو کانال است\n"
                    f"2. PRIVATE_CHANNEL_ID صحیح است\n"
                    f"3. پیامی در کانال موجود است\n\n"
                    f"خطا: {str(e)}"
                )
                return error_msg
        
        else:
            # تلاش برای خواندن مستقیم از کانال عمومی (ممکن است کار نکند)
            channel_username = f"@{SOURCE_CHANNEL}"
            logger.info(f"در حال دریافت پیام از کانال عمومی {channel_username}...")
            
            try:
                chat = await application.bot.get_chat(channel_username)
                updates = await application.bot.get_updates(limit=100)
                
                channel_message = None
                for upd in reversed(updates):
                    if (upd.channel_post and 
                        upd.channel_post.chat.username and 
                        upd.channel_post.chat.username.lower() == SOURCE_CHANNEL.lower()):
                        channel_message = upd.channel_post
                        break
                
                if not channel_message or not channel_message.text:
                    error_msg = (
                        f"❌ پیامی از کانال {channel_username} یافت نشد.\n\n"
                        f"💡 راه حل: یک کانال میانی بسازید و PRIVATE_CHANNEL_ID را تنظیم کنید.\n"
                        f"📖 راهنما: ADVANCED.md"
                    )
                    logger.error(error_msg)
                    return error_msg
                
                text = channel_message.text
                
            except Exception as e:
                logger.error(f"خطا در دریافت پیام از کانال عمومی: {e}")
                error_msg = (
                    f"⚠️ نمی‌توان مستقیماً از کانال عمومی خواند.\n\n"
                    f"💡 راه حل:\n"
                    f"1. یک کانال خصوصی بسازید\n"
                    f"2. ربات را به آن اضافه و ادمین کنید\n"
                    f"3. پیام‌ها را به آنجا forward کنید\n"
                    f"4. PRIVATE_CHANNEL_ID را در .env تنظیم کنید\n\n"
                    f"📖 جزئیات بیشتر: ADVANCED.md\n\n"
                    f"خطا: {str(e)}"
                )
                return error_msg
        
        # استخراج قیمت تتر
        tether_price = bot_instance.extract_tether_price(text)
        if not tether_price:
            error_msg = "❌ قیمت تتر در پیام کانال یافت نشد!"
            logger.error(error_msg)
            return error_msg
        
        # محاسبه نرخ مبنا
        base_rate = bot_instance.calculate_base_rate(tether_price)
        if not base_rate:
            error_msg = "❌ خطا در محاسبه نرخ مبنا!"
            logger.error(error_msg)
            return error_msg
        
        # بررسی شرط: اگر نرخ جدید کمتر از نرخ قبلی بود، از نرخ قبلی استفاده شود
        if bot_instance.last_calculated_rate and base_rate < bot_instance.last_calculated_rate:
            logger.warning(
                f"نرخ جدید ({base_rate:,.0f}) کمتر از نرخ قبلی "
                f"({bot_instance.last_calculated_rate:,.0f}) است. "
                f"از نرخ قبلی استفاده می‌شود."
            )
            base_rate = bot_instance.last_calculated_rate
        else:
            # ذخیره نرخ جدید
            bot_instance.last_calculated_rate = base_rate
            bot_instance.save_data()
        
        # ایجاد پیام نهایی
        message = bot_instance.format_message(base_rate)
        
        # ارسال به گروه مقصد
        if TARGET_GROUP_ID:
            await application.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=message
            )
            logger.info(f"پیام با موفقیت به گروه {TARGET_GROUP_ID} ارسال شد")
            return f"✅ پیام با موفقیت ارسال شد!\n\n{message}"
        else:
            logger.warning("شناسه گروه مقصد تنظیم نشده است")
            return f"⚠️ گروه مقصد تنظیم نشده، اما محاسبه انجام شد:\n\n{message}"
        
    except Exception as e:
        error_msg = f"❌ خطا در فرآیند به‌روزرسانی: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


async def scheduled_update(context: ContextTypes.DEFAULT_TYPE):
    """تابع برنامه‌ریزی شده برای اجرای خودکار"""
    logger.info("شروع به‌روزرسانی برنامه‌ریزی شده...")
    result = await fetch_and_calculate(context.application)
    logger.info(f"نتیجه به‌روزرسانی: {result}")


def main():
    """تابع اصلی اجرای ربات"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN تنظیم نشده است!")
        print("❌ لطفاً فایل .env را با BOT_TOKEN مناسب ایجاد کنید.")
        return
    
    # ایجاد اپلیکیشن بدون JobQueue (برای سازگاری با Python 3.13)
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .job_queue(None)  # غیرفعال کردن JobQueue
        .build()
    )
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setrate", set_rate))
    application.add_handler(CommandHandler("getrate", get_rate))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("update", update_rate))
    
    logger.info("ربات شروع به کار کرد...")
    print("✅ ربات در حال اجراست. برای توقف از Ctrl+C استفاده کنید.")
    print("📝 دستورات موجود:")
    print("  /start - راهنما")
    print("  /setrate <نرخ> - تنظیم نرخ یوآن")
    print("  /getrate - نمایش نرخ فعلی")
    print("  /status - وضعیت ربات")
    print("  /update - به‌روزرسانی دستی")
    
    # اجرای ربات
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

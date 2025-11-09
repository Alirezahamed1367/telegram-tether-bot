#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست جامع برای بررسی تمام قابلیت‌های ربات
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

def print_section(title):
    """چاپ عنوان بخش"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def check_env_variables():
    """بررسی متغیرهای محیطی"""
    print_section("1️⃣  بررسی متغیرهای محیطی (.env)")
    
    required_vars = {
        'BOT_TOKEN': 'توکن ربات',
        'TARGET_GROUP_ID': 'شناسه گروه هدف',
        'TELEGRAM_API_ID': 'API ID تلگرام',
        'TELEGRAM_API_HASH': 'API Hash تلگرام',
        'TELEGRAM_PHONE': 'شماره تلفن'
    }
    
    all_ok = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # نمایش بخشی از مقدار برای امنیت
            if var == 'BOT_TOKEN':
                display = f"{value[:10]}...{value[-10:]}"
            elif var == 'TELEGRAM_API_HASH':
                display = f"{value[:8]}...{value[-4:]}"
            elif var == 'TELEGRAM_PHONE':
                display = f"{value[:4]}...{value[-4:]}"
            else:
                display = value
            
            print(f"✅ {var}: {display}")
        else:
            print(f"❌ {var}: وجود ندارد! ({description})")
            all_ok = False
    
    return all_ok

def check_files():
    """بررسی فایل‌های مورد نیاز"""
    print_section("2️⃣  بررسی فایل‌ها")
    
    required_files = {
        'bot.py': 'فایل اصلی ربات',
        'auto_fetcher.py': 'اسکریپت خواندن خودکار',
        'reminder.py': 'اسکریپت یادآوری',
        'requirements.txt': 'وابستگی‌های پایتون',
        '.env': 'فایل تنظیمات محیطی',
        'user_session.session': 'فایل session تلگرام'
    }
    
    all_ok = True
    for file, description in required_files.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: موجود است ({size:,} bytes) - {description}")
        else:
            print(f"❌ {file}: وجود ندارد! ({description})")
            all_ok = False
    
    return all_ok

async def test_bot_connection():
    """تست اتصال ربات به تلگرام"""
    print_section("3️⃣  تست اتصال ربات به تلگرام")
    
    try:
        from telegram import Bot
        bot_token = os.getenv('BOT_TOKEN')
        
        if not bot_token:
            print("❌ BOT_TOKEN تنظیم نشده است")
            return False
        
        bot = Bot(bot_token)
        me = await bot.get_me()
        
        print(f"✅ ربات متصل شد:")
        print(f"   نام: {me.first_name}")
        print(f"   یوزرنیم: @{me.username}")
        print(f"   شناسه: {me.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در اتصال ربات: {e}")
        return False

async def test_telethon_session():
    """تست session تلتون"""
    print_section("4️⃣  تست Telethon Session")
    
    try:
        from telethon import TelegramClient  # type: ignore
        
        api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        api_hash = os.getenv('TELEGRAM_API_HASH', '')
        phone = os.getenv('TELEGRAM_PHONE', '')
        
        if not all([api_id, api_hash, phone]):
            print("❌ تنظیمات Telethon ناقص است")
            return False
        
        client = TelegramClient('user_session', api_id, api_hash)
        await client.connect()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Telethon متصل شد:")
            print(f"   نام: {me.first_name} {me.last_name or ''}")
            print(f"   یوزرنیم: @{me.username or 'ندارد'}")
            print(f"   شناسه: {me.id}")
            await client.disconnect()
            return True
        else:
            print("❌ Session معتبر نیست - نیاز به ورود دوباره")
            await client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ خطا در Telethon: {e}")
        return False

async def test_group_access():
    """تست دسترسی به گروه"""
    print_section("5️⃣  تست دسترسی به گروه")
    
    try:
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        group_id = os.getenv('TARGET_GROUP_ID')
        
        if not bot_token or not group_id:
            print("❌ BOT_TOKEN یا TARGET_GROUP_ID تنظیم نشده")
            return False
        
        bot = Bot(bot_token)
        chat = await bot.get_chat(chat_id=group_id)
        
        print(f"✅ دسترسی به گروه:")
        print(f"   نام: {chat.title}")
        print(f"   نوع: {chat.type}")
        print(f"   شناسه: {chat.id}")
        
        # بررسی مجوزهای ربات
        member = await bot.get_chat_member(chat_id=group_id, user_id=(await bot.get_me()).id)
        print(f"   وضعیت ربات: {member.status}")
        
        if member.status in ['administrator', 'creator']:
            print("   ✅ ربات ادمین است")
        elif member.status == 'member':
            print("   ⚠️  ربات عضو عادی است (بهتر است ادمین باشد)")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در دسترسی به گروه: {e}")
        return False

async def test_channel_read():
    """تست خواندن از کانال"""
    print_section("6️⃣  تست خواندن از کانال @tetherprice_toman")
    
    try:
        from auto_fetcher import read_channel_with_telethon
        
        text = await read_channel_with_telethon('tetherprice_toman')
        
        if text:
            print(f"✅ پیام دریافت شد:")
            print(f"\n--- شروع پیام ---")
            print(text[:200] + "..." if len(text) > 200 else text)
            print(f"--- پایان پیام ---\n")
            print(f"   طول پیام: {len(text)} کاراکتر")
            return True
        else:
            print("❌ نتوانستیم از کانال بخوانیم")
            return False
            
    except Exception as e:
        print(f"❌ خطا در خواندن کانال: {e}")
        return False

async def test_bot_instance():
    """تست instance ربات"""
    print_section("7️⃣  تست Bot Instance و محاسبات")
    
    try:
        from bot import bot_instance
        
        if not bot_instance:
            print("❌ bot_instance موجود نیست")
            return False
        
        # بررسی نرخ یوآن
        if bot_instance.yuan_rate:
            print(f"✅ نرخ یوآن تنظیم شده: {bot_instance.yuan_rate}")
        else:
            print("⚠️  نرخ یوآن تنظیم نشده - از دستور /setrate استفاده کنید")
        
        # تست محاسبات
        test_price = 1_083_150
        base_rate = bot_instance.calculate_base_rate(test_price)
        
        if base_rate:
            print(f"\n✅ تست محاسبات:")
            print(f"   قیمت تتر: {test_price:,} ریال")
            print(f"   نرخ محاسبه شده: {base_rate:,} تومان")
            
            # تست فرمت پیام
            message = bot_instance.format_message(base_rate)
            print(f"\n   پیش‌نمایش پیام:")
            print("   " + "\n   ".join(message.split('\n')))
            
            return True
        else:
            print("❌ محاسبات ناموفق بود")
            return False
            
    except Exception as e:
        print(f"❌ خطا در bot_instance: {e}")
        return False

async def test_reminder():
    """تست یادآوری"""
    print_section("8️⃣  تست ارسال یادآوری")
    
    try:
        response = input("آیا می‌خواهید پیام یادآوری به گروه ارسال شود؟ (y/n): ")
        
        if response.lower() != 'y':
            print("⏭️  تست یادآوری رد شد")
            return True
        
        print("\n📤 در حال ارسال یادآوری...")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, 'reminder.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ یادآوری ارسال شد")
            return True
        else:
            print(f"❌ خطا در ارسال یادآوری:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست یادآوری: {e}")
        return False

async def test_auto_update():
    """تست به‌روزرسانی خودکار"""
    print_section("9️⃣  تست به‌روزرسانی خودکار")
    
    try:
        response = input("آیا می‌خواهید به‌روزرسانی کامل انجام شود و به گروه ارسال شود؟ (y/n): ")
        
        if response.lower() != 'y':
            print("⏭️  تست به‌روزرسانی رد شد")
            return True
        
        print("\n📤 در حال به‌روزرسانی...")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, 'auto_fetcher.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ به‌روزرسانی انجام شد")
            print("\n--- خروجی ---")
            print(result.stdout)
            return True
        else:
            print(f"❌ خطا در به‌روزرسانی:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست به‌روزرسانی: {e}")
        return False

async def main():
    """تابع اصلی"""
    print("\n" + "🚀"*30)
    print("  تست جامع ربات تلگرام - Tether to Yuan")
    print("🚀"*30)
    
    results = []
    
    # 1. بررسی متغیرها
    results.append(("متغیرهای محیطی", check_env_variables()))
    
    # 2. بررسی فایل‌ها
    results.append(("فایل‌های پروژه", check_files()))
    
    # 3. تست اتصال ربات
    results.append(("اتصال ربات", await test_bot_connection()))
    
    # 4. تست Telethon
    results.append(("Telethon Session", await test_telethon_session()))
    
    # 5. تست دسترسی گروه
    results.append(("دسترسی به گروه", await test_group_access()))
    
    # 6. تست خواندن کانال
    results.append(("خواندن از کانال", await test_channel_read()))
    
    # 7. تست Bot Instance
    results.append(("Bot Instance", await test_bot_instance()))
    
    # 8. تست یادآوری (اختیاری)
    results.append(("یادآوری", await test_reminder()))
    
    # 9. تست به‌روزرسانی (اختیاری)
    results.append(("به‌روزرسانی خودکار", await test_auto_update()))
    
    # خلاصه نتایج
    print_section("📊 خلاصه نتایج")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    print(f"  موفق: {passed}/{total}")
    print(f"  درصد موفقیت: {passed*100/total:.1f}%")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 تبریک! همه تست‌ها موفق بودند. پروژه آماده است!")
    elif passed >= total * 0.7:
        print("⚠️  اکثر تست‌ها موفق بودند. موارد ناموفق را بررسی کنید.")
    else:
        print("❌ تعداد زیادی تست ناموفق بود. لطفاً مشکلات را برطرف کنید.")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تست توسط کاربر لغو شد.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطای غیرمنتظره: {e}")
        sys.exit(1)

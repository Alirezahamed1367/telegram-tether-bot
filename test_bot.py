#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست برای آزمایش عملکرد ربات بدون نیاز به تلگرام
"""

from bot import TetherBot

def test_extract_price():
    """تست استخراج قیمت"""
    bot = TetherBot()
    
    # نمونه متن از کانال
    sample_text = """💵 قیمت لحظه‌ای تتر

🟢 خرید تتر : 1084970 ریال
🔴 فروش تتر : 1084980 ریال

🥇 طلای 18 عیار : 104721000 ریال
🟡 سکه بهار آزادی : 1040850000 ریال

@tetherprice_toman"""
    
    price = bot.extract_tether_price(sample_text)
    print(f"✅ قیمت استخراج شده: {price:,} ریال")
    assert price == 1084980, "خطا در استخراج قیمت!"
    return price


def test_calculate_rate(tether_price):
    """تست محاسبه نرخ"""
    bot = TetherBot()
    bot.yuan_rate = 7.12
    
    base_rate = bot.calculate_base_rate(tether_price)
    print(f"✅ نرخ مبنا محاسبه شده: {base_rate:,.0f} تومان")
    
    # بررسی صحت محاسبه
    # 1084980 / 10 = 108498
    # 108498 / 7.12 = 15238.48
    # رند به بالا → 15240
    assert base_rate == 15240, f"خطا در محاسبه! انتظار: 15240، دریافت: {base_rate}"
    return base_rate


def test_format_message(base_rate):
    """تست قالب‌بندی پیام"""
    bot = TetherBot()
    bot.yuan_rate = 7.12
    
    message = bot.format_message(base_rate)
    print("\n📨 پیام نهایی:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # بررسی محتوای پیام
    assert "15,300" in message, "قیمت سطح 1 اشتباه است"
    assert "15,290" in message, "قیمت سطح 2 اشتباه است"
    assert "15,280" in message, "قیمت سطح 3 اشتباه است"
    assert "15,240" in message, "نرخ مبنا در پیام نیست"


def test_rate_decrease_condition():
    """تست شرط کاهش نرخ"""
    bot = TetherBot()
    bot.yuan_rate = 7.12
    bot.last_calculated_rate = 15500  # نرخ قبلی بالاتر
    
    # نرخ جدید پایین‌تر
    tether_price = 1000000  # یک قیمت پایین‌تر
    new_rate = bot.calculate_base_rate(tether_price)
    
    print(f"\n🔍 تست شرط کاهش نرخ:")
    print(f"   نرخ قبلی: {bot.last_calculated_rate:,.0f}")
    print(f"   نرخ جدید محاسبه شده: {new_rate:,.0f}")
    
    if new_rate < bot.last_calculated_rate:
        print(f"   ✅ شرط فعال شد - از نرخ قبلی استفاده می‌شود")
    else:
        print(f"   ℹ️ نرخ جدید بالاتر است - به‌روزرسانی می‌شود")


def main():
    """اجرای تست‌ها"""
    print("🧪 شروع تست‌های ربات...\n")
    
    try:
        # تست 1: استخراج قیمت
        print("1️⃣ تست استخراج قیمت از متن کانال")
        price = test_extract_price()
        print()
        
        # تست 2: محاسبه نرخ
        print("2️⃣ تست محاسبه نرخ مبنا")
        base_rate = test_calculate_rate(price)
        print()
        
        # تست 3: قالب‌بندی پیام
        print("3️⃣ تست قالب‌بندی پیام نهایی")
        test_format_message(base_rate)
        print()
        
        # تست 4: شرط کاهش نرخ
        print("4️⃣ تست شرط کاهش نرخ")
        test_rate_decrease_condition()
        print()
        
        print("✅ همه تست‌ها با موفقیت انجام شد!")
        
    except AssertionError as e:
        print(f"\n❌ تست ناموفق: {e}")
    except Exception as e:
        print(f"\n❌ خطا: {e}")


if __name__ == '__main__':
    main()

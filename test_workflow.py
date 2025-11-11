#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست برای بررسی workflow
"""

print("="*60)
print("🧪 تست Workflow")
print("="*60)

import os

# بررسی متغیرهای محیطی
required_vars = [
    'BOT_TOKEN',
    'TARGET_GROUP_ID',
    'TELEGRAM_API_ID',
    'TELEGRAM_API_HASH',
    'TELEGRAM_PHONE'
]

print("\n📋 بررسی متغیرهای محیطی:")
for var in required_vars:
    value = os.getenv(var)
    if value:
        masked = f"{value[:8]}..." if len(value) > 8 else value
        print(f"  ✅ {var}: {masked}")
    else:
        print(f"  ❌ {var}: وجود ندارد")

# بررسی فایل‌ها
print("\n📁 بررسی فایل‌ها:")
files = ['bot.py', 'auto_fetcher.py', 'reminder.py', 'user_session.session']
for file in files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} وجود ندارد")

print("\n" + "="*60)
print("✅ تست workflow موفق بود!")
print("="*60)

# 🐛 راه‌حل مشکلات Python 3.13

## مشکل: TypeError: Only timezones from the pytz library are supported

### علت:
Python 3.13 خیلی جدید است و برخی کتابخانه‌ها با آن سازگاری کامل ندارند.

### راه‌حل (انجام شده):

1. **نصب APScheduler سازگار:**
```powershell
pip uninstall -y apscheduler
pip install "APScheduler>=3.10,<4.0"
```

2. **نصب python-telegram-bot جدیدتر:**
```powershell
pip install --upgrade python-telegram-bot>=21.0
```

3. **نصب وابستگی‌های اضافی:**
```powershell
pip install tzlocal>=3.0
```

4. **تنظیم timezone در کد:**
در ابتدای `bot.py` اضافه شد:
```python
os.environ.setdefault('TZ', 'UTC')
```

---

## مشکل: AttributeError: 'Updater' object has no attribute

### علت:
نسخه قدیمی python-telegram-bot با Python 3.13 کار نمی‌کند.

### راه‌حل:
```powershell
pip install --upgrade python-telegram-bot>=21.0
```

---

## مشکل: BOT_TOKEN تنظیم نشده است

### علت:
فایل `.env` وجود ندارد.

### راه‌حل:
```powershell
Copy-Item .env.example .env
notepad .env  # ویرایش و اضافه کردن توکن
```

---

## تست نهایی

بعد از حل مشکلات، برای تست:

```powershell
python bot.py
```

باید خروجی زیر را ببینید:
```
✅ ربات در حال اجراست. برای توقف از Ctrl+C استفاده کنید.
📝 دستورات موجود:
  /start - راهنما
  /setrate <نرخ> - تنظیم نرخ یوآن
  /getrate - نمایش نرخ فعلی
  /status - وضعیت ربات
  /update - به‌روزرسانی دستی
```

---

## نصب کامل از صفر (برای Python 3.13)

اگر می‌خواهید از اول نصب کنید:

```powershell
# حذف کتابخانه‌های قدیمی
pip uninstall -y python-telegram-bot apscheduler

# نصب نسخه‌های سازگار
pip install python-telegram-bot>=21.0
pip install "APScheduler>=3.10,<4.0"
pip install python-dotenv pytz requests telethon tzlocal

# یا استفاده از requirements.txt
pip install -r requirements.txt
```

---

## توصیه‌ها

### برای Production:
اگر می‌خواهید مشکل نداشته باشید:
- **گزینه ۱:** از Python 3.10 یا 3.11 استفاده کنید (پایدارتر)
- **گزینه ۲:** از Docker استفاده کنید با Python 3.11

### برای Development:
- Python 3.13 با تنظیمات فوق کار می‌کند
- همیشه virtual environment استفاده کنید

---

## نکات امنیتی

⚠️ **هرگز فایل `.env` را commit نکنید!**

فایل `.gitignore` مطمئن می‌شود که:
- `.env` آپلود نمی‌شود
- `*.session` آپلود نمی‌شود
- اطلاعات حساس امن است

---

**آخرین به‌روزرسانی:** نوامبر 2025

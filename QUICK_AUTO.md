# ⚡ راهنمای فوری - ربات کاملاً خودکار

## 🎯 هدف
ربات بدون نیاز به forward دستی یا سیستم روشن، خودکار کار کند.

---

## 📝 چک‌لیست ۷ قدمه (۴۵ دقیقه)

### ✅ قدم ۱: دریافت API از تلگرام (۱۰ دقیقه)
```
□ به https://my.telegram.org بروید
□ با شماره تلفن login کنید
□ API development tools > Create application
□ API ID و API Hash را کپی کنید
```

---

### ✅ قدم ۲: ساخت ربات (۵ دقیقه)
```
□ به @BotFather پیام دهید
□ /newbot
□ توکن ربات را کپی کنید
```

---

### ✅ قدم ۳: ساخت گروه (۳ دقیقه)
```
□ New Group در تلگرام
□ ربات را اضافه کنید
□ شناسه گروه را از @userinfobot بگیرید
```

---

### ✅ قدم ۴: تست محلی (۱۰ دقیقه)
```powershell
# نصب
cd "d:\Project\Telegram Tether"
pip install -r requirements.txt

# تنظیمات
Copy-Item .env.example .env
notepad .env
# همه اطلاعات را پر کنید

# تنظیم نرخ
python bot.py
# در تلگرام: /setrate 7.12
# Ctrl+C برای توقف

# تست خودکار
python auto_fetcher.py
# کد تایید را وارد کنید
# باید در گروه پیام را ببینید!
```

---

### ✅ قدم ۵: Session به Base64 (۵ دقیقه)
```powershell
# تبدیل session file
$bytes = [System.IO.File]::ReadAllBytes("user_session.session")
$base64 = [Convert]::ToBase64String($bytes)
$base64 | Out-File -FilePath "session_base64.txt"
notepad session_base64.txt
# محتوا را کپی کنید
```

---

### ✅ قدم ۶: GitHub Secrets (۱۰ دقیقه)
```
□ GitHub > New repository
□ آپلود همه فایل‌ها
□ Settings > Secrets > Actions

□ BOT_TOKEN = توکن ربات
□ TARGET_GROUP_ID = شناسه گروه
□ TELEGRAM_API_ID = از my.telegram.org
□ TELEGRAM_API_HASH = از my.telegram.org
□ TELEGRAM_PHONE = +989123456789
□ TELETHON_SESSION = رشته base64
```

---

### ✅ قدم ۷: تست GitHub (۵ دقیقه)
```
□ Actions > Enable workflows
□ Update Tether Rate > Run workflow
□ بررسی لاگ‌ها
□ در گروه پیام را دیدید؟ ✅
```

---

## 🎉 تمام!

از این به بعد:
- ✅ هر ساعت خودکار اجرا می‌شود
- ✅ خودش از کانال می‌خواند
- ✅ بدون forward دستی
- ✅ بدون سیستم روشن

فقط وقتی نرخ یوآن عوض شد:
```
/setrate 7.15
```

---

## 🐛 مشکل دارید?

### Session کار نمی‌کند
```powershell
# دوباره بسازید
rm user_session.session
python auto_fetcher.py
# Session جدید را به GitHub بفرستید
```

### خطای "Phone number"
```
TELEGRAM_PHONE=+989123456789
# با + و کد کشور
```

### هیچ پیامی نیست
```
1. نرخ یوآن تنظیم شده? /setrate 7.12
2. همه 6 Secret در GitHub هست؟
3. لاگ Actions چی می‌گه؟
```

---

## 📚 راهنماهای کامل

- **این فایل:** خلاصه سریع ⚡
- `AUTO_SETUP.md`: راهنمای کامل خودکار 🚀
- `TUTORIAL.md`: روش دستی با forward
- `SIMPLE_GUIDE.md`: برای مبتدی‌ها

---

**موفق باشید! 💪**

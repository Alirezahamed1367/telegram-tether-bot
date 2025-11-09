# 📱 راهنمای ارسال خودکار به واتساپ

## 🎯 روش‌های ارسال خودکار به واتساپ

### ⚠️ محدودیت‌های مهم واتساپ

قبل از شروع باید بدانید:
- واتساپ API رسمی ندارد (مگر واتساپ بیزنس که پولی است)
- استفاده از روش‌های غیررسمی خطر بن شدن دارد
- نیاز به نگهداری session فعال دارد

---

## 🔥 روش 1: استفاده از WhatsApp Business API (پیشنهاد رسمی)

### مزایا:
- ✅ رسمی و مجاز
- ✅ پایدار و قابل اعتماد
- ✅ امکانات حرفه‌ای
- ✅ بدون خطر بن

### معایب:
- ❌ پولی است (حدود $0.005 هر پیام)
- ❌ نیاز به تایید کسب‌وکار
- ❌ پیچیده‌تر در راه‌اندازی

### نحوه استفاده:

1. ثبت‌نام در Meta Business:
   ```
   https://business.facebook.com/
   ```

2. راه‌اندازی WhatsApp Business API:
   ```
   https://business.whatsapp.com/products/business-api
   ```

3. دریافت توکن و شماره تایید شده

4. استفاده از کتابخانه Python:
   ```bash
   pip install twilio  # یا heyoo
   ```

5. کد نمونه:
   ```python
   from twilio.rest import Client
   
   account_sid = 'YOUR_ACCOUNT_SID'
   auth_token = 'YOUR_AUTH_TOKEN'
   client = Client(account_sid, auth_token)
   
   message = client.messages.create(
       from_='whatsapp:+14155238886',
       body='Your message here',
       to='whatsapp:+989123456789'
   )
   ```

**هزینه:** ~$15-50/ماه بسته به تعداد پیام

---

## 🚀 روش 2: استفاده از whatsapp-web.js (پیشنهاد برتر)

### مزایا:
- ✅ رایگان کامل
- ✅ استفاده از WhatsApp Web
- ✅ کد باز و فعال
- ✅ قابلیت‌های زیاد

### معایب:
- ⚠️ نیاز به اسکن QR هر چند وقت یکبار
- ⚠️ نیاز به Node.js
- ⚠️ باید session فعال بماند

### نحوه راه‌اندازی:

#### مرحله 1: نصب Node.js

```bash
# دانلود از:
https://nodejs.org/
```

#### مرحله 2: ساخت پروژه Node.js

```bash
mkdir whatsapp-bridge
cd whatsapp-bridge
npm init -y
npm install whatsapp-web.js qrcode-terminal express
```

#### مرحله 3: کد Node.js (`server.js`)

```javascript
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const app = express();

app.use(express.json());

// ایجاد کلاینت واتساپ
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox']
    }
});

// نمایش QR Code
client.on('qr', (qr) => {
    console.log('اسکن کنید:');
    qrcode.generate(qr, {small: true});
});

// آماده شدن
client.on('ready', () => {
    console.log('✅ واتساپ متصل شد!');
});

// API برای ارسال پیام
app.post('/send', async (req, res) => {
    try {
        const { phone, message } = req.body;
        
        // فرمت شماره: 989123456789@c.us
        const chatId = phone.includes('@c.us') ? phone : `${phone}@c.us`;
        
        await client.sendMessage(chatId, message);
        
        res.json({ success: true, message: 'پیام ارسال شد' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// API برای ارسال به گروه
app.post('/send-group', async (req, res) => {
    try {
        const { groupId, message } = req.body;
        
        // فرمت گروه: 123456789@g.us
        const chatId = groupId.includes('@g.us') ? groupId : `${groupId}@g.us`;
        
        await client.sendMessage(chatId, message);
        
        res.json({ success: true, message: 'پیام به گروه ارسال شد' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// لیست گروه‌ها
app.get('/groups', async (req, res) => {
    try {
        const chats = await client.getChats();
        const groups = chats.filter(chat => chat.isGroup).map(group => ({
            id: group.id._serialized,
            name: group.name
        }));
        
        res.json({ success: true, groups });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// شروع سرور
app.listen(3000, () => {
    console.log('🚀 سرور روی پورت 3000 شروع شد');
});

// اتصال به واتساپ
client.initialize();
```

#### مرحله 4: اجرای سرور

```bash
node server.js
```

اولین بار QR Code نمایش می‌دهد - با واتساپ خود اسکن کنید.

#### مرحله 5: اضافه کردن به Python Bot

در پروژه Python یک فایل `whatsapp_sender.py` بسازید:

```python
import os
import requests
import logging

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'http://localhost:3000')
WHATSAPP_GROUP_ID = os.getenv('WHATSAPP_GROUP_ID', '')  # مثال: 123456789@g.us

def send_to_whatsapp(message: str) -> bool:
    """
    ارسال پیام به گروه واتساپ
    """
    if not WHATSAPP_GROUP_ID:
        logger.warning("WHATSAPP_GROUP_ID تنظیم نشده است")
        return False
    
    try:
        response = requests.post(
            f'{WHATSAPP_API_URL}/send-group',
            json={
                'groupId': WHATSAPP_GROUP_ID,
                'message': message
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ پیام به واتساپ ارسال شد")
            return True
        else:
            logger.error(f"❌ خطا در ارسال به واتساپ: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطا در اتصال به سرور واتساپ: {e}")
        return False

def get_whatsapp_groups() -> list:
    """
    دریافت لیست گروه‌های واتساپ
    """
    try:
        response = requests.get(f'{WHATSAPP_API_URL}/groups', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('groups', [])
        else:
            return []
            
    except Exception as e:
        logger.error(f"خطا در دریافت گروه‌ها: {e}")
        return []
```

#### مرحله 6: ویرایش `auto_fetcher.py`

```python
# در ابتدای فایل import کنید:
from whatsapp_sender import send_to_whatsapp

# بعد از ارسال به تلگرام، این خط را اضافه کنید:
# ارسال به واتساپ
send_to_whatsapp(message)
```

#### مرحله 7: تنظیمات `.env`

```bash
# اضافه کردن به .env
WHATSAPP_API_URL=http://localhost:3000
WHATSAPP_GROUP_ID=123456789@g.us
```

#### مرحله 8: دریافت Group ID

```bash
# اجرای اسکریپت برای دریافت لیست گروه‌ها
curl http://localhost:3000/groups
```

یا در Python:
```python
from whatsapp_sender import get_whatsapp_groups

groups = get_whatsapp_groups()
for group in groups:
    print(f"نام: {group['name']}")
    print(f"ID: {group['id']}")
    print("-" * 50)
```

---

## 🌐 روش 3: استفاده از PyWhatKit (ساده‌ترین)

### مزایا:
- ✅ خیلی ساده
- ✅ رایگان
- ✅ کد کم

### معایب:
- ❌ نیاز به مرورگر باز
- ❌ کند
- ❌ غیرقابل اعتماد برای Production

### نحوه استفاده:

```bash
pip install pywhatkit
```

```python
import pywhatkit

# ارسال فوری (در 2 ثانیه)
pywhatkit.sendwhatmsg_instantly(
    phone_no="+989123456789",
    message="Hello from Python!",
    wait_time=15,
    tab_close=True
)

# ارسال در زمان مشخص
pywhatkit.sendwhatmsg(
    phone_no="+989123456789",
    message="Scheduled message",
    time_hour=14,
    time_min=30
)

# ارسال به گروه
pywhatkit.sendwhatmsg_to_group(
    group_id="ABC123XYZ",  # از لینک دعوت بگیرید
    message="Group message",
    time_hour=14,
    time_min=30
)
```

**نکته:** این روش مرورگر را باز می‌کند و نیاز به تعامل دارد.

---

## 🐳 روش 4: استفاده از Docker + whatsapp-web.js (پیشنهاد برای Production)

### مزایا:
- ✅ قابل استقرار در سرور
- ✅ جدا از سیستم اصلی
- ✅ راه‌اندازی آسان‌تر

### Dockerfile:

```dockerfile
FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

### docker-compose.yml:

```yaml
version: '3.8'

services:
  whatsapp-bridge:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./session:/app/.wwebjs_auth
    restart: unless-stopped
    environment:
      - NODE_ENV=production

  telegram-bot:
    build: ../telegram-bot
    depends_on:
      - whatsapp-bridge
    environment:
      - WHATSAPP_API_URL=http://whatsapp-bridge:3000
```

### اجرا:

```bash
docker-compose up -d
```

---

## 📊 مقایسه روش‌ها

| روش | هزینه | پیچیدگی | قابلیت اطمینان | پیشنهاد |
|-----|-------|---------|----------------|---------|
| WhatsApp Business API | 💰💰💰 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | کسب‌وکارهای بزرگ |
| whatsapp-web.js | 🆓 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ **پیشنهاد برتر** |
| PyWhatKit | 🆓 | ⭐ | ⭐⭐ | تست و آموزش |
| Docker + whatsapp-web.js | 🆓 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Production |

---

## 🎯 پیشنهاد نهایی من

برای پروژه شما **روش 2 (whatsapp-web.js)** را پیشنهاد می‌کنم چون:

1. ✅ **رایگان کامل**
2. ✅ **قابل اعتماد** برای استفاده روزانه
3. ✅ **آسان در راه‌اندازی**
4. ✅ **امکان استقرار در سرور** (با Docker)
5. ✅ **جامعه فعال** و مستندات خوب

### مراحل پیاده‌سازی برای پروژه شما:

1. **نصب Node.js** روی سیستم
2. **راه‌اندازی سرور whatsapp-web.js** (کد بالا)
3. **اسکن QR Code** با واتساپ خود
4. **اضافه کردن `whatsapp_sender.py`** به پروژه
5. **ویرایش `auto_fetcher.py`** برای ارسال همزمان به تلگرام و واتساپ
6. **تنظیم GitHub Actions** برای اجرای سرور Node.js

---

## 🔧 راه‌اندازی کامل (گام به گام)

### فاز 1: آماده‌سازی محلی

```bash
# نصب Node.js از nodejs.org

# ساخت پروژه واتساپ
mkdir whatsapp-bridge
cd whatsapp-bridge
npm init -y
npm install whatsapp-web.js qrcode-terminal express

# کپی کردن server.js (کد بالا)

# اجرا و اسکن QR
node server.js
```

### فاز 2: تست محلی

```bash
# در ترمینال جدید:
cd ../telegram-bot

# اضافه کردن whatsapp_sender.py
# ویرایش auto_fetcher.py

# تست
python auto_fetcher.py
```

### فاز 3: استقرار در سرور

اگر می‌خواهید در سرور استقرار دهید:

```bash
# استفاده از screen یا tmux
screen -S whatsapp
node server.js
# Ctrl+A, D برای detach

# یا استفاده از pm2
npm install -g pm2
pm2 start server.js --name whatsapp-bridge
pm2 save
pm2 startup
```

---

## 📞 پشتیبانی و منابع

- [whatsapp-web.js Docs](https://github.com/pedroslopez/whatsapp-web.js)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [PyWhatKit Docs](https://pypi.org/project/pywhatkit/)

---

## ⚠️ نکات امنیتی

1. **هرگز session را در GitHub قرار ندهید**
2. **از .gitignore استفاده کنید**
3. **توکن‌ها را در .env نگه دارید**
4. **برای production از HTTPS استفاده کنید**

---

**آیا می‌خواهید الان روش whatsapp-web.js را پیاده‌سازی کنیم؟** 🚀

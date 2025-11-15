# أوامر سريعة للرفع والنشر ⚡

أوامر جاهزة للنسخ واللصق - خطوة بخطوة!

---

## 🔧 الخطوة 1: تثبيت Git

### Windows:
1. حمّل من: https://git-scm.com/download/win
2. شغّل المثبت واتبع التعليمات

### التحقق:
```bash
git --version
```

---

## ⚙️ الخطوة 2: إعداد Git (أول مرة فقط)

افتح PowerShell في مجلد المشروع:

```powershell
cd "C:\Users\W K\Downloads\mac"

git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**استبدل**:
- `"Your Name"` باسمك
- `"your.email@example.com"` ببريدك على GitHub

---

## 📤 الخطوة 3: رفع المشروع إلى GitHub

### أ) إنشاء مستودع على GitHub:
1. اذهب إلى: https://github.com/new
2. **Repository name**: `email-phishing-detector`
3. اختر **Public**
4. **لا** تضع علامة على "Initialize with README"
5. اضغط **Create repository**

### ب) رفع الملفات:

افتح PowerShell في مجلد المشروع:

```powershell
cd "C:\Users\W K\Downloads\mac"

# تهيئة Git
git init

# إضافة جميع الملفات
git add .

# إنشاء commit
git commit -m "Initial commit: Email Phishing Detector"

# إضافة المستودع البعيد (استبدل YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/email-phishing-detector.git

# رفع الملفات
git branch -M main
git push -u origin main
```

**عند الطلب**:
- اسم المستخدم: اسمك على GitHub
- كلمة المرور: Personal Access Token (انظر أدناه)

---

## 🔑 إنشاء Personal Access Token

إذا طُلب منك كلمة المرور:

1. اذهب إلى: https://github.com/settings/tokens
2. اضغط **Generate new token (classic)**
3. **Note**: `Project Upload`
4. **Expiration**: `No expiration` (أو اختر تاريخ)
5. حدد صلاحيات: ✅ **repo** (كامل)
6. اضغط **Generate token**
7. **انسخ الرمز واحفظه** (لن يظهر مرة أخرى!)
8. استخدمه كـ "كلمة المرور" عند push

---

## 🚀 الخطوة 4: النشر على Render.com

### أ) إنشاء حساب:
1. اذهب إلى: https://render.com
2. اضغط **Get Started for Free**
3. اختر **Sign up with GitHub**

### ب) إنشاء Web Service:
1. اضغط **New +** → **Web Service**
2. اختر المستودع `email-phishing-detector`
3. اضغط **Connect**

### ج) الإعدادات:

```
Name: email-phishing-detector
Region: Frankfurt (أو أي منطقة)
Branch: main
Root Directory: (فارغ)

Environment: Python 3
Build Command: pip install --upgrade pip && pip install -r backend/requirements.txt
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### د) متغيرات البيئة (Advanced):

```
Key: PYTHONPATH
Value: /opt/render/project/src
```

### هـ) النشر:
1. اضغط **Create Web Service**
2. انتظر 5-10 دقائق
3. اضغط على الرابط المقدم! 🎉

---

## 🚀 النشر على Railway (بديل أسرع)

### أ) إنشاء حساب:
1. اذهب إلى: https://railway.app
2. اضغط **Start a New Project**
3. اختر **Deploy from GitHub repo**

### ب) النشر:
1. اختر المستودع `email-phishing-detector`
2. اضغط **Deploy Now**
3. **انتهى!** سينشر تلقائياً! 🎉

### ج) الحصول على الرابط:
1. اضغط على المشروع
2. **Settings** → **Networking**
3. اضغط **Generate Domain**

---

## ✅ اختبار الموقع

بعد النشر، اختبر:

1. **الصحة**: `https://your-url.com/health`
   - يجب أن ترى: `{"status": "ok"}`

2. **الواجهة**: `https://your-url.com`
   - يجب أن ترى صفحة الويب

3. **التحليل**: افتح الموقع وجرب تحليل رسالة!

---

## 🔄 تحديث المشروع لاحقاً

عند تعديل الملفات:

```powershell
cd "C:\Users\W K\Downloads\mac"

git add .
git commit -m "وصف التغييرات"
git push
```

**Render و Railway سيحدّثان الموقع تلقائياً!** 🎉

---

## 🆘 حل المشاكل

### Git لا يعمل؟
```bash
git --version
```
إذا لم يظهر، أعد تثبيت Git

### لا يمكن رفع الملفات؟
- استخدم Personal Access Token بدلاً من كلمة المرور
- تأكد من اسم المستخدم والبريد

### البناء فشل؟
- تحقق من Logs في Render/Railway
- تأكد من وجود `backend/requirements.txt`
- تأكد من أن `Start Command` صحيح

---

## 📞 المساعدة

- **Git Documentation**: https://git-scm.com/doc
- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app

---

## ✅ قائمة التحقق

- [ ] Git مثبت
- [ ] Git مضبوط (اسم وبريد)
- [ ] مستودع GitHub تم إنشاؤه
- [ ] الملفات مرفوعة (`git push`)
- [ ] حساب Render/Railway تم إنشاؤه
- [ ] الموقع منشور
- [ ] الموقع يعمل ✅

---

**مبروك! 🎉** موقعك الآن حي على الإنترنت!


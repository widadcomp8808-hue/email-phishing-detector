# Email Phishing Detector

نظام تحليل ذكي لرسائل البريد الإلكتروني لاكتشاف رسائل التصيد باستخدام تقنيات تعلم الآلة.

## المميزات

- ✅ تحليل رسائل البريد الإلكتروني (.eml) أو النصوص
- ✅ نظام تصنيف متقدم باستخدام ميزات متعددة
- ✅ واجهة ويب بسيطة وسهلة الاستخدام
- ✅ API مفتوحة للدمج مع أنظمة أخرى
- ✅ نتائج مفصلة مع تفسيرات عربية

## التقنيات المستخدمة

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: HTML, CSS, JavaScript
- **ML**: scikit-learn, numpy
- **Analysis**: معالجة النصوص، تحليل الروابط والنطاقات

## التشغيل المحلي

### المتطلبات

- Python 3.12
- pip

### خطوات التشغيل

1. استنساخ المشروع:
```bash
git clone <repository-url>
cd mac
```

2. إنشاء بيئة افتراضية:
```bash
cd backend
python -m venv .venv
```

3. تفعيل البيئة:
```bash
# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

4. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

5. تشغيل الخادم:
```bash
uvicorn app.main:app --reload
```

6. فتح المتصفح:
```
http://localhost:8000
```

## النشر على خوادم الاستضافة

### 1. النشر على Render.com

1. قم بإنشاء حساب على [Render.com](https://render.com)
2. اضغط على "New Web Service"
3. اربط المستودع (GitHub/GitLab)
4. اختر الخصائص التالية:
   - **Build Command**: `pip install --upgrade pip && pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

5. سيتم النشر تلقائياً بعد الرفع

### 2. النشر على Railway

1. قم بإنشاء حساب على [Railway.app](https://railway.app)
2. اضغط على "New Project" → "Deploy from GitHub repo"
3. اختر المستودع
4. سيتم النشر تلقائياً (Railway يقرأ `railway.json` تلقائياً)

### 3. النشر على Heroku

1. قم بإنشاء حساب على [Heroku](https://heroku.com)
2. تثبيت Heroku CLI
3. قم بتشغيل الأوامر التالية:
```bash
heroku create <your-app-name>
git push heroku main
```

### 4. النشر باستخدام Docker

1. بناء الصورة:
```bash
docker build -t email-phishing-detector .
```

2. تشغيل الحاوية:
```bash
docker run -p 8000:8000 email-phishing-detector
```

## استخدام API

### تحليل نص الرسالة

```bash
curl -X POST "http://localhost:8000/api/analyze/text" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent: Verify your account",
    "body": "Click here to verify your account now!",
    "headers": null
  }'
```

### تحليل ملف .eml

```bash
curl -X POST "http://localhost:8000/api/analyze/file" \
  -F "file=@email.eml"
```

### الاستجابة

```json
{
  "verdict": "phishing",
  "confidence": 0.85,
  "model_version": "0.1.0-ml",
  "metadata": {
    "subject": "Urgent: Verify your account",
    "from_address": "noreply@suspicious.tk"
  },
  "highlights": [
    "تم اكتشاف 2 كلمة/عبارة مشبوهة في الرسالة.",
    "تم اكتشاف 1 رابط يحتوي على نطاق مشبوه."
  ],
  "insights": [
    {
      "name": "suspicious_keywords",
      "value": 2,
      "weight": 0.4,
      "description": "عدد الكلمات المشبوهة المكتشفة"
    }
  ]
}
```

## البنية

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # نقطة الدخول الرئيسية
│   │   ├── routers/         # مسارات API
│   │   ├── services/        # خدمات التحليل
│   │   └── schemas.py       # نماذج البيانات
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── Dockerfile
├── render.yaml
├── railway.json
└── README.md
```

## الميزات المتقدمة

النظام يستخدم ميزات متعددة للتحليل:

- **تحليل الكلمات المفتاحية**: كلمات مشبوهة وإشارات ثقة
- **تحليل الروابط**: عدد الروابط والنطاقات المشبوهة
- **تحليل البنية**: نسبة HTML، طول الرسالة، نسبة الأحرف الكبيرة
- **تحليل اللغة**: كلمات إلحاح، تقدير الأخطاء الإملائية
- **تحليل العناوين**: فحص نطاق المرسل وعدم تطابق عنوان الرد

## التطوير المستقبلي

- [ ] إضافة نموذج ML مدرب على بيانات حقيقية
- [ ] دعم قاعدة بيانات لحفظ النتائج
- [ ] إضافة مصادقة المستخدمين
- [ ] لوحة تحكم إحصائية
- [ ] تصدير التقارير (PDF/CSV)

## الترخيص

هذا المشروع مفتوح المصدر ومتاح للاستخدام والتحسين.

## المساهمة

نرحب بمساهماتكم! يرجى فتح Issue أو Pull Request.


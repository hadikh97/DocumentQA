# راهنمای اتصال به LLM واقعی

## وضعیت فعلی
سیستم الان از **FakeLLM** استفاده می‌کند که فقط پاسخ‌های شبیه‌سازی شده می‌دهد.

## برای استفاده از LLM واقعی (HuggingFace):

### روش 1: استفاده از Environment Variable
```powershell
# توقف سرور فعلی (Ctrl+C)
# سپس اجرا با:
$env:USE_FAKE_LLM="False"
$env:POSTGRES_HOST="localhost"
$env:DEBUG="True"
.\venv\Scripts\python.exe manage.py runserver
```

### روش 2: تغییر در settings.py
در فایل `docqa_project/settings.py` خط 122 را تغییر دهید:
```python
USE_FAKE_LLM = False  # به جای True
```

## مدل پیش‌فرض
- **Model**: `google/flan-t5-base`
- **نوع**: Text-to-Text Generation
- **حجم**: حدود 990MB (اولین بار دانلود می‌شود)

## نکات مهم:
1. **اولین بار**: مدل از HuggingFace دانلود می‌شود (ممکن است چند دقیقه طول بکشد)
2. **RAM**: حداقل 4GB RAM آزاد نیاز است
3. **سرعت**: پاسخ‌ها کندتر از FakeLLM هستند (چند ثانیه)
4. **کیفیت**: پاسخ‌های واقعی و بر اساس محتوای اسناد

## تغییر مدل
می‌توانید مدل را در settings.py تغییر دهید:
```python
HUGGINGFACE_MODEL = 'google/flan-t5-large'  # مدل بزرگتر
# یا
HUGGINGFACE_MODEL = 'microsoft/DialoGPT-medium'  # مدل دیگر
```


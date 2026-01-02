# i000-mail-auth
Pymo Pro &amp; i000 Identity Team إنشاء تقنيات تخدم الجميع بنزاهة وأمان.
. هذا الدليل موجه للمطورين ليشرح لهم كيفية دمج نظام "Login with i000" والتحقق من التوقيع الرقمي (Signature) في خوادمهم لضمان أمن البيانات.

---

# 🔐 دليل دمج نظام "Login with i000" للمطورين

يركز هذا الدليل على كيفية استقبال بيانات المستخدم بعد نجاح عملية المصادقة عبر **i000 Identity** والتحقق من صحتها تقنياً لمنع التزوير.

## 🚀 نظرة عامة

عندما يقوم المستخدم بتسجيل الدخول بنجاح، سيقوم خادم i000 بإعادة توجيه المتصفح إلى رابط العودة (`redirect_uri`) الخاص بموقعك مع المعايير التالية في الرابط (URL Parameters):

* `uid`: معرف المستخدم في تليجرام.
* `email`: عنوان البريد الإلكتروني الخاص بالمستخدم (`@i000.org`).
* `ts`: الطابع الزمني للعملية (Timestamp).
* `sig`: التوقيع الرقمي المشفر (HMAC-SHA256).

---

## 🛠 المتطلبات الأساسية

قبل البدء، يجب أن تتوفر لديك البيانات التالية (تحصل عليها من لوحة تحكم المطورين):

1. **Client ID**: المعرف الفريد لتطبيقك.
2. **Client Secret**: المفتاح السري لتطبيقك (⚠️ **يجب حفظه في الخادم فقط ولا يظهر للعلن**).

---

## 🏗 آلية التحقق (Logic)

لمنع تزوير البيانات، يجب عليك إعادة إنشاء التوقيع في خادمك ومقارنته بالتوقيع المرسل. التوقيع هو عبارة عن تشفير للبيانات التالية بالترتيب:
`uid:email:ts` باستخدام مفتاحك السري `Client Secret`.

---
إليك النسخة المحدثة والنهائية لملف **README.md** الخاص بمشروعك على **GitHub**. تم تعديل كافة الروابط لتعتمد على الدومين المخصص الجديد **`auth.i000.org`**، مع إضافة شرح دقيق لكيفية التعامل مع التوقيع الرقمي (Signature) لضمان أقصى درجات الأمان.

---

# 🔐 i000 Identity: دليل دمج نظام تسجيل الدخول للمطورين

نظام **i000 Identity** هو منصة هوية رقمية تتيح للمطورين التحقق من هوية المستخدمين عبر بريدهم الإلكتروني المرتبط بـ تليجرام (`@i000.org`) بطريقة آمنة وسهلة، تشبه نظام "تسجيل الدخول بواسطة جوجل".

## 📍 روابط النظام الأساسية

* **بوابة المصادقة:** `https://auth.i000.org/authorize`
* **لوحة تحكم المطورين:** `https://auth.i000.org/developers`

---

## 🛠 آلية العمل (Authentication Flow)

1. **توجيه المستخدم:** قم بتوجيه المستخدم في موقعك إلى الرابط التالي:
```text
https://auth.i000.org/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI

```


2. **المصادقة:** يقوم المستخدم بتأكيد هويته (إما بضغطة واحدة داخل تليجرام، أو عبر كود OTP يصل لحسابه).
3. **العودة بالبيانات:** بعد النجاح، يتم توجيه المستخدم لموقعك ومعطيات الدخول في الرابط:
```text
https://your-site.com/callback?uid=ID&email=USER@i000.org&ts=TIMESTAMP&sig=SIGNATURE

```



---

## 🛡 التحقق من أمان البيانات (Signature Verification)

لمنع تزوير البيانات، يرسل النظام توقيعاً رقمياً `sig` ناتجاً عن تشفير البيانات باستخدام **Client Secret** الخاص بك. يجب عليك إعادة حساب التوقيع في خادمك ومقارنته.

### قاعدة البيانات الموقعة (Payload)

يتم إنشاء التوقيع بدمج البيانات بالتنسيق التالي (مع مراعاة الحروف الصغيرة للبريد):
`uid:email:ts`

### 💻 أمثلة برمجية للتحقق

#### 1. Node.js (الخيار الموصى به)

```javascript
const crypto = require('crypto');

function verifySignature(query, clientSecret) {
    const { uid, email, ts, sig } = query;
    const payload = `${uid}:${email.toLowerCase()}:${ts}`;
    const expectedSig = crypto.createHmac('sha256', clientSecret).update(payload).digest('hex');
    
    return expectedSig === sig;
}

```

#### 2. Python (Django/Flask)

```python
import hmac, hashlib

def verify_signature(uid, email, ts, sig, client_secret):
    payload = f"{uid}:{email.lower()}:{ts}"
    expected_sig = hmac.new(
        client_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_sig, sig)

```

#### 3. PHP

```php
function verifySignature($uid, $email, $ts, $sig, $clientSecret) {
    $payload = "$uid:" . strtolower($email) . ":$ts";
    $expectedSig = hash_hmac('sha256', $payload, $clientSecret);
    
    return hash_equals($expectedSig, $sig);
}

```

---

## ⚠️ تعليمات أمنية هامة

* **السرية التامة:** لا تقم أبداً بتضمين `Client Secret` في كود الواجهة الأمامية (Client-side JS).
* **فحص الوقت (Timestamp Check):** تأكد من أن قيمة `ts` قريبة من الوقت الحالي (فرق لا يتجاوز 5 دقائق) لمنع هجمات الإعادة (Replay Attacks).
* **الدومين المخصص:** تأكد أن جميع طلباتك موجهة إلى `auth.i000.org`.

---

## 📞 الدعم والمساعدة

للحصول على المساعدة التقنية أو الإبلاغ عن ثغرات، يرجى التواصل عبر:

* **Telegram Bot:** `@i000_org`
* **Founder:** Mohamed Shaaban (Moshft)
* **Founder:** you need join?
---

**i000 Identity System** - *Secure, Simple, and Integrated.*

---


1. **لا تسرب السر (Secret):** لا تضع الـ `client_secret` أبداً في كود الواجهة الأمامية (Frontend/JavaScript).
2. **استخدم HTTPS:** تأكد من أن رابط العودة الخاص بك يستخدم بروتوكول `https` لتشفير البيانات أثناء النقل.
3. **فحص الوقت (Timestamp):** دائماً تحقق من أن قيمة `ts` قريبة من الوقت الحالي لتجنب هجمات الإعادة (Replay Attacks).
4. **التحقق من الدومين:** تأكد دائماً من أن البريد ينتهي بـ `@i000.org` إذا كنت تقدم ميزات خاصة لمستخدمي هذا النطاق.

---

## 📞 الدعم الفني

إذا واجهت أي مشاكل في الدمج، يمكنك التواصل مع مطوري **i000 Identity** عبر بوت التليجرام الرسمي.

---

**Pymo Pro & i000 Identity Team** *إنشاء تقنيات تخدم الجميع بنزاهة وأمان.*

---

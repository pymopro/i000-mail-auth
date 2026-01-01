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

## 💻 مثال تطبيقي (Node.js)

إليك كود جاهز باستخدام مكتبة `crypto` المدمجة في Node.js للتحقق من صحة الدخول:

```javascript
const crypto = require('crypto');

/**
 * دالة التحقق من صحة بيانات i000
 * @param {Object} query - المعايير القادمة من الرابط (req.query)
 * @param {string} clientSecret - السر الخاص بتطبيقك المحفوظ في الخادم
 */
function verifyI000Auth(query, clientSecret) {
    const { uid, email, ts, sig } = query;

    // 1. فحص وجود كافة البيانات
    if (!uid || !email || !ts || !sig) {
        return { success: false, message: "بيانات ناقصة" };
    }

    // 2. التحقق من الطابع الزمني (اختياري ولكن مهم للأمن)
    // منع الهجمات التي تستخدم روابط قديمة (أقدم من 5 دقائق مثلاً)
    const now = Date.now();
    const diff = Math.abs(now - parseInt(ts));
    if (diff > 5 * 60 * 1000) {
        return { success: false, message: "انتهت صلاحية الرابط (Expired)" };
    }

    // 3. إعادة بناء الـ Payload بنفس التنسيق المعتمد في i000
    const payload = `${uid}:${email.toLowerCase()}:${ts}`;

    // 4. إنشاء التوقيع المحلي باستخدام مفتاحك السري
    const localSignature = crypto
        .createHmac('sha256', clientSecret)
        .update(payload)
        .digest('hex');

    // 5. مقارنة التوقيع المحلي بالتوقيع المرسل
    if (localSignature === sig) {
        return { success: true, user: { uid, email } };
    } else {
        return { success: false, message: "توقيع غير صالح - محاولة تزوير!" };
    }
}

// --- مثال على الاستخدام داخل Express.js ---
// app.get('/auth/callback', (req, res) => {
//    const result = verifyI000Auth(req.query, "YOUR_CLIENT_SECRET");
//    if (result.success) {
//        res.send(`مرحباً ${result.user.email}! تم تسجيل دخولك بنجاح.`);
//    } else {
//        res.status(401).send(result.message);
//    }
// });

```

--- أمثلة بلغات **Python (Django)** و **PHP**، لتسهيل الأمر على المطورين الذين يستخدمون تقنيات مختلفة للتحقق من التوقيع الرقمي (Signature) الخاص بنظام **i000 Identity**.

---

## 🐍 مثال تطبيقي باستخدام Python (Django)

في بيئة **Django**، يمكنك تنفيذ التحقق داخل الـ `View` المسؤول عن استقبال رابط العودة:

```python
import hmac
import hashlib
import time
from django.http import JsonResponse, HttpResponseBadRequest

def verify_i000_signature(request):
    # 1. استخراج المعايير من الرابط
    uid = request.GET.get('uid')
    email = request.GET.get('email', '').lower()
    ts = request.GET.get('ts')
    sig = request.GET.get('sig')
    
    client_secret = "YOUR_CLIENT_SECRET" # حفظه في settings.py أو env

    if not all([uid, email, ts, sig]):
        return HttpResponseBadRequest("بيانات ناقصة")

    # 2. التحقق من صلاحية الوقت (Timestamp) - 5 دقائق كحد أقصى
    try:
        current_ts = int(time.time() * 1000)
        if abs(current_ts - int(ts)) > 5 * 60 * 1000:
            return HttpResponseBadRequest("انتهت صلاحية الرابط")
    except ValueError:
        return HttpResponseBadRequest("تنسيق وقت غير صالح")

    # 3. إعادة بناء البيانات (Payload) بنفس الترتيب
    payload = f"{uid}:{email}:{ts}"

    # 4. إنشاء التوقيع الرقمي محلياً
    expected_sig = hmac.new(
        client_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 5. المقارنة
    if hmac.compare_digest(expected_sig, sig):
        # التوقيع صحيح - يمكنك تسجيل دخول المستخدم الآن
        return JsonResponse({"status": "success", "user": email})
    else:
        return HttpResponseBadRequest("توقيع غير صالح - محاولة تزوير")

```

---

## 🐘 مثال تطبيقي باستخدام PHP

بالنسبة لمطوري **PHP**، العملية بسيطة جداً باستخدام الدالة المدمجة `hash_hmac`:

```php
<?php

function verifyI000Auth($data, $clientSecret) {
    $uid = $data['uid'] ?? null;
    $email = strtolower($data['email'] ?? '');
    $ts = $data['ts'] ?? null;
    $sig = $data['sig'] ?? null;

    if (!$uid || !$email || !$ts || !$sig) {
        die("خطأ: بيانات ناقصة");
    }

    // 1. التحقق من الوقت (Timestamp)
    $currentTime = time() * 1000;
    if (abs($currentTime - (int)$ts) > 300000) { // 5 دقائق
        die("خطأ: الرابط منتهي الصلاحية");
    }

    // 2. بناء الـ Payload
    $payload = "$uid:$email:$ts";

    // 3. حساب التوقيع الرقمي
    $expectedSig = hash_hmac('sha256', $payload, $clientSecret);

    // 4. المقارنة الآمنة
    if (hash_equals($expectedSig, $sig)) {
        echo "تم التحقق بنجاح! مرحباً $email";
        // ابدأ الجلسة (Session) هنا
    } else {
        http_response_code(401);
        die("خطأ: محاولة تزوير البيانات!");
    }
}

// الاستخدام:
// verifyI000Auth($_GET, "YOUR_CLIENT_SECRET");
?>

```

---

### 💡 ملاحظات تقنية هامة لجميع اللغات:

* **Case Sensitivity:** دائماً قم بتحويل البريد الإلكتروني إلى **Lowercase** (حروف صغيرة) قبل إنشاء التوقيع، لأن النظام يرسله دائماً بهذا التنسيق.
* **Safe Comparison:** في PHP استخدم `hash_equals` وفي Python استخدم `hmac.compare_digest`؛ هذه الدوال مصممة لمنع هجمات التوقيت (Timing Attacks).
* **Redirect URI:** تأكد أن رابط العودة المسجل في لوحة التحكم يطابق تماماً الرابط الذي يستقبل هذه الأكواد.



## ⚠️ نصائح أمنية هامة للمطورين

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

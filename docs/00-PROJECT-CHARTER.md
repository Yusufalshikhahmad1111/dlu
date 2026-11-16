# 00 — Project Charter

## 1. الهدف

بناء مختبر سطح مكتب محلي يجعل الطالب يرى ويتعامل مع DLU من ناحية التسمية والمنطق والعنونة كما وردت في مصادر المقرر والمراجع، ثم يختبر MML ويرى أثرها على Module وPort والمشترك.

التجربة:

MML → Validation → Switch State → SQLite → DLU/Shelf/Module/Port UI

## 2. ممنوع الاختراع

لا نخترع:
- أرقام Shelves أو Modules.
- سعات منافذ.
- EQN غير متوافق.
- توزيع بطاقات تحكم اعتباطي.
- صور PCB على أنها الشكل الحقيقي.

الرسم يبقى مبسطًا كوسيلة تعليمية، بينما الهوية والأرقام والسعات والروابط تأتي من المصدر.

## 3. النموذج البصري الأساسي

DLU → Shelf → Module → Port → Subscriber

### DLU
مثال:
DLU 50

### Shelf
الترقيم المرجعي:
Shelf 0 … Shelf 7

### Module
الترقيم المرجعي:
Module 0 … Module 15

### Port
عندما تكون البطاقة SLMA8:
Port 0 … Port 7

كل Port يمثل خط مشترك واحد.

لا نعمم 0..7 على كل أنواع البطاقات؛ نوع البطاقة يحدد السعة.

## 4. EQN

العنونة الفيزيائية:
DLU-Shelf-Module-Port

مثال:
50-1-5-0

وهذا يعني:
- DLU 50
- Shelf 1
- Module 5
- Port 0

ومن هذا العنوان يصل الطالب إلى DN المشترك.

## 5. النطاق

داخل النطاق:
- Windows 11
- Offline
- SQLite
- Python + PySide6
- DLU visualizer
- Shelves
- Modules
- Ports
- Subscriber mapping
- MML
- SYP
- alarms
- CPT
- call path
- OSI/TCP/UDP lab
- signals/modulation lab

خارج النطاق:
- اتصال بمقسم EWSD حقيقي
- التحكم في Hardware حقيقي
- استنساخ software Siemens مغلق المصدر
- محاكاة كهربائية فيزيائية
- SS7/SIP production implementation

## 6. معيار النجاح الأكاديمي

إذا فتح الدكتور المشروع يجب أن يستطيع الطالب:
1. رؤية DLU.
2. فتح Shelf.
3. رؤية Modules بأرقامها.
4. فتح Module.
5. رؤية Ports.
6. اختيار Port.
7. معرفة DN المرتبط به.
8. كتابة MML.
9. رؤية أثر الأمر بصريًا.
10. تفسير سبب النجاح أو الفشل.

## 7. قاعدة المصدر

أي تفصيل Hardware جديد:

هل يوجد في المقرر أو مرجع EWSD المعتمد؟

نعم → يضاف.

لا → لا يصبح حقيقة في المحاكي، ويسجل كتفصيل TBD حتى نجد مصدرًا.

## 8. الترتيب

Foundation → Hardware Dataset → SQLite → MML → DLU UI → SYP → Calls/CPT → Labs → Packaging → Final Audit

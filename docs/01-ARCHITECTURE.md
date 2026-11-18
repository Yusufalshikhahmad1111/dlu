# 01 — Architecture

## 1. Stack المعتمد

### Python 3 + PySide6 + SQLite

بعد إعادة تقييم خيار React/Tauri مقابل طبيعة المشروع الجامعية والمطلوب التعليمي، نعتمد Python + PySide6 + SQLite.

السبب: نحتاج واجهة DLU/رفوف/Modules/Ports وOMT وSYP، لكن نريد أيضًا أن يبقى المشروع بسيطًا وOffline ومن لغة واحدة في parser وFSM وقواعد DLU وSQLite ومختبرات الإشارات.

PySide6 يوفر Qt Widgets وGraphics View المناسبة للرسم التفاعلي، وQt for Python يوفر أداة pyside6-deploy لبناء نسخة Windows executable. توثيق Qt الحالي يوصي بها للتوزيع، ويمكنها إخراج standalone أو onefile على Windows. citeturn152249search0turn152249search2

## 2. القرار الأهم: لا نخترع عتادًا

الواجهة ليست رسمًا خياليًا لـ DLU.

التسلسل الذي نعتمد عليه هو:

DLU → Shelf → Module/Board → Port → Subscriber

المراجع التي تم فحصها تصف:
- الـ DLU كوحدة إنهاء وتجميع خطوط المشتركين.
- Shelf بترقيم 0..7 في أمثلة EWSD.
- Module بترقيم 0..15 داخل Shelf في أمثلة EWSD.
- EQN بصيغة DLU-Shelf-Module-Port.
- وحدات SLMA تقليدية ذات 8 دوائر، مع أنواع أخرى ذات 16 منفذًا.
- بطاقات وأنواع أخرى لها سعات مختلفة.

لذلك:
- SLMA8 هي البطاقة التعليمية المرئية الأساسية: Ports 0..7.
- SLMA16 تعرض Ports 0..15.
- CMRL لا نعرض لها 8 منافذ كقاعدة عامة؛ السعة تأتي من نوع البطاقة والمرجع.
- لا نضع بطاقة في موضع لمجرد ملء الفراغ.

## 3. الطبقات

### A. Presentation — PySide6

مسؤولياتها:
- DLU View
- Shelf View
- Module/Card View
- Port/LED View
- Subscriber details
- OMT Terminal
- SYP
- Call Path
- Teaching Labs
- Scenarios

ممنوع:
- تنفيذ SQL من Widget
- كتابة قواعد EQN داخل الواجهة
- افتراض أن كل Card لها 8 ports
- إنشاء نسخة حالة Subscriber مختلفة عن SQLite

### B. Application Layer

Use cases:
- create_subscriber
- cancel_subscriber
- modify_subscriber
- display_subscriber
- display_range
- stat_subscriber
- test_subscriber
- configure_dlu
- diagnose_dlu
- create_command_file
- execute_command_file
- simulate_call

### C. Domain Core

Python modules مستقلة عن PySide6:
- mml/lexer.py
- mml/parser.py
- mml/normalizer.py
- mml/validator.py
- mml/dispatcher.py
- domain/eqn.py
- domain/card_capacity.py
- domain/dlu_state.py
- domain/cpt.py
- domain/call_path.py
- domain/alarms.py
- domain/events.py

### D. Persistence

SQLite repositories:
- ExchangeRepository
- DluRepository
- SlotRepository
- SubscriberRepository
- CptRepository
- AlarmRepository
- CommandFileRepository
- EventLogRepository

### E. Packaging

الهدف النهائي:
- Windows .exe
- ويمكن لاحقًا إضافة installer

نستخدم pyside6-deploy بدل إدخال سلسلة أدوات غير ضرورية. Qt توضح أنه يبني تطبيق PySide6 لسطح المكتب ويخرج .exe على Windows، مع standalone كالوضع الافتراضي الحالي وonefile كخيار صريح. citeturn152249search0turn152249search2

## 4. تدفق MML

OMT Input → Lexer → Parser → Normalizer → Validator → Use Case → SQLite Transaction → Domain Event → UI

مثال:
> cr sub: dn=2233500, eqn=50-1-5-0, lac=021, class=ms, c/s=PB;

بعد النجاح:
1. ينشأ subscriber.
2. يرتبط DN بالـ EQN.
3. يصبح Port 0 في Module 5 بالحالة idle.
4. تتحدث LED.
5. يظهر الأمر في OMT output.
6. يسجل event.

## 5. نموذج الرسم الصحيح

لا نرسم DLU كمجموعة مربعات بلا معنى.

### Level 1 — DLU
- DLU ID
- controller state
- shelves
- alarms

### Level 2 — Shelf
- Modules بمواقعها
- أرقام Module واضحة 0..15 عندما يكون هذا هو ترقيم المرجع

### Level 3 — Module/Card
- اسم البطاقة
- نوعها
- السعة
- الحالة

### Level 4 — Ports
في SLMA8:
- Port 0
- Port 1
- ...
- Port 7

كل Port يمثل خط مشترك واحد.

عند النقر على Port تظهر:
- DN
- EQN
- LAC
- Line State
- Services
- Blocking
- Events

## 6. الألوان

اللون يصف الحالة وليس نوع البطاقة:
- Gray = unassigned
- Green = idle
- Busy = active call
- Yellow = blocked / maintenance
- Red alarm marker = alarm

نوع البطاقة يظهر باسمها، وليس بلونها.

## 7. لا نستخدم صور PCB مزيفة

في النسخة الأولى نرسم representation هندسيًا مبسطًا.

لا ندعي أن الرسم صورة PCB حقيقية.

يمكن لاحقًا عرض صورة مرجعية حقيقية للبطاقة في صفحة معلومات مستقلة، مع ذكر المصدر والترخيص.

## 8. لماذا Python الآن؟

الهدف هو محاكي جامعي Offline قابل للفهم والصيانة، وليس منتج SaaS.

Python + PySide6 يعطي:
- لغة واحدة للمشروع.
- SQLite مباشرة.
- بيئة مناسبة للـ parser والاختبارات.
- Qt Graphics للرسم.
- توافقًا طبيعيًا مع NumPy/Matplotlib عند بناء مختبر الإشارات.
- مسارًا رسميًا للتوزيع عبر pyside6-deploy. citeturn152249search0turn152249search3

هذا أبسط من Tauri للمشروع الحالي مع الحفاظ على نفس المبدأ: Domain Core واحد والواجهة مجرد View للحالة.

### Communications Lab
Stage 5 يضيف communications_lab.py كنواة حسابية مستقلة عن PySide6 وSQLite. الواجهة تستدعي هذه النواة لعرض نماذج تعليمية normalized للموجات، modulation، constellation، وBER دون الادعاء بمحاكاة RF أو قناة فيزيائية كاملة.

## 9. سياسة الاستمرارية

SQLite هي مصدر الحقيقة.

أي تغيير:
MML / Scenario / Maintenance Action → DB → Event → UI

والنسخة النهائية تحفظ قاعدة البيانات في App Data مع Reset وBackup وRestore وSeed Version.

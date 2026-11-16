# DLU — Siemens EWSD Educational Simulator

محاكي تعليمي محلي لمقسم Siemens EWSD ووحدة الخطوط الرقمية DLU، مخصص لمقرر مبادئ الاتصالات على Windows 11.

> القاعدة الأساسية: لا نخترع شكلًا أو سعة أو ترقيمًا للعتاد. الرسم مبسط، لكن DLU/Shelf/Module/Port/EQN/Card Capacity مبنية على المراجع المعتمدة.

## التقنية المعتمدة

**Python 3 + PySide6 + SQLite**

- PySide6: واجهة Windows ورسوم DLU التفاعلية.
- SQLite: الحالة المحلية للمقسم.
- Python Domain Core: MML parser/FSM، EQN، card capacities، CPT، call paths، alarms.
- NumPy/Matplotlib: لاحقًا لمختبر الإشارات.
- pyside6-deploy: إخراج Windows executable.

توصي Qt حاليًا باستخدام pyside6-deploy لتوزيع تطبيقات PySide6، مع standalone أو onefile على Windows. citeturn152249search0turn152249search2

## النموذج الذي يجب أن يراه الطالب

**DLU → Shelf → Module → Port → Subscriber**

مثال:

DLU 50  
Shelf 1  
Module 5  
SLMA8  
Port 0..7

ومثال ربط:

50-1-5-0 → DN 2233500

ترقيم Shelf/Module وصيغة EQN مأخوذة من مراجع EWSD التي تمت مراجعتها. citeturn608198search0turn608198search1

## بطاقات المشتركين

- SLMA8: Ports 0..7.
- SLMA16: Ports 0..15.
- الأنواع الأخرى لا تُفترض لها سعة موحدة؛ السعة تأتي من نوع البطاقة ومرجعها.

لذلك لا يوجد hard-coded rule يقول إن كل Module فيه 8 مستخدمين.

## المبدأ المعماري

**Database → Domain Core → View**

أي أمر:
MML / Scenario / Maintenance
→ validation
→ SQLite
→ event
→ UI

ولا توجد حالة مستقلة داخل الواجهة.

## وثائق المشروع

- docs/00-PROJECT-CHARTER.md
- docs/01-ARCHITECTURE.md
- docs/02-DATABASE-SPEC.md
- docs/03-MML-SPEC.md
- docs/04-UI-UX-WIREFRAME.md
- docs/05-MILESTONES.md
- docs/06-ACADEMIC-TEST-CASES.md
- docs/07-STAGE-01-IMPLEMENTATION.md
- docs/08-HARDWARE-REFERENCE-BASIS.md

## الحالة

**Stage 0 — Foundation & Specification: مكتملة**

الخطوة التنفيذية التالية هي Stage 1:
**Hardware Dataset + SQLite + Seed + tests**

وبعد إثبات صحة النموذج نبدأ MML Core، ثم واجهة DLU.

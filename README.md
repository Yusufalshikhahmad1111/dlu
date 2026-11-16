# DLU — Siemens EWSD Educational Simulator

محاكي تعليمي محلي لمقسم Siemens EWSD ووحدة الخطوط الرقمية DLU، مخصص لمقرر مبادئ الاتصالات على Windows 11.

> هذا المستودع يبدأ من الصفر. هذه المرحلة تثبت التصميم الهندسي قبل إدخال كود التنفيذ، حتى تبقى قاعدة البيانات، مفسر MML، الواجهة البصرية، ومسار المكالمات مبنية على نموذج واحد متماسك.

## القرار التقني

**React + TypeScript + Tauri 2 + SQLite**

- React + TypeScript: بناء واجهة DLU/Shelf/Slot/Port التفاعلية، OMT، SYP، والمختبرات.
- Tauri 2: غلاف سطح مكتب Windows مع إخراج MSI وNSIS setup executable.
- SQLite: الحالة المحلية الكاملة للمقسم.
- TypeScript Domain Core: قواعد العنونة، MML parser/FSM، CPT، المكالمات، والإنذارات تبقى مستقلة عن React.
- Rust داخل Tauri يظل طبقة منصة/تكامل فقط، وليس مكان منطق المقسم.

Tauri يدعم إنشاء مثبتات Windows بصيغة MSI أو setup.exe، ويوفر إضافة SQL تدعم SQLite، وهذا مناسب لطبيعة التطبيق المحلي المطلوب. راجع docs/01-ARCHITECTURE.md.

## المبدأ الأهم

**Database → Switch Core → View**

لا يجوز للواجهة أن تمتلك حالة DLU مستقلة عن قاعدة البيانات. أي أمر MML يغير حالة المقسم يمر عبر نواة المقسم، ثم تُحدّث SQLite، ثم تعكس الواجهة الحالة الجديدة.

## النطاق الأكاديمي

يشمل المشروع تدريجيًا:

1. DLU / Side 0 / Side 1 / DLUC0 / DLUC1.
2. Shelves 0–7 وSlots 0–15.
3. SLMA وSLMA CMRL وSLMD وبطاقات التحكم والتغذية.
4. EQN ↔ DN مع التحقق من السعات.
5. CPT وخطة الترقيم السورية SNNP.
6. MML وCommand Files وFSM.
7. SYP والإنذارات وحالة الصيانة.
8. مسارات المكالمات المحلية/القطرية/الدولية والحظر.
9. مختبر OSI/TCP/UDP.
10. مختبر AM/FM/PM/PAM/PWM/PPM/PCM وASK/FSK/PSK/QPSK/QAM.

## وثائق المشروع

- docs/00-PROJECT-CHARTER.md — الرؤية، الحدود، ومبادئ النجاح.
- docs/01-ARCHITECTURE.md — المعمارية والـ stack وحدود كل طبقة.
- docs/02-DATABASE-SPEC.md — نموذج SQLite والقيود.
- docs/03-MML-SPEC.md — Lexer/Parser/FSM وقواعد الأوامر.
- docs/04-UI-UX-WIREFRAME.md — توزيع الشاشة وتجربة الاستخدام.
- docs/05-MILESTONES.md — مراحل التنفيذ والـ Definition of Done.
- docs/06-ACADEMIC-TEST-CASES.md — سيناريوهات الاختبار الأساسية أمام الدكتور.

## الحالة

**Stage 0 — Foundation & Specification**

المرحلة التالية بعد تثبيت هذه الوثائق هي تنفيذ SQLite schema + seed data + MML domain core واختبارها آليًا قبل بناء الواجهة.

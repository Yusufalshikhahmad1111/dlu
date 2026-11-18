# تقرير تدقيق مستودع DLU — الحالة الحقيقية وما الناقص للوصول إلى 100%

تاريخ التدقيق: 2026-11-18
المستودع: `Yusufalshikhahmad1111/dlu` (فرع `main`، + فرع مفتوح `stage-05-communications-labs`)

---

## 1. ما هو هذا المشروع

**DLU — Siemens EWSD Educational Simulator**: محاكي تعليمي لمقسم Siemens EWSD ووحدة الخطوط الرقمية DLU، مبني بـ **Python 3.12 + PySide6 + SQLite**، موجّه لمقرر مبادئ الاتصالات على Windows 11. المشروع منظم على شكل مراحل (Stage 0 → Stage 7) موثقة بالتفصيل في `docs/05-MILESTONES.md`، مع قاعدة صارمة: لا اختراع لشكل أو سعة أو ترقيم عتاد غير موثّق.

---

## 2. الحالة الفعلية مقابل ما يقوله README

**أهم ملاحظة في هذا التدقيق:** ملف `README.md` في فرع `main` **متأخر عن الواقع**. هو يقول إن آخر حالة مكتملة هي Stage 3 وأن "التالي: Stage 4 — Command Files"، بينما ملفات `docs/` تثبت أن:

| المرحلة | الحالة الموثقة في `docs/05-MILESTONES.md` | موجودة في الكود؟ |
|---|---|---|
| Stage 0 — Foundation & Specification | مكتملة | ✅ |
| Stage 1 — Hardware Dataset + SQLite + First GUI | Prototype runnable | ✅ |
| Stage 2 — Hardware Fidelity + MML Core | Code-complete | ✅ (`db.py`, `mml.py`, `ui.py`) |
| Stage 3 — Call Engine + CPT + Call Path | مكتملة، QA passed | ✅ (`call_engine.py`, `call_ui.py`) |
| Stage 3.5 — UX/UI Redesign | Implemented | ✅ (`theme.py`, `ui_utils.py`) |
| **Stage 4 — Command Files** | **Implemented — QA موجود** | ✅ (`command_files.py`, `command_file_ui.py`) |
| **Stage 5 — Communications Labs** | **قيد الدمج (PR #1 مفتوح)** | ⚠️ موجودة على فرع منفصل فقط |
| Stage 6 — Teaching Scenarios | لم تبدأ رسميًا | ❌ |
| Stage 7 — Packaging & Final Audit | لم تبدأ | ❌ |

**الخلاصة:** المشروع أكثر تقدمًا مما يوحي به README — أربع مراحل كاملة (0–4) موجودة فعليًا في `main` مع تقارير تنفيذ واختبارات، لكن التوثيق الأمامي (README) لم يُحدَّث منذ Stage 3.

---

## 3. اكتشاف هام: طلب دمج (Pull Request) مفتوح لم يُدمج بعد

يوجد **PR #1 — "feat: Stage 5 communications labs"** مفتوح منذ 2026-11-18، من فرع `stage-05-communications-labs` إلى `main`:

- 12 commit، **1467 سطر إضافة / 8 سطر حذف**، 10 ملفات.
- يضيف: `dlu_app/communications_lab.py` (نواة المحاكاة: OSI, TCP/UDP, AM/FM/PM, PAM/PWM/PPM/PCM, ASK/FSK/PSK/QPSK/16-QAM, Constellation, BER) و`dlu_app/communications_ui.py` (تبويب الواجهة)، ويعدّل `dlu_app/ui.py` لدمج التبويب الجديد.
- حالة الدمج: `mergeable: true` لكن `mergeable_state: unstable` — أي أن **فحوصات CI لم تنجح بالكامل بعد** (أو ما زالت معلّقة) على فرع `windows-latest` (py_compile + `tools/ui_static_audit.py` + `pytest`).
- لا يوجد عليه أي مراجعة (review) أو تعليق حتى الآن.

**هذا هو أول عنصر عملي يحتاج عملك:** يجب التأكد من أن CI الخاص بـ PR #1 أصبح أخضر بالكامل، ثم دمجه إلى `main`، ثم تحديث `README.md` و`docs/05-MILESTONES.md` لتعكس أن Stage 5 "مكتملة" وليست "لم تبدأ".

---

## 4. مشاكل وفجوات محددة (غير مرتبطة بالمراحل)

1. **`README.md` غير محدّث** — لا يذكر Stage 4 (موجودة فعلًا) ولا Stage 5 (قيد الدمج). هذا أول شيء يراه أي شخص يفتح المستودع ويعطي انطباعًا خاطئًا عن مدى الاكتمال.
2. **`pyproject.toml` → `[tool.pyside6-project].files` متأخر**: لا يزال يسرد فقط `main.py, dlu_app/__init__.py, dlu_app/db.py, dlu_app/mml.py, dlu_app/ui.py` — وينقصه `call_engine.py`, `call_ui.py`, `command_files.py`, `command_file_ui.py`, `theme.py`, `ui_utils.py`، وقريبًا `communications_lab.py`/`communications_ui.py`. لا يكسر تشغيل `main.py` مباشرة، لكنه يكسر أي استخدام لأدوات Qt Creator / `pyside6-project` على المشروع.
3. **لا يوجد `[build-system]` في `pyproject.toml`** — المشروع غير قابل للتثبيت كحزمة (`pip install .`)، وهذا سيصبح مهمًا في Stage 7 عند التغليف.
4. **Issue/PR tracker فيه عنصر واحد فقط وهو PR #1 نفسه** — لا توجد Issues منفصلة مسجّلة للمشاكل أعلاه؛ يُستحسن فتح Issues رسمية لكل بند في هذا التقرير لتتبعها.

---

## 5. قائمة تدقيق (Checklist) للوصول إلى 100%

### يجب إنجازه أولًا (لإغلاق ما هو جاهز تقريبًا)
- [ ] تشغيل/مراجعة فحوصات CI على PR #1 (`stage-05-communications-labs`) حتى تنجح بالكامل (compile + ui_static_audit + pytest على windows-latest).
- [ ] دمج PR #1 إلى `main` بعد نجاح الفحوصات.
- [ ] تحديث `README.md`: قسم "الحالة" ليعكس Stage 4 و Stage 5 كمكتملتين، وتحديث "التالي" إلى Stage 6.
- [ ] تحديث `[tool.pyside6-project].files` في `pyproject.toml` ليشمل كل ملفات `dlu_app/*.py` الحالية.

### Stage 6 — Teaching Scenarios (لم تبدأ)
- [ ] تنسيق رسمي موحّد لعرض كل سيناريو: commands / affected EQN / expected result / actual result / PASS-FAIL (كما يحدده `docs/05-MILESTONES.md`).
- [ ] سيناريو "Aleppo 8-line expansion" — موجود جزئيًا في README كوصف ("8-Line")، يحتاج تثبيت رسمي ضمن Stage 6.
- [ ] سيناريو "CMRL capacity limit" — موجود جزئيًا (وصف CARD-INCOMPATIBLE في README)، يحتاج تغليف رسمي + تقرير PASS/FAIL.
- [ ] سيناريو "DLU/card maintenance" — موجود جزئيًا (FAULT→MBL→DIAG...)، يحتاج تغليف رسمي.
- [ ] سيناريو "Billing block" — **غير موجود إطلاقًا** في الكود الحالي.
- [ ] سيناريو "International blacklist" — المنطق الأساسي (EVAL=NO blocking) موجود في Call Engine (Stage 3)، لكن لا يوجد سيناريو تعليمي رسمي يعرضه كـ Teaching Scenario.
- [ ] سيناريو "Command file overnight run" — يحتاج الاستفادة من Stage 4 (Command Files) ضمن سيناريو تعليمي كامل.

### Stage 7 — Packaging & Final Audit (لم تبدأ)
- [ ] بناء Windows executable (مثلاً عبر PyInstaller) — لا يوجد ملف `.spec` أو سكربت بناء حاليًا.
- [ ] Installer اختياري (مثلاً Inno Setup) — غير موجود.
- [ ] ميزة Reset / Backup / Restore لقاعدة البيانات SQLite — لم يتم رصدها في `dlu_app/db.py` بشكل صريح؛ تحتاج تأكيد أو إضافة.
- [ ] لقطات شاشة (screenshots) للواجهة النهائية — غير موجودة في `docs/` أو `README.md`.
- [ ] دليل مستخدم (User Manual) منفصل عن README التقني.
- [ ] تقرير اختبار أكاديمي نهائي (Final Academic Test Report) يجمع نتائج كل المراحل.

### صحة عامة / تحسينات مستمرة
- [ ] مزامنة `README.md` مع `docs/05-MILESTONES.md` بعد كل مرحلة مستقبلية مباشرة (لتفادي تكرار نفس فجوة التوثيق).
- [ ] تحديث `pyproject.toml` تلقائيًا أو يدويًا مع كل ملف جديد يُضاف إلى `dlu_app/`.
- [ ] فتح Issues رسمية على GitHub لكل بند أعلاه لتتبع التقدّم بدل الاعتماد على ملف تقرير واحد.

---

## 6. ملخص الأولويات

1. **عاجل:** إغلاق ودمج PR #1 (Stage 5) — العمل شبه جاهز وينتظر فقط نجاح CI والدمج.
2. **سريع وسهل:** تحديث `README.md` و`pyproject.toml` ليعكسا الواقع — لا يحتاج كتابة كود جديد.
3. **متوسط:** بناء Stage 6 بالكامل كسيناريوهات تعليمية موثّقة بصيغة PASS/FAIL.
4. **الأكبر المتبقي:** Stage 7 بالكامل (تغليف Windows، نسخ احتياطي/استرجاع، توثيق مستخدم نهائي) — لم يبدأ أي جزء منه بعد.

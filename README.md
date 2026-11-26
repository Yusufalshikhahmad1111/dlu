# DLU Lab 2.0 — Siemens EWSD Educational Simulator

محاكي تعليمي محلي لمقسم Siemens EWSD ووحدة الخطوط الرقمية DLU، مخصص لمقرر مبادئ الاتصالات على Windows 11.

القاعدة الأكاديمية الأساسية: لا نخترع شكلًا أو سعة أو ترقيمًا للعتاد. الرسم مبسط، لكن DLU/Shelf/Module/Port/EQN/Card Capacity مبنية على Dataset موثق، والمواضع غير المدعومة تبقى UNCONFIGURED.

## الإصدار

DLU Lab 2.0.0

Python 3.12 + PySide6 + SQLite

## المسار الأكاديمي الكامل

Learning Home
→ Hardware
→ OMT / MML
→ Call Path
→ Command Files
→ Communications
→ Scenarios

Instructor / Classroom Mode متاح للتدريس والعرض والإسقاط على الشاشة.

## الوظائف الأساسية

### Hardware

- Exchange → DLU → Side/Controller → Shelf → Module/Card → Port → Subscriber.
- Physical وLogical views.
- Inspector يعرض object/state/EQN/capacity/role/family.
- Maintenance وfault workflow.
- OMT ↔ hardware highlighting.

### OMT / MML

المحرك الحقيقي هو المصدر الوحيد للتنفيذ.

أمثلة:
stat dlu: dlu=50;
disp dlumod: dlu=50, shelf=0, module=15;
disp dlupport: eqn=50-0-15-0;
statport: eqn=50-0-15-0;
cr sub: dlu=50, type=ms, eqn=50-0-15-0, lac=021, dn=2233500;

### Call Path

Origin → CPT → Resource → Switching → Destination

الحالات المرئية تشمل REQUEST وROUTING وRESOURCE وCONNECTED وBLOCKED وRELEASED.

### Command Files

- parser حقيقي؛
- Accepted → Started → Finished → Executed/Failed؛
- HH:MM scheduling؛
- virtual clock؛
- OMT EXECMDFILE integration.

### Communications

- OSI 7-layer;
- TCP vs UDP;
- AM / FM / PM;
- PAM / PWM / PPM / PCM;
- ASK / FSK / PSK / QPSK / 16-QAM;
- constellation visualizer;
- BPSK / QPSK / 16-QAM BER basics.

النماذج normalized وتعليمية وليست محاكاة RF كهربائية كاملة.

### Teaching Scenarios

السيناريوهات الرسمية الستة:

- Aleppo 8-Line Expansion
- CMRL Capacity Limit
- DLU / Card Maintenance
- Billing Block
- International Blacklist
- Command File Overnight Run

المسار:
Objective → Observe → Execute → Diagnose → Fix → Verify → Result

### Instructor / Classroom

- scenario selection;
- reset;
- real scenario execution;
- REVEAL ANSWERS;
- expected vs actual;
- guided demonstration;
- projector mode;
- Morning/Night.

## Student experience

Stage 19 added academic context continuity:

YOU ARE HERE → NEXT

وتم ربط الـbreadcrumb والـtooltips والـaccessible descriptions بالمساحات التعليمية الحالية.

## Data safety

- SQLite live data under %USERPROFILE%\\AppData\\Local\\DLULab.
- Backup uses SQLite backup API and integrity validation.
- Restore uses staged validation and a pre-restore safety backup.
- Reset Demo يعيد الحالة التعليمية المصدرية ويحافظ على حدود الـdataset.

## تشغيل المصدر

run.bat

أو:
py -3.12 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py

الاختبارات:
python -m pip install -r requirements-dev.txt
python -m pytest -q tests

## Windows release

الـrelease الرسمي يستخدم pyside6-deploy بوضع onefile.

بناء محلي:
powershell -ExecutionPolicy Bypass -File tools\\build_windows.ps1

الـrelease build يرفض أي نسخة runtime غير 2.0.0، ثم يشغّل:

- final visual/accessibility QA؛
- packaged version check؛
- packaged smoke-test.

## الأدلة

- User Manual: docs/32-USER-MANUAL.md
- Academic Learning Guide: docs/97-STAGE-20-ACADEMIC-GUIDE.md
- Instructor / Classroom Guide: docs/98-STAGE-20-INSTRUCTOR-GUIDE.md
- Stage 20 Plan: docs/94-STAGE-20-PLAN.md
- Stage 20 Implementation: docs/95-STAGE-20-IMPLEMENTATION-REPORT.md
- Stage 20 Windows QA: docs/96-STAGE-20-WINDOWS-QA.md
- Stage 20 Closeout: docs/99-STAGE-20-CLOSEOUT.md

## Roadmap status

Stage 0 → Stage 19: completed.

Stage 20 — DLU Lab 2.0 Release: final release gate in progress until the Windows package, screenshots and complete regression are re-verified on the release tree.

No stage is closed from code changes alone; the release is closed only after the complete Windows evidence gate is green.

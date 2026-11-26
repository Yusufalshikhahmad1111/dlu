# DLU Lab 2.0.0 — Siemens EWSD Educational Simulator

محاكي تعليمي محلي لمقسم Siemens EWSD ووحدة الخطوط الرقمية DLU، مخصص لمقرر مبادئ الاتصالات على Windows 11.

> القاعدة الأساسية: لا نخترع شكلًا أو سعة أو ترقيمًا للعتاد. الرسم مبسط، لكن DLU/Shelf/Module/Port/EQN/Card Capacity مبنية على Dataset موثق.

## التقنية

Python 3.12 + PySide6 + SQLite

## Hardware-first Training Lab

المسار البصري والوظيفي:

Exchange → DLU → Side/Controller → Shelf → Module/Card → Port → Subscriber → MML

### Physical Mode
- DLU frame
- DLUC0 / DLUC1
- DIUD/PDC training area
- Shelf 0..7
- Module 0..15
- Card faceplates
- Port LEDs

### Logical Mode
DLU → Controller → DIUD → SLM → Port → DN

## Hardware Dataset

البيانات منفصلة عن الواجهة:

- data/hardware_seed.json
- data/references.json
- Source Registry داخل SQLite

### Registry الحالي
- SLMA8 — 8 ports
- SLMA16 — 16 ports
- SLMA64 — 64 ports
- CMRL — 6 ports
- SLMD — digital subscriber module
- TU
- BDE
- BDCG
- DLUC
- DIUD
- RGMG
- DCC

إذا لم يكن Placement موثقًا يبقى UNCONFIGURED.

## Seed الأكاديمي

- DLU 50 / Shelf 0 / Module 15 → SLMA8
- DLU 10 / Shelf 1 / Module 7 → CMRL
- كل DLU يملك Shelf 0..7 وModule 0..15

## OMT ↔ Hardware

أمثلة:

> stat dlu: dlu=50;
> disp dlumod: dlu=50, shelf=0, module=15;
> disp dlupport: eqn=50-0-15-0;
> statport: eqn=50-0-15-0;
> cr sub: dlu=50, type=ms, eqn=50-0-15-0, lac=021, dn=2233500;
> stat sub: lac=021, dn=2233500;
> test sub: lac=021, dn=2233500;
> can sub: lac=021, dn=2233500;

نتيجة MML التي تحتوي EQN أو DLU/Shelf/Module تربط مباشرة بالمجسم.

## Maintenance

FAULT → MBL → DIAG → REMOVE → INSTALL → ACTIVATE → VERIFY

مع سجل hardware_events وMaintenance Timeline داخل الواجهة.

## Communications Labs

تبويب **Communications** يضم:
- OSI 7-layer model.
- TCP vs UDP comparison.
- AM / FM / PM.
- PAM / PWM / PPM / PCM.
- ASK / FSK / PSK / QPSK / 16-QAM.
- QPSK / 16-QAM constellation.
- BPSK / QPSK / 16-QAM BER basics.

النماذج الحسابية normalized وتعليمية وليست محاكاة RF كهربائية كاملة.

## Scenarios

تبويب **Scenarios** يقدّم ستة Teaching Scenarios رسمية موحدة:
- Aleppo 8-Line Expansion.
- CMRL Capacity Limit.
- DLU / Card Maintenance.
- Billing Block.
- International Blacklist.
- Command File Overnight Run.

كل Scenario يعرض:
- commands/actions;
- affected EQN;
- expected result;
- actual result;
- PASS/FAIL.

التنفيذ يعيد استخدام MML وDB وCall Engine وCommand Files الفعلية، ولا ينشئ منطقًا موازيًا للتدريس.

## التشغيل على Windows 11

### Packaged release

Stage 7 produces a Windows onefile executable through Qt for Python `pyside6-deploy`. The packaged executable runs without a Python installation.

### Development

```bat
run.bat
```

أو:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

الاختبارات:

```bat
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```

## الحالة

Stage 0–6: **completed**

Stage 5 — Communications Labs:
- automated release verified;
- 63/63 tests passed at closeout;
- PR #1 merged into \`main\`.

Stage 6 — Teaching Scenarios:
- six formal PASS/FAIL scenarios;
- automated Windows release gate passed;
- 71/71 tests passed at closeout;
- PR #2 merged into \`main\`.

Stage 7 — Packaging & Final Audit: complete.

Stage 18 — Performance & Architecture Cleanup: complete — 139/139 regression, Windows QA passed.

Stage 19 — Final Academic UX Audit: complete — 143/143 regression, Windows QA passed.

Stage 20 — DLU Lab 2.0 Release: final release gate defined for full regression, accessibility/architecture compatibility, academic UX QA, Windows packaging, screenshots, manuals, and final closeout.

**Current release: DLU Lab 2.0.0**.

Stage 13:
- guided Concept → Parameters → Experiment → Visualization → Measurement → Explanation → Challenge workflow;
- improved waveform and constellation readability;
- Live Update, measurement cards, deterministic mini challenges;
- Stage 13 focused tests 6/6 passed;
- full regression and Windows functional/visual QA passed;
- five screenshot artifacts uploaded;
- merged to main at \`7a75926824f7abe6a15d35f9ec374ccff658fb87\`.

Stage 14:
- guided Objective → Observe → Execute → Diagnose → Fix → Verify → Result workflow across all six teaching scenarios;
- scenario-specific hints, diagnosis, recovery guidance and verification;
- clear PASS/FAIL meaning;
- focused tests, full regression and Windows functional/visual QA passed;
- merged to main at \`32d8a9a8397a23398181c7db7eb16203fef0ab8c\`.

Stage 15:
- academic Learn → Practice → Experiment → Challenge → Verify path;
- session-only progression over the six existing learning areas;
- Challenge requires a real PASS from an existing Teaching Scenario;
- Verify requires complete area evidence plus a scenario PASS;
- phase actions open the first missing learning area;
- focused tests 7 passed;
- full regression, Windows functional/visual QA, and DLU CI passed;
- three QA screenshots uploaded;
- merged to main at \`9b01ec4725f89c7c5a7409126dee48bc73774c6c\`.

Next planned stage: **Stage 16 — Instructor / Classroom Mode**.


Stage 16:
- separate Instructor / Classroom workspace;
- six existing teaching scenarios selectable from the real scenario catalog;
- Reset delegates to the existing demo reset lifecycle;
- expected/actual and PASS/FAIL remain hidden until explicitly revealed;
- guided demonstration reveals the existing verified scenario result one step at a time;
- projector-friendly classroom view with Morning/Night support;
- Stage 16 focused tests 7/7 passed;
- full regression 129/129 passed;
- Windows functional/visual QA passed with five screenshots;
- merged to main via PR #17.

Next planned stage: **Stage 18 — Performance & Architecture Cleanup**.

Stage 17:
- WCAG 2.2-oriented desktop accessibility hardening;
- visible keyboard focus and deterministic tab order;
- accessible names/descriptions and technical tooltips;
- explicit Hardware empty state;
- target-resolution QA at 1280×720, 1366×768, 1600×900 and 1920×1080;
- Morning/Night contrast and focus regression checks;
- Instructor PASS/FAIL answer visibility remains hidden until REVEAL ANSWERS;
- Stage 17 focused tests 5/5 passed;
- Stage 16 compatibility tests 7/7 passed;
- full regression 134/134 passed;
- Windows accessibility/resolution QA passed;
- merged to main via PR #18 at 6d29fa93c7d9f80a3160590554481c78aedaa9e0.


## DLU Lab 2.0 learning guides

- `docs/32-USER-MANUAL.md` — user manual
- `docs/94-DLU-LAB-2.0-ACADEMIC-GUIDE.md` — student academic guide
- `docs/95-DLU-LAB-2.0-INSTRUCTOR-GUIDE.md` — instructor/classroom guide

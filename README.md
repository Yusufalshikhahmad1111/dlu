# DLU — Siemens EWSD Educational Simulator

محاكي تعليمي محلي لمقسم Siemens EWSD ووحدة الخطوط الرقمية DLU، مخصص لمقرر مبادئ الاتصالات على Windows 11.

> القاعدة الأساسية: لا نخترع شكلًا أو سعة أو ترقيمًا للعتاد. الرسم مبسط، لكن DLU/Shelf/Module/Port/EQN/Card Capacity مبنية على المراجع المعتمدة.

## التقنية

**Python 3.12 + PySide6 + SQLite**

Qt توثق PySide6 كربط Python الرسمي مع Qt، وتوفر أدوات سطح المكتب للرسم التفاعلي. وللتوزيع على Windows نستخدم pyside6-deploy.

## النموذج الذي يراه الطالب

**DLU → Shelf → Module → Port → Subscriber**

مثال:

- DLU 50
- Shelf 1
- Module 5
- SLMA8
- Port 0..7

وربط مثال:

`50-1-5-0 → DN 2233500`

ترقيم Shelf/Module وصيغة EQN مأخوذة من مراجع EWSD التي تم توثيقها في `docs/08-HARDWARE-REFERENCE-BASIS.md`.

## ما يعمل الآن

- SQLite محلية تُنشأ تلقائيًا في %LOCALAPPDATA%\DLULab\dlu_lab.sqlite3.
- ALE1 مع DLU 10 وDLU 50.
- 8 Shelves لكل DLU.
- 16 Module positions لكل Shelf.
- مواضع غير موثقة تبقى UNCONFIGURED.
- SLMA8, SLMA16, CMRL, SLMD كأنواع بطاقة مع سعة صريحة.
- DLU overview.
- Shelf drill-down.
- Module/card drill-down.
- Port 0..N حسب نوع البطاقة.
- DN ↔ EQN inspection.
- OMT terminal.
- DISP, STAT, TEST, CR, CAN, MOD, CONF, DIAG.
- case-insensitive MML.
- compact command aliases مثل CRSUB: وDISPSUB:.
- quick scenarios.
- history بالأسهم Up/Down.
- basic SYP indicators.
- regression tests للنواة.

## التشغيل على Windows 11

يفضل Python 3.12.

التشغيل الأسهل:

    run.bat

أو يدويًا:

    py -3.12 -m venv .venv
    .venv\Scripts\activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python main.py

اختبارات النواة:

    python -m pip install pytest
    python -m pytest -q tests

## أوامر أول تجربة

    > disp dlu: dlu=50;
    > disp slot: dlu=50, shelf=1, module=5;
    > cr sub: dn=2233500, eqn=50-1-5-0, lac=021, class=ms, c/s=PB;
    > disp sub: dn=2233500;
    > stat sub: dn=2233500;
    > mod sub: dn=2233500, line=busy;
    > mod sub: dn=2233500, line=idle;
    > can sub: lac=021, dn=2233500;

اختبار شرط التشخيص:

    > diag dlu: dlu=10;
    > conf dlu: dlu=10, dluc0=y, ost=mbl;
    > diag dlu: dlu=10;

## الحالة

**Stage 1 — first runnable GUI/core: implemented**

النسخة الحالية هي أول Prototype تشغيلي حقيقي. الخطوة التالية هي توسيع Hardware Dataset وفق المصادر قبل إضافة مؤثرات بصرية أو بطاقات غير موثقة، ثم توسيع MML وSYP وCall Path.

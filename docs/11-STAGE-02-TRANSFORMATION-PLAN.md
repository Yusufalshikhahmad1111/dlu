# 11 — Stage 2 Transformation Plan: Hardware Fidelity

## Vision

هذه ليست مرحلة تجميل الواجهة.

الهدف هو تحويل DLU Lab من Prototype يعمل إلى مختبر بصري يجعل الطالب يفهم العتاد قبل أن يكتب MML.

المسار النهائي:

Exchange → DLU → Side / Control → Shelf → Module/Card → Ports → Subscriber → MML

القاعدة:

> لا نرسم عنصرًا كحقيقة Hardware إلا إذا كان له مصدر أو تعريف موثق في Dataset.

---

## 1. المصدر الأكاديمي الأول

المادة الجامعية هي المرجع الأول.

تثبت المحاضرات:
- مكونات DLU الأساسية: SLMA, SLMD, TU, BDE, BDCG, DLUC, RGMG, DCC.
- وجود التضاعف والـHandshake بين Active وStandby.
- SLMA/COS = 8 ports.
- CMRL = 6 ports.
- وجود SLMA بأعداد 8 و16 و64.
- EQN = DLU-Shelf-Module-Port.
- Shelf = 0..7.
- Module = 0..15.
- أمثلة MML لإنشاء ثمانية مشتركين على 50-0-15-0..7.
- خطوات استبدال بطاقة معطلة من وضع الصيانة حتى إعادة الخدمة.

المراجع الخارجية تستخدم فقط لسد التفاصيل التي لا تكفي المحاضرات لوصفها.

---

## 2. النتيجة البصرية المطلوبة

بدل الشكل الحالي:

Shelf row → small square → A8P

سنصل إلى:

### Level A — Exchange
- ALE1
- DLU inventory
- system state
- SYP alarms
- OMT

### Level B — DLU Cabinet / Frame
- frame/chassis
- labels
- control area
- Side 0
- Side 1
- DLUC0
- DLUC1
- DIUD/PDC area
- service/control modules
- shelves

لن ندعي أن الرسم هو CAD/PCB صناعي دقيق؛ هو front-elevation training model مبني على الوظائف والمكونات الموثقة.

### Level C — Shelf
- metal frame
- left/right rails
- backplane impression
- slot numbering 0..15
- card faceplates
- handles
- status LEDs
- card labels

### Level D — Module/Card
فتح Module يحول الشاشة من مربع إلى بطاقة:
- faceplate
- card name
- source-backed type
- maintenance state
- slot address
- card capacity
- port LEDs

### Level E — Ports
مثلاً SLMA8:

0 1 2 3 4 5 6 7

كل منفذ:
- LED
- port number
- DN
- EQN
- line state
- subscriber icon
- click target

---

## 3. نقلة نوعية: وضعان للعرض

### Physical Mode
يرى الطالب ما يشبه معدات المقسم:

Rack / Shelf / Card / Port

مناسب للشرح أمام الدكتور.

### Logical Mode
يرى الطالب:

DLU → DLUC → DIUD → SLM → Port → DN

مع خطوط العلاقات والحالة.

زر واضح:

PHYSICAL | LOGICAL

وهذا يفصل كيف تبدو القطعة عن كيف تعمل.

---

## 4. بطاقة SLMA8 كـ Hero Module

نبدأ ببطاقة واحدة كاملة الجودة بدل رسم عشرات البطاقات بشكل سطحي.

عند فتح SLMA8 تظهر بطاقة كاملة:

SIEMENS EWSD
SLMA — ANALOG SUBSCRIBER LINE MODULE
EQN: 50-1-5

PORT 0 — DN — IDLE
PORT 1 — DN — IDLE
PORT 2 — DN — BUSY
...
PORT 7 — UNASSIGNED

CARD: ACT   TEST: PASS

الرسومات Stylized، بينما الاسم والسعة والحالات حقيقية وفق Dataset.

---

## 5. Source-backed Hardware Dataset

ننقل Hardware من hard-coded Python إلى Dataset منظم.

مقترح:

hardware_sources
hardware_models
dlu_units
dlu_sides
shelves
modules
ports
maintenance_states
hardware_events

لكل Card/Unit:
- canonical_name
- display_name
- family
- unit_role
- port_count
- port_start
- port_end
- allowed_subscriber_types
- reference_id
- source_url
- source_note
- visual_profile

أمثلة أولية:
- SLMA8
- SLMA16
- SLMA64
- CMRL
- SLMD
- TU
- BDE
- BDCG
- RGMG
- DCC
- DLUC
- DIUD

إذا لم نملك placement موثقًا: UNCONFIGURED.

---

## 6. Installation / Replacement يصبح تفاعليًا

المحاضرة نفسها تعطي سيناريو استبدال بطاقة معطلة.

نضيف Maintenance Mode:

ENTER MAINTENANCE → DIAGNOSE → REMOVE CARD → SELECT REPLACEMENT → INSERT → ACTIVATE → VERIFY

ويُظهر النظام كل خطوة في Timeline.

هذا أفضل من تغيير قيمة في DB فقط.

---

## 7. Card Library

لوحة Hardware Library تعرض:

Type | Ports | Role | Source | Status

SLMA8 | 8 | Analog subscribers | Course | verified
SLMA16 | 16 | Analog subscribers | Course | verified
SLMA64 | 64 | Analog subscribers | Course | verified
CMRL | 6 | Coin/metering | Course | verified
SLMD | — | Digital/ISDN | Course | verified
TU | — | Test | Course | verified

والأنواع الأخرى تضاف فقط عندما نجد مصدرًا.

---

## 8. Reference Viewer

عند الضغط على HARDWARE REFERENCE تظهر:
- اسم الوحدة
- الوظيفة
- السعة
- EQN impact
- source
- source excerpt
- reference image إن وجدت
- What the student should learn

وبذلك يستطيع الطالب والدكتور معرفة مصدر كل معلومة Hardware من داخل البرنامج.

---

## 9. Visual language

### Hardware condition
- Gray: unconfigured
- Steel: installed/inactive
- Green: ACT
- Yellow: MBL / blocked
- Red: fault
- Blue: test / diagnostic

### Subscriber condition
- Gray: unassigned
- Green: idle
- Amber: ringing
- Blue pulse: active data/test
- Red pulse: busy/fault
- Yellow: blocked

### Alarm badge
- CRITICAL
- MAJOR
- MINOR

---

## 10. Physical interactions

Click → يفتح الوحدة.
Double Click → Zoom into hardware.
Hover → Tooltip فيه EQN/card type/port count/state.
Right Click → Display / Stat / Test / Configure / Maintenance / Replace / Reference.

Drag & Drop لا يستخدم للزينة:
- السحب من Hardware Library إلى Slot مسموح فقط عندما تكون العملية موثقة ومسموحة.
- إذا كان Slot غير متوافق، يظهر سبب الرفض.

---

## 11. OMT يجب أن يصبح مرتبطًا بالواجهة

لا يبقى OMT Terminal مستقلًا.

مثلاً عند تنفيذ:

stat sub: lac=052, dn=420800;

النتيجة:
- الـPort المناسب يضيء.
- EQN يظهر.
- Details panel يفتح.

وبالعكس: Click Port 0 → يظهر EQN وDN ثم زر COPY MML يولد الأمر المناسب.

---

## 12. DLU visual architecture

نفصل الرسم عن منطق التطبيق:

domain/
  hardware/
  dlu/
  cards/
  ports/

ui/
  hardware/
    dlu_scene.py
    shelf_scene.py
    module_scene.py
    port_panel.py
    card_renderer.py

data/
  hardware_seed.json
  references.json

الرندر يأخذ Dataset ولا يعرف تفاصيل MML.

---

## 13. Stage 2 sub-milestones

### 2.1 — Reference Freeze
- جمع ما تثبته المحاضرات.
- تثبيت Card Registry.
- تثبيت DLU/Shelf/Module/EQN rules.
- توثيق كل Card source.
- إنشاء hardware_seed.json.
DoD: لا يوجد Card Type بدون source/status.

### 2.2 — DLU Frame Renderer
- cabinet/frame.
- sides.
- controller blocks.
- shelves.
- physical labels.
- zoom hierarchy.
DoD: DLU 50 يظهر كجهاز تدريبي وليس Grid.

### 2.3 — Shelf Renderer
- metal frame.
- 16 slot positions.
- card faceplates.
- slot numbers.
- hover/click/selection.

### 2.4 — Hero Card
- SLMA8 renderer.
- 8 LEDs.
- port labels.
- subscriber mapping.
- state animation.

### 2.5 — Card Registry Expansion
- SLMA16.
- SLMA64.
- CMRL.
- SLMD.
- TU.
- service/control units.
- source badges.

### 2.6 — Maintenance Workflow
- fault inject.
- mbl.
- diag.
- remove.
- insert.
- act.
- verify.
- alarm lifecycle.

### 2.7 — OMT ↔ Hardware Link
MML command highlights affected hardware.

### 2.8 — Visual Audit
اختبار:
- 1366×768
- 1600×900
- 1920×1080
- 125% Windows scaling
- mouse zoom
- keyboard navigation
- no hidden modules
- no orphaned state

---

## 14. What will NOT be done

لن نضيف:
- 3D engine.
- photorealistic cabinet.
- invented PCB layouts.
- random card placements.
- fake Siemens logos/labels as if factory drawings.
- hardware details بلا source.

المشروع يحتاج engineering credibility وليس cinematic graphics.

---

## 15. Acceptance Scenario — الدكتور

الهدف أن يستطيع الدكتور:
1. يفتح ALE1.
2. يختار DLU 50.
3. يرى DLU كـHardware.
4. يدخل Shelf 0.
5. يرى Modules 0..15.
6. يختار Module 15.
7. يرى SLMA8.
8. يرى Ports 0..7.
9. يشغل 8-Line Scenario.
10. يرى LEDs تتحول إلى Idle.
11. يضغط Port 0.
12. يظهر EQN=50-0-15-0.
13. يظهر DN.
14. يفتح OMT.
15. ينفذ STAT/DISP.
16. ينتقل Highlight إلى نفس Port.
17. يجرب TEST.
18. يدخل Maintenance.
19. يعمل Diagnostic.
20. يستبدل البطاقة.
21. يعيدها ACT.
22. يتأكد أن SYP/alarms رجعت للحالة الصحيحة.

إذا تم هذا السيناريو بسلاسة، تصبح المرحلة نقلة نوعية حقيقية.

---

## 16. Definition of Done

Stage 2 لا تعتبر مكتملة عندما تبدو الواجهة أجمل.

تكتمل فقط عندما:
- Hardware hierarchy واضحة.
- Dataset source-backed.
- Module positions لا تختفي.
- Card capacities صحيحة.
- SLMA8/16/64 وCMRL مختلفة فعليًا.
- Physical وLogical modes يعملان.
- MML مرتبط بصريًا بالhardware.
- Maintenance workflow يعمل.
- Source viewer موجود.
- Regression tests تغطي Hardware rules.
- العرض الأكاديمي الكامل يعمل من البداية للنهاية.

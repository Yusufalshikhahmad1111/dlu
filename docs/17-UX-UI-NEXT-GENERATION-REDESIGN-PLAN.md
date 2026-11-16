# DLU Lab — Next-Generation UX/UI Redesign Plan

## Purpose

هذه الوثيقة تحدد نقلة UX/UI شاملة بناءً على واجهة Windows الحالية وصورة التشغيل التي تم فحصها. الهدف تحسين العرض والتفاعل فقط، مع الحفاظ على منطق Stage 1–3 وقاعدة البيانات وMML وCall Engine كما هي.

الأهداف:
- جعل مكان كتابة MML واضحًا وثابتًا دائمًا.
- تقليل ازدحام الأزرار والبيانات.
- تحويل الواجهة من developer dashboard إلى telecommunications teaching lab.
- اعتماد ألوان Space/Futuristic أكثر إشراقًا مع بقاء الواجهة أكاديمية.
- جعل hardware وports وCall Path هي العناصر البصرية الأساسية.
- إزالة العناصر المتكررة أو قليلة القيمة من الواجهة الرئيسية.

## 1. Current UI Audit

### Critical issue: MML input is visually lost

منطقة OMT الحالية تعطي الـterminal معظم الارتفاع، وخانة الأمر في الأسفل تصبح سهلة الاختفاء أو الخروج من مساحة الرؤية.

الإصلاح المطلوب:
- Terminal output قابل للتمرير مستقلًا.
- Command dock ثابت في أسفل OMT.
- command input وEXECUTE/SEND يظلان ظاهرين دائمًا.
- لا يسمح لزيادة output بإخفاء composer.

الشكل المستهدف:

OMT HEADER
TERMINAL OUTPUT
TERMINAL OUTPUT
TERMINAL OUTPUT
COMMAND DOCK
> command input                              SEND

## 2. Visual Direction

الهوية الجديدة:

DLU LAB — Space Telecommunications Laboratory

الفكرة هي مختبر اتصالات مستقبلي، وليس لعبة أو لوحة إدارة.

العناصر البصرية:
- deep-space background.
- luminous cyan/blue/violet signals.
- mint healthy state.
- amber warning/maintenance.
- coral/red fault.
- subtle glow.
- glass/metal panels.
- thin signal traces.
- large readable labels.

## 3. Color System

| Token | Purpose | Proposed value |
|---|---|---|
| SPACE-950 | application background | #050914 |
| SPACE-900 | main workspace | #08111F |
| SPACE-850 | panels | #0C1728 |
| SPACE-800 | elevated panels | #102033 |
| BORDER | normal borders | #28435E |
| TEXT | primary text | #F3F8FF |
| MUTED | secondary text | #8FA6BD |
| CYAN | signal/information | #40D9FF |
| SKY | navigation/active link | #66A8FF |
| VIOLET | digital/advanced path | #9B7BFF |
| MINT | healthy/connected | #39E6A5 |
| AMBER | warning/maintenance | #FFC857 |
| CORAL | fault/blocked | #FF6577 |

قاعدة: اللون يصف الحالة، ولا نلون كل شيء بلا معنى.

## 4. Main Layout

اعتماد أربع مناطق واضحة:

1. Header: Brand + DLU + Mode + System State.
2. SYP signal rail.
3. Main workspace: Hardware يسار + Workbench يمين.
4. Context/educational status.

القراءة الطبيعية للطالب:

Where am I? → What am I viewing? → What can I do? → What happened?

## 5. Header

إبراز:
- DLU LAB.
- Siemens EWSD · Communications Training Lab.
- DLU selector.
- PHYSICAL / LOGICAL.
- SYSTEM ACT.

اجعل SYSTEM ACT chip واضحًا مع glow خفيف فقط.

## 6. SYP

الإبقاء عليه لأنه مهم أكاديميًا، لكن تحويله إلى signal dashboard:

CRITICAL 0 | MAJOR 0 | MINOR 0 | PDC 0/120 | PATH IDLE

كل عنصر يحتوي icon + label + value + semantic color.

## 7. Hardware Navigator

تقليل كثافة الشريط الحالي.

المطلوب:
- breadcrumb واضح: DLU 50 / SHELF 0 / MODULE 15 / SLMA8.
- DLU / Shelf / Module selectors compact.
- لا تكرر Open DLU/Open Shelf/Open Module إذا كان الاختيار والـdrill-down يكفيان.

## 8. Remove Visual Clutter

العناصر التي ينبغي إزالتها من المنطقة الرئيسية أو نقلها إلى secondary actions:
- Fit كزر كبير دائم.
- Open DLU/Open Shelf/Open Module كأزرار مستقلة عند وجود navigator فعال.
- Back عندما لا توجد navigation history حقيقية.
- Hardware Library من main toolbar إلى secondary action.
- Reset Demo من الأفعال اليومية إلى menu/secondary action.
- Reference وadvanced maintenance من الصف الرئيسي.

العناصر التي تبقى بارزة:
- DLU selector.
- PHYSICAL / LOGICAL.
- System state.
- MML composer.
- primary teaching labs.
- Call Path.

## 9. Teaching Scenarios

الصف الحالي [8-Line] [CMRL] [Maintenance] [Inspect] يبدو كسطر developer buttons.

استبداله بمنطقة LAB ACTIONS.

Primary:
- 8-LINE LAB.
- CMRL LAB.

Secondary:
- Maintenance.
- Inspect.

كل Lab card يشرح الهدف قبل الزر.

8-LINE LAB
Create 8 subscriber lines
DLU → Shelf → Module → Ports 0..7
START

CMRL LAB
Demonstrate 6-port capacity
Ports 0..5 + rejected Port 6
START

## 10. OMT

OMT هو أهم نقطة تصحيحية في هذه الواجهة.

المطلوب:
- terminal scroll مستقل.
- composer ثابت في أسفل panel.
- input أكبر.
- cyan focus border.
- monospace technical font.
- history shortcuts.
- واضح أين يبدأ الأمر وأين تظهر النتيجة.

الأمر لا يجب أن يختفي أو ينضغط بسبب حجم terminal.

## 11. Call Path

تحويل Call Path من boxes عادية إلى signal-flow laboratory.

LOCAL:
DLU 50 → SN → DLU 50

NATIONAL:
DLU 50 → LTG → SN → LTG → DLU-LAC052

INTERNATIONAL:
DLU 50 → LTG → SN → International Gateway

BLOCKED:
DLU → CPT → BLOCKED / BLACK LIST

المسار النشط يستخدم luminous signal line بسيطة.
المسار المحظور يتوقف بصريًا عند نقطة الرفض.

## 12. Hardware Visualization

DLU workspace يجب أن يكون visual hero.

### Module
إظهار:
MODULE 15
SLMA8
8 PORTS

### Ports
Port 0..7 أو حسب السعة، بحجم يمكن قراءته في العرض الصفّي.

## 12.5 DLU Visual Hardware Redesign — Appearance Only

هذه المرحلة مخصصة حصريًا لتطوير **الشكل البصري للعتاد** دون حذف أو إعادة تعريف أي عنصر موجود.

### الهدف

تحويل تمثيل:
- DLU
- Shelf / Rack
- Module / Card
- Port area

من مجموعة مستطيلات ومربعات مسطحة إلى **رسم هندسي بصري أقرب إلى جهاز اتصالات حقيقي ومختبر جامعي حديث**.

### قاعدة أساسية

**Appearance-only change.**

ممنوع في هذا البند:
- حذف أي DLU.
- حذف أي Shelf.
- حذف أي Module.
- حذف أي Port.
- تغيير أرقام DLU/Shelf/Module/Port.
- تغيير EQN.
- تغيير Card Capacity.
- تغيير MML.
- تغيير Call Engine.
- تغيير navigation أو click behavior.
- تغيير source-backed hardware rules.

كل ما هو موجود حاليًا يبقى موجودًا؛ الذي يتغير هو طريقة الرسم والعرض فقط.

### DLU Frame

بدل صندوق كبير مسطح، يُرسم DLU كـ **rack / chassis** هندسي:

- outer frame واضح.
- top identification plate.
- side rails.
- screw/bolt details بسيطة.
- ventilation/technical panel details خفيفة.
- controller area مميزة بصريًا.
- shelf bays مرتبة داخل الـrack.
- status lights صغيرة.
- depth/shadow وهمية خفيفة لإعطاء إحساس ثلاثي الأبعاد بدون تحويله إلى 3D engine.

الـDLU ID يبقى بارزًا مثل:

DLU 50
DIGITAL LINE UNIT
SYSTEM ACT

### Shelf / Rack

كل Shelf يجب أن يبدو كـ **rack drawer / equipment bay** بدل صف مستطيلات.

لكل Shelf:
- frame معدني بصري.
- رقم Shelf على left rail.
- inner mounting area.
- separators بين module positions.
- subtle depth/shadow.
- active/inactive visual state.

Shelf 0..7 تبقى كلها كما هي.

### Module / Card

الموديول لا يبقى مجرد مربع مكتوب داخله SLMA8.

بدله يصبح **front faceplate** هندسية:

- top label strip.
- card identifier.
- screw/fastener details.
- connector region.
- status LED cluster.
- port bank.
- small technical markings.
- تختلف faceplate بصريًا حسب family/card type بدون تغيير أي capacity أو behavior.

أمثلة:

SLMA8:
- faceplate أوضح.
- 8 port indicators مرتبة كـconnector bank.
- card name + 8P.

SLMA16:
- نفس الهوية البصرية.
- 16 ports مرتبة بشكل مناسب.

SLMA64:
- dense professional port bank.
- layout يستغل المساحة بدل 64 مربعًا كبيرًا.

CMRL:
- شكل faceplate مختلف بصريًا عن SLMA.
- 6 ports فقط.
- إبراز نوع البطاقة، لا اختراع شكل hardware جديد غير موثق.

### Port Rendering

المنافذ تتحول من مربعات صغيرة متشابهة إلى **connector/LED units**:

- numbered port.
- status LED.
- tiny line/connector graphic.
- hover glow.
- selected state ring.
- BUSY pulse.
- BLOCKED warning marker.
- EMPTY/UNASSIGNED appearance.

الرقم يبقى واضحًا، لكن visual object يصبح أكثر واقعية.

### Visual Depth

استخدام:
- layered panels.
- bevel-like borders.
- soft inner shadows.
- thin highlights.
- metallic gradients خفيفة.
- cyan/blue signal accents.

بدون:
- photo-realistic fake PCB.
- مبالغة 3D.
- heavy neon.
- animation دائم.

### Physical Relationships

الرسم يجب أن يجعل الطالب يرى بصريًا:

DLU
↓
SHELF
↓
MODULE / CARD
↓
PORTS

مع الحفاظ على نفس click/drill-down الموجود.

### Logical Mode

لا يتغير المنطق.

نفس العناصر والعلاقات الحالية تبقى موجودة، لكن الخطوط والعقد تصبح أكثر أناقة:

- controller node.
- DIUD node.
- SLM/card node.
- port endpoints.
- signal traces.

المسار يصبح أقرب إلى **technical system diagram** بدل boxes عادية.

### Hardware Interaction Preservation

كل interaction الحالي يجب أن يبقى:

- click.
- double click.
- context menu.
- drag/drop card installation.
- selected module.
- selected port.
- OMT focus.
- reference viewer.
- maintenance actions.

التغيير البصري لا يجوز أن يكسر أي منها.

### Performance Rule

الرسم الجديد يجب أن يبقى Qt Graphics View-friendly.

يجب تجنب:
- آلاف العناصر الزخرفية غير الضرورية.
- animations مستمرة لكل port.
- heavy image assets لكل module.
- real-time effects التي تضعف الأداء.

### Visual QA

لكل مستوى يتم فحص:

1. DLU frame.
2. Shelf rack.
3. Module faceplate.
4. Port bank.
5. selected state.
6. busy state.
7. blocked state.
8. maintenance state.
9. drag/drop target.
10. logical mode.

### Success Test

عند النظر إلى الواجهة يجب أن يشعر الطالب أنه ينظر إلى:

**equipment rack → shelf → telecom card → ports**

وليس:

**grid of rectangles**.

وفي جميع الحالات تبقى نفس البيانات، نفس الوظائف، نفس العناوين، ونفس السلوك؛ الاختلاف هو **visual representation فقط**.

## 13. Port State Language

لا نعتمد على اللون وحده.

IDLE = dot + IDLE
BUSY = dot + BUSY
BLOCKED = dot + BLOCKED
EMPTY = hollow dot + EMPTY

## 14. Educational Microcopy

بدل عرض المصطلحات التقنية فقط، نعرض المصطلح + المعنى.

UNCONFIGURED
EMPTY MODULE
No card installed

OST ACT
OPERATING
ACT

EVAL=NO
BLOCKED BY CPT
EVAL = NO

## 15. Typography

- Main title: 32–36px.
- Section title: 18–22px.
- Primary controls: 14–16px.
- Technical values: 13–15px.
- Terminal: Cascadia Mono / Segoe UI Mono عندما يكون متاحًا.
- لا تستخدم 8–9px للمعلومات المهمة.

## 16. Space Theme

مسموح:
- subtle stars/texture.
- radial glow خلف workspace.
- thin signal lines.
- restrained cyan/violet gradients.
- short signal pulses.

ممنوع:
- cartoon planets.
- giant neon text.
- constant background animation.
- game-style badges.
- decorative effects تنافس hardware.

Space is atmosphere, not content.

## 17. Information Hierarchy

Level 1: System
DLU / System State / SYP

Level 2: Hardware
Shelf / Module / Port

Level 3: Action
OMT / Call Path / Teaching Lab

Level 4: Details
Reference / Events / Metadata / advanced maintenance

Level 4 يجب ألا ينافس Level 1–3 بصريًا.

## 18. Responsive Windows

دعم واضح لهذه الدقات:
- 1280×720
- 1366×768
- 1600×900
- 1920×1080

عند التضييق:
- تصغير labels الثانوية.
- collapse secondary actions.
- إبقاء MML composer ظاهرًا.
- إبقاء primary labs ظاهرًا.
- الحفاظ على readability للhardware.

## 19. Workbench Tabs

الترتيب المقترح:
OMT
CALL PATH
HARDWARE

OMT أولًا لأنه command surface.
Call Path ثانيًا لأنه Stage 3 teaching view.
Hardware للتفاصيل العميقة.

## 20. Context Card

بدل إظهار metadata كثيرة دائمًا، استخدم card صغيرة:

CURRENT OBJECT
DLU 50
Shelf 0
Module 15
SLMA8 · 8 PORTS
STATUS · ACT
REFERENCE

## 21. Remove Redundancy

احذف أو قلل تكرار:
- DLU ID في أكثر من موضع كبير.
- repeated CTRL labels.
- repeated Open buttons.
- repeated hardware metadata.
- duplicated navigation.
- oversized empty terminal regions.
- advanced maintenance controls من الصف الرئيسي.

القاعدة:
Show information where it helps the current task.

## 22. Interaction Flow

Student flow:
Select DLU
↓
Select Shelf
↓
Select Module
↓
Inspect Card
↓
Inspect Ports
↓
Run MML / Lab
↓
Observe Result

لا يجب إجبار الطالب على فهم العلاقات الداخلية للwidgets.

## 23. Empty States

بدل:
No module selected.

استخدم:
SELECT A MODULE
Choose DLU → Shelf → Module
Then inspect ports, hardware state, or run MML.

## 24. Feedback Layers

كل action مهم يحتاج:
1. Immediate visual state.
2. Technical result.
3. Educational explanation.

مثال:
Port 6 rejected
CARD-INCOMPATIBLE
CMRL provides ports 0–5 only.

## 25. Classroom Projection

- normal text >= 12px.
- high contrast.
- no color-only states.
- large status indicators.
- clear focus states.
- critical values readable from projection distance.

## 26. Animation Policy

Allowed:
- signal pulse.
- port state transition.
- short status glow.
- active-call movement.

Not allowed:
- constant animated background.
- bouncing controls.
- distracting particles.
- long decorative animations.

## 27. Implementation Order

UI-01 Layout correction
- restore visible MML composer.
- fixed OMT command dock.
- solve clipping/vertical overflow.

UI-02 Clutter removal
- remove redundant buttons.
- move advanced tools to secondary actions.
- simplify navigator.

UI-03 Design system
- color tokens.
- spacing.
- typography.
- button hierarchy.
- semantic states.

UI-04 Hardware visualization
- larger shelves/modules.
- better ports.
- clearer state indicators.

UI-05 Teaching labs
- redesign 8-Line.
- redesign CMRL.
- redesign Maintenance.
- redesign Inspect.

UI-06 Call Path
- signal-flow visual.
- active route.
- blocked route.
- resource indicator.

UI-07 OMT
- terminal hierarchy.
- fixed composer.
- command history.
- result blocks.

UI-08 Responsive QA
- 1280×720.
- 1366×768.
- 1600×900.
- 1920×1080.

UI-09 Classroom QA
- projection readability.
- click discoverability.
- student comprehension.
- professor demo flow.

## 28. Must Not Change

The redesign must not change:
- SQLite as source of truth.
- MML behavior.
- EQN semantics.
- DLU/Shelf/Module addressing.
- hardware capacities.
- CPT logic.
- Call Engine behavior.
- PDC accounting.
- Stage 1/2/3 test contracts.
- source-backed hardware rule.

UX/UI changes are presentation changes unless explicitly approved otherwise.

## 29. Definition of Done

- MML input is always visible.
- OMT output scrolls independently.
- no primary control is hidden below the viewport.
- teaching scenarios look like teaching tools.
- primary actions are obvious.
- hardware modules and ports are readable.
- state colors are consistent.
- color is not the only state indicator.
- Call Path is understandable without reading code.
- PDC usage is visible during calls.
- interface feels bright, modern, futuristic, and student-friendly.
- space theme remains professional.
- application still feels like an academic telecommunications laboratory.
- existing Stage 1–3 behavior remains unchanged.

## 30. Success Test

طالب جديد يجب أن يستطيع الإجابة من الشاشة دون شرح:
1. أين أكتب MML؟
2. أي DLU أرى؟
3. أي Shelf وModule؟
4. ما هي البطاقة؟
5. ما هي المنافذ المتاحة؟
6. ماذا حدث بعد الضغط على Lab؟
7. أين ذهبت المكالمة؟
8. لماذا رُفضت المكالمة؟
9. كم قناة PDC مستخدمة؟
10. ما حالة النظام؟

إذا لم يستطع الطالب الإجابة من الواجهة، فالـredesign لم يكتمل.

## Final Direction

DLU LAB — Space Telecommunications Laboratory

واجهة ذات:
- hardware visualization قوي.
- signal colors واضحة.
- futuristic panels نظيفة.
- MML واضح دائمًا.
- Call Path ظاهر ومفهوم.
- teaching actions سهلة الاكتشاف.

المشروع يجب أن يبدو كمختبر جامعي مصقول، وليس prototype إداري.
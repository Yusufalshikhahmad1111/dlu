# Stage 3.5.1 — UI Stability, Theme Consistency & Hardware Rendering Hardening

## Objective

هذه خطة إصلاح شاملة بعد اختبار Windows الحقيقي للواجهة. الهدف تثبيت Stage 3.5 قبل الانتقال إلى Stage 4، بدون تغيير منطق SQLite أو MML أو CPT أو Call Engine.

## P0 — Runtime crash fixes

### 1. Unify Slot representation

المشكلة الحالية: Database.get_slot يمكن أن يصل إلى مسارات الرسم كـ Slot object أو dict. هذا يسبب خلطًا بين slot.field و slot["field"]، وظهر منه AttributeError في draw_port_grid.

الحل: إنشاء adapter/ViewModel واحد للـUI، مثل SlotViewModel أو helper موحد، ثم جعل جميع دوال الرسم تتعامل مع النوع نفسه فقط.

الدوال المستهدفة: show_module, draw_port_grid, draw_full_module_slot, draw_shelf_strip, select_port, open_selected_reference وأي مسار آخر يقرأ بيانات Slot.

### 2. Palette safety

المشكلة الحالية: بعض عمليات استبدال الألوان أدخلت expressions مثل {BORDER} في Qt graphics بدل قيمة لون حقيقية، ما سبب QVariant must be holding a QColor.

الحل: ThemePalette/DesignTokens واحد، وكل QPen/QBrush/QColor يستلم string أو QColor صحيح فقط.

قاعدة: لا توجد palette placeholders داخل GraphicsView code.

### 3. Font safety

المشكلة الحالية: ظهر QFont point size <= 0.

الحل: helper مركزي لإنشاء الخطوط، يفرض minimum آمن مثل 8px ويعالج None/invalid values، مع إزالة إنشاء الخطوط المباشرة خارج helper.

يتم تدقيق ui.py وcall_ui.py وكل dialogs.

### 4. Graphics rendering safety

كل رسم hardware يمر عبر helpers موحدة للـrounded panels, status LED, connector, faceplate, rack detail, signal trace.

الهدف: منع أخطاء QColor/QPen/QBrush وإعادة أخطاء QGraphicsScene القديمة.

## P1 — Theme hardening

### 5. One source of truth for themes

لدينا الآن نظامين متوازيين في ui.py وcall_ui.py. سيتم توحيدهما في DesignTokens واحد.

Theme A: Brown + Ivory — الوضع الافتراضي.
Theme B: Brown + Silver — الوضع المعدني.

نفس palette يجب أن يغطي QWidget, QSS, GraphicsView, Call Path, dialogs, menus, Hardware Library وOMT.

### 6. Direct theme toggle

الإبقاء على زر THEME المباشر في الـHeader.

كل ضغط:
IVORY → SILVER → IVORY

ولا يبقى أي old blue/black component بعد التبديل.

## P1 — Hardware visual correctness

### 7. Module state visibility

على Shelf وقبل فتح Module يجب أن يظهر:
- EMPTY
- ACT
- MBL
- FAULT

كل حالة تستخدم icon + text + border/fill، وليس اللون وحده.

### 8. Module detail layout

عند فتح Module:
- الجهة اليسرى: faceplate + card type + family + role + capacity + EQN + reference + large status badge.
- الجهة اليمنى: Port Bank واضح.

حالة ACT/MBL/FAULT/EMPTY تبقى ظاهرة حتى لو كانت كل المنافذ فارغة.

### 9. CMRL visual case

CMRL يجب أن يعرض CMRL · 6P ومنافذ 0..5 بشكل مرئي وواضح.

Port 6 يجب أن يبقى rejected وليس valid port.

## P1 — MML and navigation synchronization

### 10. MML focus

DISP/STAT/TEST التي تحتوي DLU/Shelf/Module/EQN يجب أن تعيد الشاشة تلقائيًا إلى الهدف نفسه.

مثال:
DISP DLUMOD DLU=10 SHELF=1 MODULE=4 → الشاشة إلى Module 4.

DISP DLUPPORT EQN=10-1-7-3 → الشاشة إلى Module 7 ثم Port 3.

لا يبقى visual context على Module سابق.

### 11. Graphics item lifecycle

كل click/double-click/context callback قد يعيد بناء scene؛ لذلك لا يجوز استدعاء QGraphicsItem بعد rebuild.

يجب تدقيق:
- click
- double-click
- right-click
- drag/drop
- theme switch
- mode switch
- MML focus

## P2 — Cleanup and consistency

### 12. Hardcoded color audit

تدقيق ui.py وcall_ui.py والdialogs لإزالة old theme hex values غير المبررة.

أي لون يجب أن يكون DesignToken أو technical color موثق.

### 13. Rendering deduplication

عدم وجود أكثر من طريقة لرسم نفس:
- status badge
- connector
- module faceplate
- port state
- signal line.

### 14. Responsive geometry

تدقيق:
- 1280×720
- 1366×768
- 1600×900
- 1920×1080

خصوصًا 25 DLU، DLU rack، 16 modules، CMRL، SLMA8، SLMA16، SLMA64، Call Path وOMT composer.

لا clipping ولا overlapping ولا command input مخفي.

### 15. Performance

تقليل decorative QGraphicsItems وعدم إضافة animation أو heavy assets بشكل مستمر.

## Automated QA

إضافة اختبارات/فحوص لـ:
- Slot normalization.
- theme completeness.
- valid QColor/QBrush/QPen inputs.
- safe font sizes.
- module states.
- 0/6/8/16/64 port rendering.
- MML focus.
- theme switching.

ويضاف static audit داخلي يبحث عن:
- direct QFont creation.
- old hardcoded colors.
- palette placeholders.
- mixed Slot access.
- suspicious negative font sizes.

## Windows QA

### Boot
- لا traceback.
- لا Qt font warnings.

### Hardware
- Home.
- DLU rack.
- Shelf 0..7.
- Module 0..15.
- CMRL 6P.
- SLMA8 8P.
- state badges.

### Theme
- Brown + Ivory.
- Brown + Silver.
- تبديل ذهابًا وإيابًا.
- no mixed blue/black UI.

### MML
- DISP DLU.
- DISP DLUMOD.
- DISP DLUPPORT.
- STATPORT.

### Labs
- 8-Line.
- CMRL.
- Maintenance.
- Inspect.

### Stage 3
- LOCAL.
- NATIONAL.
- INTERNATIONAL.
- BLACK LIST.

## Definition of Done

Stage 3.5.1 لا يغلق إلا عندما:
- لا يوجد Python traceback من تفاعلات UI.
- لا يوجد QVariant QColor error.
- لا يوجد invalid font warning.
- Slot representation موحدة.
- Theme موحد بالكامل.
- IVORY/SILVER يغيران الواجهة كلها.
- Module states واضحة على Shelf وModule.
- Port Bank واضح لكل بطاقة.
- MML focus صحيح.
- click/double-click/context/drag-drop سليمة.
- Physical/Logical سليمة.
- Stage 1/2/3 regression خضراء.
- Windows manual QA ناجح على الدقات المستهدفة.

## Execution Order

P0: Slot normalization → Palette safety → Font safety → Graphics safety.
P1: Theme hardening → Module state visibility → Module detail → CMRL → MML focus → lifecycle/layer audit.
P2: hardcoded color cleanup → rendering deduplication → responsive audit → performance → static audit → extra regression.

بعد الإغلاق فقط ننتقل إلى Stage 4 — Command Files.
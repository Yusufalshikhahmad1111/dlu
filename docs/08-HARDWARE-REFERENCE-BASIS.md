# 08 — Hardware Reference Basis

## الهدف

هذه الوثيقة تمنع المشروع من التحول إلى رسم تخيلي لـ DLU.

## 1. ما تم التحقق منه

### DLU hierarchy

المراجع التي تم فحصها توضح:
- DLU وحدة إنهاء وتجميع خطوط المشتركين.
- EQN يستخدم DLU / Shelf / Module / Port.
- توجد أمثلة Shelf بترقيم 0..7.
- توجد أمثلة Module بترقيم 0..15 داخل Shelf.

مصدر عن إنشاء Module:
https://vunivere.ru/work88561/page8

مثال EQN يوضح المعنى:
https://www.scribd.com/doc/187456771/EWSD-PRIRUCNIK

### Subscriber modules

المراجع توضح:
- SLMA = Subscriber Line Module Analog.
- SLMD = Subscriber Line Module Digital.
- توجد SLMA ذات 16 منفذًا.
- بعض المراجع التدريبية تصف وحدات مشترك شائعة ذات 8 دوائر.

Siemens documentation catalog:
https://www.ven-tel.com/docs/EWSD_Documentation-Catalog.pdf

DLU/SLMA visual reference:
https://www.terratel.eu/ewsd-switching-system-upgrade-and-migrate.html

## 2. ما يعتبر حقيقة

ثابت:
- DLU ID
- Shelf numbering
- Module numbering
- EQN format
- Card type
- Card capacity
- Port numbering
- DN ↔ EQN relationship

قابل للتبسيط في الرسم:
- شكل الإطار
- طريقة رسم PCB
- LED graphics
- zoom
- colors
- animation
- ترتيب معلومات الشاشة

هذه عناصر UI ولا تعني أننا أعدنا بناء PCB أو Cabinet صناعيًا.

## 3. نموذج 8-Port

عندما يكون Card Type = SLMA8:

Module → Port 0..7 → 8 subscriber lines

مثال:
50-1-5-0 → DN 2233500

ويظهر هذا الربط أمام الطالب.

## 4. لا نعمم 8 منافذ

SLMA16:
Port 0..15

CMRL:
السعة الخاصة بها حسب مرجع المشروع.

إذن Card Capacity ليست Hard-coded على 8.

## 5. قاعدة وضع البطاقات

لا نقول إن كل Module هو SLMA.

بعض المواضع تحتوي وحدات تحكم أو اختبار أو تغذية أو أنواعًا أخرى بحسب بنية DLU/Shelf المرجعية.

إذا لم يكن موضع معيّن موثقًا في Dataset، يظهر UNCONFIGURED بدل اختراع بطاقة.

## 6. تتبع المصدر

كل Card Type جديد في hardware dataset يجب أن يملك:
- canonical name
- source
- capacity
- supported port range
- educational notes

## 7. الصور

صور PCB أو DLU الحقيقية تستخدم كمراجع بصرية أو صفحات معلومات فقط عندما يكون المصدر واضحًا والترخيص مناسبًا.

الـ DLU Visualizer الأساسي يبقى رسمًا هندسيًا مبسطًا يحافظ على الحقيقة المنطقية ولا يدعي أنه صورة مصنع.

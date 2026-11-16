# 02 — SQLite Database Specification

## 1. هدف النموذج

النموذج يحفظ الحالة التي يراها الطالب في الواجهة ويُرجعها MML نفسها.

## 2. الجداول الأساسية

### exchanges

يمثل المقسم:
- exchange_code PK
- lac
- city_name
- sn_status

مثال:
ALE1 | 021 | ALEPPO | act

### dlus

يمثل DLU:
- dlu_id PK
- exchange_code FK
- dluc0_state
- dluc1_state
- pdc_count
- is_isolated

### slots

يمثل موضع البطاقة:
dlu_id + shelf + module

القيود:
- shelf: 0..7
- module: 0..15

ويحتوي:
- card_type
- ost

قيم card_type الأولية:
- EMPTY
- SLMA8
- SLMA16
- CMRL
- SLMD
- DIUD
- TU
- RGMG
- DCC

### subscribers

يمثل DN المرتبط بمنفذ حقيقي.

PK:
- (lac, dn)

Unique:
- (dlu_id, shelf, module, port)

الحقول:
- sub_type
- dial_mode
- line_state
- cos_flags
- optrcl
- blk_reason

### cpt_routes

يمثل قواعد التوجيه:
- dest
- code
- sym
- eval
- name
- route_type

PK:
- (dest, code)

### alarms

- alarm_id
- unit_ref
- severity
- message
- active
- created_at

severity:
- CRITICAL
- MAJOR
- MINOR

### command_files

- file_name
- raw_commands
- status
- scheduled_at
- executed_log

status:
- Accepted
- Started
- Finished
- Executed
- Failed

## 3. جدول إضافي أوصى بإضافته

### event_log

هذا تحسين مقصود عن النموذج الأولي.

السبب: العرض الجامعي يحتاج أن نثبت ماذا حدث، وليس فقط الحالة النهائية.

الحقول:
- event_id
- event_type
- aggregate_type
- aggregate_id
- payload_json
- created_at

## 4. قواعد البيانات المهمة

### EQN

الصيغة:
DLU-Shelf-Module-Port

لكن المخزن فعليًا في حقول منفصلة لا كنص فقط.

السبب: منع أخطاء parsing والاستعلام وتسهيل uniqueness.

### Card capacity

- CMRL: ports 0..5.
- SLMA8: ports 0..7.
- SLMA16: ports 0..15.

أي محاولة خارج السعة تفشل قبل INSERT.

### DN

لا يوجد DN مزدوج داخل نفس LAC.

### Subscriber ↔ Slot

لا يوجد منفذ يستوعب مشتركين.

## 5. Seed Dataset الأول

الإصدار الأول من قاعدة العرض يجهز:
- ALE1
- DLU 10
- DLU 50
- CPT لدمشق/حلب/الحسكة والمجموعة الأساسية من SNNP.
- الطوارئ 110/112/113.
- أمثلة PLMN.
- BLACK LIST لـ 00972.
- بطاقة SLMA جديدة على 50-1-5.
- بيانات مسبقة تسمح مباشرة بسيناريو 2233500–2233507.

## 6. معاملات SQLite

عمليات cr/can/mod/conf/diag التي تغير أكثر من جدول يجب أن تكون transaction واحدة.

مثال:
conf dlu قد يغير dluc state + slot state + alarm.

يجب أن تنجح المعاملة كلها أو تتراجع كلها.

## 7. قاعدة ذهبية

الـ UI لا يكتب SQL مباشرة.

المسار الوحيد:
UI → Use Case → Repository → SQLite

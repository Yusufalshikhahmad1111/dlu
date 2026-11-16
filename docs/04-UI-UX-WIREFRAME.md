# 04 — UI / UX Wireframe

## 1. الهدف

الواجهة يجب أن تبدو كمختبر تشغيل مقسم، لا كلوحة إدارة CRUD.

المعلومة البصرية الأهم هي حالة المقسم الآن.

## 2. الشاشة الرئيسية

~~~text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ALE1   SYS: ACT   CRITICAL 0   MAJOR 1   MINOR 2   TRAFFIC 37/120          │
├───────────────────────────────┬──────────────────────────────────────────────┤
│                               │ OMT / TERMINAL                               │
│        DLU OVERVIEW           │ > stat sub: dn=2233500;                     │
│                               │                                              │
│  Side 0    Side 1             │ RESULT                                       │
│  DLUC0     DLUC1              │ DN      EQN         STATE     ...            │
│                               │ 2233500  50-1-5-0   idle                    │
│  Shelf 0  [cards...]          │                                              │
│  Shelf 1  [cards...]          │ >                                            │
│  ...                           ├──────────────────────────────────────────────┤
│  Shelf 7  [cards...]          │ QUICK MACROS                                 │
│                               │ [Expand 8 Lines] [CMRL Demo] [Fault/Repair] │
│                               │ [Black List]     [Call Demo]                 │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ selected: DLU 50 → Shelf 1 → Slot 5 → SLMA8                                  │
│ Ports: ● ● ● ● ○ ○ ○ ○     Legend: gray=free  green=idle  yellow=mbl/blk   │
└──────────────────────────────────────────────────────────────────────────────┘
~~~

## 3. DLU interactions

### Level 1

Click DLU:
- show DLU summary.
- show DLUC0/DLUC1.
- show alarm state.
- show channel usage.

### Level 2

Click Shelf:
- zoom into 16 slots.

### Level 3

Click Slot/Card:
- show card type.
- card state.
- port matrix.
- subscriber mapping.

### Level 4

Click Port:
- show DN.
- LAC.
- line state.
- services.
- block reason.
- recent events.

## 4. Visual semantics

- Gray: unassigned/free.
- Green: subscriber idle.
- Blue/Red pulse: busy/call.
- Yellow: blk or mbl.
- Red alarm marker: hardware fault/critical.

الألوان ليست decorative؛ كل لون له معنى تشغيلي واحد.

## 5. OMT

المطلوب من الطرفية:
- command input.
- history.
- command completion.
- output text.
- structured result table.
- clear screen.
- macro insertion.
- optional clock acceleration for command file scheduling.

## 6. SYP

شريط دائم في أعلى الشاشة:
- CRITICAL.
- MAJOR.
- MINOR.
- PDC usage.
- current traffic.
- DLU active/standby health.

Clicking an alarm يفتح مصدره.

## 7. Call Path mode

عند بدء call، تتحول الشاشة إلى visual trace:

### Local
DLU → SN → DLU

### National
DLU → LTG → SN → LTG → DLU

### International
DLU → LTG → SN → Gateway

### Rejected
SUB → CPT → BLACK LIST / REJECT

المطلوب أن يرى الطالب سبب القرار، لا animation بلا معنى.

## 8. Labs navigation

Sidebar:
- Exchange
- DLU
- OMT
- Calls
- OSI/TCP
- Signals & Modulation
- Scenarios
- Database/Reset
- About

## 9. Responsive strategy

الهدف الأساسي desktop 1366×768 وما فوق.

لا نطارد mobile design. عند الشاشات الأصغر نستخدم:
- collapsible DLU.
- drawer للـ OMT.
- modal للport details.

## 10. Accessibility / teaching

- labels واضحة.
- tooltip لكل لون.
- command error لا يظهر كرقم فقط.
- كل macro يعرض الأوامر التي سينفذها قبل التنفيذ.
- reset demo state واضح.

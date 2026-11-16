# 04 — UI / UX Wireframe

## الهدف

الواجهة هي مختبر DLU وليست Dashboard عامة.

الطالب يجب أن يفهم بصريًا العلاقة:

DLU → Shelf → Module → Port → Subscriber

## الشاشة الرئيسية

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ALE1   DLU 50   SYSTEM: ACT   CRIT 0   MAJOR 0   MINOR 1                  │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ DLU HARDWARE                  │ OMT                                         │
│                               │ > stat sub: dn=2233500;                     │
│ Side 0        Side 1          │                                             │
│ DLUC0         DLUC1           │ DN       EQN        STATE                    │
│                               │ 2233500  50-1-5-0  idle                     │
│ Shelf 0  [..16 modules..]    │                                             │
│ Shelf 1  [..16 modules..]    │ >                                            │
│ Shelf 2  [..16 modules..]    ├─────────────────────────────────────────────┤
│ ...                           │ MACROS                                      │
│ Shelf 7  [..16 modules..]    │ [8-Line Demo] [CMRL] [Maintenance]          │
│                               │ [Call Demo]  [Blacklist]                    │
├───────────────────────────────┴─────────────────────────────────────────────┤
│ Selected: DLU 50 → Shelf 1 → Module 5 → SLMA8                              │
│ Ports: 0 1 2 3 4 5 6 7                                                     │
│        ● ● ● ● ○ ○ ○ ○                                                     │
│        DN DN DN DN -- -- -- --                                              │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

## Level 1 — DLU

النقر على DLU يظهر:
- DLU ID
- controller states
- channel information when available
- alarms
- shelves

## Level 2 — Shelf

عند النقر:
- نكبر الـ Shelf.
- نعرض Modules بمواقعها.
- الرقم جزء من EQN.

مثال:
Shelf 1
Module 0 ... Module 15

ولا نغير الترقيم لمجرد أن التصميم أجمل.

## Level 3 — Module

مثال:
50-1-5

يعرض:
- Card type
- Card state
- capacity
- ports

إذا كانت SLMA8:
0 1 2 3 4 5 6 7

إذا كانت بطاقة مختلفة، تُعرض سعتها الفعلية.

## Level 4 — Port

مثال:
EQN = 50-1-5-0

وتفاصيل:
- DN = 2233500
- LAC = 021
- line state = idle
- services
- block
- test status

## الألوان

- Gray = unassigned
- Green = idle
- Busy = active call
- Yellow = blocked / maintenance
- Red alarm marker = alarm

الألوان لا تمثل نوع البطاقة.

## OMT

- history
- command input
- raw response
- structured data
- error code
- affected EQN
- quick macro preview

## التعليم

النقر على Port يجب أن يعرض العلاقة مباشرة:

DN 2233500
⇅
EQN 50-1-5-0

وهذا من أهم أهداف الواجهة.

## قاعدة عدم الاختراع

أي عنصر بصري لا نستطيع ربطه ببيانات Hardware أو Dataset معروف لا يظهر كحقيقة في الشاشة.

الـ zoom والselection والtooltips والlegend أدوات عرض فقط، وليست ادعاءات عن العتاد.

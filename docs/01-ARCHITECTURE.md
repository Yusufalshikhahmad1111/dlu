# 01 — Architecture

## 1. Stack المختار

### React + TypeScript + Tauri 2 + SQLite

هذا هو الخيار الوحيد المعتمد للمشروع.

السبب: التطبيق يحتاج واجهة رسومية كثيفة التفاعل (DLU/Shelves/Slots/LEDs + OMT + SYP) وفي الوقت نفسه يحتاج تطبيق Windows محليًا قابلًا للتوزيع. Tauri يتيح إنشاء MSI أو setup.exe على Windows، وإضافة SQL الرسمية تدعم SQLite. كما أن واجهة React تمنحنا SVG/Canvas طبيعيًا للرسم التفاعلي.

المتطلبات الحالية في توثيق Tauri تشمل بيئة Windows مع Microsoft C++ Build Tools وWebView2، وإضافة SQL الحالية تتطلب Rust حديثًا، لذلك سنثبت نسخة Rust مستقرة مناسبة عند إنشاء المشروع الفعلي بدل hard-code نسخة قديمة.

المراجع الرسمية:
- https://tauri.app/distribute/windows-installer/
- https://v2.tauri.app/plugin/sql/
- https://tauri.app/start/prerequisites/

## 2. الطبقات

### A. Presentation

React + TypeScript + SVG/Canvas

المسؤوليات:
- DLU visualizer.
- Shelf/Slot/Card/Port panels.
- OMT terminal.
- SYP.
- call path animation.
- labs.
- macros.

ممنوع:
- تنفيذ SQL مباشر من مكوّن UI.
- اتخاذ قرارات تشغيلية محلية.
- نسخ حالة subscriber داخل component ثم اعتبارها الحقيقة.

### B. Application Layer

Use-cases:

- CreateSubscriber
- CancelSubscriber
- ModifySubscriber
- DisplaySubscriber
- DisplayRange
- StatSubscriber
- TestSubscriber
- ConfigureDlu
- DiagnoseDlu
- CreateCommandFile
- ExecuteCommandFile
- SimulateCall

هذه الطبقة تدير transaction boundaries ونتائج الأوامر.

### C. Domain Core

المكونات الأساسية:

- MmlLexer
- MmlParser
- MmlCommandModel
- MmlValidator
- DluStateMachine
- EqnAddress
- CardCapacityPolicy
- CptRouter
- CallPathEngine
- AlarmEngine
- CommandFileEngine

هذه الطبقة لا تعرف React أو Tauri.

### D. Persistence

SQLite repositories:

- ExchangeRepository
- DluRepository
- SlotRepository
- SubscriberRepository
- CptRepository
- AlarmRepository
- CommandFileRepository
- EventLogRepository

### E. Tauri Shell

المسؤوليات:
- فتح/حفظ database file.
- filesystem paths.
- packaging.
- native window commands.
- future export/import.

لا نضع MML parser في Rust.

## 3. تدفق تنفيذ الأمر

Input → Lexer → Parser → Normalizer → Validator → FSM/Use-case → Transaction → Event → UI

مثال الأمر:

~~~text
> cr sub: dn=2233500, eqn=50-1-5-0, lac=021, class=ms, c/s=PB;
~~~

1. Lexer يجزئ النص.
2. Parser يبني command AST.
3. Normalizer يوحد case وaliases.
4. Validator يتحقق من DN/EQN/card/port.
5. Use-case يتحقق من business rules.
6. SQLite transaction تنفذ.
7. Event يصدر SubscriberCreated.
8. UI تعيد query للحالة.
9. LED يصبح أخضر.
10. OMT يعرض response structured/raw.

## 4. حالة DLU

لكل DLU:

- dluc0: act | standby | mbl
- dluc1: act | standby | mbl
- is_isolated: boolean

قاعدة المصافحة التعليمية:

- يوجد جانب واحد Active على الأقل في الحالة الطبيعية.
- تحويل Active إلى mbl يستلزم رفع الجانب الآخر إلى Active إذا كان صالحًا.
- إذا انتهت الوحدة بلا جانب Active، ينشأ CRITICAL alarm.

## 5. الأحداث

- SubscriberCreated
- SubscriberCancelled
- SubscriberModified
- DluStateChanged
- CardStateChanged
- AlarmRaised
- AlarmCleared
- CallStarted
- CallEnded
- CommandFileStatusChanged

## 6. الوحدات البصرية

DLU renderer ليس صورة ثابتة.

كل عنصر مرسوم ناتج عن بيانات:

DLU → Side → Shelf → Slot → Card → Port

وبالتالي:
- تغيير slot.card_type يغير بطاقة الواجهة.
- تغيير subscriber.line_state يغير LED.
- تغيير blk_reason يغير اللون.
- تغيير ost يغير حالة الوحدة.

## 7. لماذا ليس Electron؟

Electron خيار صالح تقنيًا، وهو رسميًا يعتمد على Chromium وNode ويُعبأ عبر Electron Forge. لكنه يحمل runtime أكبر، بينما مشروعنا لا يحتاج Node في زمن التشغيل إلا إذا اخترناه عمدًا.

نحن نريد أن تكون طبقة التشغيل المحلية أقرب لتطبيق Windows، مع بقاء كل منطق المادة في TypeScript. لذلك اخترنا Tauri.

مرجع Electron الرسمي:
https://www.electronjs.org/docs/latest/tutorial/application-distribution

## 8. سياسة الاستمرارية

قاعدة البيانات تُحفظ في مسار بيانات التطبيق المحلي، وليس داخل مجلد source عند التشغيل النهائي.

سنضيف لاحقًا:
- Reset Demo State.
- Export Database.
- Import Backup.
- Seed Dataset Version.

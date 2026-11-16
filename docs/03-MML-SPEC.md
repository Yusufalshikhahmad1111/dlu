# 03 — MML Specification

## 1. الهدف

محاكاة واجهة أوامر MML المطلوبة في المقرر، مع مرونة في case والصيغ التي ظهرت في المواد، دون الادعاء أنها implementation صناعي كامل من Siemens.

## 2. شكل الأمر

الشكل القياسي للمحاكي:

~~~text
> COMMAND;
~~~

والصيغ البديلة المسموح بها في المواد مثل:
- > cr sub: ...
- > CRSUB: ...
- > Disp sub: ...

تُطبع داخليًا إلى نموذج موحد.

## 3. الأفعال

### Mutating
- CR
- CAN
- MOD
- CONF
- DIAG
- EXECMDFILE

### Read-only
- DISP
- STAT
- TEST

TEST في هذه المواصفة يعتبر استعلامًا/فحصًا ما لم يتطلب سيناريو المادة تغيير حالة.

## 4. Normalized command model

~~~ts
type MmlCommand = {
  verb: MmlVerb;
  object?: string;
  params: Record<string, string>;
  raw: string;
}
~~~

ولا يسمح core بتنفيذ raw مباشرة.

## 5. Lexer

المهام:
1. التحقق من >
2. التحقق من ;
3. فصل command verb.
4. فصل object عند وجوده.
5. فصل parameters بواسطة comma.
6. الاحتفاظ بالنص raw لأغراض OMT.
7. عدم كسر && داخل range.

## 6. Normalization

يتم تحويل:
- lower/upper case.
- aliases مثل CRSUB ↔ CR SUB.
- tolerant syntax لبعض صور التدريب.

لكن normalization لا يتجاوز قواعد المقرر.

## 7. Validation

### Syntax validation

أمر بدون ; → syntax error.

### Address validation

50-1-5-7 صالح لبطاقة SLMA8.

10-1-7-6 غير صالح إذا كانت البطاقة CMRL.

### State validation

diag على وحدة act → مرفوض.

يجب أولاً:
ost=mbl

ثم يسمح diag.

### Business validation

- DN موجود مسبقًا.
- EQN مستخدم.
- Card غير موجودة.
- Card type غير متوافق.
- subscriber blocked يحاول خدمة محظورة.

## 8. Dispatcher

بعد parse + validation:
CommandDispatcher يوجه إلى use-case محدد.

لا يجوز أن يعرف parser تفاصيل SQLite.

## 9. الأوامر الأولية

### Create

~~~text
> cr sub: dn=2233500, eqn=50-1-5-0, lac=021, class=ms, c/s=PB;
~~~

### Cancel

~~~text
> can sub: dn=2233500;
~~~

### Modify

~~~text
> mod sub: dn=2233500, cos=cw;
> mod sub: dn=2233500, blk=accsusp;
~~~

### Display

~~~text
> disp sub: dn=2233500;
> disp sub: dn=2233500 && 2233507;
~~~

### Status / Test

~~~text
> stat sub: dn=2233500;
> test sub: dn=2233500;
~~~

### DLU configuration

~~~text
> conf dlu: dlu=10, dluc0=y, ost=mbl;
~~~

### Diagnostic

~~~text
> diag dlu: dlu=10;
~~~

لكن فقط بعد تحقق شرط mbl.

## 10. Range parsing

المشغل:
&&

يعني نطاقًا متسلسلًا في سياق الأوامر التي تدعم ذلك.

أول نسخة من النظام لن تبني expression language عامة؛ تدعم فقط range forms المحددة بالمقرر.

## 11. Command Files

وضع parser مستقل للكتل:

~~~text
> block-demo;
> mod sub: dn=2233500, blk=accsusp;
> disp sub: dn=2233500;
> endfile;
~~~

ثم:

~~~text
> execmdfile: file=block-demo, time=02:00;
~~~

والحالة:
Accepted → Started → Finished → Executed

مع Failed إذا تعذر تنفيذ أمر داخلي.

## 12. FSM

FSM الأولى صغيرة ومقيدة.

### DLU side

ACT ↔ STANDBY
ACT → MBL
STANDBY → ACT
MBL → ACT

الانتقالات المنفذة تمر عبر policy.

### Diagnostic guard

ACT --diag--> REJECT

MBL --diag--> EXECUTE

### Alarm rule

إذا لم يوجد جانب Active صالح:
CRITICAL alarm

## 13. OMT output contract

~~~ts
type MmlResult = {
  ok: boolean;
  command: string;
  code: string;
  message: string;
  data?: unknown;
  stateChanges?: string[];
  alarms?: string[];
}
~~~

الواجهة تستطيع عرض:
- output text.
- structured table.
- affected objects.

## 14. Error codes

- MML-SYNTAX
- MML-UNKNOWN-COMMAND
- EQN-INVALID
- EQN-NOT-FOUND
- PORT-OUT-OF-RANGE
- PORT-OCCUPIED
- DN-EXISTS
- DN-NOT-FOUND
- CARD-INCOMPATIBLE
- STATE-GUARD
- ROUTE-BLOCKED

هذه الأكواد ستُستخدم في tests والواجهة.

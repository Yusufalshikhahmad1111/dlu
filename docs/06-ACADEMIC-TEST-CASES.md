# 06 — Academic Test Cases

هذه السيناريوهات هي المرجع الأساسي لقبول الـ core قبل الواجهة المتقدمة.

## TC-01 — Aleppo 8-line expansion

Initial:
- LAC 021.
- DLU 50.
- SLMA8 في 50-1-5.
- ports 0..7 فارغة.

Execute:

~~~text
> cr sub: dn=2233500, eqn=50-1-5-0, lac=021, class=ms, c/s=PB;
...
> cr sub: dn=2233507, eqn=50-1-5-7, lac=021, class=ms, c/s=PB;
~~~

Expected:
- 8 subscribers created.
- all 8 ports green/idle.
- no duplicate DN/EQN.
- range display returns the eight records.

## TC-02 — CMRL six-port guard

Initial:
- CMRL at 10-1-7.

Create:
- DN 2250500..2250505 on ports 0..5.

Attempt:
- DN 2250506 on port 6.

Expected:
- command rejected.
- code PORT-OUT-OF-RANGE.
- port 6 remains unassigned.

Then:

~~~text
> can sub: lac=021, dn=2250500;
~~~

Expected:
- port 0 becomes free/gray.

## TC-03 — Maintenance before diagnostic

Initial:
- DLU active.

Attempt:

~~~text
> diag dlu: dlu=10;
~~~

Expected:
- rejected with STATE-GUARD.

Then:

~~~text
> conf dlu: dlu=10, dluc0=y, ost=mbl;
~~~

Expected:
- active/standby policy applied.
- partner promoted if valid.
- no inconsistent dual-active state.

Then:

~~~text
> diag dlu: dlu=10;
~~~

Expected:
- diagnostic accepted.

## TC-04 — Command file

Example:

~~~text
> block-demo;
> mod sub: dn=2233500, blk=accsusp;
> disp sub: dn=2233500;
> endfile;
~~~

Then:

~~~text
> execmdfile: file=block-demo, time=02:00;
~~~

Expected:
Accepted → Started → Finished → Executed

and subscriber visual state becomes yellow/blocked.

## TC-05 — Black list

Dial:
00972...

Expected:
- CPT resolves to EVAL=NO.
- call path stops.
- reason shown as BLACK LIST.
- no voice channel allocated.

## TC-06 — Local call

A calls B in same exchange.

Expected path:
DLU → SN → DLU

Expected:
- both ports become busy during simulated call.
- traffic counter increments.
- returning to idle releases resources.

## TC-07 — National call

Cross-LAC call.

Expected path:
DLU → LTG → SN → LTG → DLU

Expected:
- trunk resource reserved.
- channel usage visible.
- release restores capacity.

## TC-08 — Teaching verification

For every macro the UI must expose:
- commands used.
- expected state.
- actual state.
- PASS/FAIL.

هذا يحول العرض من مؤثرات بصرية إلى تجربة تقييم أكاديمية قابلة للإثبات.

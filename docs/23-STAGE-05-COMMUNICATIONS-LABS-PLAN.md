# Stage 5 — Communications Labs Plan

## الهدف
إضافة مختبر اتصالات أكاديمي تفاعلي إلى DLU Lab بدون المساس بمنطق DLU/MML/CPT/Call Engine/Command Files.

## نطاق التنفيذ
1. OSI
   - طبقات OSI السبع بترتيب ثابت.
   - وظيفة مختصرة لكل طبقة.
   - أمثلة تعليمية.
   - مقارنة TCP مقابل UDP على مستوى النقل والتطبيق العملي.
2. Analog modulation
   - AM
   - FM
   - PM
   - رسم الإشارة الزمنية من معادلات محددة المعلمات.
3. Pulse modulation
   - PAM
   - PWM
   - PPM
   - PCM
   - عرض مفهوم sampling/quantization/encoding في PCM.
4. Digital modulation
   - ASK
   - FSK
   - PSK
   - QPSK
   - 16-QAM
   - توليد waveform قصير من bitstream ثابت وقابل للتكرار.
5. Constellation + BER basics
   - constellation لـ QPSK و16-QAM.
   - theoretical BER لـ BPSK/QPSK.
   - empirical BER simulation deterministic بالـseed لـ BPSK/QPSK/16-QAM.
6. UX
   - تبويب Communications داخل DLU Lab.
   - اختيار المختبر من بطاقات واضحة.
   - شرح/معلمات/رسم/نتيجة في شاشة واحدة.
   - نفس نظام الألوان والخطوط الموجود حاليًا.
7. الجودة
   - pure-domain tests.
   - no new runtime dependency.
   - source static audit compatibility.
   - regression all tests via Windows CI.
   - Windows manual QA checklist.

## قواعد هندسية
- Domain core لا يستورد PySide6.
- الحسابات deterministic عند إعطاء seed.
- لا نستعمل random غير مضبوط في الاختبارات.
- لا نربط المختبر بقاعدة SQLite؛ المختبر مستقل وتعليمي.
- لا ندعي محاكاة فيزيائية كهربائية أو RF حقيقية؛ النتائج التعليمية normalized.
- كل نتيجة تحمل اسم النموذج والمعلمات المستخدمة.
- الحفاظ على Stage 1–4 دون تغيير سلوكي.

## Definition of Done
- جميع المختبرات المذكورة قابلة للتشغيل من الواجهة.
- المعادلات/الـmapping موحدة في وحدة domain واحدة.
- tests تغطي كل نوع modulation، حدود parameters، constellation، BER، وOSI/TCP/UDP.
- CI أخضر.
- تقرير تنفيذ + QA checklist.
- تحديث milestone وREADME.

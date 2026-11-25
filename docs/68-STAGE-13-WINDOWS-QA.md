# Stage 13 — Windows QA

**Status:** COMPLETE — Windows QA passed

## Target

Windows 11 / Python 3.12 / PySide6.

## Visual coverage

The Stage 13 runner captures:

- OSI/TCP/UDP — Morning;
- AM/FM/PM — Night;
- 16-QAM waveform + constellation — Night;
- BER + constellation — Morning;
- PCM pulse train — Morning.

## Functional checks

- five experiment tabs build;
- live update toggle works;
- analog waveform/measurement updates;
- pulse PCM code output is readable;
- QPSK and 16-QAM constellation evidence is visible;
- BER theory/empirical measurement is deterministic;
- Morning/Night theme switches without breaking the lab.

## Acceptance

The stage is only marked complete after:

1. Stage 13 focused tests pass;
2. full regression passes;
3. UI static audit passes;
4. Windows functional visual QA passes and screenshots are uploaded;
5. any CI/QA defects are fixed and re-run.


## Final evidence

- Windows runner passed compile, static audit, focused tests, full regression, and functional visual QA.
- Artifact \`DLU-Stage13-Communications-Lab-2-QA\` contains 5 screenshots: OSI, Analog, 16-QAM, BER, and PCM.
- Verification required two fixes: a BER plot syntax error and a BPSK constellation presentation fallback.

# Stage 5 — Communications Labs Implementation Report

## Status

Implementation complete. Automated CI and Windows manual QA are the release gates.

## Delivered

### 1. OSI + transport
- Seven OSI layers with purpose and examples.
- TCP vs UDP comparison covering connection model, reliability, ordering, overhead, and common use.

### 2. Analog modulation
- AM, FM, PM.
- Parameterized normalized time-domain waveforms.
- Formula and teaching explanation shown beside the plot.

Models:
- AM: s(t) = [1 + μ sin(2π fₘ t)] cos(2π f_c t)
- FM: s(t) = cos(2π f_c t + β sin(2π fₘ t))
- PM: s(t) = cos(2π f_c t + kₚ sin(2π fₘ t))

The AM lab explicitly reports over-modulation when μ > 1.

### 3. Pulse modulation
- PAM
- PWM
- PPM
- PCM

PCM displays sample count, quantization depth, and generated binary code words.

### 4. Digital modulation
- ASK
- FSK
- BPSK/PSK
- QPSK
- 16-QAM

The waveform generator uses a fixed bitstream by default, making classroom comparisons reproducible.

### 5. Constellation + BER
- QPSK constellation with Gray labels.
- 16-QAM normalized 16-point constellation.
- Theoretical AWGN BER for BPSK/QPSK.
- Standard approximate AWGN BER model for 16-QAM.
- Deterministic empirical BER simulation for BPSK/QPSK/16-QAM using an explicit seed.

## Engineering decisions

- dlu_app/communications_lab.py contains no PySide6 or SQLite imports.
- dlu_app/communications_ui.py is presentation-only and uses the existing theme system.
- No new runtime package was added.
- Existing DLU, MML, CPT, Call Engine, and Command File state remain separate.
- Normalized teaching plots are intentionally not presented as electrical/RF-accurate simulation.

## Tests

tests/test_communications_lab.py covers OSI ordering, TCP/UDP profiles, deterministic analog and pulse generation, digital modulation, constellation cardinality and normalization, invalid input validation, theoretical BER behavior, deterministic empirical BER, and BER curve generation.

## UI integration

New right-side tab: Communications.
Sub-labs: OSI / TCP / UDP; AM / FM / PM; PAM / PWM / PPM / PCM; ASK / FSK / PSK / QPSK / 16-QAM; Constellation / BER.

Theme switching is propagated through the same Ivory/Silver palette used by the existing DLU UI.

## Definition of Done

Implementation side: complete.
Release side: GitHub Windows CI green, then Windows manual QA using docs/25-STAGE-05-WINDOWS-QA.md.
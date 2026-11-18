# Stage 5 — Windows QA Checklist

## 1. Launch
- Run run.bat or python main.py.
- Confirm no startup exception.

## 2. Communications tab
- Open Communications.
- Confirm the five labs are selectable.
- Toggle Ivory/Silver theme and confirm the lab remains readable.

## 3. OSI / TCP / UDP
- Confirm all seven OSI layers appear in order 7 → 1.
- Confirm TCP and UDP rows are visible.
- Confirm reliability, ordering, and common-use fields are readable.

## 4. Analog
- Run AM, FM, and PM.
- Confirm each produces a waveform and formula.
- Set AM μ > 1 and confirm the over-modulation warning appears.

## 5. Pulse
- Run PAM, PWM, PPM, and PCM.
- Confirm the waveform changes between modes.
- For PCM, confirm binary code words are shown.
- Change sample count and PCM bit depth and regenerate.

## 6. Digital
- Run ASK, FSK, PSK, QPSK, and 16-QAM with the default bitstream.
- Confirm the waveform changes according to the selected modulation.
- Confirm QPSK and 16-QAM show constellation points.
- Enter an invalid bitstream character and confirm a clear validation message.

## 7. BER
- Run BPSK, QPSK, and 16-QAM BER.
- Confirm the theoretical curve decreases as Eb/N0 increases.
- Confirm empirical points appear.
- Change seed and confirm the empirical result can change.
- Use SHOW CONSTELLATION for QPSK and 16-QAM.

## 8. Regression smoke check
- Open OMT and run > stat dlu: dlu=50;
- Open Command Files and confirm the Stage 4 workbench still loads.
- Open Call Path and confirm the existing Call Engine tab still loads.

## Release gate
Stage 5 is complete only after CI is green and all sections above pass on Windows 11.
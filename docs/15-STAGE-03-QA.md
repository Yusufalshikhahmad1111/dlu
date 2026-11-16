# Stage 3 — Final QA Checklist

## Automated coverage

The Stage 3 test suite verifies:

- source-backed SLMA8 demo preparation.
- LOCAL DLU → SN → DLU path.
- real caller/called ports change to busy.
- LOCAL release returns both ports to idle.
- NATIONAL DLU → LTG → SN → LTG → logical remote DLU/LAC path.
- NATIONAL consumes one PDC voice channel.
- INTERNATIONAL DLU → LTG → SN → International Gateway path.
- INTERNATIONAL consumes one PDC voice channel.
- CPT EVAL=NO for 00972 blocks before resource reservation.
- busy caller guard.
- deterministic longest-specific CPT match.

All Stage 1 and Stage 2 tests remain in the same CI regression suite.

## Windows manual release gate

1. Start the application with run.bat.
2. Open the CALL ENGINE · CPT · CALL PATH tab.
3. Press PREPARE DEMO.
4. Confirm caller 2233500 and called 2233501.
5. Press LOCAL.
6. Confirm the path DLU 50 → SN → DLU 50.
7. Open Hardware and verify ports 0 and 1 show BUSY.
8. Press RELEASE.
9. Verify ports 0 and 1 return to IDLE and PDC is 0/120.
10. Press NATIONAL.
11. Confirm DLU 50 → LTG → SN → LTG → DLU-LAC052.
12. Verify PDC is 1/120.
13. Press RELEASE and verify PDC returns to 0/120.
14. Press INTERNATIONAL.
15. Confirm International Gateway and PDC 1/120.
16. Press RELEASE.
17. Press BLACK LIST.
18. Confirm CPT EVAL=NO, reason BLACK LIST, and PDC remains 0/120.
19. Verify no Python traceback appears.
20. Verify the existing Stage 2 hardware controls still work.

The final release gate is the Windows runtime audit.

# Stage 7 — Windows QA Checklist

## Automated release gate

- [ ] Python compile.
- [ ] UI static audit.
- [ ] Full pytest regression.
- [ ] Windows onefile executable exists under `dist/`.
- [ ] Packaged `.exe --smoke-test` returns exit code 0.
- [ ] Five final screenshots are generated.
- [ ] Screenshots are uploaded as the `DLU-Lab-Screenshots` artifact.
- [ ] Executable is uploaded as the `DLU-Lab-Windows` artifact.

## Manual Windows session

### Launch
- [ ] Double-click the packaged DLU Lab executable.
- [ ] Main window opens without console errors.
- [ ] `DLU LAB` title and version/release appearance are correct.

### Preservation
- [ ] Hardware Physical view opens.
- [ ] Hardware Logical view opens.
- [ ] OMT accepts `> help;`.
- [ ] Command Files tab opens.
- [ ] Call Path tab opens.
- [ ] Communications tab opens.
- [ ] Scenarios tab lists all six scenarios.

### Backup / restore
- [ ] Create a database backup.
- [ ] Confirm backup file exists and is a valid SQLite database.
- [ ] Change demo data.
- [ ] Restore the backup.
- [ ] Application restarts and the previous subscriber/data state is restored.
- [ ] Automatic pre-restore backup exists in the backups folder.

### Final scenarios
- [ ] Aleppo 8-Line Expansion → PASS.
- [ ] CMRL Capacity Limit → PASS.
- [ ] DLU / Card Maintenance → PASS.
- [ ] Billing Block → PASS.
- [ ] International Blacklist → PASS.
- [ ] Command File Overnight Run → PASS.

### Reset
- [ ] Tools → Reset Demo requires confirmation.
- [ ] Reset restores source-backed placements.

## Packaging note

Qt's official deployment documentation identifies `pyside6-deploy` as the deployment tool and supports Windows `.exe` output with explicit onefile mode. citeturn322529search0
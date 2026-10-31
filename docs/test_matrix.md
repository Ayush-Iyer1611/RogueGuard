# Test Matrix — RogueGuard

| ID | Test | Expected result | Evidence to capture |
|---|---|---|---|
| T01 | Inventory identifies principal, roles and resource scope | Account details are visible | Screenshot of inventory |
| T02 | Each retained permission has a documented purpose | Required roles are shown beside granted roles | Screenshot of role comparison |
| T03 | Contain a synthetic identity with excess grants | Excess grants removed; status becomes QUARANTINED | Before/after screenshots |
| T04 | Verify required and unrelated access after containment | Required roles retained; unrelated roles absent | Role comparison screenshot |
| T05 | Containment preserves evidence | Timestamped audit event appears | Audit trail screenshot |
| T06 | Trigger a controlled unexpected error | Safe failure; no secrets exposed | Redacted output/log |
| T07 | Inspect source, output and logs for sensitive data | No real credentials or personal data present | Sanitised source/log review |
| T08 | Repeat the complete test set | Results reproducible; limitations recorded | Completed matrix |

**Important:** Mark tests PASS only after performing them and capturing evidence. The application is a local simulation; cloud-side tests require authorised Floci access and mentor approval.

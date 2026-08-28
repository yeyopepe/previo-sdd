```mermaid
flowchart TD
    Start([Invocation of pv-update])

    Start --> S1Read[Read .claude/pv-context.json best-effort]
    S1Read --> S1Exists{Does the file exist?}
    S1Exists -->|No| S1Info[INFO: the framework is not initialized, run pv-init]
    S1Info --> End1([End: nothing to audit])
    S1Exists -->|Yes| S2Run

    S2Run[Run audit-context.py] --> S2Empty{problems comes back empty?}
    S2Empty -->|Yes, and lastVerifiedVersion already exists| S2Healthy[INFO: healthy configuration]
    S2Healthy --> End2([End: nothing to fix])
    S2Empty -->|Yes, but no lastVerifiedVersion| S35Run
    S2Empty -->|No, there are problems| S3Loop

    S3Loop[Walk each returned problem, in order] --> S3Kind{Problem type}
    S3Kind -->|context-invalid-json| S3Invalid[ASK: fix the JSON by hand or state the intended structure]
    S3Invalid --> S3InvalidDec{JSON already fixed?}
    S3InvalidDec -->|Yes| S2Run
    S3InvalidDec -->|No, still waiting| End3Blocked([End: blocked by invalid JSON])

    S3Kind -->|version-check-downgrade| S3Downgrade[Run mark-verified.py --block]
    S3Downgrade --> S3DowngradeAsk[ASK: was the downgrade intentional?]
    S3DowngradeAsk --> S3DowngradeDec{User's answer}
    S3DowngradeDec -->|It was intentional| S3DowngradeConfirm[Run mark-verified.py --confirm-downgrade]
    S3DowngradeConfirm --> S3Next
    S3DowngradeDec -->|It was not intentional| S3DowngradeGuide[INFO: how to restore the correct files]
    S3DowngradeGuide --> End3Blocked2([End: blocked, blocked=true stays])

    S3Kind -->|Any other problem id| S3Fix[Apply the corresponding deterministic fix]
    S3Fix --> S3Next{More problems left to process?}
    S3Next -->|Yes| S3Loop
    S3Next -->|No| S35Run

    S35Run[Run mark-verified.py --clear] --> S4Rerun[Rerun audit-context.py to confirm]
    S4Rerun --> S4Report[INFO: final report grouped by area]
    S4Report --> EndOK([End: audit completed])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

```mermaid
flowchart TD
    Start([Invocation of pv-how])

    Start --> S0Check[Check framework initialized and version verified]
    S0Check --> S0Ok{Initialized, verified, not blocked?}
    S0Ok -->|No| S0Info[INFO: run pv-init/pv-update first]
    S0Info --> End0([End: stopped])
    S0Ok -->|Yes| S01Codes

    S01Codes[Run get-max-change-codes.py] --> S01Behind{Current xxxx lower than another already implemented/closed?}
    S01Behind -->|Yes| S01Warn[INFO: this entry is older than one already further along]
    S01Warn --> S1Identify
    S01Behind -->|No| S1Identify

    S1Identify[Identify the entry] --> S1Given{xxxx/description given?}
    S1Given -->|No| S1List[List inProgress/ entries]
    S1List --> S1Ask[ASK: which one to plan?]
    S1Ask --> S1AskDec{User picks one?}
    S1AskDec -->|None pending| End1([End: nothing to plan])
    S1AskDec -->|Picked| S1Found
    S1Given -->|Yes| S1Found{Found under inProgress/?}
    S1Found -->|No| S1NotFound[INFO: already implemented, or not found]
    S1NotFound --> End1b([End: not found])
    S1Found -->|Yes| S11Validate

    S11Validate[Read description.md and design_* files for inconsistencies] --> S11Issue{Inconsistency or gap found?}
    S11Issue -->|Yes| S11Ask[ASK: how to resolve it?]
    S11Ask --> S11Fix[Update affected documents with the answer]
    S11Fix --> S11Validate
    S11Issue -->|No| S2PlanExists

    S2PlanExists{plan.md already exists?}
    S2PlanExists -->|No| S3Write
    S2PlanExists -->|Yes| S2Ask[ASK: re-analyze from scratch or implement current plan.md?]
    S2Ask --> S2Dec{User choice}
    S2Dec -->|Re-analyze| S3Write
    S2Dec -->|Implement current plan| S31Risk

    S3Write[Read description.md Type: fix scopes strictly to root cause, change has full scope] --> S3Doubt{Technical doubts remain?}
    S3Doubt -->|Yes| S3Ask[ASK: resolve technical doubt]
    S3Ask --> S3Analysis
    S3Doubt -->|No| S3Analysis
    S3Analysis[Invoke pv-internal-tech-analysis for context] --> S3WritePlan[Write plan.md sections a-e]
    S3WritePlan --> S31Risk

    S31Risk[Invoke pv-internal-tech-risks on plan.md/description.md] --> S31Write[Write risk median to .metadata.json via set-metadata.py --set-risk]
    S31Write --> S31Detail{User asks for the 9-factor detail, now or later?}
    S31Detail -->|Yes| S31AddSection[Show detail and add section f Risk analysis to plan.md]
    S31AddSection --> S32Ask
    S31Detail -->|No| S32Ask

    S32Ask[ASK: implement now?] --> S32Dec{User confirms?}
    S32Dec -->|Yes| S32Do[Invoke pv-do on the same xxxx]
    S32Do --> EndDo([End: continues in pv-do])
    S32Dec -->|No| EndPending([End: stays planned, pending implementation])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

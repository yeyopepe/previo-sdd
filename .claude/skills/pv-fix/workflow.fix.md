```mermaid
flowchart TD
    Start([Invocation of pv-fix])

    Start --> S0Check[Check framework initialized and version verified]
    S0Check --> S0Ok{Initialized, verified, not blocked?}
    S0Ok -->|No| S0Info[INFO: run pv-init/pv-update first]
    S0Info --> End0([End: stopped])
    S0Ok -->|Yes| S1Understand

    S1Understand[Understand the request at the functional level] --> S1Ambiguous{Ambiguity about correct behavior?}
    S1Ambiguous -->|Yes| S1Ask[ASK: clarify expected behavior]
    S1Ask --> S2Analysis
    S1Ambiguous -->|No| S2Analysis

    S2Analysis[Invoke pv-internal-tech-analysis for context] --> S2Fast{Meets every fast criterion?}

    S2Fast -->|Yes, fast: trivial, bug or not| FT1

    S2Fast -->|No, and it's a bug| S3Doc
    S2Fast -->|No, and not a bug| S2Warn[INFO: doesn't qualify as fast nor a bug, unmet criterion]
    S2Warn --> S2New[Invoke pv-new with the request as-is]
    S2New --> EndNew([End: continues in pv-new])

    S3Doc[Invoke pv-internal-workflow: create description.md/history.md, type=fix] --> S3Flow{Flow, sequence or state interaction to represent?}
    S3Flow -->|Yes| S3Diagram[Invoke diagrams skill for functional diagram, include in description.md]
    S3Diagram --> S4Visual
    S3Flow -->|No| S4Visual

    S4Visual{Has a visual component?} -->|Yes| S4Mockup[Invoke mockups skill: create design_*.html]
    S4Mockup --> S41Data
    S4Visual -->|No| S41Data

    S41Data{Defines/uses structured data?} -->|Yes| S41Write[Write design_data_*.md tables directly]
    S41Write --> S5Validate
    S41Data -->|No| S5Validate

    S5Validate{Any diagram, design_*.html or design_data_*.md generated?}
    S5Validate -->|No| S6Chain
    S5Validate -->|Yes| S5Ask[ASK: does the representation reflect expected behavior?]
    S5Ask --> S5Dec{User confirms?}
    S5Dec -->|Changes requested| S5Adjust[Adjust and present again]
    S5Adjust --> S5Ask
    S5Dec -->|Confirmed| S6Chain

    S6Chain[Invoke pv-how on the same xxxx, scoped strictly to root cause] --> EndHow([End: continues in pv-how -> pv-do])

    FT1[Invoke pv-internal-workflow: create description.md/history.md, type=fast] --> FT2[Apply the change directly in code]
    FT2 --> FT2Check{Turns out not trivial while implementing? architecture/style touched, or scope grows}
    FT2Check -->|Yes| FT2Undo[Undo partial edits if any]
    FT2Undo --> FT2Route{Is it a bug?}
    FT2Route -->|Yes| S3Doc
    FT2Route -->|No| S2Warn
    FT2Check -->|No| FT3[Document applied changes in description.md]
    FT3 --> FT4[Invoke pv-internal-workflow: move inProgress to implemented]
    FT4 --> FT5[INFO: confirm what was implemented and the doc path]
    FT5 --> EndFast([End: fast-track completed])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

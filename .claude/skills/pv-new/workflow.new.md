```mermaid
flowchart TD
    Start([Invocation of pv-new])

    Start --> S0Check[Check framework initialized and version verified]
    S0Check --> S0Ok{Initialized, verified, not blocked?}
    S0Ok -->|No| S0Info[INFO: run pv-init/pv-update first]
    S0Info --> End0([End: stopped])
    S0Ok -->|Yes| S01Given

    S01Given{xxxx given at invocation?}
    S01Given -->|No| S02Todo
    S01Given -->|Yes| S01Exists{Folder exists at inProgress/xxxx?}
    S01Exists -->|Yes, new info given| S01Extend[Follow extend-entry.md in full]
    S01Extend --> EndExtend([End: entry extended])
    S01Exists -->|Yes, no new info, review/re-analyze| S1Understand
    S01Exists -->|No| S02Todo

    S02Todo{Invoked as /pv-new todo code?}
    S02Todo -->|Yes| S02Follow[Follow todo-mode.md in full]
    S02Follow --> EndTodo([End: entry created from todo idea])
    S02Todo -->|No| S1Understand

    S1Understand[Review request and code: build list of usual functional doubts - edge cases, coexistence, data scope, roles, visual definition] --> S1Propose[Propose an answer for each point, flag open questions]
    S1Propose --> S1Present[Present the full list at once]
    S1Present --> S1Dec{Doubts to resolve or open questions?}
    S1Dec -->|Yes| S1Ask[ASK: confirm/correct proposals, resolve open questions]
    S1Ask --> S2Doc
    S1Dec -->|No, all confirmed inline| S2Doc

    S2Doc[Invoke pv-internal-workflow: create description.md/history.md, type=change] --> S2Flow{Flow, steps or state interaction to represent?}
    S2Flow -->|Yes| S2Diagram[Invoke diagrams skill for functional diagram per use case, include in description.md]
    S2Diagram --> S3Visual
    S2Flow -->|No| S3Visual

    S3Visual{Which representation cases apply? not mutually exclusive}
    S3Visual -->|Visual/style change| S3Mockup[Invoke mockups skill: create design_*.html]
    S3Visual -->|UI navigation/interaction| S3NavList[List distinct navigation use cases, publish as text]
    S3NavList --> S3NavWrite[Create one design_navigation_*.md per use case]
    S3Visual -->|Structured data| S31Data[Write design_data_*.md tables directly]
    S3Visual -->|None apply| S4Validate

    S3Mockup --> S4Validate
    S3NavWrite --> S4Validate
    S31Data --> S4Validate

    S4Validate{Any diagram, design_*.html, design_navigation_*.md or design_data_*.md generated?}
    S4Validate -->|No| S5State
    S4Validate -->|Yes| S4Ask[ASK: does the representation reflect what you had in mind?]
    S4Ask --> S4Dec{User confirms?}
    S4Dec -->|Changes requested| S4Adjust[Adjust file s or diagram and present again]
    S4Adjust --> S4Ask
    S4Dec -->|Confirmed| S5State

    S5State[INFO: change documented, next step is pv-how] --> S5Now{User wants to implement now?}
    S5Now -->|Yes| S5How[Invoke pv-how directly on the xxxx]
    S5How --> EndHow([End: continues in pv-how])
    S5Now -->|No| EndOK([End: documented, pending pv-how])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

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
    S01Exists -->|Yes, new info given| S01ExtendInit[PROGRESS: init extend-entry list]
    S01ExtendInit --> S01Extend[Follow extend-entry.md in full]
    S01Extend --> S01ExtendClose[PROGRESS: close]
    S01ExtendClose --> EndExtend([End: entry extended])
    S01Exists -->|Yes, no new info, review/re-analyze| S1Init
    S01Exists -->|No| S02Todo

    S02Todo{Invoked as /pv-new todo code?}
    S02Todo -->|Yes| S02TodoInit[PROGRESS: init todo-mode list]
    S02TodoInit --> S02Follow[Follow todo-mode.md in full]
    S02Follow --> S02TodoClose[PROGRESS: close]
    S02TodoClose --> EndTodo([End: entry created from todo idea])
    S02Todo -->|No| S1Init

    S1Init[PROGRESS: init normal-flow list] --> S1Progress[PROGRESS: understand in_progress]
    S1Progress --> S1Understand[Review request and code: build list of usual functional doubts - edge cases, coexistence, data scope, roles, visual definition]
    S1Understand --> S1Propose[Propose an answer for each point, flag open questions]
    S1Propose --> S1Present[Present the full list at once]
    S1Present --> S1Dec{Doubts to resolve or open questions?}
    S1Dec -->|Yes| S1Ask[ASK: confirm/correct proposals, resolve open questions]
    S1Ask --> S1Done
    S1Dec -->|No, all confirmed inline| S1Done
    S1Done[PROGRESS: understand completed] --> S2Progress[PROGRESS: document in_progress]

    S2Progress --> S2Doc[Invoke pv-internal-workflow: create description.md/history.md, type=change]
    S2Doc --> S2Flow{Flow, steps or state interaction to represent?}
    S2Flow -->|Yes| S2Diagram[Invoke diagrams skill for functional diagram per use case, include in description.md]
    S2Diagram --> S2Done
    S2Flow -->|No| S2Done
    S2Done[PROGRESS: document completed] --> S3Progress[PROGRESS: represent in_progress]

    S3Progress --> S3Visual{Which representation cases apply? not mutually exclusive}
    S3Visual -->|Visual/style change| S3Mockup[Invoke mockups skill: create design_*.html]
    S3Visual -->|UI navigation/interaction| S3NavList[List distinct navigation use cases, publish as text]
    S3NavList --> S3NavWrite[Create one design_navigation_*.md per use case]
    S3Visual -->|Structured data| S31Data[Write design_data_*.md tables directly]
    S3Visual -->|None apply| S3Done

    S3Mockup --> S3Done
    S3NavWrite --> S3Done
    S31Data --> S3Done
    S3Done[PROGRESS: represent completed] --> S4Progress[PROGRESS: validate in_progress]

    S4Progress --> S4Validate{Any diagram, design_*.html, design_navigation_*.md or design_data_*.md generated?}
    S4Validate -->|No| S4Done
    S4Validate -->|Yes| S4Ask[ASK: does the representation reflect what you had in mind?]
    S4Ask --> S4Dec{User confirms?}
    S4Dec -->|Changes requested| S4Adjust[Adjust file s or diagram and present again]
    S4Adjust --> S4Ask
    S4Dec -->|Confirmed| S4Done
    S4Done[PROGRESS: validate completed] --> S5HookCheck

    S5HookCheck{20-after-entry.md defines steps?}
    S5HookCheck -->|Yes| S5HookRun[Run 20-after-entry steps in order, workFolder and xxxx substituted; a failure stops before handing off to pv-how]
    S5HookRun --> S5ChainProgress[PROGRESS: chain-pv-how in_progress]
    S5HookCheck -->|No| S5ChainProgress

    S5ChainProgress --> S5State[INFO: change documented, next step is pv-how]
    S5State --> S5Now{User wants to implement now?}
    S5Now -->|Yes| S5Done[PROGRESS: chain-pv-how completed]
    S5Done --> S5How[Invoke pv-how directly on the xxxx]
    S5How --> EndHow([End: continues in pv-how])
    S5Now -->|No| S5Close[PROGRESS: close]
    S5Close --> EndOK([End: documented, pending pv-how])

    End0 --> EndClose0[PROGRESS: close]

    classDef hook fill:#d9770e,color:#fff
    class S5HookCheck,S5HookRun hook

    classDef progress fill:#0891b2,color:#fff
    class S01ExtendInit,S01ExtendClose,S02TodoInit,S02TodoClose,S1Init,S1Progress,S1Done,S2Progress,S2Done,S3Progress,S3Done,S4Progress,S4Done,S5ChainProgress,S5Done,S5Close,EndClose0 progress
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.
- Orange nodes — the project's own hook insertion point (`stuff/hooks/new/*.md`): the check for defined steps and the run of those steps. Optional; a hook with no steps is skipped silently.
- Teal nodes — `[PROGRESS: ...]` nodes: invoke the skill configured in `framework.skills.progress`, if any. Optional; skipped silently when unconfigured.

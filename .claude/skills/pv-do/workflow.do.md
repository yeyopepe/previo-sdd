```mermaid
flowchart TD
    Start([Invocation of pv-do])

    Start --> S0Check[Check framework initialized and version verified]
    S0Check --> S0Ok{Initialized, verified, not blocked?}
    S0Ok -->|No| S0Info[INFO: run pv-init/pv-update first]
    S0Info --> End0([End: stopped])
    S0Ok -->|Yes| S0Progress

    S0Progress[PROGRESS: init] --> S1Identify

    S1Identify[Identify the entry] --> S1Given{xxxx/description given?}
    S1Given -->|No| S1List[List inProgress/ entries that have plan.md]
    S1List --> S1Ask[ASK: which one to implement?]
    S1Ask --> S1AskDec{User picks one?}
    S1AskDec -->|None ready| End1([End: nothing to implement, plan with pv-how first])
    S1AskDec -->|Picked| S15Progress
    S1Given -->|Yes| S1Found{Found under inProgress/ with plan.md?}
    S1Found -->|No plan.md| S1NoPlan[INFO: not planned yet, run pv-how first]
    S1NoPlan --> End1b([End: not planned])
    S1Found -->|Not in inProgress/| S1NotFound[INFO: already implemented, or not found]
    S1NotFound --> End1c([End: not found])
    S1Found -->|Yes| S15Progress

    S15Progress[PROGRESS: hooks in_progress] --> S15Load
    S15Load[List stuff/hooks/do/NN-slug.md files, match by NN id, parse each file's Step blocks]
    S15Load --> S20Hook{10-before-implementation.md defines steps?}
    S20Hook -->|Yes| S20Run[Run 10-before-implementation steps in order, workFolder and xxxx substituted; a failure stops implementation]
    S20Run --> S15Done
    S20Hook -->|No| S15Done
    S15Done[PROGRESS: hooks completed] --> S2Progress

    S2Progress[PROGRESS: implement in_progress] --> S2Impl
    S2Impl[Implement plan.md section b one task at a time, marking each box on completion] --> S2Viable{Plan viable as written?}
    S2Viable -->|No| S2Stop[INFO: explain why the plan isn't viable]
    S2Stop --> EndClose2[PROGRESS: close]
    EndClose2 --> End2([End: stopped, plan needs rework])
    S2Viable -->|Yes| S2Arch[Apply plan.md section c architecture changes, if any]
    S2Arch --> S2Done[PROGRESS: implement completed]
    S2Done --> S2VerifyProgress[PROGRESS: verify in_progress]
    S2VerifyProgress --> S2Verify[Run plan.md section e verification items one at a time, if any]
    S2Verify --> S2Reread[Reread whole plan.md for unchecked b/e boxes, complete any left pending]
    S2Reread --> S2VerifyDone[PROGRESS: verify completed]

    S2VerifyDone --> S21Progress[PROGRESS: docs in_progress]
    S21Progress --> S21Docs[Update docs.tech.architectureDocDir / docs.functional.featuresDocPathDir / docs.tech.styleBibleDocDir that the change touched]
    S21Docs --> S21Done[PROGRESS: docs completed]
    S21Done --> S22Hook{20-after-implementation.md defines steps?}
    S22Hook -->|Yes| S22Run[Run 20-after-implementation steps in order, workFolder and xxxx substituted; a failure stops before the folder moves]
    S22Run --> S3Progress
    S22Hook -->|No| S3Progress

    S3Progress[PROGRESS: move in_progress] --> S3Move
    S3Move[Invoke pv-internal-workflow action=move, inProgress to implemented] --> S3Done[PROGRESS: move completed]
    S3Done --> S3Close[PROGRESS: close]
    S3Close --> S4Confirm[INFO: what was implemented, which docs updated, folder moved; plus any hooks that ran]
    S4Confirm --> EndOK([End: implemented])

    End0 --> EndClose0[PROGRESS: close]
    End1 --> EndClose1[PROGRESS: close]
    End1b --> EndClose1b[PROGRESS: close]
    End1c --> EndClose1c[PROGRESS: close]

    classDef hook fill:#d9770e,color:#fff
    class S20Hook,S20Run,S22Hook,S22Run hook

    classDef progress fill:#0891b2,color:#fff
    class S0Progress,S15Progress,S15Done,S2Progress,S2Done,S2VerifyProgress,S2VerifyDone,S21Progress,S21Done,S3Progress,S3Done,S3Close,EndClose0,EndClose1,EndClose1b,EndClose1c,EndClose2 progress
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.
- Orange nodes — the project's own hook insertion points (`stuff/hooks/do/*.md`): the check for defined steps and the run of those steps. Optional; a hook with no steps is skipped silently.
- Teal nodes — `[PROGRESS: ...]` nodes: invoke the skill configured in `framework.skills.progress`, if any. Optional; skipped silently when unconfigured.

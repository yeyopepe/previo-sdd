```mermaid
flowchart TD
    Start([Invocation of pv-review-architecture])

    Start --> S0Check[Check framework initialized and version verified]
    S0Check --> S0Ok{Initialized, verified, not blocked?}
    S0Ok -->|No| S0Info[INFO: run pv-init/pv-update first]
    S0Info --> End0([End: stopped])
    S0Ok -->|Yes| S0Resolve[Resolve sourcecodeDir]
    S0Resolve --> S0ResOk{Resolution succeeded?}
    S0ResOk -->|No| S0ResInfo[INFO: run pv-update first]
    S0ResInfo --> End0
    S0ResOk -->|Yes| S1Read

    S1Read[Read the whole source tree: structure first, then content, depth where the checklist flags something] --> S2Checklist[Apply the fixed checklist: SoC/cohesion, SRP, size, SOLID, DRY, KISS, coupling/layering, folder structure, naming, dead weight]
    S2Checklist --> S3Build[Consolidate findings into a numbered proposal list: what/why/destination, ordered by impact]
    S3Build --> S3OutOfScope{Any valuable improvement needs new/removed code?}
    S3OutOfScope -->|Yes| S3Label[Label it separately as out of scope, not a numbered proposal]
    S3Label --> S4Present
    S3OutOfScope -->|No| S4Present

    S4Present[INFO: present the full numbered proposal list] --> S4Ask[ASK: create entries for all, some, or none?]
    S4Ask --> S4Dec{Any proposals selected?}
    S4Dec -->|None| EndList([End: list is the deliverable])
    S4Dec -->|Some/all| S5Loop[For each selected proposal]

    S5Loop --> S5Ask[ASK: this proposal as pv-todo idea or pv-new change?]
    S5Ask --> S5Route{User's choice}
    S5Route -->|pv-todo| S6Todo[Invoke pv-todo with the proposal's what/why/destination as the idea]
    S5Route -->|pv-new| S6New[Invoke pv-new with the proposal's what/why/destination, plus explicit note: update docs.tech in full detail after implementing]
    S6Todo --> S5More
    S6New --> S5More
    S5More{More selected proposals pending?}
    S5More -->|Yes| S5Loop
    S5More -->|No| S7Summary[INFO: final summary, proposal -> pv-todo code or pv-new xxxx]
    S7Summary --> EndDone([End: entries created])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.
- The `pv-todo`/`pv-new` choice (S5Ask) is asked **per proposal**, never assumed or defaulted — a batched question covering several proposals at once is allowed, but every proposal's destination must still be explicitly answered by the user.

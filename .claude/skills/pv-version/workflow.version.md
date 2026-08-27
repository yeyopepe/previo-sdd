```mermaid
flowchart TD
    Start([Invocation of pv-version])

    Start --> S02Intent

    S02Intent{Purely informational invocation about the build process?}
    S02Intent -->|Yes| S02Update[Update stuff/how-to-compile-version.md]
    S02Update --> S02Ask[ASK: launch the versioning process now with this updated procedure?]
    S02Ask --> S02Dec{User confirms?}
    S02Dec -->|No| End02([End: build procedure updated only])
    S02Dec -->|Yes| S05Guard
    S02Intent -->|No, wants a release| S05Guard

    S05Guard[List changes/implemented/ folders] --> S05Empty{implemented/ empty?}
    S05Empty -->|Yes| S1Resolve
    S05Empty -->|No| S05Loop[Take next pending entry]
    S05Loop --> S05AskEntry[ASK: does this entry move to closed?]
    S05AskEntry --> S05EntryDec{User confirms?}
    S05EntryDec -->|Yes| S05Move[move-change.py implemented to closed]
    S05Move --> S05Guard
    S05EntryDec -->|No| S05Wait[Wait for confirmation, no skipping]
    S05Wait --> S05AskEntry

    S1Resolve[Resolve XXXX] --> S1Given{XXXX given at invocation?}
    S1Given -->|No| S1Ask[ASK: which XXXX to use]
    S1Ask --> S2Folder
    S1Given -->|Yes| S2Folder

    S2Folder[Run init-version-folder.py] --> S2Exists{versions/XXXX already exists?}
    S2Exists -->|No| S3Check
    S2Exists -->|Yes| S2AskConflict[ASK: continue over it or choose another XXXX?]
    S2AskConflict --> S2ConflictDec{Choice}
    S2ConflictDec -->|Another XXXX| S1Resolve
    S2ConflictDec -->|Continue over it| S3Check

    S3Check{how-to-compile-version.md exists?} -->|No| S3Ask[ASK: exact build procedure]
    S3Ask --> S3Write[Write how-to-compile-version.md from template]
    S3Write --> S4Run
    S3Check -->|Yes| S4Run

    S4Run[Run the build command s from how-to-compile-version.md] --> S4Ok{Command succeeds and expected file appears?}
    S4Ok -->|No| S4Stop[INFO: explain the failure]
    S4Stop --> End4([End: build failed])
    S4Ok -->|Yes| S4Copy[copy-build-artifacts.py to versions/XXXX/files/]

    S4Copy --> S5Docs[Run copy-docs.py: zip the three docs.tech/docs.functional dirs]
    S5Docs --> S6Changelog[Invoke pv-internal-changelog on versions/XXXX/]
    S6Changelog --> S7Summary[INFO: summary of deliverable, docs, changelog]
    S7Summary --> EndOK([End: release prepared])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

```mermaid
flowchart TD
    Start([Invocation of pv-init])

    Start --> S0Base[Check base tooling: git, python]
    S0Base --> S0Cond{Any tool missing?}
    S0Cond -->|No| S1Run
    S0Cond -->|Yes| S0Ask[ASK: how to install the missing one]
    S0Ask --> S0Dec{User wants to install now?}
    S0Dec -->|Yes, installs it| S0Verify[Reinstall and re-verify the tool]
    S0Verify --> S1Run
    S0Dec -->|Won't or can't| S0Proceed[ASK: continue without it or stop here?]
    S0Proceed --> S0ProceedDec{Continue?}
    S0ProceedDec -->|Yes| S1Run
    S0ProceedDec -->|No| End0([End: init stopped])

    S1Run[Run check-context.py] --> S1Exists{.claude/pv-context.json exists?}
    S1Exists -->|No| S2Explore
    S1Exists -->|Yes, but invalid JSON, check-context.py fails, or missingRequired non-empty on an already-initialized project| S1Broken[Invoke pv-update]
    S1Broken --> S1Resume{Does pv-update leave anything pending for pv-init?}
    S1Resume -->|No| End1([End: resolved by pv-update])
    S1Resume -->|Yes| S2Explore

    S1Exists -->|Yes, valid JSON, framework does not exist| S2Explore
    S1Exists -->|"Yes, valid JSON, framework complete (missingRequired empty)"| S1Complete{"hasLanguage and no optionals pending?"}
    S1Complete -->|Yes, all complete| S1AskReset[ASK: reinitialize from scratch?]
    S1AskReset --> S1ResetDec{User confirms reset?}
    S1ResetDec -->|Yes| S1Erase[Erase current framework]
    S1Erase --> S2Explore
    S1ResetDec -->|No| S5Scaffold

    S1Complete -->|Language and/or some optional missing| S1AskComplete[ASK: complete the pending fields or leave as is?]
    S1AskComplete --> S1CompleteDec{User wants to complete?}
    S1CompleteDec -->|Yes| S3Ask
    S1CompleteDec -->|No| S5Scaffold

    S2Explore[Explore the repo for clues: architecture, features, style, source code] --> S3Ask

    S3Ask[Walk the framework fields in schema.json] --> S3Lang[ASK: interaction language and whether it's split by area]
    S3Lang --> S3Docs[Confirm/migrate architectureDocDir, styleBibleDocDir, featuresDocPathDir]
    S3Docs --> S3Src[ASK: confirm proposed sourcecodeDir]
    S3Src --> S3SrcCheck[Check whether that folder exists and has content]
    S3SrcCheck --> S3SrcDec{Folder empty or nonexistent?}
    S3SrcDec -->|Yes| S3Num
    S3SrcDec -->|No, code already there| S3SrcAsk["ASK: choose documentation level to generate at the end — minimal or full"]
    S3SrcAsk --> S3SrcMode[Keep the chosen mode in conversation memory]
    S3SrcMode --> S3Num

    S3Num[numberWidth: silent unless the user wants another value] --> S3Skills[skills.mockups/diagrams: write defaults silently]
    S3Skills --> S3Models[Compute skillModels with collect-skill-models.py and confirm with the user]
    S3Models --> S4Write

    S4Write[Write/merge .claude/pv-context.json] --> S5Scaffold

    S5Scaffold[Run scaffold-project.py] --> S5NewDoc{Any new docs.tech placeholder generated?}
    S5NewDoc -->|Yes| S5Info[INFO: the architectureDocDir/styleBibleDocDir placeholder was generated]
    S5Info --> S5Ask[ASK: what do you want to contribute to 01-overview.md?]
    S5Ask --> S5Edit[Edit 01-overview.md with the answer]
    S5Edit --> S55Check
    S5NewDoc -->|No| S55Check

    S55Check{Was existing code detected in step 3 and a mode chosen?}
    S55Check -->|No| S6Verify
    S55Check -->|Yes| S55Analysis["5.5.1 Invoke pv-internal-tech-analysis (bootstrap:true) over sourcecodeDir; keep the context in memory"]
    S55Analysis --> S55Style["5.5.2 Invoke pv-internal-doc-technical: writing rules + architectureDocDir category checklist"]
    S55Style --> S55Arch["5.5.3 Write architectureDocDir per the chosen mode (files via pv-internal-doc-files find+upsert) and populate 00-namespace.md"]
    S55Arch --> S55ArchCheck{"architectureDocDir has real {NNN}-*.md files, INDEX.md up to date, and 00-namespace.md populated?"}
    S55ArchCheck -->|No| S55Arch
    S55ArchCheck -->|Yes| S55Pres["5.5.4 Decide whether the project has a presentation layer"]
    S55Pres --> S55Bible["5.5.5 Invoke pv-internal-doc-style and write styleBibleDocDir at full depth (both modes) if there is a presentation layer; otherwise only naming, or leave it intentionally empty"]
    S55Bible --> S55Features["5.5.6 Build the EXHAUSTIVE feature list and, for each one, pv-internal-doc-features find + upsert (codes=init)"]
    S55Features --> S55FeatCheck{"Is there one {NNN}-*.md per feature on the list, and does INDEX.md list them all?"}
    S55FeatCheck -->|No, features missing| S55Features
    S55FeatCheck -->|Yes| S55Info["5.5.7 INFO: for each docs dir, file count, depth (minimal/full) and style-bible status; 00-namespace.md populated"]
    S55Info --> S6Verify

    S6Verify[Re-verify with check-context.py] --> S6Scaffold[Check scaffold-project.py output]
    S6Scaffold --> S6PvPy[Confirm pv.py overwritten]
    S6PvPy --> S6Summary[INFO: final summary of the whole configuration]
    S6Summary --> EndOK([End: init completed])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

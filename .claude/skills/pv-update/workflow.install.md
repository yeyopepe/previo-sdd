```mermaid
flowchart TD
    Start([Invocation of pv-update install])

    Start --> S2Resolve[Resolve target version: latest, or the --version tag the user asked for]
    S2Resolve --> S2Ask{Version unclear from the prompt?}
    S2Ask -->|Yes| S2AskUser[ASK: latest, or a specific version?]
    S2AskUser --> S2Resolve
    S2Ask -->|No| S1Report

    S1Report[Run install-framework.py WITHOUT --yes: query GitHub Releases, print latest official + newer pre-release if any] --> S3Compare

    S3Compare{install-framework.py's version check, against the resolved tag whatever its origin} -->|Tag doesn't parse as X.Y.Z| S3RejectFormat[INFO: tag isn't a valid version, not installing]
    S3RejectFormat --> EndReject([End: nothing installed])
    S3Compare -->|Older than installed, incl. when 'latest' itself resolves older than an installed pre-release| S3RejectDowngrade[INFO: pv-update install never downgrades, not installing]
    S3RejectDowngrade --> EndReject
    S3Compare -->|Equal or newer| S3SameCheck{Resolved tag == installed version exactly?}

    S3SameCheck -->|Yes| S3SameWarn[INFO: this reinstalls everything from scratch, same version, no upgrade]
    S3SameWarn --> S3PrereleaseCheck{Target is a pre-release?}
    S3SameCheck -->|No, strictly newer| S3PrereleaseCheck

    S3PrereleaseCheck -->|Yes| S3PrereleaseWarn[INFO: pre-release, not recommended for normal use]
    S3PrereleaseWarn --> S3Print
    S3PrereleaseCheck -->|No| S3Print

    S3Print[Script prints 'Resolved target version: X' and stops -- nothing installed yet] --> S3Confirm[ASK: confirm installing THIS EXACT resolved tag, naming it explicitly, even if it differs from what 'latest' implied]
    S3Confirm -->|User declines or asks for a different version| S2Resolve
    S3Confirm -->|User confirms this exact tag| S4Install

    S4Install[Re-run install-framework.py --version resolved_tag --yes: deletes any local install.sh/.ps1 first, downloads a fresh copy from previo-sdd main to a temp file, runs it, deletes it] --> S4Result{Platform script succeeded?}
    S4Result -->|No| S4Fail[INFO: installation failed, show the error]
    S4Fail --> EndFail([End: installation failed])
    S4Result -->|Yes| S5Chain[INFO: installed, now auditing the configuration]
    S5Chain --> S5Audit[Continue into audit mode workflow.audit.md, starting at S1Read]
    S5Audit --> EndOK([End: installed and audited])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

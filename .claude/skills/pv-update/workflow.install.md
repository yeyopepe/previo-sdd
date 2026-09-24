```mermaid
flowchart TD
    Start([Invocation of pv-update install])

    Start --> S1Report[Run install-framework.py: query GitHub Releases, print latest official + newer pre-release if any]
    S1Report --> S2Resolve[Resolve target version: latest, or the --version tag the user asked for]
    S2Resolve --> S2Ask{Version unclear from the prompt?}
    S2Ask -->|Yes| S2AskUser[ASK: latest, or a specific version?]
    S2AskUser --> S2Resolve
    S2Ask -->|No| S3Compare

    S3Compare{install-framework.py's version check} -->|Tag doesn't parse as X.Y.Z| S3RejectFormat[INFO: tag isn't a valid version, not installing]
    S3RejectFormat --> EndReject([End: nothing installed])
    S3Compare -->|Older than installed| S3RejectDowngrade[INFO: pv-update install never downgrades, not installing]
    S3RejectDowngrade --> EndReject
    S3Compare -->|Equal or newer| S3PrereleaseCheck{Target is a pre-release?}

    S3PrereleaseCheck -->|Yes| S3PrereleaseWarn[INFO: pre-release, not recommended for normal use]
    S3PrereleaseWarn --> S4Install
    S3PrereleaseCheck -->|No| S4Install

    S4Install[Invoke install.sh/install.ps1 with the resolved tag] --> S4Result{Platform script succeeded?}
    S4Result -->|No| S4Fail[INFO: installation failed, show the error]
    S4Fail --> EndFail([End: installation failed])
    S4Result -->|Yes| S5Remind[INFO: installed, run /pv-update audit mode next]
    S5Remind --> EndOK([End: installed])
```

Legend:
- `[Text]` — internal step, the skill acts without talking to the user.
- `[INFO: Text]` — the skill informs the user; doesn't block, continues without waiting for a reply.
- `[ASK: Text]` — the skill informs and asks for confirmation/input; blocking, doesn't proceed without the user's answer.
- `{Text}` — decision branch; each outgoing edge carries its own label.

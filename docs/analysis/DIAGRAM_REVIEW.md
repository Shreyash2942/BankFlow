# ATM diagram review

Reviewed on 2026-09-22. All four raster diagrams were inspected visually; all three Visio files were opened read-only as ZIP archives and their page shape text and connector endpoints were inspected. No source diagram or application file was modified. This review concerns the legacy ATM design, not an implemented BankFlow architecture.

## What the diagrams establish

The shared core is one ATM withdrawal session: card insertion, PIN verification, at most three failed PIN attempts, amount entry, funds checking, cash dispensing, balance update, and session completion. The legacy rule closes an account when the remaining balance is zero. Customer, ATM, and bank/account responsibilities are separated in the activity and sequence views. The program implements these responsibilities in one script rather than separate services or account objects.

## Findings requiring reconciliation

| Finding | Evidence | Implication for the next design |
|---|---|---|
| Debit and cash order conflict | The sequence diagram performs debit and receives success at messages 16-19, then dispenses at 20. The activity diagram dispenses at 11 and updates at 12. `atm_simulation.py` prints dispensing before subtracting the amount. | Select a single transaction lifecycle and describe failure/reversal behavior before implementing persistent transactions. |
| Revised state machine loses the retry path | The JPG connects Increment Attempts to the final state. VSDX connector 1049 runs from grouped Increment Attempts shape 1014 to final shape 1035. The separate Retry label 1052 has no connector endpoints. | One failed PIN must not terminate the session if the intended limit is three; redraw and test the retry transition. |
| Retention/ejection conflict | Revised state machine Customer Rejected entry says both ?Card Retained Message? and ?Eject Card?; activity, original PNG, and code say retained. | Define one terminal outcome and align diagram labels and behavior. |
| Activity balance messages connect to PIN rejection | VSDX 1084 and 1085 connect bank Check Balance to Reject Customer; 1086 connects Reject Customer back to bank Check Balance with label Sufficient Funds. These paths are visible in the JPG. | Balance checking must connect to withdrawal validation, not the PIN-attempt failure branch. |
| Activity has bypass and disconnected endings | Connector 1079 runs Amount <= Balance? directly to View Message, alongside the cash-dispense path. Reject Customer and Display Transaction Complete have no outgoing attached connectors in the XML. Take Cash and Receipt has no incoming attached connector. | Make success, rejection, cash delivery, and card/session termination paths unambiguous. |
| Activity has an unexplained validation loop | Connector 1088 returns post-withdrawal Check Account Balance to Validate Withdrawal Amount with label ?Chceck Balance.? | Clarify whether this is a bank query or another withdrawal; the code ends after one withdrawal. |
| Sequence request/selection arrows point the wrong way for their names | Messages 2 Request PIN and 10 Request Amount run Customer to ATM; 9 Select Withdrawal runs ATM to Customer. XML endpoints confirm the visual directions. | ATM requests input; customer submits PIN, selection, and amount. Correct endpoints before deriving interfaces. |
| Sequence chronology and alternatives are incomplete | Verify PIN is drawn above Enter PIN; valid and invalid replies precede an unconditional Display Menu. The only `alt` fragment is funds sufficient/insufficient. | Add authentication alternatives and retry termination; ensure input precedes its verification. |
| Revised state machine omits amount rejection | Request Withdrawal goes directly to Withdrawal, whose entry dispenses and updates. No invalid or insufficient-funds branch appears. Original PNG and code cover these cases. | Retain the original PNG?s amount-validation concepts when revising the state model. |
| Original PNG repeats increment semantics | The PIN-failure transition says `attempts = attempts + 1`, and Increment Attempts has entry `incrementCounter()`. | Specify exactly one counter increment per failed PIN; implementing both literally would double-count. |
| Original PNG amount guards overlap | `Amount <= Balance` and `Amount <= 0` can both hold. | Success must require a positive, valid amount as well as sufficient funds. |

These are findings about the files as drawn, not assumptions that the author intended the erroneous paths.

## Agreement with the Python baseline

`authenticate_customer()` correctly increments once after a wrong PIN and returns to the prompt until the third failure. This matches the activity?s main authentication path and the original PNG?s intended retry flow, but not the revised state diagram?s attached increment-to-final connector.

`request_withdrawal()` loops on nonnumeric, nonpositive, and excessive amounts. The original PNG models nonpositive and excessive amounts; the activity models excessive amounts; the revised state machine and sequence are incomplete for these cases. The code uses Python `float`, so its existing numeric check does not reject `nan`; a future numeric specification should explicitly require finite, positive values with the chosen monetary precision.

`run_atm()` initializes a fresh $500 balance for each session, simulates one card and one withdrawal, prints cash delivery, subtracts the amount, and prints CLOSED when the result equals zero. It has no persisted account closure, bank service, menu selection, receipt implementation, card hardware, transaction record, or multi-session account state. Diagram messages describing those concepts should therefore be treated as design intent or simulation output, not proof of implemented capabilities.

## Editable Visio coverage

| Editable source | Page 1 shapes | Attached connector endpoints | Comparison with raster export |
|---|---:|---:|---|
| ATM System - UML Activity Diagram.vsdx | 81 | 71 | Text, numbering, decisions, and problematic bank/rejection connections agree with corresponding JPG. |
| ATM System - UML State Machine Diagram.vsdx | 54 | 30 | State labels and attached transitions agree with corresponding JPG; XML confirms missing attached retry connector. |
| SEQUENCE DIAGRAM.vsdx | 58 | 49 | Message text and directions agree with corresponding JPG, including Request PIN/Request Amount/Select Withdrawal anomalies. |

Counts include nested/group shapes and text labels. Endpoint counts are attachment records, not a count of messages or arrows. XML inspection was not a Visio render: no claim is made about pixel-exact layout fidelity, embedded media, or every style attribute. The older `ATM System State machine Diagram.png` has no corresponding editable file in this set and contains more validation/retry detail than the revised state machine.

## Extraction artifacts and limits

- `.graphify_chunk_02.json`: activity image, 32 nodes and 39 edges.
- `.graphify_chunk_03.json`: revised state machine JPG, 14 nodes and 17 edges.
- `.graphify_chunk_04.json`: original state machine PNG, 18 nodes and 24 edges.
- `.graphify_chunk_05.json`: sequence image, 31 nodes and 52 edges.
- `.diagram_xml_review.json`: shape text and attachment records from the three VSDX archives for auditing.

Every fragment preserves image provenance. Explicit diagram relationships use EXTRACTED; interpretation is marked INFERRED; the revised diagram?s disconnected intended retry destination is AMBIGUOUS. No inferred transition was silently substituted for an erroneous drawn one. No separate author rationale is stated in these diagrams; the inferred rationale nodes describe separation of responsibilities only. Token counters are zero because per-agent token accounting is unavailable, not because extraction incurred no tokens.

Recommended first design step: reconcile the session state machine, monetary invariants, transaction ordering, card rejection behavior, and zero-balance account policy against the new requirements before using these diagrams as implementation contracts.


Snapshot note: this report records the pre-Day-1 review. For current implementation status, read [project memory](../MEMORY.md). Historical source paths refer to the supplied workspace; original assets now live under `docs/original-college-project/`.

# Image review: legacy ATM prototype

Reviewed 2026-09-22 using direct image inspection of all eight assigned images and comparison with `atm_simulation.py`. The image filenames are provenance labels; their embedded dates do not establish creation dates or authorship. Original assets were not changed. Graph chunks 06-13 retain separate provenance for each image. Diagram statements describe intended design, while transcript statements describe visible example outcomes; neither proves persistent storage, backend integration, or a functioning BankFlow application.

## Inventory and duplication

| Graph chunk | Source | What it contains |
|---|---|---|
| 06 | `ChatGPT Image Aug 31, 2026, 07_45_29 PM.png` | Numbered activity diagram with Customer, ATM System, and Bank / Account System swimlanes |
| 07 | `ChatGPT Image Aug 31, 2026, 07_47_23 PM.png` | Byte-identical copy of chunk 06's image |
| 08 | `ChatGPT Image Aug 31, 2026, 07_47_42 PM.png` | Standalone state machine with authentication, withdrawal, and account status branches |
| 09 | `ChatGPT Image Aug 31, 2026, 07_56_47 PM.png` | Composite state machine, numbered activity, and sequence diagram |
| 10 | `ATM_Execution_Screenshots/customer_rejected.png` | Three wrong PIN inputs followed by rejection |
| 11 | `ATM_Execution_Screenshots/incorrect_then_correct_pin.png` | Two wrong PIN inputs, successful third input, then withdrawal |
| 12 | `ATM_Execution_Screenshots/successful_withdrawal.png` | Correct first PIN input, then withdrawal |
| 13 | `ATM_Execution_Screenshots/zero_balance_account_closed.png` | Withdrawal of the full starting balance, then account closure message |

The two activity images have SHA-256 `9760DE46E38F424975D332D7C9626552A01EC5D326E945E15606B7FCDD694EFF`. They are one design artifact in two files, not independent confirmation of a requirement.

## What the images agree on

The legacy concept is an ATM session: accept a card, request and validate a PIN, count failed attempts, authenticate or reject, validate a withdrawal amount, dispense cash, update the balance, and finish. Three incorrect PINs lead to rejection and card retention. A zero balance leads to an automatic account-closure outcome. Positive remaining balances lead to a transaction-complete message. The bank and account database drawn in diagrams are intended collaborators, not evidence of corresponding implemented services.

The four transcript images show these exact examples:

| Scenario | PIN inputs | Withdrawal | Displayed outcome |
|---|---|---|---|
| Successful withdrawal | `2468` | $100 from $500 | $400; ACTIVE; session ends |
| Retry then success | `1111`, `2222`, `2468` | $100 from $500 | Third input succeeds; $400; ACTIVE |
| Rejection | `1111`, `2222`, `3333` | None | Failure counts 1/3, 2/3, 3/3; card retained; access denied |
| Full withdrawal | `2468` | $500 from $500 | $0; CLOSED; session ends |

These are useful acceptance-example seeds. They do not show malformed withdrawal input, nonpositive amounts, insufficient funds, persistence across sessions, concurrent transactions, canceled operations, or failures while updating balances or dispensing cash.

## Diagram contradictions and modeling defects

1. **Numbered activity diagram (both duplicate images):** the visible solid arrow goes from Request PIN to Validate PIN, with another arrow pointing from Validate PIN toward Enter PIN. The numbered list and Python code instead require entry before validation. Bank Check Balance dashed connections visually run into the Reject Customer area. These routing defects should be corrected before treating arrows as executable process rules.
2. **Standalone state machine:** Customer Rejected explicitly contains both “Display Card Retained Message” and “Eject Card,” while its notes say the card is retained. The retry label is disconnected from a clear Increment Attempts → PIN Entry route; the increment path visibly reaches the final-state route. The withdrawal path also omits an amount-validation/insufficient-funds branch.
3. **Composite activity panel:** step 6 is duplicated; the No branch of PIN Correct reaches an increment box connected to a final node, while another increment box is placed above the attempts decision. The decision's labeled routing does not express a coherent retry-versus-reject loop. Both outgoing balance-decision labels read Yes. Step 11 is labeled Take Cash and Receipt rather than Dispense Cash as in the code.
4. **Composite sequence versus prototype:** the sequence panel depicts debit/update success before cash is dispensed. The prototype (`atm_simulation.py:103-107`), duplicate activity images, and transcript examples depict cash dispense before the balance update. A future implementation needs one explicit transaction ordering and a defined failure policy.
5. **Composite state machine:** incorrect PIN is represented as a Validate PIN self-transition without a clear route back to PIN Entry for new input. Its PIN Entry self-transition validates format, but the Python function only compares input to a constant (`atm_simulation.py:27-35`).

## Relationship to the code and next version

The example inputs and outputs match the constants and branches visible in `atm_simulation.py`: PIN `2468`, three attempts, and a $500 starting balance (`:10-12`); authentication and rejection (`:20-49`); single withdrawal (`:52-76`, `:101`); and zero-balance closure versus ACTIVE output (`:112-121`). This review did not execute the script; compare the separate prototype validation artifact for runtime evidence.

The code is a console simulation: it resets a local balance each session (`:81`), has no account identity lookup or bank/database service, and prints card retention, cash dispense, and account closure as messages. CLOSED is not a persisted account state. The screenshot images therefore support the legacy demonstration's intended behavior but do not establish that the expanded BankFlow requirements are implemented.

For the upgrade, preserve these four behavioral examples as a traceable legacy baseline, reconcile diagram flow defects against the requirements, define whether automatic closure at zero remains part of the next version, and choose a canonical editable diagram source. Specify account/session states separately, real monetary validation and storage, transaction ordering, and failure outcomes before mapping the legacy console steps into services or UI screens. The requirements documents should determine the final scope; these legacy raster diagrams alone should not drive it.


Snapshot note: this report records the pre-Day-1 review. For current implementation status, read [project memory](../MEMORY.md). Historical source paths refer to the supplied workspace; original assets now live under `docs/original-college-project/`.

# BankFlow UI Reference Map

The supplied design references live in the sibling `../ui-design-images` directory. They are
visual specifications; the Streamlit application renders the product UI from maintainable Python
and CSS rather than embedding the mockups as screenshots.

## Implemented V1 screens

| Reference image | Streamlit implementation | Status |
|---|---|---|
| `login page.png` | `app.py` | Implemented |
| `account-dashboard.png` | `pages/1_Dashboard.py` | Implemented |
| `Withdraw Funds - UI Design.png` | `pages/2_Withdraw.py` | Implemented |
| `Deposit Funds - UI Design.png` | `pages/3_Deposit.py` | Implemented |
| `Transaction History - UI Design.png` | `pages/4_Transaction_History.py` | Implemented |
| `Authentication and transaction.png` | Authentication errors and transaction receipts | Implemented in the relevant flow |
| `End Session (Logout) - UI Design.png` | Confirmed sidebar end-session dialog | Implemented |

The implementation follows the reference palette, dark authenticated navigation, account metrics,
two-column transaction forms, quick amount controls, searchable transaction history, success and
warning states, responsive stacking, and persistent demo-environment labeling.

## Phase 2 screen contracts

| Reference image | Streamlit implementation | Status |
|---|---|---|
| `Analytics Dashboard - UI Design.png` | `pages/5_Analytics.py` operational metrics | Implemented |
| `Analytics Dashboard - UI Design 2.png` | `pages/5_Analytics.py` transaction amount views | Implemented within V1 mart scope |
| `Transactions Dashboard - UI Design.png` | Event-stream transaction monitoring | Planned for V2 |
| `Platform Status - UI Design.png` | `pages/6_Platform_Status.py` live service/build health | Implemented for V1 services |
| `About bankflow.png` | Project, architecture, and technology overview | Planned |
| `End Session (Logout) - UI Design-1.2.png` | Expanded demo/session management | Planned |

These later screens should only display values backed by real BankFlow services, topics, pipelines,
or persisted records. Their supplied images define layout and visual treatment, while the Phase 2
milestones provide the data required to implement them honestly.

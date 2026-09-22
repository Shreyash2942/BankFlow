# BankFlow Design System

**Project Name:** BankFlow  
**Repository Name:** `BankFlow`  
**Document Type:** UI / Visual Design System  
**Primary Interface:** Streamlit  
**Design Direction:** Modern, minimal, trustworthy, data-focused  

---

# 1. Design Overview

BankFlow should visually communicate three qualities:

1. **Trust** — the interface should feel reliable and financially secure.
2. **Clarity** — users should understand what action to take without confusion.
3. **Modern Engineering** — the interface should look current, clean, and portfolio-ready without becoming visually complicated.

The design should support both sides of the project:

- **ATM Application Experience**
- **Data / Analytics Platform Experience**

The ATM portion should feel simple and focused.

The analytics portion should feel structured, professional, and data-driven.

BankFlow should avoid overly decorative banking visuals, excessive animation, crowded dashboards, and complex navigation.

---

# 2. Design Principles

## 2.1 Simple First

Every screen should have one primary purpose.

Examples:

- Authentication screen → enter PIN
- Dashboard → understand account status
- Withdrawal screen → perform withdrawal
- Analytics screen → understand platform metrics

Avoid presenting too many actions at the same time.

---

## 2.2 Clear Visual Hierarchy

Information should appear in this order:

```text
Page Title
    ↓
Important Status / Balance
    ↓
Primary Action
    ↓
Supporting Information
    ↓
Secondary Actions
```

Users should immediately recognize:

- where they are
- what the most important information is
- what action they can take next

---

## 2.3 Trustworthy Visual Language

BankFlow is a financial-system simulation.

The design should use:

- stable colors
- consistent spacing
- clear labels
- predictable navigation
- restrained use of red
- clear confirmation messages
- visible system status

Avoid:

- neon colors
- excessive gradients
- playful fonts
- unnecessary animations
- ambiguous buttons

---

## 2.4 Data Should Be Easy to Scan

Analytics pages should prioritize:

- key metrics
- trend charts
- simple tables
- consistent status indicators
- clear date/time labels

Charts should answer a specific question rather than simply fill space.

---

## 2.5 Consistency Across V1 and V2

Version 2 should extend the visual system rather than introduce a new one.

Application screens and data-platform screens should share:

- typography
- spacing
- card styles
- status colors
- button styles
- navigation
- data table styling

---

# 3. Brand Identity

## Product Name

**BankFlow**

## Product Tagline

> Event-Driven ATM Transaction and Analytics Platform

Alternative short tagline for the application:

> Secure Transactions. Observable Data.

---

## Brand Personality

BankFlow should feel:

- professional
- modern
- secure
- calm
- technical
- reliable
- clean

BankFlow should not feel:

- playful
- flashy
- overly corporate
- visually dense
- like a real commercial bank product

The project should clearly remain a technical portfolio demonstration.

---

# 4. Color Palette

The palette uses navy for trust, emerald for successful actions, neutral grays for structure, and red/amber only for important states.

---

## 4.1 Primary Colors

### BankFlow Navy

```text
HEX: #0F172A
RGB: 15, 23, 42
```

Use for:

- navigation
- main headings
- important text
- dark backgrounds
- brand elements

---

### BankFlow Blue

```text
HEX: #2563EB
RGB: 37, 99, 235
```

Use for:

- primary buttons
- active navigation
- links
- selected states
- informational highlights

---

### BankFlow Emerald

```text
HEX: #059669
RGB: 5, 150, 105
```

Use for:

- successful transactions
- connected services
- positive balance indicators
- confirmations
- success badges

---

# 5. Supporting Colors

## Background

```text
#F8FAFC
```

Main application background.

---

## Surface / Card

```text
#FFFFFF
```

Used for:

- cards
- forms
- metrics
- tables
- content containers

---

## Primary Text

```text
#0F172A
```

---

## Secondary Text

```text
#475569
```

---

## Muted Text

```text
#64748B
```

---

## Border

```text
#E2E8F0
```

---

## Success

```text
#059669
```

---

## Warning

```text
#D97706
```

---

## Error

```text
#DC2626
```

---

## Information

```text
#2563EB
```

---

# 6. Status Color Rules

Status colors should always have semantic meaning.

| Status | Color | Use |
|---|---|---|
| Success | `#059669` | completed transactions, connected services |
| Information | `#2563EB` | active state, general information |
| Warning | `#D97706` | low attempts remaining, attention needed |
| Error | `#DC2626` | failed transaction, locked card |
| Neutral | `#64748B` | inactive / unavailable / demo mode |

Do not use red for decoration.

Red should indicate an actual problem or destructive state.

---

# 7. Typography

The interface should use a clean sans-serif style.

## Primary Font

Recommended:

```text
Inter
```

Fallback:

```text
Arial
Helvetica
sans-serif
```

Streamlit's default sans-serif typography may be retained when custom font loading is unnecessary.

---

## Typography Scale

### Display / Hero

```text
32–40 px
Weight: 700
```

Example:

```text
Welcome to BankFlow
```

---

### Page Title

```text
28–32 px
Weight: 700
```

---

### Section Heading

```text
20–24 px
Weight: 600
```

---

### Card Metric

```text
28–36 px
Weight: 700
```

Example:

```text
$2,450.00
```

---

### Body

```text
15–16 px
Weight: 400
```

---

### Small / Metadata

```text
12–14 px
Weight: 400
```

Used for:

- timestamps
- account suffix
- system metadata
- help text

---

# 8. Spacing System

Use an 8-pixel spacing system.

```text
4 px   = micro spacing
8 px   = small
16 px  = standard
24 px  = medium
32 px  = large
48 px  = section
64 px  = major section
```

Streamlit layouts should avoid tightly stacked widgets.

Preferred spacing between:

```text
Label → Input          8 px
Input → Button        16 px
Cards                 16–24 px
Sections              32–48 px
Page blocks           48–64 px
```

---

# 9. Layout System

## 9.1 Main Page Width

Use Streamlit:

```python
st.set_page_config(
    page_title="BankFlow",
    page_icon="🏦",
    layout="wide"
)
```

Main content should remain visually centered.

Avoid stretching important forms across the entire screen.

---

## 9.2 Application Layout

```text
┌──────────────────────────────────────────────────────┐
│ BankFlow                           Demo Environment  │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Page Title                                           │
│ Supporting description                               │
│                                                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Primary Content                                  │ │
│ │                                                  │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ Secondary Content                                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 9.3 Dashboard Grid

Desktop:

```text
┌──────────────────────────────────────────────────┐
│ Available Balance                                │
│ $2,450.00                                        │
└──────────────────────────────────────────────────┘

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Withdraw     │ │ Deposit      │ │ Transactions │
└──────────────┘ └──────────────┘ └──────────────┘

┌──────────────────────────────────────────────────┐
│ Recent Transactions                              │
└──────────────────────────────────────────────────┘
```

---

# 10. Navigation

Recommended navigation:

```text
BankFlow
│
├── Dashboard
├── Withdraw
├── Deposit
├── Transaction History
├── Analytics
├── Platform Status
└── About
```

Navigation can use Streamlit's multipage navigation.

The authenticated ATM session should remain visually separate from project/documentation pages.

---

# 11. Core UI Components

## 11.1 Header

Contents:

```text
BankFlow
Event-Driven ATM Platform

DEMO MODE
```

The demo badge should always be visible.

Recommended badge:

```text
DEMO MODE
```

Style:

- neutral or blue background
- compact size
- uppercase
- rounded corners

---

## 11.2 Balance Card

Purpose:

Display the most important account information.

Example:

```text
Available Balance

$2,450.00

Checking •••• 2048
```

Design:

- large amount
- muted account number
- white surface
- subtle border
- 12–16 px radius
- generous padding

---

## 11.3 Metric Card

Example:

```text
Transactions Today
154
+12% vs yesterday
```

Use for:

- total transactions
- success rate
- withdrawal volume
- failed authentication
- locked cards

---

## 11.4 Primary Button

Examples:

```text
Authenticate
Withdraw
Deposit
Continue
```

Style:

```text
Background: #2563EB
Text: #FFFFFF
Radius: 8–10 px
Font Weight: 600
```

Only one primary button should dominate a form.

---

## 11.5 Secondary Button

Examples:

```text
Cancel
Back
View History
```

Style:

```text
Background: #FFFFFF
Border: #CBD5E1
Text: #334155
```

---

## 11.6 Destructive Button

Examples:

```text
End Session
Reset Demo
```

Use carefully.

Do not make every session-ending action bright red.

Red should be reserved for destructive or irreversible behavior.

---

# 12. Input Components

## PIN Input

Example:

```text
Enter PIN

[ •••• ]

Attempts remaining: 3

[ Authenticate ]
```

Requirements:

- password-masked input
- no PIN displayed in logs
- clear attempts remaining
- warning after failed attempt
- error state after lockout

---

## Amount Input

Example:

```text
Withdrawal Amount

$ [ 100.00 ]

Quick Select

[ $20 ] [ $50 ] [ $100 ] [ $200 ]

[ Withdraw ]
```

Rules:

- numeric input only
- clear currency formatting
- show available balance nearby
- show validation before transaction execution

---

# 13. Status Messages

## Success

```text
✓ Transaction Successful

$100.00 withdrawn
Remaining balance: $2,350.00
```

Use:

```text
Emerald indicator
```

---

## Warning

```text
⚠ Incorrect PIN

2 attempts remaining
```

Use amber.

---

## Error

```text
Transaction Declined

Requested: $3,000.00
Available: $2,450.00
```

Use red.

---

## Locked State

```text
Card Locked

Maximum PIN attempts reached.
The demo card has been temporarily locked.
```

Use strong error styling but keep language calm.

---

# 14. Transaction Table

Recommended columns:

| Date / Time | Transaction ID | Type | Amount | Status |
|---|---|---|---:|---|
| Sep 22, 3:20 PM | TX5001 | Withdrawal | -$100.00 | Success |
| Sep 22, 1:05 PM | TX4998 | Deposit | +$500.00 | Success |
| Sep 21, 5:45 PM | TX4988 | Withdrawal | -$3,000.00 | Declined |

Rules:

- right-align currency
- use badges for status
- format timestamps consistently
- avoid unnecessary database fields

---

# 15. Analytics Design

Analytics pages should answer clear questions.

---

## 15.1 Metric Row

Recommended first row:

```text
Transactions Today
Successful
Declined
Total Volume
```

Second row:

```text
Withdrawals
Deposits
Authentication Failures
Locked Cards
```

---

## 15.2 Charts

Recommended charts:

### Transaction Volume Over Time

Purpose:

```text
How is transaction activity changing?
```

Chart:

```text
Line chart
```

---

### Transaction Types

Purpose:

```text
What types of transactions are occurring?
```

Chart:

```text
Bar chart
```

---

### Success vs Decline

Purpose:

```text
How many transactions succeed?
```

Chart:

```text
Bar or donut-style representation
```

---

### Hourly Activity

Purpose:

```text
When is the system busiest?
```

Chart:

```text
Column chart
```

---

## Chart Rules

Use:

- limited palette
- clear axes
- readable labels
- meaningful titles
- visible units
- tooltips where supported

Avoid:

- unnecessary 3D charts
- too many colors
- decorative charts without a question
- more than 4 major charts on one page

---

# 16. Platform Status Components

Example:

```text
Platform Status

PostgreSQL       ● Connected
Redis            ● Connected
Kafka            ● Connected
Airflow          ● Running
Spark            ● Available
HDFS             ● Available
Iceberg          ● Available
```

Status mapping:

```text
Connected / Healthy     → Emerald
Warning / Degraded      → Amber
Unavailable             → Red
Demo / Not Required     → Gray
```

---

# 17. Version 1 Screen Designs

## 17.1 Welcome Screen

```text
┌───────────────────────────────────────────────┐
│                  BankFlow                     │
│      Event-Driven ATM Transaction Platform    │
│                                               │
│              DEMO ENVIRONMENT                 │
│                                               │
│        [ Insert / Select Demo Card ]           │
│                                               │
│     No real financial data is collected.      │
└───────────────────────────────────────────────┘
```

---

## 17.2 Authentication Screen

```text
┌───────────────────────────────────────────────┐
│ BankFlow                                      │
│                                               │
│ Enter Your PIN                                │
│                                               │
│ [ •••• ]                                      │
│                                               │
│ Attempts remaining: 3                         │
│                                               │
│ [ Authenticate ]                              │
│                                               │
│ Demo PIN: 2468                                │
└───────────────────────────────────────────────┘
```

---

## 17.3 Account Dashboard

```text
┌────────────────────────────────────────────────────────┐
│ BankFlow                               DEMO MODE        │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Welcome, Demo Customer                                 │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Available Balance                                  │ │
│ │ $2,450.00                                          │ │
│ │ Checking •••• 2048                                 │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ [ Withdraw ]     [ Deposit ]     [ History ]           │
│                                                        │
│ Recent Transactions                                    │
│ ------------------------------------------------------ │
│ Withdrawal       -$100.00        Successful            │
│ Deposit          +$500.00        Successful            │
│ Withdrawal      -$3000.00        Declined              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 17.4 Withdrawal Screen

```text
Withdraw Funds

Available Balance
$2,450.00

Withdrawal Amount
[ $100.00 ]

Quick Amount

[ $20 ] [ $50 ] [ $100 ] [ $200 ]

[ Withdraw Funds ]
```

---

## 17.5 Transaction Result

```text
✓ Transaction Successful

Amount Withdrawn
$100.00

New Balance
$2,350.00

Transaction ID
TX500123

[ Return to Dashboard ]
```

---

# 18. Version 2 Screen Designs

Version 2 extends the same design language.

---

## 18.1 Streaming Analytics

```text
BankFlow Data Platform

Events Processed
1,204,521

Streaming Rate
2,450 events/min

Pipeline Status
Healthy

Bronze Records     1,204,521
Silver Records     1,202,894
Gold Records          32,441
```

---

## 18.2 Lakehouse Status

```text
Lakehouse

Bronze        Healthy
Silver        Healthy
Gold          Healthy

Last Pipeline Run
Sep 22, 2026 3:30 PM

Data Quality
99.86%
```

---

# 19. Iconography

Use icons only when they improve recognition.

Recommended concepts:

```text
🏦 Bank / application
💳 Card
🔐 Authentication
💰 Balance
↓ Withdrawal
↑ Deposit
📜 History
📊 Analytics
⚙ Platform
✓ Success
⚠ Warning
✕ Error
```

For a more professional final interface, simple line icons may replace emoji.

Avoid using multiple icon styles on the same page.

---

# 20. Border Radius

Recommended:

```text
Inputs             8 px
Buttons            8 px
Cards             12 px
Large Panels      16 px
Status Badges      999 px / pill
```

---

# 21. Shadows

Use subtle shadows only on major cards.

Example:

```css
box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
```

Avoid strong floating-card effects.

---

# 22. Accessibility

BankFlow should target accessible visual behavior.

Requirements:

- sufficient text contrast
- readable font sizes
- status must not depend on color alone
- labels must accompany inputs
- buttons should use descriptive text
- error messages should explain the correction
- tables should use readable headings
- keyboard navigation should remain usable
- avoid flashing or rapid animations

Example:

Do not show only:

```text
●
```

Instead show:

```text
● Kafka Connected
```

---

# 23. Responsive Behavior

BankFlow should work primarily on desktop but remain usable on smaller screens.

Desktop:

```text
3–4 metric cards per row
```

Tablet:

```text
2 metric cards per row
```

Small screen:

```text
1 card per row
```

Transaction forms should never require horizontal scrolling.

---

# 24. Motion and Animation

Animation should be minimal.

Acceptable:

- Streamlit spinner while loading
- progress indicator during pipeline execution
- brief success confirmation
- subtle loading states

Avoid:

- animated backgrounds
- bouncing buttons
- auto-playing effects
- decorative transitions

---

# 25. Streamlit Styling Strategy

Use Streamlit's native components wherever possible.

Recommended components:

```python
st.metric()
st.button()
st.form()
st.text_input()
st.number_input()
st.dataframe()
st.tabs()
st.columns()
st.status()
st.success()
st.warning()
st.error()
st.info()
```

Custom CSS should be limited to:

- brand colors
- card presentation
- navigation polish
- typography adjustments
- spacing improvements
- status badges

Do not override Streamlit so heavily that the application becomes difficult to maintain.

---

# 26. Suggested Theme Configuration

Example `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2563EB"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#0F172A"
font = "sans serif"
```

---

# 27. Visual States

Every important component should support:

```text
Default
Hover
Active
Disabled
Loading
Success
Warning
Error
```

Example transaction button:

```text
Default      → Withdraw
Loading      → Processing...
Success      → Transaction Complete
Error        → Transaction Failed
```

---

# 28. Design Do / Don't

## Do

- keep pages focused
- use consistent spacing
- emphasize account balance clearly
- show transaction confirmation
- identify demo mode
- use meaningful charts
- maintain consistent status colors
- make errors actionable

## Don't

- overcrowd screens
- use unnecessary gradients
- display sensitive values
- show real card/PIN information
- place core logic in UI code
- add charts only for visual decoration
- overuse red
- use inconsistent button styles

---

# 29. Visual Identity Summary

BankFlow's visual identity is defined by:

```text
Trustworthy Navy
        +
Clear Blue Actions
        +
Emerald Success States
        +
Neutral White / Gray Surfaces
        +
Clean Sans-Serif Typography
        +
Generous Spacing
        +
Simple Data Visualization
```

The interface should feel like a modern technical banking simulator rather than a commercial banking website.

---

# 30. Final Design Direction

The finished BankFlow experience should communicate:

> **Simple enough to understand immediately, professional enough to demonstrate in a technical interview, and structured enough to support a growing data platform.**

Version 1 should feel like a polished ATM transaction application.

Version 2 should feel like the same product expanded with a professional analytics and data-platform layer.

The design system should remain consistent across both versions so the project visually communicates one coherent engineering platform rather than multiple disconnected demos.

<!-- converted from CSC505_ATM_Final_Project_Report_APA7.docx -->






ATM System Design and Implementation
Final Project Report

Shreyashkumar Patel
Colorado State University Global
CSC505 – Principles of Software Engineering
Instructor: Dr. Steven A. Evans
September 13, 2026

ATM System Design and Implementation
Introduction
The automated teller machine (ATM) final project demonstrates how software engineering concepts can be transformed from written requirements into models, executable logic, and testable behavior. The project focuses on a withdrawal workflow in which a customer must successfully authenticate before receiving access to account funds. The required behavior includes PIN validation, counting unsuccessful authentication attempts, rejecting a customer when the attempt limit is reached, completing a withdrawal, evaluating the resulting account balance, and closing the account when the balance becomes zero. Although the simulation is intentionally small, the project illustrates the same progression used in larger software systems: requirements are analyzed, behavior is modeled, implementation logic is developed, and test cases verify that the resulting software follows the design.
Unified Modeling Language (UML) was selected as the primary modeling approach because it provides standardized structural and behavioral notations for communicating software designs. The Object Management Group (2017) maintains UML as a formal modeling specification, making it appropriate for representing the ATM states, workflow, and interactions among participating components. Three UML views were developed for this project: a state machine diagram, a numbered activity diagram, and a sequence diagram. The state machine is the primary diagram because the assignment specifically requires state transitions, guards, actions, and internal entry or exit behavior. The activity and sequence diagrams provide complementary views that make the implementation easier to understand and verify.
Project Requirements and Objectives
The central objective of the project is to model and simulate a secure withdrawal transaction. The customer cannot proceed directly to a withdrawal. Authentication must occur first, and authentication is performed by checking a PIN. A correct PIN grants access, while an incorrect PIN increases a failed-attempt counter. The project uses a maximum of three unsuccessful attempts. If the counter reaches the limit, the customer is rejected and the ATM session ends. These requirements create both normal and exception paths that must be represented in the UML model and in the Python program.
After successful authentication, the system requests a withdrawal amount and validates the request against the current account balance. A valid withdrawal causes the ATM to dispense cash and subtract the amount from the balance. The balance is then evaluated. If funds remain, the transaction completes and the account stays active. If the updated balance is exactly zero, the account is closed. The simulation also includes an insufficient-funds path so that a request larger than the available balance is rejected without incorrectly modifying the account.
The project was designed around traceability. Each major activity in the activity diagram is assigned a number from 1 through 16, and the Python program prints those same numbers during execution. This creates a direct relationship between the visual model and the running program. Traceability is valuable because it allows a reviewer to compare requirements, design steps, implementation behavior, and test evidence rather than treating each artifact as unrelated documentation (Pressman & Maxim, 2020).
UML Modeling Approach
State Machine Diagram
The state machine diagram is the primary behavioral model for the ATM. It begins at an initial node and moves to an Idle state while the ATM waits for a card. In accordance with the assignment requirements, state boxes include internal behavior using entry and exit notation. For example, the Idle and PIN Entry states contain actions that occur when the state is entered or exited. This notation makes the internal responsibility of a state visible without creating unnecessary external transitions.
Transitions between states use the required event, guard, and action pattern. The general format is Event [guard] / action. For example, a PIN validation transition can be represented as CheckPin [PIN correct] / authenticate customer. An unsuccessful result can be represented as CheckPin [PIN incorrect and attempts < 3] / increment attempt counter. When the attempt limit is reached, a transition such as CheckPin [PIN incorrect and attempts >= 3] / reject customer moves the session to a terminal rejection state. Guards are important because they identify the condition that must be true before a transition is allowed, while actions identify the work performed as a consequence of the event (Object Management Group, 2017).
The state model also represents withdrawal and balance behavior. After authentication, the customer enters a withdrawal state, the amount is validated, and the balance is updated after cash is dispensed. The final account status depends on the updated balance. A positive balance leads to a completed transaction, while a zero balance causes the account to close. The model therefore captures both the normal path and the required terminal conditions.

Figure 1 ATM System - UML State Machine Diagram
Activity Diagram
The activity diagram presents the ATM as a step-by-step workflow rather than as a collection of states. Sixteen numbered activities are used to make the execution order explicit. The workflow begins with starting the ATM session and inserting the card, continues through PIN request and validation, and branches at decision points for PIN correctness, failed-attempt limits, withdrawal validity, and zero balance. Numbering the activities also makes the diagram easier to compare with the terminal output of the Python simulation.
Decision nodes are especially useful in this model. A PIN-correct decision directs the workflow either to authentication or to the failed-attempt counter. A second decision determines whether the maximum number of attempts has been reached. Later, the withdrawal amount is checked against the balance, and the final balance is evaluated to determine whether the account remains active or must close. These decisions correspond directly to Python if statements and loops, showing how an analysis model can guide implementation logic.

Figure 2 ATM System - UML Activity Diagram
Sequence Diagram
The sequence diagram adds an interaction-oriented view. It represents the Customer, ATM, Bank System, and Account Database as separate participants. Messages are shown in time order, including card insertion, PIN submission, PIN verification, balance retrieval, debit requests, balance updates, cash dispensing, and user feedback. This diagram is useful because it separates the responsibilities of the user interface from those of account verification and data management. It also illustrates how a seemingly simple ATM withdrawal depends on coordinated communication among multiple components.

Figure – 3 : UML Sequence Diagram
Python Implementation
The Python program implements the behavior represented in the UML diagrams. The program is intentionally organized into small functions rather than placing all logic in a single block. The print_step function standardizes numbered output, authenticate_customer controls the PIN verification loop, request_withdrawal validates the transaction amount, and run_atm coordinates the complete session. This organization improves readability and separates responsibilities, which supports maintainability and testing.
For demonstration purposes, the simulation uses a test PIN of 2468, a starting balance of $500.00, and a maximum of three PIN attempts. These values are configuration data for the classroom simulation rather than recommended production security practices. A real ATM would not store a plaintext PIN directly in application source code. Production authentication would rely on protected credential handling, secure communication, controlled authentication mechanisms, and additional safeguards. Current NIST authentication guidance emphasizes managing authenticators and authentication processes as security-sensitive functions (Temoshok et al., 2025).
The authentication loop is designed so that the withdrawal logic cannot execute unless PIN validation succeeds. Each unsuccessful attempt increments the counter. If the counter reaches three, the authentication function returns a failure result, the customer is rejected, and the program ends the session. If authentication succeeds, the program requests a withdrawal amount and rejects nonnumeric values, nonpositive amounts, and requests that exceed the available balance. A valid amount is subtracted from the balance only after validation.

After the balance is updated, the program evaluates whether it equals zero. A zero balance produces an account-closed status; otherwise, the program reports the updated balance and an active account. The final output therefore reflects the same decisions shown in the state and activity models. The implementation demonstrates the software engineering principle that design artifacts should guide code rather than exist only as separate documentation (Pressman & Maxim, 2020).
Testing and Execution Results
Four execution scenarios were used to verify the most important paths through the system. The scenarios were selected from the required behavior and from common exception conditions. Each execution was captured as a screenshot for submission. The results are summarized in Table 1.
Table 1
ATM Simulation Test Scenarios and Results






Output -Scenario 1 : Successful withdrawal

Output -Scenario 2: Incorrect then correct PIN

Output -Scenario 3 : Customer rejection

Output -Scenario 4 : Zero-balance closure



The successful-withdrawal test confirms the main path from authentication through cash dispensing and balance update. The second test verifies that the failed-attempt counter can recover when a later PIN is correct. The rejection test confirms that authentication failures are bounded rather than allowing unlimited attempts. The zero-balance test confirms the assignment-specific rule that an account is closed when the post-withdrawal balance reaches zero. Together, the four tests exercise the primary positive path and the most important alternate paths represented in the UML diagrams.
Security and Software Quality Considerations
Authentication, input validation, and controlled state transitions are central quality concerns in the ATM simulation. A withdrawal should never be possible before authentication, and failed attempts should not leave the program in an ambiguous state. The attempt counter provides a simple control against unlimited PIN guessing. The program also validates withdrawal input before modifying the balance, which protects the account state from invalid or unsupported values.
The classroom simulation is not intended to represent a production banking security architecture. A real implementation would require encrypted communications, protected PIN processing, secure credential storage, transaction logging, authorization controls, hardware security protections, monitoring, recovery procedures, and extensive security testing. The NIST Secure Software Development Framework recommends integrating security practices throughout the software development life cycle instead of treating security as a final add-on (Scarfone et al., 2022). Applying that principle to an ATM means considering authentication and transaction risks during requirements, design, implementation, testing, deployment, and maintenance.
Software quality is also supported by consistency across artifacts. The activity numbers displayed by the Python program correspond to the activity diagram, the state transitions implement the required events and guards, and the execution screenshots provide evidence that the major branches behave as expected. This consistency makes the project easier to review and reduces the risk that the implementation diverges from its design documentation.

Conclusion
The ATM final project demonstrates the relationship among requirements analysis, UML modeling, implementation, testing, security, and software quality. The state machine diagram provides the most direct representation of the required state-oriented behavior and follows the specified Event [guard] / action transition notation while using entry and exit actions within state boxes. The activity diagram presents the same behavior as a numbered workflow, and the sequence diagram shows how the customer, ATM, bank services, and account data interact over time.
The Python simulation translates those models into executable behavior and demonstrates successful authentication, repeated PIN failures, customer rejection, withdrawal validation, balance updates, and account closure. The four execution scenarios verify both normal and alternate paths. As a complete phase-two deliverable, the project shows that software engineering artifacts are most useful when requirements, diagrams, code, and tests remain aligned throughout development.

References
Object Management Group. (2017). OMG Unified Modeling Language (OMG UML), version 2.5.1. https://www.omg.org/spec/UML/2.5.1
Pressman, R. S., & Maxim, B. R. (2020). Software engineering: A practitioner's approach (9th ed.). McGraw-Hill Education.
Scarfone, K., Souppaya, M., & Dodson, D. (2022). Secure Software Development Framework (SSDF) version 1.1: Recommendations for mitigating the risk of software vulnerabilities (NIST Special Publication 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218
Temoshok, D., Fenton, J., Choong, Y.-Y., Lefkovitz, N., Regenscheid, A., Galluzzo, R., & Richer, J. (2025). Digital identity guidelines: Authentication and authenticator management (NIST Special Publication 800-63B-4). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-63b-4
| Scenario | Test Input | Expected Result | Observed Result |
| --- | --- | --- | --- |
| Successful withdrawal | PIN 2468; withdraw $100 | Authentication succeeds; $100 is dispensed; balance becomes $400. | Passed |
| Incorrect then correct PIN | Two incorrect PINs, then 2468; withdraw $100 | Counter increases twice; third PIN authenticates; withdrawal completes. | Passed |
| Customer rejection | Three incorrect PIN entries | Attempt count reaches 3; customer is rejected; session ends without withdrawal. | Passed |
| Zero-balance closure | PIN 2468; withdraw $500 | Full balance is dispensed; balance becomes $0; account closes. | Passed |
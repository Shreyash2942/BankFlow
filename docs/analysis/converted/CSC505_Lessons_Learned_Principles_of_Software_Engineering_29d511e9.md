<!-- converted from CSC505_Lessons_Learned_Principles_of_Software_Engineering.docx -->








Lessons Learned in Principles of Software Engineering
Shreyashkumar Patel

Colorado State University Global
CSC505 – Principles of Software Engineering
Dr. Steven A. Evans
September 13, 2026

Lessons Learned in Principles of Software Engineering
Introduction
Principles of Software Engineering changed my understanding of software development from a coding-focused activity into a complete engineering process. The course showed that successful software requires more than correct source code. Software engineering teams must understand the problem, identify stakeholder needs, select an appropriate process, model and design the solution, implement it carefully, evaluate the user experience, test it, and address quality and security. Pressman and Maxim (2020) emphasize that software engineering combines processes, methods, practices, and tools to create dependable software. Across the eight modules, the strongest lesson was how these activities connect throughout the software development life cycle.
Software Engineering Foundations
Module 1 introduced the nature of software, software processes, and professional software engineering practices. The most important lesson was the difference between programming and software engineering. Programming is one development activity, while software engineering also includes communication, planning, requirements, modeling, design, testing, documentation, maintenance, and teamwork. This changed how I approach a programming problem. Instead of starting immediately with code, I now consider what the software must accomplish, who will use it, and what information is needed before implementation.
The module also demonstrated why defined processes matter. A process gives a project structure and helps teams determine what work must be completed and how progress will be evaluated.
Software also changes after release because requirements, users, technologies, and risks change. Designing for maintainability is therefore as important as making the first version work correctly (Pressman & Maxim, 2020).
Software Process Models, Waterfall, Prototyping, and Agile
Modules 2 and 3 examined task sets, Waterfall, prototyping, Agile, Scrum, and prototype evaluation. The Waterfall Model provides an orderly sequence of activities and can work well when requirements are stable. However, the Adaptive Waterfall assignment showed me why a strictly sequential process can be difficult when requirements change or feedback arrives late. Redesigning the model with more flexibility made the limitations of a one-direction process easier to understand.
Prototyping demonstrated another way to reduce uncertainty. An early representation of a system allows stakeholders to evaluate an idea before extensive development occurs. Feedback can reveal missing requirements or incorrect assumptions while changes are still less expensive. Agile and Scrum extend this idea by supporting short development cycles, inspection, adaptation, and collaboration (Schwaber & Sutherland, 2020).
The Agile discussions also showed that Agile values should not be interpreted too literally. For example, valuing working software over comprehensive documentation does not mean eliminating useful documentation. Requirements, architecture decisions, test information, and maintenance guidance may still be essential. The larger lesson was that no process model is universally best. Project size, risk, requirement stability, stakeholder involvement, regulatory needs, and uncertainty should influence the choice of process.
Human Aspects of Software Engineering
Module 4 focused on developer characteristics, software teams, team structures, global teams, and communication. The Developer Builder Pattern assignment made this topic practical by combining curiosity, adaptability, and collaboration with UML and Python. The assignment reinforced that technical ability alone does not make an effective software engineer. Curiosity supports learning and problem solving, adaptability helps developers respond to changing requirements and technologies, and collaboration allows teams to combine different skills and perspectives.
Global and distributed teams create additional challenges involving communication, schedules, responsibilities, and knowledge sharing. Clear documentation, defined roles, regular communication, and constructive feedback help reduce these challenges. This lesson applies beyond software development because most professional work depends on people coordinating effectively rather than working in isolation.
Requirements Engineering and Analysis Modeling
Module 5 was one of the most practical parts of the course because it covered requirements engineering, requirements gathering, use cases, analysis models, and requirements modeling. The key lesson was that a system can be programmed correctly and still fail if the requirements are incomplete or misunderstood. Functional requirements describe what the system must do, while nonfunctional requirements address qualities such as security, reliability, performance, availability, and usability.
Use cases improved my understanding of system behavior by requiring identification of actors, preconditions, normal flows, alternative flows, and exceptions.
The Pothole Tracking and Repair System assignment demonstrated how quickly a simple idea can become a detailed software problem. The system had to manage citizen reports, pothole locations and severity, districts, priorities, work orders, repair crews, equipment, labor, material usage, repair status, costs, and damage information. Modeling these relationships showed why development teams must understand business rules before designing the software.
This module changed how I approach real-world problems. Before considering implementation, I now see value in identifying stakeholders, required information, business decisions, possible exceptions, and success criteria. Good requirements reduce the risk of building software that technically works but does not solve the intended problem.
Software Design, Architecture, Components, and User Experience
Modules 6 and 7 moved from understanding requirements to organizing the solution. Module 6 covered the design process, design concepts, architecture, agility and architecture, and architectural decisions. Module 7 continued with class-based components, component-level design, user interface analysis, and user experience. Together, these modules demonstrated that requirements explain what a system should accomplish, while design explains how its parts will work together.
UML became especially useful because it provides standardized ways to represent structural and behavioral views of software (Object Management Group, 2017). Class diagrams can show classes and relationships, use-case diagrams can represent interactions, activity diagrams can show workflows, and state machine diagrams can represent changes in system state. Creating UML diagrams during the course helped me see modeling as a way to find missing relationships or unclear logic before those problems become source-code defects.
Component-level design also reinforced the value of clear responsibilities and understandable interfaces. At the same time, user interface and user experience design showed that technical correctness is not enough. A system can perform accurate calculations and still be unsuccessful if users cannot understand its workflow. Software should therefore be designed from both the developer's and the user's perspective, with usability considered during requirements and design rather than at the end.
Software Quality, Security Engineering, and Testing
Module 8 connected the earlier lessons through software quality, quality assurance, security engineering, threat modeling, risk prioritization, mitigation, and testing. Software quality means more than avoiding program crashes. Quality software should satisfy requirements, protect information, handle expected and unexpected conditions, remain understandable, and provide reliable service. Quality assurance supports these goals through reviews, standards, testing, and process controls (Pressman & Maxim, 2020).
Security engineering was another major lesson. Security should be considered throughout development rather than added after implementation. The National Institute of Standards and Technology recommends integrating secure development practices across the software life cycle to reduce vulnerabilities and address their causes (Scarfone et al., 2022). Threat modeling and risk analysis help teams identify threats, prioritize them, and select appropriate controls.
The ATM final project brings several course concepts together. Authentication must occur before withdrawal, the PIN may be correct or incorrect, unsuccessful attempts must be counted, customers must be rejected after the attempt limit, and an account must close when its balance reaches zero. These rules are simultaneously requirements, security controls, state transitions, business logic, and test cases.
Testing therefore needs to include successful withdrawals as well as incorrect PIN attempts, rejection conditions, balance conditions, and boundary cases.
Real-World Application and Personal Growth
The most important change from this course is how I now approach software problems. A basic approach might move directly from a problem to coding. After Principles of Software Engineering, I would first identify the problem and stakeholders, gather and validate requirements, evaluate risks, choose an appropriate process, model the system, design the architecture and components, implement the solution, test normal and abnormal conditions, review security, gather feedback, and improve the product.
This approach applies to banking, healthcare, government, retail, and many other systems. Even in smaller projects, writing requirements, considering edge cases, modeling relationships, separating responsibilities, testing failures, and considering user experience can prevent later problems. I also gained a stronger appreciation for communication and documentation because developers must clearly share requirements, design decisions, system behavior, and maintenance information with others.








Conclusion
Principles of Software Engineering expanded my understanding of professional software development by connecting software foundations, process models, Waterfall, prototyping, Agile and Scrum, teamwork, requirements, use cases, architecture, UML, component design, UI/UX, quality assurance, security engineering, threat modeling, and testing. The assignments turned these topics into practical skills rather than isolated concepts.
Working code is only one measure of success. Effective software must solve the correct problem, support users, remain maintainable, protect information, and handle failures. The course changed my mindset from coding first to understanding and designing first.


References
Object Management Group. (2017). OMG Unified Modeling Language (OMG UML), version 2.5.1. https://www.omg.org/spec/UML/2.5.1
Pressman, R. S., & Maxim, B. R. (2020). Software engineering: A practitioner's approach (9th ed.). McGraw-Hill Education.
Scarfone, K., Souppaya, M., & Dodson, D. (2022). Secure Software Development Framework (SSDF) version 1.1: Recommendations for mitigating the risk of software vulnerabilities (NIST Special Publication 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218
Schwaber, K., & Sutherland, J. (2020). The Scrum guide: The definitive guide to Scrum: The rules of the game. https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf
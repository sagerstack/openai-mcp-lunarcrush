# Epic Artifact

## Purpose & Overview

The Epic artifact defines outcome-focused capabilities that group related user stories and establish clear business value delivery. Epics serve as the bridge between strategic MVP planning and implementable user stories, ensuring that development work advances strategic objectives while maintaining user-centered focus.

### Key Objectives
- **Capability Definition**: Define outcome-focused capabilities that deliver measurable business value
- **Story Grouping**: Organize related user stories around common business outcomes
- **Strategic Alignment**: Ensure epic development advances OKR objectives and MVP goals
- **Value Framework**: Establish clear success criteria and measurement approach

### Integration Points
- **Input from**: MVP iteration planning and epic themes
- **Created by**: `/create-epic` command with business-analyst sub-agent
- **Contains**: User stories that implement epic capabilities
- **Feeds into**: `/create-story` command for user story breakdown, then `/solution` for implementation planning

## Epic Template Structure

```markdown
# Epic: {epic-name}

## Metadata
| Field | Value |
|-------|-------|
| ID | EP-### |
| Title | [Descriptive 3-word epic title] |
| MVP Reference | MVP-### |
| Created | YYYY-MM-DD HH:mm:ss |
| Status | Draft / Final |
| Status History | [Date: Status - Reason for change] |
| Last Updated | YYYY-MM-DD HH:mm:ss |

## Epic Overview
**What**: [Clear description of the capability being delivered]
**Why**: [Business value and strategic importance - connection to MVP objectives]
**Success**: [High-level definition of epic success and completion criteria]

## Success Metrics
| Metric | Target Value | Measurement Method | Data Source |
|--------|--------------|-------------------|-------------|
| [Primary metric] | [Target] | [Method] | [Source] |
| [Secondary metric] | [Target] | [Method] | [Source] |

## User Stories List

### Story Portfolio Overview
| ID | Title | Status | Priority | GitHub Issue | Business Value |
|----|-------|--------|----------|--------------|----------------|
| STR-### | [Story title] | Draft | Must-have | - | [Value description] |
| STR-### | [Story title] | Draft | Should-have | - | [Value description] |
| STR-### | [Story title] | Draft | Could-have | - | [Value description] |

## Epic Sequencing and Dependency Rules

### Dependency Types and Sequencing Impact
- **Blocking Dependency**: Epic B blocks Epic A completion → Sequence B before A (B must finish before A starts)
  - Example: "EP-020 Token Mapping" blocks "EP-019 US-057 Cross-Chain Arbitrage" (arbitrage requires token equivalence mapping)
- **Prerequisite Dependency**: Epic B is prerequisite for Epic A → B starts before A, but A can start when B is 50%+ complete
  - Example: "EP-015 Network Integration" is prerequisite for "EP-016 DEX Integration" (DEX can start when RPC connections established)
- **Informational Dependency**: Epic B informs Epic A design → No sequencing impact, but A should reference B outputs
  - Example: "EP-017 Caching" informs "EP-019 Route Optimization" (optimization can use cache, but doesn't block)

### Sequencing Priority Calculation
- **P1 (Foundation)**: No blocking dependencies OR only depends on completed epics (external dependencies allowed)
  - Example: EP-015 Network Integration (no internal dependencies)
  - Start: Immediately
- **P2 (Mid-Layer)**: Depends on 1-2 P1 epics (can start when dependencies 50%+ complete)
  - Example: EP-020 Token Mapping (depends on EP-017 Caching for token metadata)
  - Start: When EP-017 token metadata retrieval complete
- **P3 (High-Layer)**: Depends on 3+ epics OR depends on P2 epics (can start when dependencies 75%+ complete)
  - Example: EP-019 Route Optimization (depends on EP-018 Price Discovery + EP-020 Token Mapping)
  - Start: When EP-018 route generation complete AND EP-020 mapping service operational

### Dependency Validation Checklist
- [ ] All blocking dependencies identified in "Epic Dependencies" table with "Blocking" type
- [ ] Dependent epics (what blocks on this epic) documented with clear impact explanation
- [ ] Sequencing justification provided (why this epic sequenced at this position in MVP epic table)
- [ ] Cross-epic integration points defined (how this epic's outputs are consumed by dependent epics)
- [ ] Dependency resolution timeline estimated (when blockers will be resolved to unblock dependent work)
- [ ] No circular dependencies exist (Epic A → Epic B → Epic A creates deadlock)

### Data Flow Dependency Patterns
- **Data Foundation Pattern**: Mapping/normalization epics MUST precede consumption epics
  - Producer Epic (generates canonical data) → Consumer Epic (uses canonical data)
  - Example: Token Mapping Service (EP-020) produces canonical token IDs → Cross-Chain Arbitrage (EP-019 US-057) consumes mappings
- **Integration Pattern**: Network/API connection epics precede data processing epics
  - Foundation Epic (establishes connectivity) → Processing Epic (uses connections)
  - Example: Network Integration (EP-015) establishes RPC → DEX Integration (EP-016) monitors transactions via RPC
- **Business Logic Pattern**: Core algorithms precede optimization/advanced features
  - Core Epic (basic algorithm) → Enhancement Epic (optimization/ML)
  - Example: Price Discovery (EP-018) finds routes → Route Optimization (EP-019) optimizes routes

## Dependencies & Prerequisites

### Epic Dependencies
| Dependency | Type | Impact | Owner | Status | Resolution Timeline |
|------------|------|--------|-------|--------|-------------------|
| [Dependency 1] | [Blocking / Prerequisite / Informational] | [Impact description - what blocks if dependency unmet] | [Owner] | [Status] | [Timeline] |
| [Dependency 2] | [Blocking / Prerequisite / Informational] | [Impact description - what blocks if dependency unmet] | [Owner] | [Status] | [Timeline] |

**Dependency Type Definitions**:
- **Blocking**: Dependent epic CANNOT start until this epic completes (hard dependency)
- **Prerequisite**: Dependent epic can start when this epic is 50%+ complete (soft dependency)
- **Informational**: Dependent epic references outputs but no sequencing constraint (reference only)

### External Dependencies
- **System Dependencies**: External systems or services required (third-party APIs, infrastructure)
- **Data Dependencies**: Data sources or data availability requirements (authoritative data, reference data)
- **Team Dependencies**: Other teams or resources required for completion (platform team, security team)
- **Technology Dependencies**: Technology stack or infrastructure requirements (languages, frameworks, tools)

### Internal Dependencies
- **Other Epics**: Dependencies on other epics within same MVP (list Epic IDs with dependency type)
- **Technical Prerequisites**: Technical work required before epic start (architecture decisions, proof-of-concepts)
- **Business Prerequisites**: Business decisions or approvals required (scope approval, budget allocation)
- **Resource Prerequisites**: Team members or skills required (backend developer, data analyst)

## Acceptance Criteria

### Epic Acceptance Criteria
- **Functional Acceptance**: [Functional requirements for epic completion]
- **User Experience Acceptance**: [UX quality and usability criteria]
- **Performance Acceptance**: [Performance and reliability criteria]
- **Business Acceptance**: [Business value and outcome criteria]

### Definition of Done (Epic Level)
- [ ] All must-have user stories completed and accepted
- [ ] Epic success criteria validated and measured
- [ ] User acceptance testing completed successfully
- [ ] Epic documentation and knowledge transfer complete
- [ ] Business stakeholder sign-off obtained
- [ ] Epic retrospective and lessons learned captured

## Risk Assessment & Mitigation

### High-Priority Risks
**Risk 1: [Risk Description]**
- **Probability**: [High/Medium/Low]
- **Impact**: [High/Medium/Low]
- **Mitigation Strategy**: [Strategy to address risk]
- **Contingency Plan**: [Backup plan if risk materializes]
- **Owner**: [Risk owner and monitoring responsibility]

**Risk 2: [Risk Description]**
- **Probability**: [High/Medium/Low]
- **Impact**: [High/Medium/Low]
- **Mitigation Strategy**: [Strategy to address risk]
- **Contingency Plan**: [Backup plan if risk materializes]
- **Owner**: [Risk owner and monitoring responsibility]

### Risk Monitoring
- **Risk Review Frequency**: [How often risks will be reviewed]
- **Risk Escalation Criteria**: [Conditions triggering risk escalation]
- **Risk Mitigation Tracking**: [How mitigation progress will be tracked]

## User Experience Framework

### User Journey
- **Primary User Journey**: [Main user journey supported by epic]
- **User Touchpoints**: [Key user interaction points and interfaces]
- **Experience Goals**: [User experience objectives and quality criteria]
- **Usability Requirements**: [Usability and accessibility requirements]

### Design Considerations
- **Design Principles**: [Design principles and guidelines for epic]
- **Interface Requirements**: [User interface and interaction requirements]
- **Responsive Design**: [Multi-device and responsive design considerations]
- **Accessibility**: [Accessibility standards and inclusive design requirements]

## Open Questions
| Question | Priority | User Response | Research Method | Success Criteria | Owner | Timeline |
|----------|----------|---------------|-----------------|------------------|-------|----------|
| What user workflows should this epic support? | High | [INSERT_USER_RESPONSE_HERE] | User journey mapping | Documented workflow diagram | Product Manager | Week 1 |
| Should feature X be included in epic scope or deferred? | Medium | [INSERT_USER_RESPONSE_HERE] | Scope validation | Clear scope boundary definition | Business Analyst | Week 1 |
| What business rules govern condition Y? | High | [INSERT_USER_RESPONSE_HERE] | Business logic analysis | Validated business rules | Business Analyst | Week 2 |

*Note: Open Questions focus on functional scope, user workflows, and feature boundaries. Technical implementation questions are addressed at user story level with solution-architect guidance.*

## Changelog
| Date | Author | Summary | Sections Affected | Reason |
|------|--------|---------|------------------|--------|
| YYYY-MM-DD HH:mm:ss | Business Analyst | Initial epic creation | All sections | Epic planning and breakdown |
| YYYY-MM-DD HH:mm:ss | Business Analyst | [Specific changes made] | [Affected sections] | [Reason for change] |

*Note: Changelog tracks epic evolution and planning decisions*
```
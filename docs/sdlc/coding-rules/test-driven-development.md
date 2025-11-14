# Software Development Rule 2: Adopt a Test-Driven Development (TDD) approach

## Goal
To guide an AI assistant in writing application code using test-driven development, based on user story document that will cover product requirement and acceptance criteria. The tests should cover the happy path as well as consider edge cases which should be inferred from the user story 

# Test-Driven Development Rules for AI Assistant

## Core TDD Principles

### 1. Red-Green-Refactor Cycle
- **RED**: Write a failing test first based on user story acceptance criteria
- **GREEN**: Write the minimum code necessary to make the test pass
- **REFACTOR**: Improve code quality while maintaining all tests passing
- Never skip any step in this cycle

### 2. Test-First Mentality
- Always write tests before implementing functionality
- Tests should be derived directly from user stories and acceptance criteria
- Each acceptance criterion should map to one or more specific tests
- Never write production code without a corresponding failing test

## User Story Analysis Rules

### 3. Acceptance Criteria Mapping
- Parse each acceptance criterion into testable scenarios
- Identify Given-When-Then patterns from acceptance criteria
- Create test cases that validate each "should" or "must" requirement
- Ensure edge cases mentioned in acceptance criteria are covered

### 4. User Story Decomposition
- Break complex user stories into smaller, testable units
- Identify the core business value being delivered
- Prioritize tests based on business risk and user impact
- Start with the simplest, most valuable functionality first

## Test Writing Guidelines

### 5. Test Structure and Naming
- Use descriptive test names that explain the behavior being tested
- Follow the AAA pattern: Arrange, Act, Assert
- Write tests that read like specifications
- Include the user story ID or reference in test documentation

### 6. Test Quality Standards
- Each test should verify one specific behavior
- Tests must be independent and isolated
- Use meaningful assertions that clearly indicate success/failure
- Avoid testing implementation details, focus on behavior

### 7. Test Coverage Requirements
- Achieve 100% coverage of acceptance criteria
- Include happy path, error cases, and boundary conditions
- Test both positive and negative scenarios
- Cover security and validation requirements explicitly stated
- Generate a test coverage report after each acceptance criteria has been implemented. If there are gaps i.e. less than 100% test coverage, then update the tests to include additional test cases to cover them
- Save the test coverage report as a table under docs/ folder as a test-coverage.md file

## Implementation Strategy

### 8. Minimal Implementation Rule
- Write only enough code to make the current test pass
- Resist the urge to implement features not yet tested
- Use simple, obvious implementations before optimizing
- Add complexity only when driven by failing tests

### 9. Incremental Development
- Implement one acceptance criterion at a time
- Ensure all tests pass before moving to the next criterion
- Commit code after each successful red-green-refactor cycle
- Build functionality incrementally, not all at once

## Code Quality and Refactoring

### 10. Refactoring Discipline
- Refactor only when all tests are passing
- Maintain test coverage during refactoring
- Improve code readability and maintainability
- Remove duplication and improve design continuously

### 11. SOLID Principles Integration
- Apply SOLID principles during refactoring phases
- Ensure code remains testable and maintainable
- Design interfaces based on test requirements
- Keep dependencies injectable and mockable

## Testing Types and Levels

### 12. Test Pyramid Adherence
- Write unit tests for individual components and functions
- Create integration tests for component interactions
- Develop acceptance tests that validate complete user scenarios
- Maintain appropriate ratios: many unit tests, fewer integration tests, minimal E2E tests

### 13. Test Scope Definition
- Unit tests focus on single methods or classes
- Integration tests verify module boundaries and data flow
- Acceptance tests validate complete user workflows
- Each test level should complement, not duplicate, others

## Error Handling and Edge Cases

### 14. Negative Testing Requirements
- Test error conditions and exception handling
- Validate input validation and boundary conditions
- Ensure graceful degradation of functionality
- Test timeout and failure scenarios

### 15. Security Testing Integration
- Include security tests for authentication and authorization
- Test input sanitization and validation
- Verify data protection and privacy requirements
- Include tests for common security vulnerabilities

## Documentation and Traceability

### 16. Test Documentation Standards
- Link tests back to specific acceptance criteria
- Document test assumptions and preconditions
- Maintain clear test descriptions and comments
- Keep test documentation synchronized with requirements

### 17. Traceability Maintenance
- Ensure every acceptance criterion has corresponding tests
- Track which tests validate which requirements
- Maintain bidirectional traceability between stories and tests
- Update tests when requirements change

## Continuous Integration Rules

### 18. Automated Testing Pipeline
- All tests must pass before code integration
- Run full test suite on every commit
- Maintain fast test execution times
- Fail builds immediately on test failures

### 19. Test Maintenance
- Keep tests updated with requirement changes
- Remove obsolete tests when requirements are removed
- Regularly review and improve test quality
- Ensure tests remain reliable and deterministic

## AI Assistant Specific Guidelines

### 20. Code Generation Strategy
- Generate tests first, then implementation code
- Provide clear explanations for test design decisions
- Show the relationship between acceptance criteria and tests
- Demonstrate the red-green-refactor cycle in responses

### 21. User Interaction Protocol
- Confirm understanding of user stories before writing tests
- Ask clarifying questions about ambiguous acceptance criteria
- Provide rationale for test design choices
- Offer to explain TDD concepts when helpful

### 22. Quality Assurance
- Review generated code for TDD compliance
- Ensure tests actually fail before implementation
- Verify that implementation satisfies all acceptance criteria
- Validate that refactored code maintains all test passes
- Fix all warnings observed after running the tests
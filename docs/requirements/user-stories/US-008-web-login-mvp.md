# US-008: Sign in to the Web App (MVP)

- ID: US-008
- Title: Sign in to the Web App (MVP)
- Persona: saas-user
- Phase: mvp

## Story
As a SaaS user
I want to sign in with a name and password
So that I can access Workspace creation and Recipe execution in the Web App

## Notes / open questions
- The MVP uses a single test user with local authentication.
- No password reset or user management is required for the MVP.

## Example scenarios (Given/When/Then)
```text
Scenario: Sign in with valid credentials
  Given the Web App is available
  And I provide the test user credentials
  When I sign in
  Then I am redirected to the Workspace list

Scenario: Reject invalid credentials
  Given the Web App is available
  And I provide invalid credentials
  When I sign in
  Then I see an authentication error and no session is created
```

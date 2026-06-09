const API_URL = 'http://localhost:8000';

describe('Login Form', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('successfully logs in with valid credentials and redirects to the home page', () => {
    cy.intercept('POST', `${API_URL}/auth/token`, {
      statusCode: 200,
      body: { access_token: 'test-access-token-12345' },
    }).as('loginRequest');

    cy.intercept('GET', `${API_URL}/auth/me`, {
      statusCode: 200,
      body: {
        id: 1,
        email: 'user@test.com',
        name: 'Test',
        surname: 'User',
        is_superuser: false,
      },
    }).as('meRequest');

    cy.get('[data-test="email"] input').type('user@test.com');
    cy.get('[data-test="password"] input').type('password123');

    cy.get('button[type="submit"]').click();

    cy.wait('@loginRequest');
    cy.url().should('include', '/home');
  });

  it('shows an error message when submitting incorrect credentials', () => {
    cy.intercept('POST', `${API_URL}/auth/token`, {
      statusCode: 401,
      body: { detail: 'Incorrect email or password' },
    }).as('loginRequest');

    cy.get('[data-test="email"] input').type('wrong@test.com');
    cy.get('[data-test="password"] input').type('wrongpassword123');

    cy.get('button[type="submit"]').click();

    cy.wait('@loginRequest');
    cy.contains('Не верный Email или пароль').should('be.visible');
  });
});

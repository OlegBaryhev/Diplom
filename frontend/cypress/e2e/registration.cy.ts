const API_URL = 'http://localhost:8000';

describe('Registration Form', () => {
  beforeEach(() => {
    cy.visit('/register');
  });

  it('shows validation errors when submitting an empty form', () => {
    cy.get('button[type="submit"]').click();

    cy.get('[data-test="email"]').should('contain.text', 'Обязательное поле');
    cy.get('[data-test="name"]').should('contain.text', 'Обязательное поле');
    cy.get('[data-test="password"]').should('contain.text', 'Обязательное поле');
    cy.get('[data-test="password-confirmation"]').should('contain.text', 'Обязательное поле');
  });

  it('successfully registers a new user and redirects to the login page', () => {
    cy.intercept('POST', `${API_URL}/auth/register`, {
      statusCode: 200,
      body: {
        id: 1,
        email: 'newuser@test.com',
        name: 'Test',
        surname: 'User',
      },
    }).as('registerRequest');

    cy.get('[data-test="email"] input').type('newuser@test.com');
    cy.get('[data-test="name"] input').type('Test');
    cy.get('[data-test="surname"] input').type('User');
    cy.get('[data-test="password"] input').type('password123');
    cy.get('[data-test="password-confirmation"] input').type('password123');

    cy.get('button[type="submit"]').click();

    cy.wait('@registerRequest');
    cy.url().should('include', '/login');
  });
});

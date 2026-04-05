describe('Авторизация', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('Показывает ошибки валидации при пустых полях', () => {
    cy.get('button[type=submit]').click();
    cy.contains('Поле обязательно для заполнения').should('exist');
  });

  it('Показывает ошибку при неверном email формате', () => {
    cy.get('[data-test=email]').type('invalid-email');
    cy.get('[data-test=password]').type('12345678');
    cy.get('button[type=submit]').click();
    cy.contains('Некорректный email').should('exist');
  });

  it('Показывает ошибку при пароле меньше 8 символов', () => {
    cy.get('[data-test=email]').type('test@example.com');
    cy.get('[data-test=password]').type('123');
    cy.get('button[type=submit]').click();
    cy.contains('Пароль должен быть не менее 8 символов').should('exist');
  });

  it('Авторизуется при правильных данных', () => {
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: { access_token: 'fake-token' },
    }).as('loginRequest');

    cy.get('[data-test=email]').type('user@example.com');
    cy.get('[data-test=password]').type('validpassword');
    cy.get('button[type=submit]').click();

    cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);

    cy.url().should('not.include', '/login');
  });

  it('Показывает ошибку при неверном email или пароле, полученной с API', () => {
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 401,
      body: { detail: 'Incorrect email or password' },
    }).as('loginRequest');

    cy.get('[data-test=email]').type('wrong@example.com');
    cy.get('[data-test=password]').type('wrongpassword');
    cy.get('button[type=submit]').click();

    cy.wait('@loginRequest');
    cy.contains('Не верный Email или пароль').should('ecxist');
  });
});

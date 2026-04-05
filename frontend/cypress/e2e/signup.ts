describe('Регистрация', () => {
  beforeEach(() => {
    cy.visit('/register');
  });

  it('Показывает ошибки при пустых полях', () => {
    cy.get('button[type=submit]').click();
    cy.contains('Поле обязательно для заполнения').should('exist');
  });

  it('Показывает ошибку при некорректном email', () => {
    cy.get('[data-test=email]').type('not-an-email');
    cy.get('[data-test=name]').type('Олег');
    cy.get('[data-test=password]').type('12345678');
    cy.get('[data-test=password-confirmation]').type('12345678');
    cy.get('button[type=submit]').click();
    cy.contains('Некорректный email').should('exist');
  });

  it('Показывает ошибку, если пароль и подтверждение не совпадают', () => {
    cy.get('[data-test=email]').type('test@example.com');
    cy.get('[data-test=name]').type('Олег');
    cy.get('[data-test=password]').type('password123');
    cy.get('[data-test=password-confirmation]').type('password321');
    cy.get('button[type=submit]').click();
    cy.contains('Пароль не подтвержден!').should('exist');
  });

  it('Показывает ошибку при пароле меньше 8 символов', () => {
    cy.get('[data-test=email]').type('test@example.com');
    cy.get('[data-test=name]').type('Олег');
    cy.get('[data-test=password]').type('12345');
    cy.get('[data-test=password-confirmation]').type('12345');
    cy.get('button[type=submit]').click();
    cy.contains('Пароль должен быть не менее 8 символов').should('exist');
  });

  it('Успешно регистрируется и редиректит на логин', () => {
    cy.intercept('POST', '/api/auth/register', {
      statusCode: 200,
      body: { detail: 'success' },
    }).as('registerRequest');

    cy.get('[data-test=email]').type('newuser@example.com');
    cy.get('[data-test=name]').type('Олег');
    cy.get('[data-test=password]').type('strongpassword');
    cy.get('[data-test=password-confirmation]').type('strongpassword');
    cy.get('button[type=submit]').click();

    cy.wait('@registerRequest');
    cy.url().should('include', '/login');
  });

  it('Показывает ошибку если пользователь уже существует', () => {
    cy.intercept('POST', '/api/auth/register', {
      statusCode: 400,
      body: { detail: 'User with this email already exists' },
    }).as('registerRequest');

    cy.get('[data-test=email]').type('existing@example.com');
    cy.get('[data-test=name]').type('Олег');
    cy.get('[data-test=password]').type('strongpassword');
    cy.get('[data-test=password-confirmation]').type('strongpassword');
    cy.get('button[type=submit]').click();

    cy.wait('@registerRequest');
    cy.contains('Пользователь уже существует!').should('exist');
  });
});

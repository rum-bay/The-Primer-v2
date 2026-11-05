const { defineConfig } = require('cypress');
module.exports = defineConfig({ video: false, defaultCommandTimeout: 15000,
  e2e: { baseUrl: 'http://127.0.0.1:4173', specPattern: 'cypress/e2e/**/*.cy.js' } });

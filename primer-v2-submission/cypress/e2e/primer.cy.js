describe('The Primer v2: ONNX and story regression', () => {
  it('matches all five Python ONNX oracle probabilities within 1e-4', () => {
    cy.visit('/web/?test=parity&source=sentetik');
    cy.get('[data-cy=model-status]').should('contain.text', 'ONNX model ready');
    cy.get('[data-cy=parity-run]').click();
    cy.get('[data-cy=parity-results]').should('contain.text', 'PASS').and('contain.text', 'case-5');
  });

  it('loads ONNX and preserves all 21 decision steps', () => {
    cy.visit('/web/?source=sentetik');
    cy.get('[data-cy=model-status]').should('contain.text', 'ONNX model ready');
    cy.get('[data-cy=consent]').check(); cy.get('[data-cy=start]').click();
    for (let i = 0; i < 21; i += 1) {
      cy.get('[data-cy=choice]').eq(i % 3).click(); cy.get('[data-cy=commit]').click();
      cy.get(i % 2 ? '[data-cy=help-no]' : '[data-cy=help-yes]').click();
      cy.get('[data-cy=p]').invoke('text').then(text => {
        const tutorOn = Number(text) >= 0.55;
        cy.get('[data-cy=tutor]').should(tutorOn ? 'be.visible' : 'not.be.visible');
        if (i < 20) {
          cy.get('[data-cy=next]').click();
          cy.get('#story').should('contain.text', tutorOn ? 'süre baskısı kaldırıldı' : 'Sahne zorluğu');
          cy.get('[data-cy=timer]').should(tutorOn ? 'not.be.visible' : 'be.visible');
        }
      });
    }
    cy.get('[data-cy=finish]').should('be.visible').click();
    cy.contains('Katılımın için teşekkürler.').should('be.visible');
    cy.get('[data-cy=session-count]').should('have.text', '0');
  });
});

(function () {
  'use strict';

  var config = window.DATA_BOAR_FORM_CONFIG || {};
  var hubspot = config.hubspot || {};

  function showStatus(elementId, message, kind) {
    var el = document.getElementById(elementId);
    if (!el) return;
    el.hidden = false;
    el.textContent = '';
    el.className = 'form-status is-' + (kind || 'info');
    el.appendChild(document.createTextNode(message));
  }

  function splitName(fullName) {
    var parts = fullName.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) {
      return { firstname: '', lastname: '' };
    }
    if (parts.length === 1) {
      return { firstname: parts[0], lastname: '' };
    }
    return {
      firstname: parts[0],
      lastname: parts.slice(1).join(' '),
    };
  }

  function hubspotConfigured() {
    return Boolean(hubspot.portalId && hubspot.demoFormGuid);
  }

  function submitDemoToHubSpot(form) {
    var nome = form.querySelector('[name="nome_completo"]');
    var email = form.querySelector('[name="email"]');
    var empresa = form.querySelector('[name="company"]');
    var cargo = form.querySelector('[name="jobtitle"]');
    var telefone = form.querySelector('[name="phone"]');
    var segmento = form.querySelector('[name="segmento"]');
    var desafio = form.querySelector('[name="message"]');
    var agendamento = form.querySelector('[name="demo_preferred_datetime"]');

    var nameParts = splitName(nome ? nome.value : '');
    var fields = [
      { objectTypeId: '0-1', name: 'firstname', value: nameParts.firstname },
      { objectTypeId: '0-1', name: 'lastname', value: nameParts.lastname },
      { objectTypeId: '0-1', name: 'email', value: email ? email.value.trim() : '' },
      { objectTypeId: '0-1', name: 'company', value: empresa ? empresa.value.trim() : '' },
      { objectTypeId: '0-1', name: 'jobtitle', value: cargo ? cargo.value : '' },
      { objectTypeId: '0-1', name: 'phone', value: telefone ? telefone.value.trim() : '' },
      {
        objectTypeId: '0-1',
        name: 'message',
        value: [
          desafio ? desafio.value.trim() : '',
          segmento && segmento.value ? 'Segmento: ' + segmento.value : '',
          agendamento && agendamento.value
            ? 'Preferência de agendamento: ' + agendamento.value
            : '',
        ]
          .filter(Boolean)
          .join('\n\n'),
      },
    ].filter(function (field) {
      return field.value;
    });

    var endpoint =
      'https://api.hsforms.com/submissions/v3/integration/submit/' +
      encodeURIComponent(hubspot.portalId) +
      '/' +
      encodeURIComponent(hubspot.demoFormGuid);

    return fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fields: fields,
        context: {
          pageUri: window.location.href,
          pageName: document.title,
        },
      }),
    });
  }

  var demoForm = document.getElementById('demo-request-form');
  if (demoForm) {
    demoForm.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!demoForm.reportValidity()) {
        return;
      }

      var submitBtn = demoForm.querySelector('[type="submit"]');
      var statusId = 'demo-form-status';

      if (!hubspotConfigured()) {
        var mailto = config.fallbackMailto || 'contact@databoar.com.br';
        showStatus(
          statusId,
          'Captura online em configuração. Envie um e-mail para ' +
            mailto +
            ' para agendar sua demonstração.',
          'info'
        );
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalLabel = submitBtn.textContent;
        submitBtn.textContent = 'Enviando…';
      }

      submitDemoToHubSpot(demoForm)
        .then(function (response) {
          if (!response.ok) {
            throw new Error('HubSpot submit failed: ' + response.status);
          }
          demoForm.reset();
          showStatus(
            statusId,
            'Recebemos seu pedido. Nossa equipe entrará em contato em breve.',
            'success'
          );
        })
        .catch(function () {
          showStatus(
            statusId,
            'Não foi possível enviar agora. Tente novamente ou escreva para ' +
              (config.fallbackMailto || 'contact@databoar.com.br') +
              '.',
            'error'
          );
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            if (submitBtn.dataset.originalLabel) {
              submitBtn.textContent = submitBtn.dataset.originalLabel;
            }
          }
        });
    });
  }

  var loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      event.preventDefault();
      showStatus(
        'login-form-status',
        'O painel do dataBOAR estará disponível em breve. Agende uma demonstração para conhecer a plataforma.',
        'info'
      );
    });
  }
})();

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

  function hubspotConfigured() {
    return Boolean(hubspot.portalId && hubspot.demoFormGuid);
  }

  function val(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    return el ? el.value.trim() : '';
  }

  function isChecked(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    return Boolean(el && el.checked);
  }

  var CONSENT_PROCESS_TEXT =
    'Autorizo a DataBoar a armazenar e tratar meus dados pessoais para responder a este contato.';
  var CONSENT_MARKETING_TEXT =
    'Aceito receber comunicações e novidades da DataBoar. Posso cancelar quando quiser.';

  function submitDemoToHubSpot(form) {
    var preferred = val(form, 'demo_preferred_datetime');
    var messageParts = [
      val(form, 'message'),
      preferred ? 'Preferência de agendamento: ' + preferred : '',
    ].filter(Boolean);

    // Enquanto o subscriptionTypeId de marketing não estiver configurado, preserva
    // o opt-in do titular na mensagem para não perder o sinal de consentimento.
    if (!hubspot.marketingSubscriptionTypeId && isChecked(form, 'consent_marketing')) {
      messageParts.push('Opt-in de comunicações (marketing): Sim');
    }

    var rawFields = {
      firstname: val(form, 'firstname'),
      lastname: val(form, 'lastname'),
      email: val(form, 'email'),
      company: val(form, 'company'),
      jobtitle: val(form, 'jobtitle'),
      phone: val(form, 'phone'),
      industry: val(form, 'industry'),
      message: messageParts.join('\n\n'),
    };

    var fields = Object.keys(rawFields)
      .filter(function (k) {
        return rawFields[k];
      })
      .map(function (k) {
        return { objectTypeId: '0-1', name: k, value: rawFields[k] };
      });

    // LGPD — consentimento granular: tratamento (obrigatório) + comunicações (opcional)
    var communications = [];
    if (hubspot.marketingSubscriptionTypeId) {
      communications.push({
        value: isChecked(form, 'consent_marketing'),
        subscriptionTypeId: Number(hubspot.marketingSubscriptionTypeId),
        text: CONSENT_MARKETING_TEXT,
      });
    }
    var legalConsentOptions = {
      consent: {
        consentToProcess: true,
        text: CONSENT_PROCESS_TEXT,
        communications: communications,
      },
    };

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
        legalConsentOptions: legalConsentOptions,
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

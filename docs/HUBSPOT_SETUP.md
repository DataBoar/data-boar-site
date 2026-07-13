# HubSpot lead capture (GitHub Pages)

The demo form on `agende-demonstracao.html` submits leads via HubSpot's **public** form
integration endpoint (`portalId` + `formGuid`). A **private** HubSpot API key must **never**
ship in this repository or in browser JavaScript.

## GitHub Actions secrets

In **DataBoar/data-boar-site** → Settings → Secrets and variables → Actions, set:

| Secret | Description |
| ------ | ----------- |
| `HUBSPOT_PORTAL_ID` | HubSpot account portal ID |
| `HUBSPOT_DEMO_FORM_GUID` | GUID of the "Agendar demonstração" form |
| `HUBSPOT_REGION` | Optional; default `na1` (use `eu1` for EU portals) |

The workflow `.github/workflows/pages-deploy.yml` writes `js/form-config.js` from these
secrets at deploy time only.

## Enable Actions-based Pages deploy

1. Settings → Pages → Build and deployment → Source: **GitHub Actions**
2. Merge a PR that includes `pages-deploy.yml`
3. Confirm the workflow run injects config and publishes the site

Until secrets exist, the form shows a **mailto fallback** (`contact@databoar.com.br`) instead
of failing silently.

## HubSpot form field mapping

Align the HubSpot form with these `name` attributes (see `js/forms.js`):

| Form label (PT) | HubSpot property |
| --------------- | ---------------- |
| Nome completo | `firstname` + `lastname` (split on first space) |
| E-mail corporativo | `email` |
| Empresa | `company` |
| Cargo | `jobtitle` |
| Telefone | `phone` |
| Segmento + desafio + data | combined in `message` |

Custom HubSpot properties require updating the field list in `js/forms.js`.

## Login page

`login.html` does not send credentials to HubSpot. Submit shows an "em breve" message and
points visitors to the demo form until product SSO is wired.

## Out of scope (operator only)

- DNS, Cloudflare, custom domain, MX records
- Storing private HubSpot app tokens in the repo

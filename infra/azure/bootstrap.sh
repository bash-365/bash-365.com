#!/usr/bin/env bash
# One-time Azure bootstrap for bash-365.com Static Web Apps.
#
# Creates (or reuses) the resource group, Entra app + federated credentials
# for GitHub OIDC, role assignment, and the Bicep Static Web App.
# Does not link a GitHub repo on the SWA (that regenerates the retired
# token workflow). Does not write secrets into files.
#
# Prerequisites: az CLI, logged in with rights to create RGs, SWAs, and
# Entra applications. Optional: gh CLI to print copy-paste secret commands.
#
# Usage:
#   az login
#   ./infra/azure/bootstrap.sh
#
# Optional env overrides:
#   AZURE_RESOURCE_GROUP   default rg-bash365-prod
#   GITHUB_REPOSITORY      default bash-365/bash-365.com
#   ENTRA_APP_NAME         default sp-bash365-swa-github

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PARAM_FILE="${ROOT}/parameters.prod.json"
BICEP_FILE="${ROOT}/main.bicep"

RG_NAME="${AZURE_RESOURCE_GROUP:-rg-bash365-prod}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-bash-365/bash-365.com}"
ENTRA_APP_NAME="${ENTRA_APP_NAME:-sp-bash365-swa-github}"
DEPLOYMENT_NAME="${DEPLOYMENT_NAME:-swa-bash365-prod}"

param_value() {
  python3 - "$PARAM_FILE" "$1" <<'PY'
import json, sys
params = json.load(open(sys.argv[1]))["parameters"]
print(params[sys.argv[2]]["value"])
PY
}

LOCATION="$(param_value location)"
SWA_NAME="$(param_value staticWebAppName)"

need_az() {
  if ! command -v az >/dev/null 2>&1; then
    echo "az CLI is required. Install: https://learn.microsoft.com/cli/azure/install-azure-cli" >&2
    exit 1
  fi
}

ensure_login() {
  if ! az account show >/dev/null 2>&1; then
    echo "Not logged in. Run: az login" >&2
    exit 1
  fi
}

ensure_fed_cred() {
  local app_id="$1"
  local cred_name="$2"
  local subject="$3"
  local existing
  existing="$(az ad app federated-credential list --id "$app_id" --query "[?name=='${cred_name}'].name" -o tsv 2>/dev/null || true)"
  if [[ -n "$existing" ]]; then
    echo "Federated credential ${cred_name} already exists."
    return 0
  fi
  az ad app federated-credential create --id "$app_id" --parameters "$(cat <<JSON
{
  "name": "${cred_name}",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "${subject}",
  "description": "GitHub Actions OIDC for ${GITHUB_REPOSITORY}",
  "audiences": ["api://AzureADTokenExchange"]
}
JSON
)" >/dev/null
  echo "Created federated credential ${cred_name}."
}

need_az
ensure_login

SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
TENANT_ID="$(az account show --query tenantId -o tsv)"
echo "Subscription: ${SUBSCRIPTION_ID}"
echo "Tenant:       ${TENANT_ID}"
echo "Resource group: ${RG_NAME} (${LOCATION})"
echo "Static Web App: ${SWA_NAME}"
echo "GitHub repo:    ${GITHUB_REPOSITORY}"

az group create --name "$RG_NAME" --location "$LOCATION" --tags project=bash365 env=prod >/dev/null
echo "Resource group ready."

APP_ID="$(az ad app list --display-name "$ENTRA_APP_NAME" --query "[0].appId" -o tsv)"
if [[ -z "$APP_ID" ]]; then
  APP_ID="$(az ad app create --display-name "$ENTRA_APP_NAME" --query appId -o tsv)"
  echo "Created Entra app ${ENTRA_APP_NAME} (${APP_ID})."
else
  echo "Reusing Entra app ${ENTRA_APP_NAME} (${APP_ID})."
fi

SP_OID="$(az ad sp list --filter "appId eq '${APP_ID}'" --query "[0].id" -o tsv)"
if [[ -z "$SP_OID" ]]; then
  SP_OID="$(az ad sp create --id "$APP_ID" --query id -o tsv)"
  echo "Created service principal ${SP_OID}."
else
  echo "Reusing service principal ${SP_OID}."
fi

ensure_fed_cred "$APP_ID" "github-main" "repo:${GITHUB_REPOSITORY}:ref:refs/heads/main"
ensure_fed_cred "$APP_ID" "github-pull-request" "repo:${GITHUB_REPOSITORY}:pull_request"

RG_ID="$(az group show --name "$RG_NAME" --query id -o tsv)"
EXISTING_ROLE="$(az role assignment list --assignee "$APP_ID" --scope "$RG_ID" --role Contributor --query "[0].id" -o tsv 2>/dev/null || true)"
if [[ -z "$EXISTING_ROLE" ]]; then
  az role assignment create \
    --assignee-object-id "$SP_OID" \
    --assignee-principal-type ServicePrincipal \
    --role Contributor \
    --scope "$RG_ID" >/dev/null
  echo "Assigned Contributor on ${RG_NAME}."
else
  echo "Contributor already assigned on ${RG_NAME}."
fi

az deployment group create \
  --name "$DEPLOYMENT_NAME" \
  --resource-group "$RG_NAME" \
  --template-file "$BICEP_FILE" \
  --parameters "@${PARAM_FILE}" \
  --query properties.outputs \
  --output json

DEFAULT_HOSTNAME="$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RG_NAME" --query defaultHostname -o tsv)"
ORIGIN_PREFIX="https://${DEFAULT_HOSTNAME%%.*}"

echo
echo "Bootstrap complete."
echo "Default hostname:  https://${DEFAULT_HOSTNAME}"
echo "SWA_ORIGIN_PREFIX: ${ORIGIN_PREFIX}"
echo
echo "Add these GitHub Actions secrets (repo → Settings → Secrets and variables → Actions):"
echo "  AZURE_CLIENT_ID       ${APP_ID}"
echo "  AZURE_TENANT_ID       ${TENANT_ID}"
echo "  AZURE_SUBSCRIPTION_ID ${SUBSCRIPTION_ID}"
echo "  CLAUDE_CODE_OAUTH_TOKEN   (preferred)  or  ANTHROPIC_API_KEY"
echo
echo "Optional GitHub Actions variables (defaults match this bootstrap if unset):"
echo "  AZURE_RESOURCE_GROUP      ${RG_NAME}"
echo "  AZURE_STATIC_WEB_APP_NAME ${SWA_NAME}"
echo
if command -v gh >/dev/null 2>&1; then
  echo "Copy-paste (does not set the chat credential):"
  echo "  gh secret set AZURE_CLIENT_ID --body '${APP_ID}' --repo ${GITHUB_REPOSITORY}"
  echo "  gh secret set AZURE_TENANT_ID --body '${TENANT_ID}' --repo ${GITHUB_REPOSITORY}"
  echo "  gh secret set AZURE_SUBSCRIPTION_ID --body '${SUBSCRIPTION_ID}' --repo ${GITHUB_REPOSITORY}"
  echo "  gh variable set AZURE_RESOURCE_GROUP --body '${RG_NAME}' --repo ${GITHUB_REPOSITORY}"
  echo "  gh variable set AZURE_STATIC_WEB_APP_NAME --body '${SWA_NAME}' --repo ${GITHUB_REPOSITORY}"
fi
echo
echo "Do not flip DNS yet. Deploy via .github/workflows/azure-swa.yml, smoke"
echo "https://${DEFAULT_HOSTNAME}, then run ./infra/azure/cutover.sh"

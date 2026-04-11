#!/usr/bin/env bash
#
# install.sh — Instala las skills autorales de Gustavo Carreño desde
# github.com/GustavoCarreno/claude-skills al ~/.claude/skills/ del usuario.
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/GustavoCarreno/claude-skills/main/install.sh | bash
#
# O clonando manualmente primero:
#   git clone https://github.com/GustavoCarreno/claude-skills /tmp/claude-skills
#   bash /tmp/claude-skills/install.sh
#
# Requisitos: git, bash. No requiere sudo ni permisos de admin.

set -euo pipefail

REPO_URL="https://github.com/GustavoCarreno/claude-skills.git"
SKILLS_DIR="${HOME}/.claude/skills"
TMP_DIR="$(mktemp -d -t claude-skills-install-XXXXXX)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

# Verificar que git esté disponible
if ! command -v git > /dev/null 2>&1; then
  echo "Error: git no está instalado o no está en el PATH." >&2
  echo "Instálalo con tu package manager (apt, brew, etc.) y vuelve a correr." >&2
  exit 1
fi

echo "Clonando repo desde ${REPO_URL}..."
git clone --quiet --depth 1 "${REPO_URL}" "${TMP_DIR}"

mkdir -p "${SKILLS_DIR}"

installed=()
for dir in "${TMP_DIR}"/*/; do
  name="$(basename "${dir}")"
  # Ignorar carpetas ocultas
  case "${name}" in .*) continue;; esac
  # Ignorar carpetas que no tengan SKILL.md (no son skills)
  if [[ ! -f "${dir}SKILL.md" ]]; then
    continue
  fi

  echo "Instalando skill: ${name}"
  rm -rf "${SKILLS_DIR}/${name}"
  cp -r "${dir}" "${SKILLS_DIR}/${name}"
  installed+=("${name}")
done

echo ""
if [[ ${#installed[@]} -eq 0 ]]; then
  echo "Advertencia: no se encontraron skills para instalar en el repo." >&2
  exit 1
fi

echo "✓ Skills instaladas en ${SKILLS_DIR}:"
for name in "${installed[@]}"; do
  echo "  - ${name}"
done
echo ""
echo "Siguiente paso: en tu terminal de claude, corre /exit y luego claude"
echo "para que las skills aparezcan en tu lista."

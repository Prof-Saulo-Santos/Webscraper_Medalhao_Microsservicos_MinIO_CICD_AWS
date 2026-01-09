# AI AGENT RULES (`AGENTS.MD`)

Este arquivo define as **Leis do Projeto** que devem ser seguidas estritamente por qualquer Agente de IA (Cursor, Windsurf, Copilot, etc.) que trabalhe neste repositório.

## 1. Segurança & Git (`.gitignore`)
*   **PROIBIDO:** Nunca altere o `.gitignore` da raiz (ou de qualquer subdiretório) para permitir a leitura de arquivos sensíveis (como `.env`).
*   **SECRETS:** Se precisar verificar credenciais, peça ao usuário para validar ou solicite a criação de um script de diagnóstico seguro. Não tente "burlar" as regras do git para ler senhas.
*   **MONOREPO:** Este é um monorepo.
    *   Regras globais (`.env`, `__pycache__`, `.DS_Store`) ficam no `.gitignore` da **Raiz**.
    *   Serviços individuais podem ter `.gitignore` próprios APENAS para arquivos exclusivos daquele serviço (ex: `models/`, `cache/`, `node_modules/`).

## 2. Documentação (`docs/`)
*   **INTEGRIDADE:** Ao atualizar um arquivo de documentação (ex: `passo_a_passo_fase_2.md`), **NUNCA delete ou sobrescreva** seções inteiras inadvertidamente.
*   **VERIFICAÇÃO:** Antes de confirmar uma edição na documentação, verifique se scripts importantes (como `routes.py`, `tests/`) não foram removidos. A documentação deve ser o "Espelho da Verdade" do código.

## 3. Configuração & Consistência
*   **AUDITORIA:** Antes de criar configurações para um novo serviço (Fase N+1), **leia** os arquivos de configuração dos serviços anteriores (Fase N).
*   **PADRÕES:** Mantenha nomes de variáveis (`AWS_ACCESS_KEY_ID`, `MINIO_ROOT_USER`) idênticos entre os serviços para evitar confusão. Não invente novos nomes se já existe um padrão.

## 4. Testes & Qualidade
*   **MOCKS:** Testes Unitários (`tests/`) devem rodar isolados. Use `unittest.mock` ou `moto` para simular serviços externos.
*   **AMBIENTE:** Se o código usa variáveis de ambiente para conectar em serviços (ex: `S3_ENDPOINT`), certifique-se de que o teste faça o **patch** dessas variáveis para não tentar conectar na rede real (ou no Docker) durante o teste local.
*   **TESTE ANTES DE FALAR:** Se fizer uma correção de bug ("Agora vai funcionar"), rode o comando de verificação (ex: `make test` ou `curl`) antes de anunciar o sucesso ao usuário.

## 5. Docker
*   **CACHE:** Utilize `.dockerignore` para evitar contextos de build gigantes (excluir `venv`, `models`, `cache`).
*   **CREDENCIAIS:** Nunca chumbe credenciais no Dockerfile. Use `env_file` ou Secrets no Docker Compose.

# Painel Brasileirão 2026

Painel local para a Série A usando football-data.org. A chave fica no servidor Python, não no JavaScript do navegador.

## Estrutura

```text
brasileirao-dashboard/
├── app.py
├── .env.example
├── .env              # você cria; contém sua chave privada
├── .gitignore
└── static/
    ├── index.html
    ├── styles.css
    └── app.js
```

## 1. Requisitos

Python 3 instalado. No terminal do VS Code, confira com `python --version` ou `py --version`.

## 2. Configure a chave

Na pasta principal, crie um arquivo chamado `.env` (sem `.txt`) com esta linha, substituindo o exemplo pela sua chave NOVA:

```text
FOOTBALL_DATA_TOKEN=SUA_CHAVE_NOVA_AQUI
```

Não use a chave que foi exposta na conversa e não compartilhe o `.env`.

## 3. Inicie

No terminal aberto na pasta `brasileirao-dashboard`, rode:

```powershell
python app.py
```

Se não funcionar, tente `py app.py`. Depois abra `http://127.0.0.1:8000` no navegador. Para parar, pressione `Ctrl+C` no terminal.

## 4. Ao mudar de pasta

Mova a pasta inteira, incluindo o arquivo `.env`. Abra a pasta nova no VS Code (File > Open Folder), abra um terminal novo e rode `python app.py` ou `py app.py`. Se não mover o `.env`, crie-o novamente na pasta nova. A variável temporária do PowerShell não é mantida automaticamente em terminais novos; este projeto lê a chave do `.env`.

## 5. Cache e atualização

O servidor guarda uma resposta válida por até 24 horas e a página consulta novamente após esse período. O servidor precisa ficar aberto. O botão de atualizar respeita o cache para evitar chamadas excessivas.

## Problemas comuns

- **Chave não configurada:** confira se `.env` está na pasta principal e contém `FOOTBALL_DATA_TOKEN=...`.
- **HTTP 401/403:** chave inválida ou plano sem permissão para a classificação de 2026.
- **HTTP 429:** limite de consultas atingido; aguarde antes de tentar de novo.
- **Página não abre:** verifique se o terminal continua rodando e use `http://127.0.0.1:8000`.

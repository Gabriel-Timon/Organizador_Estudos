# Organizador de Estudos

[![CI](https://github.com/Gabriel-Timon/Organizador_Estudos/actions/workflows/ci.yml/badge.svg)](https://github.com/Gabriel-Timon/Organizador_Estudos/actions/workflows/ci.yml)

API REST para organizar matérias, tarefas e sessões de estudo, acompanhar prazos e consolidar o tempo dedicado por período e por matéria.

## Sobre o projeto

O **Organizador de Estudos** é uma aplicação backend construída com FastAPI, SQLAlchemy e SQLite. A API modela o ciclo completo de planejamento e acompanhamento dos estudos:

- cadastro, consulta, edição e exclusão de matérias;
- criação e gerenciamento do status de tarefas (`pendente`, `em_andamento` e `concluida`);
- filtros de tarefas por matéria, prioridade, status e atraso;
- registro de sessões de estudo com validação de duração e data;
- relatórios de produtividade, incluindo total estudado, média diária, matéria mais estudada e evolução dos últimos sete dias;
- validação de dados com Pydantic e regras de integridade entre matérias, tarefas e sessões;
- suíte de testes automatizados com banco SQLite isolado em memória;
- integração contínua configurada com GitHub Actions.

O projeto é voltado para estudantes que desejam transformar o planejamento de estudos em dados acompanháveis e para demonstrar a construção de uma API Python organizada, validada e testada.

## Tecnologias

| Tecnologia | Uso |
| --- | --- |
| Python 3.10+ | Linguagem principal |
| FastAPI | Criação da API REST e documentação OpenAPI |
| Pydantic v2 | Schemas, serialização e validações de entrada |
| SQLAlchemy 2 | ORM, consultas e relacionamentos |
| SQLite | Persistência local padrão |
| Pytest | Testes automatizados |
| GitHub Actions | Integração contínua |

## Arquitetura

```text
app/
├── database.py  # engine SQLAlchemy, sessões e configuração do banco
├── main.py      # aplicação FastAPI, rotas e consultas de relatório
├── models.py    # entidades Materia, Tarefa e SessaoEstudo
└── schemas.py   # contratos de entrada/saída e validações Pydantic

tests/
├── conftest.py  # banco de teste em memória e override da dependência
└── test_main.py # testes de rotas, regras e relatórios
```

O relacionamento principal do domínio é:

```text
Materia 1 ──── N Tarefa
Materia 1 ──── N SessaoEstudo
```

Cada requisição que acessa dados recebe uma sessão SQLAlchemy por injeção de dependência. O ambiente de testes substitui essa sessão por um banco SQLite em memória, evitando alterar o banco local de desenvolvimento.

## Funcionalidades da API

### Matérias

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/materias` | Cria uma matéria e normaliza o nome |
| `GET` | `/materias` | Lista todas as matérias |
| `GET` | `/materias/{id}` | Consulta uma matéria pelo identificador |
| `PUT` | `/materias/{id}` | Atualiza os dados da matéria |
| `DELETE` | `/materias/{id}` | Remove uma matéria sem vínculos |

Uma matéria não pode ser excluída enquanto possuir tarefas ou sessões de estudo vinculadas; nesses casos a API retorna `409 Conflict`.

### Tarefas

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/tarefas` | Cria uma tarefa associada a uma matéria |
| `GET` | `/tarefas` | Lista tarefas com filtros opcionais |
| `GET` | `/tarefas/{id}` | Consulta uma tarefa pelo identificador |
| `PUT` | `/tarefas/{id}` | Atualiza dados e status da tarefa |
| `PATCH` | `/tarefas/{id}/concluir` | Marca a tarefa como concluída |
| `DELETE` | `/tarefas/{id}` | Remove uma tarefa |

Os filtros aceitos em `GET /tarefas` são `materia_id`, `prioridade`, `status` e `atrasadas=true`. Ao concluir uma tarefa, a API registra `data_conclusao` automaticamente.

### Sessões e relatórios

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/sessoes` | Registra uma sessão de estudo |
| `GET` | `/sessoes` | Lista sessões, com filtro opcional por matéria |
| `DELETE` | `/sessoes/{id}` | Remove uma sessão |
| `GET` | `/relatorios/resumo` | Retorna indicadores gerais de produtividade |
| `GET` | `/relatorios/tempo-por-materia` | Soma o tempo estudado por matéria |
| `GET` | `/relatorios/ultimos-7-dias` | Agrupa o tempo estudado por dia |

As sessões aceitam duração entre 1 e 720 minutos e não permitem datas futuras. Os relatórios utilizam consultas agregadas com SQLAlchemy (`SUM`, `COUNT`, `GROUP BY` e ordenação temporal).

## Como executar

### Pré-requisitos

- Python 3.10 ou superior;
- `pip`;
- Git, caso o projeto seja clonado do GitHub.

### Instalação

```bash
git clone https://github.com/Gabriel-Timon/Organizador_Estudos.git
cd Organizador_Estudos

python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Instale as dependências de desenvolvimento:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### Iniciar a API

```bash
python -m uvicorn app.main:app --reload
```

Por padrão, a aplicação cria `organizador_estudos.db` no diretório de execução. Esse arquivo é local e está excluído do versionamento. Para apontar a aplicação para outra URL compatível com SQLAlchemy, defina a variável `DATABASE_URL` antes de iniciar:

```bash
# Windows PowerShell
$env:DATABASE_URL = "sqlite:///./organizador_estudos.db"

# macOS/Linux
export DATABASE_URL="sqlite:///./organizador_estudos.db"
```

Depois de iniciar, acesse:

- `http://127.0.0.1:8000/` — mensagem de boas-vindas;
- `http://127.0.0.1:8000/docs` — Swagger UI interativo;
- `http://127.0.0.1:8000/redoc` — documentação ReDoc.

## Exemplos de uso

Criar uma matéria:

```bash
curl -X POST http://127.0.0.1:8000/materias \
  -H "Content-Type: application/json" \
  -d '{"nome":"Python","descricao":"Backend e APIs","cor":"#3776AB"}'
```

Criar uma tarefa vinculada à matéria retornada:

```bash
curl -X POST http://127.0.0.1:8000/tarefas \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Estudar FastAPI","materia_id":1,"prioridade":"alta","data_limite":"2026-09-15"}'
```

Consultar tarefas atrasadas:

```bash
curl "http://127.0.0.1:8000/tarefas?atrasadas=true"
```

Resposta resumida esperada:

```json
{
  "tarefas_concluidas": 3,
  "tarefas_pendentes": 5,
  "tarefas_atrasadas": 1,
  "materia_mais_estudada": "Python",
  "total_estudado_minutos": 840,
  "media_diaria_ultimos_sete_dias": 72.9
}
```

## Testes

Execute a suíte completa com:

```bash
python -m pytest -q
```

Os testes cobrem o endpoint raiz, CRUD de matérias, validação de payloads, vínculos entre entidades, filtros e transições de tarefas, sessões de estudo e os três relatórios. O workflow em `.github/workflows/ci.yml` executa esses testes a cada push na branch `main` e em pull requests.

## Qualidade e decisões técnicas

- Separação entre modelos ORM (`app/models.py`) e schemas de API (`app/schemas.py`);
- injeção de dependência para controlar o ciclo de vida das sessões do banco;
- validações de domínio na entrada, como nomes/títulos não vazios, prioridades enumeradas, duração máxima e datas não futuras;
- consultas agregadas no banco para os relatórios, evitando cálculos de produtividade apenas em memória;
- proteção contra exclusão de matérias com dados dependentes;
- testes isolados com `StaticPool` e banco SQLite em memória;
- CI reproduzível a partir de `requirements-dev.txt`.

## Próximos passos

O backend está preparado para evoluir. Algumas extensões naturais são autenticação de usuários, migrações com Alembic, paginação de listagens, uma interface web e suporte a um banco de dados de produção.

## Licença

Este repositório ainda não declara uma licença de uso. Defina uma licença antes de distribuir o projeto ou aceitar contribuições externas.

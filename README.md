# Hit Digital Full Stack Challenge

Aplicação para consultar vários usuários da API JSONPlaceholder em uma única operação. O backend controla concorrência, retentativas e falhas parciais; o frontend recebe os IDs, valida a entrada e apresenta os resultados da consulta.

## Stack

Backend:

- Python 3.11
- FastAPI
- HTTPX
- Pydantic
- pytest
- Ruff

Frontend:

- React
- TypeScript
- Vite
- Vitest
- React Testing Library

Infraestrutura:

- Docker
- Docker Compose
- GitHub Actions

## Arquitetura

O fluxo principal do backend é `API route -> UserFetchService -> UserProvider -> JsonPlaceholderUserProvider -> HTTPX`. A abstração de provider mantém os detalhes do JSONPlaceholder fora da regra de orquestração, sem adicionar camadas que o escopo não exige.

As chamadas ao provedor são assíncronas e têm concorrência limitada por um semáforo. Retentativas são feitas somente para erros transitórios — respostas 429 e 5xx, timeout ou falha de rede — e a falha de um usuário fica isolada, permitindo devolver os demais resultados do lote.

No frontend, componentes cuidam da apresentação, uma função separada faz o parsing e a validação dos IDs, o módulo de API delimita o contrato HTTP e o componente principal orquestra o estado local da única consulta.

## Executando com Docker

Na raiz do repositório:

```bash
docker compose up --build
```

Serviços disponíveis:

- frontend: http://localhost:3000
- backend: http://localhost:8000
- documentação da API: http://localhost:8000/docs

Para encerrar e remover os containers:

```bash
docker compose down
```

## Executando sem Docker

O backend requer Python 3.11 ou superior. No PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install ".[dev]"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Em outro terminal, com Node.js 22:

```powershell
cd frontend
npm ci
npm run dev
```

O frontend usa `http://localhost:8000` por padrão. Para apontar para outra API, copie `frontend/.env.example` para `frontend/.env` e ajuste `VITE_API_BASE_URL`.

## Testes e qualidade

Backend, a partir de `backend`:

```powershell
ruff check .
ruff format --check .
pytest
```

Frontend, a partir de `frontend`:

```powershell
npm run test:run
npm run lint
npm run build
```

## Principais decisões técnicas

- O `AsyncClient` é criado uma vez no lifespan do FastAPI e reutilizado, em vez de abrir um cliente por requisição ou por usuário.
- Um semáforo mantém a concorrência dentro do limite configurado.
- O provider isola a integração com o JSONPlaceholder da orquestração da consulta.
- Retentativas são restritas a 429, 5xx, timeout e falhas de rede. Erros permanentes não são repetidos.
- Falha parcial faz parte de uma resposta bem-sucedida do lote: usuários encontrados ficam em `users` e IDs com falha ficam em `failed`.
- Não há banco ou cache porque a operação atual não mantém estado e persistência não resolveria um requisito existente.
- Estado local do React e `fetch` nativo atendem ao único fluxo de requisição sem justificar bibliotecas adicionais de estado ou consulta.

## O que eu melhoraria com mais tempo

- Adicionaria logs estruturados, métricas e tracing para observar latência, volume e falhas do provedor.
- Passaria a respeitar `Retry-After` e avaliaria jitter e circuit breaker se os limites e o comportamento real do provedor justificassem.
- Ampliaria os testes de integração e adicionaria um fluxo E2E no navegador.
- Definiria configuração do frontend em runtime caso a estratégia de implantação exigisse reutilizar a mesma imagem em ambientes diferentes.

## Se precisasse consultar milhares de usuários

Eu evitaria manter todo o processamento preso a uma única requisição HTTP. Dividiria os IDs em lotes processados por uma fila e workers, com concorrência e limites do provedor explícitos, e persistiria o status e o resultado do job quando a consulta assíncrona fosse necessária. Para acessos repetidos, avaliaria cache. Também adicionaria métricas, tracing e mecanismos de resiliência como retry com jitter e circuit breaker. Se o provedor oferecesse um endpoint em lote, eu o usaria antes de simplesmente aumentar o paralelismo.

## Uso de IA

Usei o OpenAI Codex como apoio durante a implementação, principalmente para acelerar partes do código, testes e revisão. As decisões de arquitetura, escopo e comportamento foram feitas por mim.

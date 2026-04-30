# 🛫 Voe Comilhas — Agente Inteligente de Cotação

Sistema completo de atendimento via WhatsApp com inteligência artificial para cotação de passagens aéreas.

## Arquitetura

```
WhatsApp → Uazapi → Webhook FastAPI → OpenAI API → Supabase
                                                ↓
                              Painel Admin React ← → Página Pública de Proposta
```

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python · FastAPI · Uvicorn |
| IA | OpenAI API (gpt-4.1-mini) |
| Banco | Supabase (PostgreSQL) |
| WhatsApp | Uazapi |
| Frontend | React · Vite · Tailwind CSS |

---

## 1. Criar projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) → **New project**
2. Escolha nome, senha e região (preferencialmente São Paulo - `sa-east-1`)
3. Aguarde o projeto ser criado (~2 minutos)

---

## 2. Rodar o schema.sql

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em **New query**
3. Cole o conteúdo de `/backend/schema.sql`
4. Clique em **Run**

As tabelas criadas serão:
- `clientes`
- `cotacoes`
- `mensagens`
- `opcoes_voo`
- `webhook_logs`

---

## 3. Configurar variáveis de ambiente

### Backend

```bash
cd backend
cp .env.example .env
```

Edite o `.env` com seus dados:

```env
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Onde achar: Supabase → Settings → API
# Use a "service_role" key (não a "anon" key)

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini

# Uazapi
UAZAPI_BASE_URL=https://api.uazapi.com
UAZAPI_TOKEN=seu_token
UAZAPI_ADMIN_TOKEN=seu_admin_token
UAZAPI_INSTANCE_ID=sua_instancia

# URL pública do backend (usada para configurar o webhook)
WEBHOOK_PUBLIC_URL=https://seu-ngrok.ngrok-free.app
```

### Frontend

```bash
cd frontend
cp .env.example .env
```

```env
VITE_API_URL=http://localhost:8000
```

Em produção, aponte para a URL do seu backend publicado.

---

## 4. Instalar e rodar o backend

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn main:app --reload --port 8000
```

O backend estará disponível em: `http://localhost:8000`

Documentação interativa (Swagger): `http://localhost:8000/docs`

---

## 5. Instalar e rodar o frontend

```bash
cd frontend

# Instalar dependências
npm install

# Rodar servidor de desenvolvimento
npm run dev
```

O painel estará disponível em: `http://localhost:5173`

---

## 6. Configurar a Uazapi

1. Acesse o painel da sua instância Uazapi
2. Crie uma instância e conecte o WhatsApp escaneando o QR Code
3. Anote:
   - **Base URL** da API
   - **Token** da instância
   - **Admin Token**
   - **Instance ID**
4. Adicione esses dados no `.env` do backend

---

## 7. Configurar o Webhook

O webhook é configurado **automaticamente** ao iniciar o backend, desde que `WEBHOOK_PUBLIC_URL` esteja preenchido corretamente.

Para desenvolvimento local, você precisa expor o backend via ngrok:

---

## 8. Usar o ngrok (desenvolvimento local)

```bash
# Instalar ngrok: https://ngrok.com/download

# Expor o backend
ngrok http 8000
```

O ngrok vai gerar uma URL como: `https://abc123.ngrok-free.app`

Coloque essa URL no `.env`:

```env
WEBHOOK_PUBLIC_URL=https://abc123.ngrok-free.app
```

Depois **reinicie o backend** para que o webhook seja registrado automaticamente na Uazapi.

---

## 9. Testar mensagem do WhatsApp

1. Abra o WhatsApp no celular
2. Envie uma mensagem para o número conectado à Uazapi
3. O agente deve responder automaticamente
4. Acompanhe os logs no terminal do backend

Exemplo de conversa:
```
Você: Oi
Agente: Olá! Seja bem-vindo à Voe Comilhas. Vou te ajudar a encontrar a melhor opção de passagem. Sua viagem será ida e volta ou somente ida?
Você: Ida e volta
Agente: Ótimo! Qual será a cidade de origem?
...
```

---

## 10. Acessar o Dashboard

Acesse: `http://localhost:5173/dashboard`

Você verá:
- Contagem de cotações por status
- Lista de todas as cotações
- Busca e filtros
- Acesso ao detalhe de cada cotação

---

## 11. Gerar uma proposta

1. Acesse uma cotação pelo dashboard
2. Na seção **Opções de Voo**, clique em **+ Adicionar**
3. Preencha os dados do voo (companhia, trecho, horário, valor, etc.)
4. Adicione até 3 opções de voo
5. Clique em **Gerar Link da Proposta**
6. Copie o link gerado e envie para o cliente

O cliente poderá visualizar as opções em: `/proposta/{CODIGO}`

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/cotacoes` | Listar cotações |
| `GET` | `/cotacoes/{id}` | Detalhe da cotação |
| `PATCH` | `/cotacoes/{id}` | Atualizar dados |
| `PATCH` | `/cotacoes/{id}/status` | Atualizar status |
| `POST` | `/cotacoes/{id}/opcoes` | Adicionar opção de voo |
| `GET` | `/cotacoes/{id}/opcoes` | Listar opções de voo |
| `POST` | `/cotacoes/{id}/gerar-proposta` | Gerar link de proposta |
| `GET` | `/cotacoes/{id}/mensagens` | Histórico de mensagens |
| `GET` | `/propostas/{codigo}` | Proposta pública |
| `POST` | `/webhook/uazapi` | Recebe mensagens do WhatsApp |

---

## Status das Cotações

| Status | Descrição |
|--------|-----------|
| `dados_incompletos` | Coleta de dados em andamento |
| `novo` | Dados completos, aguardando cotação |
| `em_cotacao` | Equipe buscando opções |
| `proposta_enviada` | Link de proposta enviado |
| `aguardando_cliente` | Esperando resposta do cliente |
| `vendido` | Venda confirmada |
| `perdido` | Não convertido |

---

## Estrutura do Projeto

```
voe-comilhas/
├── backend/
│   ├── main.py                  # App FastAPI principal
│   ├── config.py                # Configurações centralizadas
│   ├── requirements.txt
│   ├── schema.sql               # Schema do Supabase
│   ├── .env.example
│   ├── routes/
│   │   ├── webhook_uazapi.py    # Webhook do WhatsApp
│   │   ├── cotacoes.py          # CRUD de cotações
│   │   ├── clientes.py          # CRUD de clientes
│   │   └── propostas.py        # Proposta pública
│   ├── services/
│   │   ├── agente_openai.py     # IA de atendimento
│   │   ├── uazapi.py            # Integração WhatsApp
│   │   └── supabase_service.py # Banco de dados
│   └── schemas/
│       ├── cotacao_schema.py
│       ├── cliente_schema.py
│       └── proposta_schema.py
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── pages/
    │   │   ├── Dashboard.jsx         # Lista de cotações
    │   │   ├── CotacaoDetalhe.jsx    # Detalhe + proposta
    │   │   └── PropostaPublica.jsx   # Página do cliente
    │   └── components/
    │       ├── Layout.jsx
    │       ├── CotacaoCard.jsx
    │       ├── StatusBadge.jsx
    │       └── PropostaOption.jsx
    └── package.json
```

---

## Produção

Para publicar em produção:

**Backend:** Railway, Render, Fly.io, ou VPS própria

**Frontend:** Vercel, Netlify, ou junto com o backend

**Dicas:**
- Remova `"*"` do CORS em `main.py` e coloque apenas a URL do frontend em produção
- Use HTTPS obrigatoriamente para o webhook funcionar
- Configure `APP_ENV=production` no `.env`

---

Desenvolvido para a **Voe Comilhas** 🛫

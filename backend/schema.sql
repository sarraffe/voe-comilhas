-- =============================================
-- Voe Comilhas - Schema do Banco de Dados
-- Execute este arquivo no SQL Editor do Supabase
-- =============================================

-- ============ CLIENTES ============
create table if not exists clientes (
  id uuid primary key default gen_random_uuid(),
  nome text,
  whatsapp text unique not null,
  created_at timestamp with time zone default now()
);

-- ============ COTAÇÕES ============
create table if not exists cotacoes (
  id uuid primary key default gen_random_uuid(),
  cliente_id uuid references clientes(id) on delete cascade,
  tipo_viagem text,                          -- ida_volta | somente_ida
  origem text,
  destino text,
  data_ida date,
  data_volta date,
  adultos integer default 1,
  criancas integer default 0,
  bebes integer default 0,
  bagagem_23kg boolean default false,
  quantidade_malas integer default 0,
  forma_pagamento text,
  observacoes text,
  status text default 'dados_incompletos',   -- dados_incompletos | novo | em_cotacao | proposta_enviada | aguardando_cliente | vendido | perdido
  codigo_proposta text unique,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- ============ MENSAGENS ============
create table if not exists mensagens (
  id uuid primary key default gen_random_uuid(),
  cliente_id uuid references clientes(id) on delete cascade,
  cotacao_id uuid references cotacoes(id) on delete set null,
  origem_mensagem text not null,             -- cliente | agente
  conteudo text not null,
  created_at timestamp with time zone default now()
);

-- ============ OPÇÕES DE VOO ============
create table if not exists opcoes_voo (
  id uuid primary key default gen_random_uuid(),
  cotacao_id uuid references cotacoes(id) on delete cascade,
  companhia text,
  origem text,
  destino text,
  data_voo date,
  horario_saida text,
  horario_chegada text,
  paradas text,
  bagagem text,
  regras text,
  valor_total numeric,
  destaque text,
  validade timestamp with time zone,
  created_at timestamp with time zone default now()
);

-- ============ LOGS DE WEBHOOK ============
create table if not exists webhook_logs (
  id uuid primary key default gen_random_uuid(),
  origem text,
  payload jsonb,
  created_at timestamp with time zone default now()
);

-- ============ TRIGGER: updated_at em cotacoes ============
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger update_cotacoes_updated_at
  before update on cotacoes
  for each row execute function update_updated_at_column();

-- ============ ÍNDICES PARA PERFORMANCE ============
create index if not exists idx_clientes_whatsapp on clientes(whatsapp);
create index if not exists idx_cotacoes_cliente_id on cotacoes(cliente_id);
create index if not exists idx_cotacoes_status on cotacoes(status);
create index if not exists idx_cotacoes_codigo_proposta on cotacoes(codigo_proposta);
create index if not exists idx_mensagens_cliente_id on mensagens(cliente_id);
create index if not exists idx_mensagens_cotacao_id on mensagens(cotacao_id);
create index if not exists idx_opcoes_voo_cotacao_id on opcoes_voo(cotacao_id);

-- ============ ROW LEVEL SECURITY (RLS) ============
-- Para uso com service_role_key (backend), não precisa de políticas específicas.
-- Ativar RLS se quiser proteger acesso direto ao banco pelo frontend.
-- alter table clientes enable row level security;
-- alter table cotacoes enable row level security;
-- alter table mensagens enable row level security;
-- alter table opcoes_voo enable row level security;
-- alter table webhook_logs enable row level security;

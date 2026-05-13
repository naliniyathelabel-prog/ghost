-- Ghost MVP Schema
-- Migration: 001_init
-- Run in Supabase SQL editor

-- Users (managed by Supabase Auth, extend with profile)
create table if not exists public.ghost_profiles (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references auth.users(id) on delete cascade not null unique,
  name         text,
  tone         text not null default 'casual',       -- casual | formal | hinglish
  language     text not null default 'english',
  description  text,
  sample_replies jsonb default '[]'::jsonb,          -- array of strings
  custom_instructions text,
  active       boolean not null default false,
  tier         text not null default 'free',         -- free | pro | business
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

create table if not exists public.contacts (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references auth.users(id) on delete cascade not null,
  phone        text not null,
  name         text,
  policy       text not null default 'auto',         -- auto | ask | never
  created_at   timestamptz default now(),
  unique(user_id, phone)
);

create table if not exists public.message_logs (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references auth.users(id) on delete cascade not null,
  contact_phone text not null,
  direction    text not null,                        -- inbound | outbound
  text         text not null,
  ai_generated boolean default false,
  rating       smallint,                             -- 1 (thumbs up) | -1 (thumbs down) | null
  created_at   timestamptz default now()
);

-- Indexes
create index if not exists idx_message_logs_user_id on public.message_logs(user_id);
create index if not exists idx_message_logs_contact on public.message_logs(user_id, contact_phone);
create index if not exists idx_contacts_user_id on public.contacts(user_id);

-- Row Level Security
alter table public.ghost_profiles enable row level security;
alter table public.contacts enable row level security;
alter table public.message_logs enable row level security;

create policy "Users own their ghost profile"
  on public.ghost_profiles for all
  using (auth.uid() = user_id);

create policy "Users own their contacts"
  on public.contacts for all
  using (auth.uid() = user_id);

create policy "Users own their message logs"
  on public.message_logs for all
  using (auth.uid() = user_id);

-- Rollback:
-- drop table if exists public.message_logs;
-- drop table if exists public.contacts;
-- drop table if exists public.ghost_profiles;

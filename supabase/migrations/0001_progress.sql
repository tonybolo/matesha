-- Схема для синхронизации прогресса между устройствами (шаг после MVP).
-- Приложение пока хранит прогресс в localStorage; эти таблицы повторяют его структуру
-- (web/src/store/progress.ts), чтобы потом переключиться без изменения логики.

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text not null default '',
  grade int not null default 8,
  xp int not null default 0,
  streak int not null default 0,
  last_day date,
  updated_at timestamptz not null default now()
);

create table if not exists public.topic_progress (
  user_id uuid not null references auth.users (id) on delete cascade,
  topic_id text not null,
  step_reached int not null default 0,
  explain_done boolean not null default false,
  check_best int not null default 0,
  check_passed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, topic_id)
);

create table if not exists public.task_progress (
  user_id uuid not null references auth.users (id) on delete cascade,
  topic_id text not null,
  task_id text not null,
  attempts int not null default 0,
  solved boolean not null default false,
  first_try boolean not null default false,
  revealed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, topic_id, task_id)
);

-- Каждый видит и меняет только свои строки.
alter table public.profiles enable row level security;
alter table public.topic_progress enable row level security;
alter table public.task_progress enable row level security;

create policy "profiles: свои строки" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "topic_progress: свои строки" on public.topic_progress
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "task_progress: свои строки" on public.task_progress
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

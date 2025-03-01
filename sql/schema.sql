create table resumes (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references auth.users(id),
    template_id text,
    name text,
    phone text,
    email text,
    position text,
    content text,
    created_at timestamp default now()
);

create table orders (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references auth.users(id),
    amount int,
    status text,
    created_at timestamp default now()
);

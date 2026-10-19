CREATE TABLE users (
    id uuid PRIMARY KEY,
    first_name varchar(100) NOT NULL CHECK (length(btrim(first_name)) > 0),
    second_name varchar(100) NOT NULL CHECK (length(btrim(second_name)) > 0),
    birthdate date NOT NULL CHECK (birthdate <= CURRENT_DATE),
    gender varchar(11) NOT NULL CHECK (gender IN ('male', 'female', 'other', 'unspecified')),
    biography varchar(2000) NOT NULL CHECK (length(btrim(biography)) > 0),
    city varchar(100) NOT NULL CHECK (length(btrim(city)) > 0),
    password_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    token_hash char(64) PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamptz NOT NULL,
    CHECK (expires_at > created_at)
);

CREATE TABLE IF NOT EXISTS role_permissions_log (
    id SERIAL PRIMARY KEY,
    role TEXT NOT NULL,
    route TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
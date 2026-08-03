-- Introduces the credential store required to replace PKG_SECURITY.authenticate(),
-- which issued sessions on email lookup alone with no password check (confirmed
-- CRITICAL defect). No USER_CREDENTIALS-equivalent table existed in the legacy
-- schema (ASMP-004) - this is a net-new design, not a port.
CREATE TABLE user_credentials (
    id                     BIGSERIAL PRIMARY KEY,
    employee_id            BIGINT NOT NULL,
    email                  VARCHAR(254) NOT NULL,
    password_hash          VARCHAR(255) NOT NULL,
    role                   VARCHAR(30) NOT NULL DEFAULT 'EMPLOYEE',
    account_locked         BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_attempts  INTEGER NOT NULL DEFAULT 0,
    last_login_at          TIMESTAMP,
    created_at             TIMESTAMP NOT NULL DEFAULT now(),
    updated_at             TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_credentials_employee_id UNIQUE (employee_id),
    CONSTRAINT uq_user_credentials_email UNIQUE (email)
);

-- Email is the sole authentication lookup key, so its uniqueness is a
-- security-load-bearing constraint, not just a data-quality one.
CREATE INDEX idx_user_credentials_email ON user_credentials (email);

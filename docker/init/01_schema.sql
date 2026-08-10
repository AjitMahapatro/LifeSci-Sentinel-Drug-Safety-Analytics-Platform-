-- LifeSci Sentinel warehouse schema bootstrap.
-- This DDL was not present in the repository (it was created manually in the
-- original PostgreSQL instance). It re-creates the authoritative `warehouse`
-- star schema exactly as the load_all.py scripts expect.

CREATE SCHEMA IF NOT EXISTS warehouse;

-- Dimension: date
CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key    INTEGER PRIMARY KEY,
    date        DATE NOT NULL,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  VARCHAR(16) NOT NULL,
    quarter     INTEGER NOT NULL
);

-- Dimension: drug
CREATE TABLE IF NOT EXISTS warehouse.dim_drug (
    drug_key   SERIAL PRIMARY KEY,
    drug_name  VARCHAR(255) NOT NULL UNIQUE
);

-- Dimension: reaction
CREATE TABLE IF NOT EXISTS warehouse.dim_reaction (
    reaction_key   SERIAL PRIMARY KEY,
    reaction_name  VARCHAR(255) NOT NULL UNIQUE
);

-- Fact: drug safety events
CREATE TABLE IF NOT EXISTS warehouse.fact_drug_safety_events (
    event_id   VARCHAR(64) PRIMARY KEY,
    drug_key   INTEGER NOT NULL REFERENCES warehouse.dim_drug (drug_key),
    date_key   INTEGER NOT NULL REFERENCES warehouse.dim_date (date_key),
    serious    INTEGER NOT NULL
);

-- Fact: event - reaction bridge
CREATE TABLE IF NOT EXISTS warehouse.fact_event_reaction (
    event_id      VARCHAR(64) NOT NULL REFERENCES warehouse.fact_drug_safety_events (event_id),
    reaction_key  INTEGER NOT NULL REFERENCES warehouse.dim_reaction (reaction_key),
    PRIMARY KEY (event_id, reaction_key)
);

-- Indexes used by the analytics queries
CREATE INDEX IF NOT EXISTS idx_fact_drug_safety_drug
    ON warehouse.fact_drug_safety_events (drug_key);
CREATE INDEX IF NOT EXISTS idx_fact_drug_safety_date
    ON warehouse.fact_drug_safety_events (date_key);
CREATE INDEX IF NOT EXISTS idx_fact_drug_safety_serious
    ON warehouse.fact_drug_safety_events (serious);
CREATE INDEX IF NOT EXISTS idx_fact_event_reaction_event
    ON warehouse.fact_event_reaction (event_id);
CREATE INDEX IF NOT EXISTS idx_fact_event_reaction_reaction
    ON warehouse.fact_event_reaction (reaction_key);

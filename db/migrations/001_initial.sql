CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS tenant (
  tenant_id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS principal (
  principal_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(tenant_id),
  external_key TEXT NOT NULL,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  is_administrator BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE (tenant_id, external_key)
);

CREATE TABLE IF NOT EXISTS principal_group (
  principal_id UUID NOT NULL REFERENCES principal(principal_id),
  group_id UUID NOT NULL,
  group_key TEXT NOT NULL,
  PRIMARY KEY (principal_id, group_id)
);

CREATE TABLE IF NOT EXISTS principal_label (
  principal_id UUID NOT NULL REFERENCES principal(principal_id),
  label_type TEXT NOT NULL CHECK (label_type IN ('role', 'region')),
  label_value TEXT NOT NULL,
  PRIMARY KEY (principal_id, label_type, label_value)
);

CREATE TABLE IF NOT EXISTS connector (
  connector_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(tenant_id),
  source_type TEXT NOT NULL,
  status TEXT NOT NULL,
  capability_label TEXT NOT NULL,
  checkpoint TEXT,
  last_successful_sync TIMESTAMPTZ,
  item_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  capability_gaps JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS source_item (
  item_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(tenant_id),
  connector_id UUID NOT NULL REFERENCES connector(connector_id),
  external_id TEXT NOT NULL,
  source_type TEXT NOT NULL,
  title TEXT NOT NULL,
  locator TEXT NOT NULL,
  canonical_url TEXT,
  lifecycle_state TEXT NOT NULL,
  content_version TEXT NOT NULL,
  acl_version TEXT NOT NULL,
  source_updated_at TIMESTAMPTZ,
  indexed_at TIMESTAMPTZ NOT NULL,
  content_hash TEXT NOT NULL,
  UNIQUE (connector_id, external_id)
);

CREATE TABLE IF NOT EXISTS content_version (
  content_version_id UUID PRIMARY KEY,
  item_id UUID NOT NULL REFERENCES source_item(item_id),
  version_key TEXT NOT NULL,
  body TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  is_current BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (item_id, version_key)
);

CREATE TABLE IF NOT EXISTS source_acl (
  item_id UUID NOT NULL REFERENCES source_item(item_id),
  acl_version TEXT NOT NULL,
  subject_type TEXT NOT NULL,
  subject_key TEXT NOT NULL,
  permission TEXT NOT NULL CHECK (permission = 'read'),
  is_current BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (item_id, acl_version, subject_type, subject_key)
);

CREATE TABLE IF NOT EXISTS content_chunk (
  chunk_id UUID PRIMARY KEY,
  item_id UUID NOT NULL REFERENCES source_item(item_id),
  content_version_id UUID NOT NULL REFERENCES content_version(content_version_id),
  ordinal INTEGER NOT NULL,
  text_hash TEXT NOT NULL,
  body TEXT NOT NULL,
  embedding vector(1536),
  UNIQUE (content_version_id, ordinal)
);

CREATE TABLE IF NOT EXISTS query_record (
  query_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(tenant_id),
  principal_id UUID NOT NULL REFERENCES principal(principal_id),
  query_hash TEXT NOT NULL,
  query_text_redacted TEXT,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS answer_record (
  answer_id UUID PRIMARY KEY,
  query_id UUID NOT NULL REFERENCES query_record(query_id),
  status TEXT NOT NULL,
  provider_key TEXT NOT NULL,
  prompt_hash TEXT,
  response_hash TEXT,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS citation (
  citation_id UUID PRIMARY KEY,
  answer_id UUID NOT NULL REFERENCES answer_record(answer_id),
  item_id UUID NOT NULL REFERENCES source_item(item_id),
  locator TEXT NOT NULL,
  coverage_state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_run (
  sync_run_id UUID PRIMARY KEY,
  connector_id UUID NOT NULL REFERENCES connector(connector_id),
  mode TEXT NOT NULL,
  status TEXT NOT NULL,
  checkpoint_before TEXT,
  checkpoint_after TEXT,
  items_seen INTEGER NOT NULL DEFAULT 0,
  items_upserted INTEGER NOT NULL DEFAULT 0,
  items_deleted INTEGER NOT NULL DEFAULT 0,
  items_rejected INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  idempotency_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS feedback (
  feedback_id UUID PRIMARY KEY,
  query_id UUID NOT NULL REFERENCES query_record(query_id),
  answer_id UUID REFERENCES answer_record(answer_id),
  rating TEXT NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_event (
  event_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(tenant_id),
  actor_principal_id UUID REFERENCES principal(principal_id),
  event_type TEXT NOT NULL,
  query_id UUID,
  item_id UUID,
  connector_id UUID,
  decision TEXT,
  reason_code TEXT,
  correlation_id UUID,
  created_at TIMESTAMPTZ NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS source_item_tenant_lifecycle_idx ON source_item (tenant_id, lifecycle_state);
CREATE INDEX IF NOT EXISTS audit_event_tenant_created_idx ON audit_event (tenant_id, created_at DESC);

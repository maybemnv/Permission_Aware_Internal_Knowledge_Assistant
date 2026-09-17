-- Follow-up production hardening; keep 001_initial.sql reproducible and intact.
ALTER TABLE principal ADD COLUMN IF NOT EXISTS auth_issued_at timestamptz;
ALTER TABLE principal ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE source_item ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
ALTER TABLE source_acl ADD COLUMN IF NOT EXISTS revoked_at timestamptz;

CREATE INDEX IF NOT EXISTS source_item_tenant_state_idx
  ON source_item (tenant_id, lifecycle_state, source_updated_at);
CREATE INDEX IF NOT EXISTS content_version_current_item_idx
  ON content_version (item_id, is_current);
CREATE INDEX IF NOT EXISTS source_acl_current_item_idx
  ON source_acl (item_id, acl_version, is_current);
CREATE INDEX IF NOT EXISTS sync_run_connector_status_idx
  ON sync_run (connector_id, status, started_at DESC);

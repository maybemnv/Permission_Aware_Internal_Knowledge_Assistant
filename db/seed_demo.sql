INSERT INTO tenant (tenant_id, name, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'Demo tenant', 'active')
ON CONFLICT (tenant_id) DO NOTHING;

INSERT INTO principal (principal_id, tenant_id, external_key, email, is_administrator)
VALUES
  ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'allowed-user', 'allowed@example.com', FALSE),
  ('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'denied-user', 'denied@example.com', FALSE),
  ('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', 'unmapped-user', 'unmapped@example.com', FALSE),
  ('00000000-0000-0000-0000-000000000013', '00000000-0000-0000-0000-000000000001', 'changed-group-user', 'changed@example.com', FALSE),
  ('00000000-0000-0000-0000-000000000014', '00000000-0000-0000-0000-000000000001', 'admin-user', 'admin@example.com', TRUE)
ON CONFLICT (principal_id) DO NOTHING;

INSERT INTO principal_group (principal_id, group_id, group_key)
VALUES
  ('00000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000001', 'group-travel'),
  ('00000000-0000-0000-0000-000000000011', '20000000-0000-0000-0000-000000000002', 'group-operations')
ON CONFLICT (principal_id, group_id) DO NOTHING;

INSERT INTO principal_label (principal_id, label_type, label_value)
VALUES
  ('00000000-0000-0000-0000-000000000010', 'role', 'employee'),
  ('00000000-0000-0000-0000-000000000010', 'region', 'us-east'),
  ('00000000-0000-0000-0000-000000000011', 'role', 'employee'),
  ('00000000-0000-0000-0000-000000000011', 'region', 'us-east')
ON CONFLICT (principal_id, label_type, label_value) DO NOTHING;

INSERT INTO connector (connector_id, tenant_id, source_type, status, capability_label, capability_gaps)
VALUES
  ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'google_drive', 'healthy', 'fixture', '["provider auth not configured"]'),
  ('10000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'sharepoint', 'degraded', 'fixture', '["provider ACL fidelity unverified"]'),
  ('10000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'slack', 'configured', 'blocked', '["live connector blocked for prototype"]'),
  ('10000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'teams', 'configured', 'unverified', '["capability test required"]'),
  ('10000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'notion', 'healthy', 'fixture', '["fixture adapter only"]'),
  ('10000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'confluence', 'configured', 'unverified', '["capability test required"]'),
  ('10000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', 'jira', 'degraded', 'fixture', '["incremental feed is simulated"]'),
  ('10000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', 'github', 'configured', 'blocked', '["provider auth not configured"]')
ON CONFLICT (connector_id) DO NOTHING;

INSERT INTO source_item (
  item_id, tenant_id, connector_id, external_id, source_type, title, locator,
  canonical_url, lifecycle_state, content_version, acl_version, source_updated_at,
  indexed_at, content_hash
)
VALUES
  (
    '30000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000005',
    'notion-travel-policy', 'notion', 'Travel reimbursement policy',
    'notion://policies/travel-reimbursement#regional-rules', NULL, 'active', 'v1', 'v1',
    TIMESTAMPTZ '2026-08-07 12:00:00+00', TIMESTAMPTZ '2026-08-09 12:00:00+00', 'hash-item-travel-policy'
  ),
  (
    '30000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    'drive-travel-approval-form', 'google_drive', 'Travel approval form',
    'drive://forms/travel-approval', NULL, 'active', 'v1', 'v1',
    TIMESTAMPTZ '2026-08-07 12:00:00+00', TIMESTAMPTZ '2026-08-09 12:00:00+00', 'hash-item-approval-form'
  ),
  (
    '30000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000008',
    'github-restricted-project', 'github', 'Restricted project launch notes',
    'github://internal/restricted-project/launch.md', NULL, 'active', 'v1', 'v1',
    TIMESTAMPTZ '2026-08-07 12:00:00+00', TIMESTAMPTZ '2026-08-09 12:00:00+00', 'hash-item-restricted-project'
  )
ON CONFLICT (item_id) DO NOTHING;

INSERT INTO content_version (
  content_version_id, item_id, version_key, body, content_hash, created_at, is_current
)
VALUES
  (
    '40000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001', 'v1',
    'Employees in us-east may claim economy travel and lodging with receipts. Submit the travel approval form before booking and file reimbursement within 30 days.',
    'hash-item-travel-policy', TIMESTAMPTZ '2026-08-07 12:00:00+00', TRUE
  ),
  (
    '40000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000002', 'v1',
    'Use the Travel Approval Form for manager approval, cost center, itinerary, and receipts.',
    'hash-item-approval-form', TIMESTAMPTZ '2026-08-07 12:00:00+00', TRUE
  ),
  (
    '40000000-0000-0000-0000-000000000003',
    '30000000-0000-0000-0000-000000000003', 'v1',
    'Secret restricted project launch details must not be shown to ordinary employees.',
    'hash-item-restricted-project', TIMESTAMPTZ '2026-08-07 12:00:00+00', TRUE
  )
ON CONFLICT (content_version_id) DO NOTHING;

INSERT INTO source_acl (item_id, acl_version, subject_type, subject_key, permission, is_current)
VALUES
  ('30000000-0000-0000-0000-000000000001', 'v1', 'group', 'group-travel', 'read', TRUE),
  ('30000000-0000-0000-0000-000000000002', 'v1', 'group', 'group-travel', 'read', TRUE),
  ('30000000-0000-0000-0000-000000000003', 'v1', 'group', 'group-restricted-project', 'read', TRUE)
ON CONFLICT (item_id, acl_version, subject_type, subject_key) DO NOTHING;

INSERT INTO content_chunk (chunk_id, item_id, content_version_id, ordinal, text_hash, body)
VALUES
  (
    '50000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001', 0, 'hash-chunk-travel-policy',
    'Employees in us-east may claim economy travel and lodging with receipts. Submit the travel approval form before booking and file reimbursement within 30 days.'
  ),
  (
    '50000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000002',
    '40000000-0000-0000-0000-000000000002', 0, 'hash-chunk-approval-form',
    'Use the Travel Approval Form for manager approval, cost center, itinerary, and receipts.'
  ),
  (
    '50000000-0000-0000-0000-000000000003',
    '30000000-0000-0000-0000-000000000003',
    '40000000-0000-0000-0000-000000000003', 0, 'hash-chunk-restricted-project',
    'Secret restricted project launch details must not be shown to ordinary employees.'
  )
ON CONFLICT (chunk_id) DO NOTHING;

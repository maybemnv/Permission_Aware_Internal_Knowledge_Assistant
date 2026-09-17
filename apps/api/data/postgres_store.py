"""Small PostgreSQL/pgvector repository used outside fixture mode."""

from __future__ import annotations

from typing import Any

from apps.api.domain.contracts import (
    LifecycleState,
    PrincipalContext,
    SearchCandidate,
    SearchFilters,
    SourcePermission,
    SourceType,
)


class PostgresStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        import psycopg

        return psycopg.connect(self.database_url)

    def ping(self) -> None:
        """Fail readiness when the configured database cannot be reached."""
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    def get_principal(self, principal_key: str) -> PrincipalContext | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT principal_id, tenant_id, email, auth_issued_at, is_administrator "
                "FROM principal WHERE external_key = %s AND status = 'active'",
                (principal_key,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            principal_id, tenant_id, email, issued, administrator = row
            cursor.execute(
                "SELECT group_key FROM principal_group WHERE principal_id = %s", (principal_id,)
            )
            groups = [item[0] for item in cursor.fetchall()]
            cursor.execute(
                "SELECT label_type, label_value FROM principal_label WHERE principal_id = %s",
                (principal_id,),
            )
            labels = cursor.fetchall()
        return PrincipalContext(
            tenant_id=str(tenant_id), principal_id=str(principal_id), email=email,
            group_ids=groups,
            role_labels=[value for kind, value in labels if kind == "role"],
            region_labels=[value for kind, value in labels if kind == "region"],
            auth_issued_at=issued,
            is_administrator=administrator,
        )

    def get_item(self, item_id: str) -> SearchCandidate | None:
        items = self._query_items("si.item_id = %s", (item_id,))
        return items[0] if items else None

    def save_item(self, item: SearchCandidate) -> None:
        raise NotImplementedError("connector writes must use the sync repository boundary")

    def list_candidates(
        self, tenant_id: str, query: str, filters: SearchFilters | None = None
    ) -> list[SearchCandidate]:
        terms = [term for term in query.casefold().split() if term not in {"a", "an", "and", "are", "for", "my", "of", "the", "what", "with"}]
        if not terms:
            return []
        clauses = ["si.tenant_id = %s", "si.lifecycle_state IN ('active', 'stale')"]
        values: list[Any] = [tenant_id]
        for term in terms:
            clauses.append("(cv.body ILIKE %s OR si.title ILIKE %s)")
            values.extend([f"%{term}%", f"%{term}%"])
        if filters and filters.source_types:
            clauses.append("si.source_type = ANY(%s)")
            values.append([item.value for item in filters.source_types])
        rows = self._query_items(" AND ".join(clauses), tuple(values))
        return [item.model_copy(update={"score": float(sum(term in f"{item.title} {item.body}".casefold() for term in terms))}) for item in rows]

    def _query_items(self, where: str, values: tuple[Any, ...]) -> list[SearchCandidate]:
        sql = (
            "SELECT si.item_id, si.tenant_id, si.source_type, si.title, si.locator, "
            "si.source_updated_at, si.indexed_at, si.lifecycle_state, si.acl_version, "
            "si.content_hash, cv.body, COALESCE(json_agg(json_build_object(" 
            "'subject_type', sa.subject_type, 'subject_key', sa.subject_key)) "
            "FILTER (WHERE sa.subject_key IS NOT NULL), '[]') "
            "FROM source_item si JOIN content_version cv ON cv.item_id = si.item_id AND cv.is_current "
            "LEFT JOIN source_acl sa ON sa.item_id = si.item_id AND sa.acl_version = si.acl_version "
            f"WHERE {where} GROUP BY si.item_id, cv.body"
        )
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(sql, values)
            rows = cursor.fetchall()
        result = []
        for item_id, tenant_id, source_type, title, locator, updated, indexed, lifecycle, acl_version, content_hash, body, acl in rows:
            result.append(SearchCandidate(
                item_id=str(item_id), tenant_id=str(tenant_id), source_type=SourceType(source_type),
                title=title, body=body, locator=locator, source_updated_at=updated,
                indexed_at=indexed, lifecycle_state=LifecycleState(lifecycle), acl_version=acl_version,
                acl_subjects=[SourcePermission(subject_type=row["subject_type"], subject_key=row["subject_key"]) for row in acl],
                metadata={"content_hash": content_hash},
            ))
        return result

"""T0-10, T1-01, T1-09, T2-01: migration lên/xuống và ràng buộc bắt buộc của lược đồ."""

import uuid

import pytest
from alembic import command
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from tests.conftest import alembic_config

pytestmark = pytest.mark.integration


def test_upgrade_downgrade_roundtrip(database_url: str, migrated_url: str) -> None:
    cfg = alembic_config(migrated_url)
    command.downgrade(cfg, "base")
    engine = create_engine(migrated_url)
    try:
        tables = set(inspect(engine).get_table_names())
        assert tables <= {"alembic_version"}
        command.upgrade(cfg, "head")
        tables = set(inspect(engine).get_table_names())
        expected = {
            "users", "access_grants", "sessions", "login_failures", "documents", "jobs", "chunks",
            "conversations", "messages", "citations", "feedback", "audit_records", "usage_events",
            "document_acl",
        }  # fmt: skip
        assert expected <= tables
    finally:
        engine.dispose()


@pytest.fixture
def conn(runtime):  # type: ignore[no-untyped-def]
    with runtime.engine.connect() as c:
        yield c


def _user(conn, login: str = "u") -> uuid.UUID:  # type: ignore[no-untyped-def]
    uid = uuid.uuid4()
    conn.execute(text("INSERT INTO users (id, login) VALUES (:id, :l)"), {"id": uid, "l": login})
    return uid


def test_access_grant_check_constraints(conn) -> None:  # type: ignore[no-untyped-def]
    uid = _user(conn)
    with pytest.raises(IntegrityError):
        conn.execute(
            text(
                "INSERT INTO access_grants (user_id, role, status) VALUES (:u, 'admin', 'active')"
            ),
            {"u": uid},
        )
    conn.rollback()
    uid = _user(conn, "u2")
    with pytest.raises(IntegrityError):
        conn.execute(
            text("INSERT INTO access_grants (user_id, role, status) VALUES (:u, 'bd', 'paused')"),
            {"u": uid},
        )


def test_login_is_unique(conn) -> None:  # type: ignore[no-untyped-def]
    _user(conn, "trung")
    with pytest.raises(IntegrityError):
        _user(conn, "trung")


def _document(conn, owner: uuid.UUID, status: str = "ready") -> uuid.UUID:  # type: ignore[no-untyped-def]
    did = uuid.uuid4()
    conn.execute(
        text(
            "INSERT INTO documents (id, owner_id, file_name, size_bytes, storage_key, status) "
            "VALUES (:id, :o, 'a.pdf', 1, 'k', :s)"
        ),
        {"id": did, "o": owner, "s": status},
    )
    return did


def test_document_status_and_reason_constraints(conn) -> None:  # type: ignore[no-untyped-def]
    owner = _user(conn)
    with pytest.raises(IntegrityError):
        _document(conn, owner, "archived")
    conn.rollback()
    owner = _user(conn)
    did = _document(conn, owner, "failed")
    with pytest.raises(IntegrityError):
        conn.execute(
            text("UPDATE documents SET failure_reason = 'virus' WHERE id = :id"), {"id": did}
        )


def test_chunk_requires_page(conn) -> None:  # type: ignore[no-untyped-def]
    did = _document(conn, _user(conn))
    vector = "[" + ",".join(["0.1"] * 1024) + "]"
    with pytest.raises(IntegrityError):
        conn.execute(
            text(
                "INSERT INTO chunks (id, document_id, page, ordinal, text, embedding) "
                "VALUES (:id, :d, NULL, 0, 't', CAST(:e AS vector))"
            ),
            {"id": uuid.uuid4(), "d": did, "e": vector},
        )


def test_job_kind_constraint(conn) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(IntegrityError):
        conn.execute(text("INSERT INTO jobs (kind, payload) VALUES ('email', '{}')"))


def test_deleting_message_cascades_to_citations_and_feedback(conn) -> None:  # type: ignore[no-untyped-def]
    uid = _user(conn)
    did = _document(conn, uid)
    cid, mid = uuid.uuid4(), uuid.uuid4()
    conn.execute(
        text("INSERT INTO conversations (id, user_id) VALUES (:c, :u)"), {"c": cid, "u": uid}
    )
    conn.execute(
        text(
            "INSERT INTO messages (id, conversation_id, role, content) VALUES (:m, :c, 'assistant', 'x')"
        ),
        {"m": mid, "c": cid},
    )
    conn.execute(
        text(
            "INSERT INTO citations (message_id, document_id, document_name, page) "
            "VALUES (:m, :d, 'a.pdf', 1)"
        ),
        {"m": mid, "d": did},
    )
    conn.execute(
        text("INSERT INTO feedback (message_id, user_id, value) VALUES (:m, :u, 'helpful')"),
        {"m": mid, "u": uid},
    )
    conn.execute(text("DELETE FROM messages WHERE id = :m"), {"m": mid})
    assert conn.execute(text("SELECT count(*) FROM citations")).scalar() == 0
    assert conn.execute(text("SELECT count(*) FROM feedback")).scalar() == 0


def test_audit_and_usage_tables_have_no_content_columns(runtime) -> None:  # type: ignore[no-untyped-def]
    insp = inspect(runtime.engine)
    for table in ("audit_records", "usage_events"):
        columns = {c["name"] for c in insp.get_columns(table)}
        assert not columns & {"question", "content", "text", "answer", "body"}, table

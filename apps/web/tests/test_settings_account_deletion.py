"""Tests for account deletion behavior in settings."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import UUID

import pytest
from arbolab.core.security import LabRole
from sqlmodel import Session, SQLModel, create_engine, select
from starlette.requests import Request

from apps.web.core.paths import ensure_workspace_paths, resolve_workspace_paths
from apps.web.core.security import get_password_hash
from apps.web.models.user import User, UserWorkspaceAssociation, Workspace
from apps.web.routers.settings import delete_account


def create_session() -> Session:
    """Create an in-memory SQLModel session.

    Returns:
        In-memory SQLModel session.
    """
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def create_user(session: Session, email: str, password: str) -> User:
    """Create a user with a hashed password.

    Args:
        session: Active database session.
        email: Email address for the user.
        password: Plaintext password to hash.

    Returns:
        Persisted user instance.
    """
    user = User(email=email, hashed_password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_workspace(session: Session, name: str) -> Workspace:
    """Create and persist a workspace.

    Args:
        session: Active database session.
        name: Workspace display name.

    Returns:
        Persisted workspace instance.
    """
    workspace = Workspace(name=name)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


def link_user_workspace(
    session: Session,
    user: User,
    workspace: Workspace,
    role: LabRole = LabRole.ADMIN,
) -> None:
    """Link a user to a workspace via the association table.

    Args:
        session: Active database session.
        user: User to associate.
        workspace: Workspace to associate.
        role: Access role for the association.
    """
    association = UserWorkspaceAssociation(
        user_id=user.id,
        workspace_id=workspace.id,
        role=role,
    )
    session.add(association)
    session.commit()


def create_workspace_storage(workspace_id: UUID) -> Path:
    """Create workspace storage and return the base directory.

    Args:
        workspace_id: Workspace identifier.

    Returns:
        Base directory for the workspace storage.
    """
    paths = resolve_workspace_paths(workspace_id)
    ensure_workspace_paths(paths)
    return paths.workspace_root.parent


def user_association_ids(session: Session, user_id: UUID) -> list[UUID]:
    """Return workspace IDs associated with a user.

    Args:
        session: Active database session.
        user_id: User identifier.

    Returns:
        Workspace IDs linked to the user.
    """
    stmt = select(UserWorkspaceAssociation.workspace_id).where(
        UserWorkspaceAssociation.user_id == user_id
    )
    return list(session.exec(stmt).all())


def workspace_user_ids(session: Session, workspace_id: UUID) -> list[UUID]:
    """Return user IDs associated with a workspace.

    Args:
        session: Active database session.
        workspace_id: Workspace identifier.

    Returns:
        User IDs linked to the workspace.
    """
    stmt = select(UserWorkspaceAssociation.user_id).where(
        UserWorkspaceAssociation.workspace_id == workspace_id
    )
    return list(session.exec(stmt).all())


def build_request() -> Request:
    """Create a minimal request with a mutable session.

    Returns:
        Minimal Starlette request with a session dict.
    """
    scope: dict[str, object] = {
        "type": "http",
        "headers": [],
        "session": {},
    }
    return Request(scope)


def test_delete_account_requires_password(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Account deletion fails without a valid password."""
    monkeypatch.setenv("ARBO_DATA_ROOT", str(tmp_path))
    session = create_session()

    user = create_user(session, "user@example.com", "secret")
    workspace = create_workspace(session, "Solo Lab")
    link_user_workspace(session, user, workspace)
    base_dir = create_workspace_storage(workspace.id)

    response = asyncio.run(
        delete_account(
            request=build_request(),
            password="wrong-password",
            user_id=user.id,
            session=session,
        )
    )

    assert response.status_code == 200
    assert session.get(User, user.id) is not None
    assert session.get(Workspace, workspace.id) is not None
    assert base_dir.exists()


def test_delete_account_removes_orphaned_workspaces_and_storage(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Deletes user, orphaned workspaces, and their storage directories."""
    monkeypatch.setenv("ARBO_DATA_ROOT", str(tmp_path))
    session = create_session()

    user = create_user(session, "user@example.com", "secret")
    other_user = create_user(session, "other@example.com", "shared")

    solo_workspace = create_workspace(session, "Solo Lab")
    shared_workspace = create_workspace(session, "Shared Lab")

    link_user_workspace(session, user, solo_workspace)
    link_user_workspace(session, user, shared_workspace)
    link_user_workspace(session, other_user, shared_workspace, role=LabRole.VIEWER)

    solo_base_dir = create_workspace_storage(solo_workspace.id)
    shared_base_dir = create_workspace_storage(shared_workspace.id)

    response = asyncio.run(
        delete_account(
            request=build_request(),
            password="secret",
            user_id=user.id,
            session=session,
        )
    )

    assert response.status_code == 200
    assert session.get(User, user.id) is None
    assert session.get(User, other_user.id) is not None
    assert session.get(Workspace, solo_workspace.id) is None
    assert session.get(Workspace, shared_workspace.id) is not None
    assert user_association_ids(session, user.id) == []
    assert workspace_user_ids(session, shared_workspace.id) == [other_user.id]
    assert not solo_base_dir.exists()
    assert shared_base_dir.exists()

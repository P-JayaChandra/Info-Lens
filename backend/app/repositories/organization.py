import uuid
from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import UserRole
from app.models.organization import Organization, OrganizationMembership
from app.repositories.base import BaseRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository(BaseRepository[Organization, OrganizationCreate, OrganizationUpdate]):
    def __init__(self):
        super().__init__(Organization)

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Optional[Organization]:
        """Look up organization by unique url slug."""
        stmt = (
            select(Organization)
            .where(Organization.slug == slug.lower().strip())
            .where(Organization.is_deleted.is_(False))
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_user_organizations(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[Organization]:
        """Fetch all organizations a user belongs to."""
        stmt = (
            select(Organization)
            .join(OrganizationMembership, Organization.id == OrganizationMembership.organization_id)
            .where(OrganizationMembership.user_id == user_id)
            .where(OrganizationMembership.is_active.is_(True))
            .where(Organization.is_deleted.is_(False))
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_membership(
        self, session: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[OrganizationMembership]:
        """Get membership record for a specific user and organization."""
        stmt = (
            select(OrganizationMembership)
            .where(OrganizationMembership.organization_id == org_id)
            .where(OrganizationMembership.user_id == user_id)
            .options(selectinload(OrganizationMembership.user))
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def add_membership(
        self,
        session: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        role: UserRole = UserRole.MEMBER,
    ) -> OrganizationMembership:
        """Create or reactivate membership in organization."""
        membership = await self.get_membership(session, org_id, user_id)
        if membership:
            membership.role = role
            membership.is_active = True
        else:
            membership = OrganizationMembership(
                organization_id=org_id,
                user_id=user_id,
                role=role,
                is_active=True,
            )
            session.add(membership)

        await session.flush()
        await session.refresh(membership)
        return membership

    async def remove_membership(
        self, session: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Deactivate or remove membership."""
        membership = await self.get_membership(session, org_id, user_id)
        if membership:
            await session.delete(membership)
            await session.flush()
            return True
        return False

    async def list_members(
        self, session: AsyncSession, org_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> Sequence[OrganizationMembership]:
        """List active members of an organization."""
        stmt = (
            select(OrganizationMembership)
            .where(OrganizationMembership.organization_id == org_id)
            .where(OrganizationMembership.is_active.is_(True))
            .options(selectinload(OrganizationMembership.user))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_storage_usage(
        self, session: AsyncSession, org_id: uuid.UUID, delta_bytes: int
    ) -> Optional[Organization]:
        """Adjust storage usage bytes atomically."""
        org = await self.get(session, org_id)
        if org:
            new_storage = max(0, org.storage_used_bytes + delta_bytes)
            org.storage_used_bytes = new_storage
            session.add(org)
            await session.flush()
        return org


organization_repository = OrganizationRepository()

import uuid
from typing import Any, Dict, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository
from app.schemas.audit import AuditLogFilter


class AuditLogRepository(BaseRepository[AuditLog, Any, Any]):
    def __init__(self):
        super().__init__(AuditLog)

    async def log_event(
        self,
        session: AsyncSession,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create and persist an immutable audit trail entry."""
        audit_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )
        session.add(audit_entry)
        await session.flush()
        await session.refresh(audit_entry)
        return audit_entry

    async def list_filtered(
        self,
        session: AsyncSession,
        filter_params: AuditLogFilter,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[AuditLog]:
        """Query audit events with multiple criteria."""
        stmt = select(AuditLog)
        if filter_params.user_id:
            stmt = stmt.where(AuditLog.user_id == filter_params.user_id)
        if filter_params.organization_id:
            stmt = stmt.where(AuditLog.organization_id == filter_params.organization_id)
        if filter_params.action:
            stmt = stmt.where(AuditLog.action == filter_params.action)
        if filter_params.resource_type:
            stmt = stmt.where(AuditLog.resource_type == filter_params.resource_type)
        if filter_params.start_date:
            stmt = stmt.where(AuditLog.created_at >= filter_params.start_date)
        if filter_params.end_date:
            stmt = stmt.where(AuditLog.created_at <= filter_params.end_date)

        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()


audit_log_repository = AuditLogRepository()

import json
from typing import Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.core.logging import logger

from app.models import AuditLog, AuditAction


class AuditService:
    """Simple helper service for writing audit logs."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        user_id: Optional[int],
        entity_type: str,
        entity_id: Optional[int],
        action: AuditAction,
        data_before: Optional[Any] = None,
        data_after: Optional[Any] = None,
        metadata: Optional[Any] = None,
    ) -> Optional[AuditLog]:
        """
        Log an audit event. Returns None if logging fails (e.g., table doesn't exist).
        This allows the application to continue functioning even if audit logging is unavailable.
        """
        def _serialize(obj: Any) -> Optional[str]:
            if obj is None:
                return None
            if isinstance(obj, str):
                return obj
            try:
                return json.dumps(obj, default=str)
            except Exception:
                return json.dumps(str(obj))

        # Use a savepoint to isolate audit logging from the main transaction
        # This way, if audit logging fails, it won't rollback the main transaction
        savepoint = None
        try:
            # Create a savepoint before attempting audit logging
            savepoint = self.db.begin_nested()
            
            log = AuditLog(
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                data_before=_serialize(data_before),
                data_after=_serialize(data_after),
                metadata_json=_serialize(metadata),
            )
            self.db.add(log)
            self.db.flush()  # Flush to check for errors
            savepoint.commit()  # Commit the savepoint (nested transaction)
            self.db.refresh(log)
            return log
        except OperationalError as e:
            # Handle missing table gracefully - rollback only the savepoint
            if "no such table" in str(e).lower() or "does not exist" in str(e).lower():
                if savepoint:
                    savepoint.rollback()  # Rollback only the savepoint, not the main transaction
                logger.warning(
                    f"Audit logging unavailable: audit_logs table not found. "
                    f"Event: {action.value} on {entity_type} (id: {entity_id}) by user {user_id}"
                )
                return None
            # Re-raise other database errors
            if savepoint:
                savepoint.rollback()
            raise
        except Exception as e:
            # Rollback the savepoint to prevent affecting the main transaction
            if savepoint:
                try:
                    savepoint.rollback()
                except Exception:
                    pass  # Ignore rollback errors
            # Log other errors but don't crash the request
            logger.error(f"Failed to create audit log: {type(e).__name__}: {str(e)}", exc_info=True)
            return None



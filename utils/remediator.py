#!/usr/bin/env python3
"""
Remediator Integration for Wasteless UI
========================================

This module provides integration with the backend EC2Remediator.
It handles execution of remediation actions from the UI.

Author: Wasteless Team
"""

import os
import sys
from typing import List, Dict, Any
import logging
from datetime import datetime, date

# Add backend path to sys.path to import backend modules
# Path structure: wasteless-ui/utils/ -> go up 2 levels -> wasteless/
BACKEND_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..', '..',
    'wasteless'
))

if os.path.exists(BACKEND_PATH):
    sys.path.insert(0, BACKEND_PATH)
else:
    logging.warning(f"Backend path not found: {BACKEND_PATH}")

logger = logging.getLogger(__name__)


def sanitize_for_json(obj: Any) -> Any:
    """
    Convert datetime objects to ISO format strings for JSON serialization.

    Args:
        obj: Object that may contain datetime objects

    Returns:
        Sanitized object with datetimes converted to strings
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_json(item) for item in obj)
    else:
        return obj


class RemediatorProxy:
    """
    Proxy class to execute remediation actions via the backend engine.

    This provides a clean interface for the UI to trigger backend operations.
    """

    def __init__(self, dry_run: bool = True):
        """
        Initialize the remediator proxy.

        Args:
            dry_run: If True, no actual AWS actions are executed
        """
        self.dry_run = dry_run
        self._remediator = None

    def _get_remediator(self):
        """Lazy load the EC2Remediator from backend."""
        if self._remediator is None:
            try:
                # Save current directory
                original_cwd = os.getcwd()

                # Change to backend directory (EC2Remediator expects config files there)
                os.chdir(BACKEND_PATH)

                from src.remediators.ec2_remediator import EC2Remediator
                self._remediator = EC2Remediator(dry_run=self.dry_run)
                logger.info(f"✅ EC2Remediator initialized (dry_run={self.dry_run})")

                # Restore original directory
                os.chdir(original_cwd)
            except ImportError as e:
                # Restore original directory on error
                os.chdir(original_cwd)
                logger.error(f"❌ Cannot import EC2Remediator: {e}")
                logger.error(f"   Backend path: {BACKEND_PATH}")
                logger.error(f"   Make sure wasteless backend is cloned next to wasteless-ui")
                raise Exception(
                    f"Cannot import backend remediator. "
                    f"Make sure wasteless backend is installed at: {BACKEND_PATH}"
                )
            except Exception as e:
                # Restore original directory on error
                os.chdir(original_cwd)
                raise
        return self._remediator

    def execute_recommendations(
        self,
        conn,
        recommendation_ids: List[int]
    ) -> List[Dict]:
        """
        Execute multiple recommendations.

        Args:
            conn: PostgreSQL database connection
            recommendation_ids: List of recommendation IDs to execute

        Returns:
            List of execution results with status and details
        """
        results = []
        remediator = self._get_remediator()

        for rec_id in recommendation_ids:
            try:
                # Get instance_id and recommendation details from database
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        w.resource_id,
                        r.recommendation_type,
                        r.action_required,
                        w.confidence_score
                    FROM recommendations r
                    JOIN waste_detected w ON r.waste_id = w.id
                    WHERE r.id = %s
                """, (rec_id,))

                row = cursor.fetchone()
                cursor.close()

                if not row:
                    results.append({
                        'recommendation_id': rec_id,
                        'success': False,
                        'error': f'Recommendation {rec_id} not found in database',
                        'instance_id': None
                    })
                    continue

                instance_id, rec_type, action, confidence = row

                # Only execute stop or terminate actions
                if rec_type not in ['stop_instance', 'terminate_instance']:
                    results.append({
                        'recommendation_id': rec_id,
                        'instance_id': instance_id,
                        'success': False,
                        'error': f'Action type {rec_type} not supported yet (only stop/terminate)',
                        'recommendation_type': rec_type
                    })
                    continue

                # Execute the stop action (works for both stop and terminate intent)
                result = remediator.stop_instance(
                    instance_id=instance_id,
                    recommendation_id=rec_id,
                    reason=action
                )

                # Add recommendation_id to result
                result['recommendation_id'] = rec_id
                result['recommendation_type'] = rec_type
                result['confidence'] = float(confidence)

                # Sanitize datetime objects for JSON serialization
                result = sanitize_for_json(result)

                results.append(result)

            except Exception as e:
                logger.error(f"Error executing recommendation {rec_id}: {e}")
                results.append({
                    'recommendation_id': rec_id,
                    'success': False,
                    'error': str(e),
                    'instance_id': None
                })

        return results

    def reject_recommendations(
        self,
        conn,
        recommendation_ids: List[int],
        reason: str = "Rejected by user"
    ) -> Dict:
        """
        Reject recommendations (mark as rejected in database).

        Args:
            conn: PostgreSQL database connection
            recommendation_ids: List of recommendation IDs to reject
            reason: Optional reason for rejection

        Returns:
            Dict with count of rejected recommendations
        """
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE recommendations
                SET status = 'rejected',
                    updated_at = NOW()
                WHERE id = ANY(%s)
                RETURNING id
            """, (recommendation_ids,))

            rejected_ids = [row[0] for row in cursor.fetchall()]
            conn.commit()
            cursor.close()

            return {
                'success': True,
                'rejected_count': len(rejected_ids),
                'rejected_ids': rejected_ids
            }
        except Exception as e:
            logger.error(f"Error rejecting recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'rejected_count': 0
            }


def check_backend_available() -> bool:
    """
    Check if the backend is available and properly configured.

    Returns:
        True if backend can be imported, False otherwise
    """
    try:
        sys.path.insert(0, BACKEND_PATH)
        from src.remediators.ec2_remediator import EC2Remediator
        return True
    except ImportError:
        return False


def get_backend_path() -> str:
    """Get the expected backend path."""
    return BACKEND_PATH

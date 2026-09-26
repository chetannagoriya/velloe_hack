"""
Data Store Module

Handles reading/writing assessment data to JSON files.
Provides persistence layer for workflow session data.
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
import time


# Constants
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
DATA_DIR = Path("/tmp/data/sessions") if IS_SERVERLESS else Path("data/sessions")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class DataStoreError(Exception):
    """Raised when data persistence operations fail."""
    pass


def _get_session_file_path(session_id: str) -> Path:
    """
    Get the file path for a session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Path object for the session file
    """
    return DATA_DIR / f"{session_id}.json"


def _acquire_file_lock(file_handle, timeout: int = 5):
    """
    Acquire an exclusive lock on a file with timeout.
    Cross-platform implementation using msvcrt on Windows and fcntl on Unix.
    
    Args:
        file_handle: Open file handle
        timeout: Maximum time to wait for lock in seconds
    
    Raises:
        DataStoreError: If lock cannot be acquired
    """
    start_time = time.time()
    
    if sys.platform == 'win32':
        import msvcrt
        while True:
            try:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except IOError:
                if time.time() - start_time >= timeout:
                    raise DataStoreError("Timeout waiting for file lock")
                time.sleep(0.1)
    else:
        import fcntl
        import errno
        while True:
            try:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except IOError as e:
                if e.errno != errno.EAGAIN:
                    raise DataStoreError(f"Failed to acquire file lock: {str(e)}")
                if time.time() - start_time >= timeout:
                    raise DataStoreError("Timeout waiting for file lock")
                time.sleep(0.1)


def _release_file_lock(file_handle):
    """
    Release file lock.
    Cross-platform implementation.
    
    Args:
        file_handle: Open file handle
    """
    try:
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass  # Ignore errors during unlock


def save_session_data(session_id: str, data: dict) -> bool:
    """
    Saves complete session data to JSON file.
    
    Args:
        session_id: Session identifier
        data: Complete session data dictionary
    
    Returns:
        True if saved successfully, False otherwise
    
    Raises:
        DataStoreError: If save operation fails
    """
    try:
        file_path = _get_session_file_path(session_id)
        
        # Ensure data directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        # Write to file with locking
        with open(file_path, 'w') as f:
            _acquire_file_lock(f)
            try:
                json.dump(data, f, indent=2)
            finally:
                _release_file_lock(f)
        
        return True
    
    except Exception as e:
        raise DataStoreError(f"Failed to save session data: {str(e)}")


def load_session_data(session_id: str) -> Optional[dict]:
    """
    Loads session data from JSON file.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Session data dictionary or None if not found
    
    Raises:
        DataStoreError: If load operation fails (other than file not found)
    """
    try:
        file_path = _get_session_file_path(session_id)
        
        if not file_path.exists():
            return None
        
        # Read from file with locking
        with open(file_path, 'r') as f:
            _acquire_file_lock(f)
            try:
                data = json.load(f)
            finally:
                _release_file_lock(f)
        
        return data
    
    except FileNotFoundError:
        return None
    
    except json.JSONDecodeError as e:
        raise DataStoreError(f"Invalid JSON in session file: {str(e)}")
    
    except Exception as e:
        raise DataStoreError(f"Failed to load session data: {str(e)}")


def update_assessment(session_id: str, assessment_type: str, assessment_data: dict) -> bool:
    """
    Updates specific assessment within session data.
    
    Args:
        session_id: Session identifier
        assessment_type: Type of assessment ('gad7', 'phq9', 'emotion', 'lifestyle')
        assessment_data: Assessment data dictionary
    
    Returns:
        True if updated successfully, False otherwise
    
    Raises:
        DataStoreError: If update operation fails
    """
    try:
        # Load existing session data or create new
        data = load_session_data(session_id)
        
        if data is None:
            # Create new session data structure
            data = {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'workflow_state': {
                    'current_step': 'gad7',
                    'completed_steps': [],
                    'is_complete': False
                },
                'assessments': {}
            }
        
        # Ensure assessments key exists
        if 'assessments' not in data:
            data['assessments'] = {}
        
        # Add completed_at timestamp if not present
        if 'completed_at' not in assessment_data:
            assessment_data['completed_at'] = datetime.now().isoformat()
        
        # Update assessment
        data['assessments'][assessment_type] = assessment_data
        
        # Save updated data
        return save_session_data(session_id, data)
    
    except Exception as e:
        raise DataStoreError(f"Failed to update assessment: {str(e)}")


def get_assessment(session_id: str, assessment_type: str) -> Optional[dict]:
    """
    Retrieves specific assessment data.
    
    Args:
        session_id: Session identifier
        assessment_type: Type of assessment ('gad7', 'phq9', 'emotion', 'lifestyle')
    
    Returns:
        Assessment data dictionary or None if not found
    
    Raises:
        DataStoreError: If retrieval operation fails
    """
    try:
        data = load_session_data(session_id)
        
        if data is None:
            return None
        
        if 'assessments' not in data:
            return None
        
        return data['assessments'].get(assessment_type)
    
    except Exception as e:
        raise DataStoreError(f"Failed to retrieve assessment: {str(e)}")


def update_workflow_state(session_id: str, workflow_state: dict) -> bool:
    """
    Updates workflow state within session data.
    
    Args:
        session_id: Session identifier
        workflow_state: Workflow state dictionary
    
    Returns:
        True if updated successfully, False otherwise
    
    Raises:
        DataStoreError: If update operation fails
    """
    try:
        # Load existing session data or create new
        data = load_session_data(session_id)
        
        if data is None:
            # Create new session data structure
            data = {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'assessments': {}
            }
        
        # Update workflow state
        data['workflow_state'] = workflow_state
        
        # Save updated data
        return save_session_data(session_id, data)
    
    except Exception as e:
        raise DataStoreError(f"Failed to update workflow state: {str(e)}")


def delete_session_data(session_id: str) -> bool:
    """
    Deletes a session file from data store.
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if deleted or file did not exist, False on failure
    """
    try:
        file_path = _get_session_file_path(session_id)
        if file_path.exists():
            file_path.unlink()
        return True
    except Exception as e:
        print(f"Failed to delete session {session_id}: {e}", file=sys.stderr)
        return False


"""
Workflow Orchestrator Module

Manages the complete analysis workflow state and transitions.
Coordinates the sequential flow of assessments: GAD-7, PHQ-9, emotion detection, and lifestyle questionnaire.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict
import uuid


# Error handling classes
class CameraAccessError(Exception):
    """Raised when camera access fails during emotion detection."""
    pass


class DataStoreError(Exception):
    """Raised when data persistence operations fail."""
    pass


# Data models
@dataclass
class WorkflowSession:
    """Represents the state of a workflow session."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    current_step: str
    completed_steps: List[str] = field(default_factory=list)
    is_complete: bool = False


@dataclass
class GAD7Result:
    """GAD-7 assessment result."""
    score: int
    severity: str  # 'minimal', 'mild', 'moderate', 'severe'
    completed_at: datetime


@dataclass
class PHQ9Result:
    """PHQ-9 assessment result."""
    score: int
    severity: str  # 'minimal', 'mild', 'moderate', 'moderately_severe', 'severe'
    completed_at: datetime


@dataclass
class EmotionResult:
    """Emotion detection result."""
    detected_emotion: str
    confidence: float
    mood_data: dict
    completed_at: datetime


@dataclass
class LifestyleData:
    """Lifestyle questionnaire responses."""
    hobbies: str
    eating_habits: str
    daily_life: str
    sleep_schedule: str
    meditation: str
    exercise: str
    feel_good_activities: str
    happiness_triggers: str
    completed_at: datetime


# Workflow Orchestrator class
class WorkflowOrchestrator:
    """Manages the complete analysis workflow state and transitions."""
    
    WORKFLOW_STEPS = [
        'gad7',
        'phq9',
        'emotion',
        'lifestyle',
        'report'
    ]
    
    def __init__(self, session_id: str, workflow_state: Optional[WorkflowSession] = None):
        """
        Initialize orchestrator with session ID.
        
        Args:
            session_id: Unique identifier for the workflow session
            workflow_state: Optional existing workflow state to restore
        """
        self.session_id = session_id
        
        if workflow_state:
            self.workflow_state = workflow_state
        else:
            # Create new workflow state
            self.workflow_state = WorkflowSession(
                session_id=session_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                current_step=self.WORKFLOW_STEPS[0],
                completed_steps=[],
                is_complete=False
            )
    
    def get_current_step(self) -> str:
        """Returns current workflow step name."""
        return self.workflow_state.current_step
    
    def get_next_step(self) -> Optional[str]:
        """Returns next workflow step or None if complete."""
        try:
            current_index = self.WORKFLOW_STEPS.index(self.workflow_state.current_step)
            if current_index < len(self.WORKFLOW_STEPS) - 1:
                return self.WORKFLOW_STEPS[current_index + 1]
            return None
        except ValueError:
            return None
    
    def advance_step(self) -> bool:
        """
        Advances to next step, returns success status.
        
        Returns:
            True if advanced successfully, False if already at last step
        """
        next_step = self.get_next_step()
        if next_step:
            # Add current step to completed steps
            if self.workflow_state.current_step not in self.workflow_state.completed_steps:
                self.workflow_state.completed_steps.append(self.workflow_state.current_step)
            
            # Move to next step
            self.workflow_state.current_step = next_step
            self.workflow_state.updated_at = datetime.now()
            
            # Check if workflow is complete
            if next_step == 'report':
                self.workflow_state.is_complete = True
            
            return True
        return False
    
    def get_progress(self) -> dict:
        """
        Returns progress info: {current: int, total: int, percent: float, completed_count: int}.
        
        Returns:
            Dictionary with current step number, total steps, percentage, and completed count
        """
        try:
            current_index = self.WORKFLOW_STEPS.index(self.workflow_state.current_step)
            current_step_num = current_index + 1
            total_steps = len(self.WORKFLOW_STEPS)
            
            # Calculate progress based on completed steps, not current step
            completed_count = len(self.workflow_state.completed_steps)
            percent = (completed_count / total_steps) * 100
            
            return {
                'current': current_step_num,
                'total': total_steps,
                'percent': round(percent, 1),
                'completed_count': completed_count,
                'completed_steps': self.workflow_state.completed_steps
            }
        except ValueError:
            return {
                'current': 0,
                'total': len(self.WORKFLOW_STEPS),
                'percent': 0.0,
                'completed_count': 0,
                'completed_steps': []
            }
    
    def is_complete(self) -> bool:
        """Returns True if workflow is complete."""
        return self.workflow_state.is_complete
    
    def to_dict(self) -> dict:
        """Convert workflow state to dictionary."""
        return {
            'session_id': self.workflow_state.session_id,
            'created_at': self.workflow_state.created_at.isoformat(),
            'updated_at': self.workflow_state.updated_at.isoformat(),
            'current_step': self.workflow_state.current_step,
            'completed_steps': self.workflow_state.completed_steps,
            'is_complete': self.workflow_state.is_complete
        }


# Workflow management functions
def start_workflow() -> str:
    """
    Creates new workflow session, returns session_id.
    
    Returns:
        Unique session ID (UUID string)
    """
    session_id = str(uuid.uuid4())
    return session_id


def get_workflow_state(session_id: str, session_data: dict) -> dict:
    """
    Retrieves current workflow state from session data.
    
    Args:
        session_id: Session identifier
        session_data: Session data dictionary containing workflow_state
    
    Returns:
        Dictionary with workflow state information
    """
    if 'workflow_state' in session_data:
        return session_data['workflow_state']
    
    # Return default state if not found
    return {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'current_step': WorkflowOrchestrator.WORKFLOW_STEPS[0],
        'completed_steps': [],
        'is_complete': False
    }


def restore_workflow_from_session(session_id: str, session_data: dict) -> WorkflowOrchestrator:
    """
    Restores WorkflowOrchestrator from session data.
    
    Args:
        session_id: Session identifier
        session_data: Session data dictionary containing workflow_state
    
    Returns:
        WorkflowOrchestrator instance with restored state
    """
    workflow_state_dict = get_workflow_state(session_id, session_data)
    
    # Convert dict to WorkflowSession object
    workflow_session = WorkflowSession(
        session_id=workflow_state_dict['session_id'],
        created_at=datetime.fromisoformat(workflow_state_dict['created_at']),
        updated_at=datetime.fromisoformat(workflow_state_dict['updated_at']),
        current_step=workflow_state_dict['current_step'],
        completed_steps=workflow_state_dict.get('completed_steps', []),
        is_complete=workflow_state_dict.get('is_complete', False)
    )
    
    return WorkflowOrchestrator(session_id, workflow_session)


def save_assessment_data(session_id: str, assessment_type: str, data: dict) -> bool:
    """
    Saves assessment data to persistent storage.
    
    This is a wrapper function that will use the data_store module.
    
    Args:
        session_id: Session identifier
        assessment_type: Type of assessment ('gad7', 'phq9', 'emotion', 'lifestyle')
        data: Assessment data dictionary
    
    Returns:
        True if saved successfully, False otherwise
    """
    # Import here to avoid circular dependency
    from data_store import update_assessment
    
    try:
        return update_assessment(session_id, assessment_type, data)
    except Exception as e:
        raise DataStoreError(f"Failed to save assessment data: {str(e)}")


# Assessment score calculation and severity classification functions

def calculate_assessment_score(assessment_type: str, responses: List[int]) -> int:
    """
    Calculate total score for GAD-7 or PHQ-9 assessment.
    
    Args:
        assessment_type: Type of assessment ('gad7' or 'phq9')
        responses: List of response values (0-3 for each question)
    
    Returns:
        Total score (sum of all responses)
    
    Raises:
        ValueError: If assessment_type is invalid or responses are invalid
    """
    if assessment_type not in ['gad7', 'phq9']:
        raise ValueError(f"Invalid assessment type: {assessment_type}")
    
    expected_length = 7 if assessment_type == 'gad7' else 9
    if len(responses) != expected_length:
        raise ValueError(f"{assessment_type.upper()} requires {expected_length} responses, got {len(responses)}")
    
    # Validate all responses are in range 0-3
    for i, response in enumerate(responses):
        if not isinstance(response, int) or response < 0 or response > 3:
            raise ValueError(f"Invalid response at index {i}: {response}. Must be integer 0-3")
    
    return sum(responses)


def calculate_severity(assessment_type: str, score: int) -> str:
    """
    Determine severity level based on assessment score.
    
    Args:
        assessment_type: Type of assessment ('gad7' or 'phq9')
        score: Total assessment score
    
    Returns:
        Severity level string
    
    Raises:
        ValueError: If assessment_type or score is invalid
    """
    if assessment_type == 'gad7':
        # GAD-7 severity ranges
        if score < 0 or score > 21:
            raise ValueError(f"GAD-7 score must be 0-21, got {score}")
        
        if score <= 4:
            return 'minimal'
        elif score <= 9:
            return 'mild'
        elif score <= 14:
            return 'moderate'
        else:  # 15-21
            return 'severe'
    
    elif assessment_type == 'phq9':
        # PHQ-9 severity ranges
        if score < 0 or score > 27:
            raise ValueError(f"PHQ-9 score must be 0-27, got {score}")
        
        if score <= 4:
            return 'minimal'
        elif score <= 9:
            return 'mild'
        elif score <= 14:
            return 'moderate'
        elif score <= 19:
            return 'moderately_severe'
        else:  # 20-27
            return 'severe'
    
    else:
        raise ValueError(f"Invalid assessment type: {assessment_type}")


def is_session_expired(session_data: dict, timeout_hours: int = 24) -> bool:
    """
    Check if a session has expired based on last update time.
    
    Args:
        session_data: Session data dictionary with 'updated_at' field
        timeout_hours: Number of hours before session expires (default: 24)
    
    Returns:
        True if session is expired, False otherwise
    """
    from datetime import timedelta
    
    if not session_data or 'workflow_state' not in session_data:
        return True
    
    workflow_state = session_data['workflow_state']
    if 'updated_at' not in workflow_state:
        return True
    
    try:
        # Parse updated_at timestamp
        updated_at_str = workflow_state['updated_at']
        if isinstance(updated_at_str, str):
            updated_at = datetime.fromisoformat(updated_at_str)
        else:
            updated_at = updated_at_str
        
        # Check if expired
        now = datetime.now()
        time_diff = now - updated_at
        return time_diff > timedelta(hours=timeout_hours)
    
    except (ValueError, TypeError):
        # If we can't parse the timestamp, consider it expired
        return True


def can_resume_workflow(session_data: dict) -> bool:
    """
    Check if a workflow session can be resumed.
    
    Args:
        session_data: Session data dictionary
    
    Returns:
        True if workflow can be resumed, False otherwise
    """
    if not session_data:
        return False
    
    # Check if session is expired
    if is_session_expired(session_data):
        return False
    
    # Check if workflow is already complete
    workflow_state = session_data.get('workflow_state', {})
    if workflow_state.get('is_complete', False):
        return False
    
    # Check if there's a valid current step
    current_step = workflow_state.get('current_step')
    if not current_step or current_step not in WorkflowOrchestrator.WORKFLOW_STEPS:
        return False
    
    return True


def get_resume_url(session_data: dict) -> Optional[str]:
    """
    Get the URL to resume a workflow from its current step.
    
    Args:
        session_data: Session data dictionary
    
    Returns:
        URL path to resume workflow, or None if cannot resume
    """
    if not can_resume_workflow(session_data):
        return None
    
    workflow_state = session_data.get('workflow_state', {})
    current_step = workflow_state.get('current_step')
    
    # Map steps to URLs
    step_urls = {
        'gad7': '/complete-analysis/gad7',
        'phq9': '/complete-analysis/phq9',
        'emotion': '/complete-analysis/emotion',
        'lifestyle': '/complete-analysis/lifestyle',
        'report': '/complete-analysis/report'
    }
    
    return step_urls.get(current_step)

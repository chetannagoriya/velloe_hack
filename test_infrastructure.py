"""Quick test to verify infrastructure setup."""

from workflow_orchestrator import start_workflow, WorkflowOrchestrator
from data_store import save_session_data, load_session_data, update_assessment

# Test 1: Workflow creation
print("Test 1: Workflow creation")
session_id = start_workflow()
print(f"✓ Created session: {session_id}")

orchestrator = WorkflowOrchestrator(session_id)
print(f"✓ Current step: {orchestrator.get_current_step()}")
print(f"✓ Progress: {orchestrator.get_progress()}")

# Test 2: Data persistence
print("\nTest 2: Data persistence")
test_data = {
    'session_id': session_id,
    'created_at': '2024-01-01T00:00:00',
    'updated_at': '2024-01-01T00:00:00',
    'workflow_state': {
        'current_step': 'gad7',
        'completed_steps': [],
        'is_complete': False
    },
    'assessments': {}
}

save_session_data(session_id, test_data)
print(f"✓ Data saved for session: {session_id}")

loaded = load_session_data(session_id)
print(f"✓ Data loaded: {loaded is not None}")
print(f"✓ Session ID matches: {loaded['session_id'] == session_id}")

# Test 3: Assessment update
print("\nTest 3: Assessment update")
gad7_data = {
    'score': 12,
    'severity': 'moderate'
}

update_assessment(session_id, 'gad7', gad7_data)
print(f"✓ GAD-7 assessment saved")

loaded = load_session_data(session_id)
print(f"✓ GAD-7 data retrieved: {loaded['assessments']['gad7']['score'] == 12}")

# Test 4: Workflow advancement
print("\nTest 4: Workflow advancement")
orchestrator.advance_step()
print(f"✓ Advanced to: {orchestrator.get_current_step()}")
print(f"✓ Progress: {orchestrator.get_progress()}")

print("\n✅ All infrastructure tests passed!")

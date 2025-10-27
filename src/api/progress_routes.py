"""
Progress tracking routes for long-running operations
Provides Server-Sent Events (SSE) for real-time progress updates
"""

from flask import Blueprint, Response, request, current_app
import json
import time
from typing import Dict, Any
import uuid

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

# Store active progress sessions
active_sessions = {}

class ProgressTracker:
    """Track progress for long-running operations"""
    
    def __init__(self, session_id: str, operation: str, total_steps: int = 100):
        self.session_id = session_id
        self.operation = operation
        self.total_steps = total_steps
        self.current_step = 0
        self.status = "starting"
        self.message = f"Starting {operation}..."
        self.details = {}
        self.start_time = time.time()
        
    def update(self, step: int = None, message: str = None, details: Dict = None, status: str = None):
        """Update progress"""
        if step is not None:
            self.current_step = step
        if message is not None:
            self.message = message
        if details is not None:
            self.details.update(details)
        if status is not None:
            self.status = status
            
    def get_progress_data(self) -> Dict[str, Any]:
        """Get current progress as dictionary"""
        elapsed = time.time() - self.start_time
        percentage = min(100, (self.current_step / self.total_steps) * 100) if self.total_steps > 0 else 0
        
        return {
            'session_id': self.session_id,
            'operation': self.operation,
            'status': self.status,
            'message': self.message,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'percentage': round(percentage, 1),
            'elapsed_time': round(elapsed, 1),
            'details': self.details
        }
    
    def complete(self, message: str = None):
        """Mark operation as complete"""
        self.status = "complete"
        self.current_step = self.total_steps
        if message:
            self.message = message

def create_progress_session(operation: str, total_steps: int = 100) -> str:
    """Create a new progress tracking session"""
    session_id = str(uuid.uuid4())
    tracker = ProgressTracker(session_id, operation, total_steps)
    active_sessions[session_id] = tracker
    return session_id

def update_progress(session_id: str, **kwargs):
    """Update progress for a session"""
    if session_id in active_sessions:
        active_sessions[session_id].update(**kwargs)

def complete_progress(session_id: str, message: str = None):
    """Complete a progress session"""
    if session_id in active_sessions:
        active_sessions[session_id].complete(message)

def get_progress(session_id: str) -> Dict[str, Any]:
    """Get current progress for a session"""
    if session_id in active_sessions:
        return active_sessions[session_id].get_progress_data()
    return None

@progress_bp.route('/stream/<session_id>')
def progress_stream(session_id: str):
    """Server-Sent Events stream for progress updates"""
    
    def generate():
        """Generate SSE data"""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"
            
            last_update = None
            while session_id in active_sessions:
                tracker = active_sessions[session_id]
                current_data = tracker.get_progress_data()
                
                # Only send update if data changed
                if current_data != last_update:
                    yield f"data: {json.dumps({'type': 'progress', **current_data})}\n\n"
                    last_update = current_data.copy()
                
                # Check if operation is complete
                if tracker.status in ['complete', 'error', 'cancelled']:
                    yield f"data: {json.dumps({'type': 'complete', **current_data})}\n\n"
                    # Clean up session after completion
                    if session_id in active_sessions:
                        del active_sessions[session_id]
                    break
                
                time.sleep(0.5)  # Update every 500ms
                
        except Exception as e:
            error_data = {
                'type': 'error',
                'session_id': session_id,
                'error': str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@progress_bp.route('/status/<session_id>')
def get_progress_status(session_id: str):
    """Get current progress status (REST endpoint)"""
    progress_data = get_progress(session_id)
    if progress_data:
        return {'success': True, 'progress': progress_data}
    else:
        return {'success': False, 'error': 'Session not found'}, 404

@progress_bp.route('/cancel/<session_id>', methods=['POST'])
def cancel_progress(session_id: str):
    """Cancel a progress session"""
    if session_id in active_sessions:
        active_sessions[session_id].update(status='cancelled', message='Operation cancelled by user')
        return {'success': True, 'message': 'Operation cancelled'}
    else:
        return {'success': False, 'error': 'Session not found'}, 404
"""
MathVerse Animation Engine - Celery Worker Configuration
Asynchronous task queue for background rendering jobs.
"""

import os
from celery import Celery
from kombu import Queue

# Set up Django settings module if needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
celery_app = Celery(
    'mathverse-animation',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
    include=['worker.tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Result settings
    result_expires=86400,  # 24 hours
    task_track_started=True,
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_queues={
        'render': {
            'exchange': 'render',
            'routing_key': 'render',
            'queue_arguments': {'x-max-priority': 10}
        },
    },
    task_default_queue='render',
    task_default_routing_key='render',
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    
    # Concurrency settings (adjust based on available resources)
    worker_concurrency=4,
    task_soft_time_limit=600,  # 10 minutes soft limit
    task_time_limit=660,  # 11 minutes hard limit
    
    # Rate limiting
    task_default_rate_limit='10/m',
    
    # Retry settings
    task_default_max_retries=3,
    task_default_retry_delay=60,  # seconds
    
    # Logging
    worker_log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    task_log_format='%(asctime)s - %(name)s - %(levelname)s - [%(task_id)] %(message)s',
)


# Task routing configuration
@celery_app.task(bind=True, ignore_result=False)
def render_animation_task(self, job_id: str, scene_data: dict):
    """
    Celery task to render a mathematical animation.
    
    Args:
        job_id: Unique identifier for this render job
        scene_data: Dictionary containing scene configuration
    
    Returns:
        dict with render status and results
    """
    from worker.tasks import process_render_job
    return process_render_job(job_id, scene_data, self.request.id)


# Health check task
@celery_app.task(bind=True)
def health_check_task(self):
    """Periodic health check for the worker"""
    return {
        'status': 'healthy',
        'worker': self.app.hostname,
        'active': len(self.app.active_tasks),
        'scheduled': len(self.app.schedule),
    }


# Cleanup task for old results
@celery_app.task(bind=True)
def cleanup_old_results(self, max_age_seconds: int = 86400):
    """Clean up old task results and temporary files"""
    from utils.cleanup import cleanup_temp_files, cleanup_old_outputs
    
    cleaned_temp = cleanup_temp_files(max_age_seconds)
    cleaned_outputs = cleanup_old_outputs(max_age_seconds)
    
    return {
        'cleaned_temp_files': cleaned_temp,
        'cleaned_outputs': cleaned_outputs,
    }


# Register periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-every-hour': {
        'task': 'cleanup_old_results',
        'schedule': 3600.0,  # Every hour
        'kwargs': {'max_age_seconds': 86400},
    },
    'health-check-every-minute': {
        'task': 'health_check_task',
        'schedule': 60.0,  # Every minute
    },
}


if __name__ == '__main__':
    celery_app.start()

from database.repository import Repository
from services.tracking_service import TrackingService

def get_repository() -> Repository:
    """Dependency for providing a Repository instance."""
    return Repository()

def get_tracking_service() -> TrackingService:
    """Dependency for providing the TrackingService with injected repository."""
    repo = get_repository()
    return TrackingService(repo)

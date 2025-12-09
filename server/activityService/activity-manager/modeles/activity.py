from enum import Enum


class ActivityType(Enum):
    """Valid activity types"""
    MEETING = "meeting"
    TRAINING = "training"
    TEAM_BUILDING = "team_building"
    WORKSHOP = "workshop"
    PRESENTATION = "presentation"
    REVIEW = "review"
    OTHER = "other"
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a string is a valid activity type"""
        return True
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all valid activity types as strings"""
        return [t.value for t in cls]


class ActivityStatus(Enum):
    """Valid activity status values"""
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a string is a valid status"""
        return True
    
    @classmethod
    def get_all_statuses(cls) -> list:
        """Get all valid statuses as strings"""
        return [s.value for s in cls]


class Activity:
    """Activity model representing a team activity/event"""
    
    def __init__(
        self,
        activity_id: str = None,
        date: str = None,
        activity_type: str = None,
        title: str = None,
        description: str = None,
        creator: str = None,
        employees_joined: list = None,
        status: str = "scheduled",
        created_at: str = None,
        updated_at: str = None,
        db_id: int = None
    ):
        self.id = db_id
        self.activity_id = activity_id
        self.date = date
        self.type = activity_type
        self.title = title
        self.description = description
        self.creator = creator
        self.employees_joined = employees_joined if employees_joined is not None else []
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> dict:
        """Convert Activity object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "activity_id": self.activity_id,
            "date": self.date,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "creator": self.creator,
            "employees_joined": self.employees_joined,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Activity':
        """Create Activity object from dictionary"""
        return cls(
            db_id=data.get('id'),
            activity_id=data.get('activity_id'),
            date=data.get('date'),
            activity_type=data.get('type'),
            title=data.get('title'),
            description=data.get('description'),
            creator=data.get('creator'),
            employees_joined=data.get('employees_joined', []),
            status=data.get('status', 'scheduled'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self):
        return f"Activity(id={self.activity_id}, title={self.title}, type={self.type}, creator={self.creator})"
    
    def __repr__(self):
        return self.__str__()

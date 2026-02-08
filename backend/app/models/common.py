import enum

class ProjectStatus(str, enum.Enum):
    draft = 'draft'
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'

class ApprovalAction(str, enum.Enum):
    submitted = 'submitted'
    approved = 'approved'
    rejected = 'rejected'

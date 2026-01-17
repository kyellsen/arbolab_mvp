from enum import Enum


class LabRole(str, Enum):
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"

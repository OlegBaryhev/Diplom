from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(JSON, nullable=False)

    def has_permission(self, section: str, action: str) -> bool:
        perms = self.permissions.get(section, {})
        if "all_subsections" in perms:
            return action in perms["all_subsections"]
        return action in perms.get("all", [])
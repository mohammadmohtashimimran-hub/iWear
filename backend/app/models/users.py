"""User, Role, UserRole, Permission, RolePermission, Session — security & access control."""
from datetime import datetime

from app.extensions import db


# Association table: User <-> Role (many-to-many). Alias for compatibility.
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(32))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = db.relationship(
        "Role",
        secondary=user_roles,
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic",
    )
    sessions = db.relationship("Session", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", back_populates="user", lazy="dynamic", foreign_keys="AuditLog.user_id")

    def has_permission(self, code):
        """True if any of the user's roles has the given permission code."""
        for role in self.roles:
            for rp in role.role_permissions:
                if rp.permission and rp.permission.code == code:
                    return True
        return False


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    role_permissions = db.relationship(
        "RolePermission",
        back_populates="role",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role_permissions = db.relationship(
        "RolePermission",
        back_populates="permission",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class RolePermission(db.Model):
    __tablename__ = "role_permissions"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship("Role", back_populates="role_permissions")
    permission = db.relationship("Permission", back_populates="role_permissions")

    __table_args__ = (db.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="sessions")

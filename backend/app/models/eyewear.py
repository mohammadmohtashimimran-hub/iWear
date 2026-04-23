"""FrameType, LensType, LensIndex, LensCoating, PrescriptionRecord, PrescriptionDetail — eyewear domain."""
from datetime import datetime

from app.extensions import db


class FrameType(db.Model):
    __tablename__ = "frame_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)


class LensType(db.Model):
    __tablename__ = "lens_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)


class LensIndex(db.Model):
    __tablename__ = "lens_indexes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.Numeric(6, 2), nullable=False)


class LensCoating(db.Model):
    __tablename__ = "lens_coatings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)


class PrescriptionRecord(db.Model):
    __tablename__ = "prescription_records"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="prescription_records")
    prescription_details = db.relationship(
        "PrescriptionDetail",
        back_populates="prescription_record",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class PrescriptionDetail(db.Model):
    __tablename__ = "prescription_details"

    id = db.Column(db.Integer, primary_key=True)
    prescription_record_id = db.Column(
        db.Integer,
        db.ForeignKey("prescription_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    eye_side = db.Column(db.String(16), nullable=False)  # e.g. 'left', 'right'
    sphere = db.Column(db.Numeric(6, 2))
    cylinder = db.Column(db.Numeric(6, 2))
    axis = db.Column(db.Numeric(6, 2))
    add_power = db.Column(db.Numeric(6, 2))
    pd = db.Column(db.Numeric(6, 2))  # pupillary distance

    prescription_record = db.relationship("PrescriptionRecord", back_populates="prescription_details")

"""Store/app configuration — vendor-configurable without code changes."""
from app.extensions import db


class StoreSetting(db.Model):
    __tablename__ = "store_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))


class Country(db.Model):
    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

    cities = db.relationship("City", back_populates="country", lazy="dynamic", cascade="all, delete-orphan")


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)

    country = db.relationship("Country", back_populates="cities")

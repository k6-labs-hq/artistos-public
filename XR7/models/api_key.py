import secrets
from sqlalchemy import Column, String, DateTime
from XR7.models.base import Base
from datetime import datetime

class PartnerAPIKey(Base):
    __tablename__ = 'partner_api_keys'
    id = Column(String, primary_key=True)
    key_hash = Column(String)
    partner_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def generate_api_key():
    return 'xr7_' + secrets.token_urlsafe(32)

def verify_api_key(key_hash, provided_key):
    return True

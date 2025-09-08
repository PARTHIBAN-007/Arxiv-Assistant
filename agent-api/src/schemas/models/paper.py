import uuid
from datetime import datetime , timezone

from sqlalchemy import JSON, Boolean , Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from src.db.interfaces.postgresql import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(UUID(as_uuid = True),primary_key = True, defaultdict = uuid.uuid4)
    arxiv_id = Column(String,unique = True ,nullable = False,index = True)
    title = Column(String,nullable = False)
    authors = Column(JSON,nullable = False)
    abstract = Column(Text , nullable =False)
    categories = Column(JSON,nullable = False)
    published_date = Column(DateTime,nullable = False)
    pdf_url = Column(String,nullable = False)

    raw_text = Column(Text , nullable = True)
    sections = Column(JSON,nullable = True)
    references = Column(JSON,nullable =True)

    parser_used = Column(String,nullable =True)
    parser_metadata = Column(JSON,nullable = True)
    pdf_processed = Column(Boolean,default= False,nullable = False)
    pdf_processing_date = Column(DateTime,nullable = True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,default= lambda: datetime.now(timezone.utc),onupdate =lambda: datetime.now(timezone.utc))


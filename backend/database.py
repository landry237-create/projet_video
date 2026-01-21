from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Configuration PostgreSQL
DATABASE_URL = "postgresql://postgres:0000@localhost:5432/videoai_db"

try:
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Connexion PostgreSQL configurée")
except Exception as e:
    print(f"❌ Erreur connexion BD: {e}")
    print("⚠️  Assurez-vous que PostgreSQL est installé et en cours d'exécution")
    raise

# ============================================
# MODELS
# ============================================
class VideoModel(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    status = Column(String, default="processing")
    language = Column(String, nullable=True)
    animals = Column(String, nullable=True)  # Stocke "Oui" ou "Non"
    subtitles_path = Column(String, nullable=True)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "file_id": self.file_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "status": self.status,
            "language": self.language,
            "animals": self.animals,
            "subtitles_path": self.subtitles_path,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

# Créer les tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation BD: {e}")

# Get session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
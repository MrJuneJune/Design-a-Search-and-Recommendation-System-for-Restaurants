from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

class DBFactory:
    _instance = None

    def __init__(self, db_url: str = None):
        if DBFactory._instance is not None:
            raise Exception("Use DBFactory.get_instance() instead of constructor.")

        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb")
        self._engine = create_engine(self.db_url, echo=False, future=True)
        self._session_factory = scoped_session(
            sessionmaker(bind=self._engine, autocommit=False, autoflush=False)
        )

        DBFactory._instance = self

    @classmethod
    def get_instance(cls, db_url: str = None):
        if cls._instance is None:
            cls(db_url)
        return cls._instance

    def get_engine(self):
        return self._engine

    def get_session_factory(self):
        return self._session_factory

    def dispose(self):
        self._engine.dispose()
        DBFactory._instance = None


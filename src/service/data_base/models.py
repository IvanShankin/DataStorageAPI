from sqlalchemy import Column, Integer, String, DateTime, BigInteger, LargeBinary, UniqueConstraint, text
from sqlalchemy.sql import func

from src.service.data_base.core import Base


class SecretsStrings(Base):
    __tablename__ = "secrets_strings"

    string_id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    version = Column(Integer, nullable=True, server_default=text("1")) # версия пользователя

    encrypted_data = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary(12), nullable=False)
    sha256 = Column(LargeBinary(32), nullable=False) # контроль целостности

    enc_version = Column(Integer, nullable=False, server_default=text("1")) # версия сервера
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("name", "version"),
    )


class SecretsFiles(Base):
    __tablename__ = "secrets_files"

    file_id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(Integer, nullable=False, server_default=text("1")) # версия пользователя

    storage_key = Column(String(255), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    sha256 = Column(LargeBinary(32), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("name", "version"),
    )

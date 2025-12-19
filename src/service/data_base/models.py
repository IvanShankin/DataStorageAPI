from sqlalchemy import Column, Integer, String, DateTime, BigInteger, LargeBinary, UniqueConstraint, text, Boolean, \
    false, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.service.data_base.core import Base


class Secrets(Base):
    __tablename__ = "secrets"

    secret_id = Column(BigInteger, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    is_deleted = Column(Boolean, nullable=False, server_default=false())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    secret_string = relationship("SecretsStrings", back_populates="secret")
    secret_file = relationship("SecretsFiles", back_populates="secret")


class SecretsStrings(Base):
    __tablename__ = "secrets_strings"

    string_id = Column(BigInteger, primary_key=True)
    secret_id = Column(ForeignKey("secrets.secret_id"), nullable=False)

    version = Column(Integer, nullable=True, server_default=text("1")) # версия пользователя

    encrypted_data = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary(12), nullable=False)
    sha256 = Column(LargeBinary(32), nullable=False) # контроль целостности

    enc_version = Column(Integer, nullable=False) # версия сервера
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    secret = relationship("Secrets", back_populates="secret_string")


class SecretsFiles(Base):
    __tablename__ = "secrets_files"

    file_id = Column(BigInteger, primary_key=True)
    secret_id = Column(ForeignKey("secrets.secret_id"), nullable=False)

    version = Column(Integer, nullable=False, server_default=text("1")) # версия пользователя

    storage_key = Column(String(255), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    sha256 = Column(LargeBinary(32), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    secret = relationship("Secrets", back_populates="secret_file")
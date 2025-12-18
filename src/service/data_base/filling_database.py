import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import DB_NAME
from src.service.data_base.core import POSTGRES_SERVER_URL, SQL_DB_URL, Base


async def create_database():
    """Создает базу данных и все таблицы в ней (если существует, то ничего не произойдёт) """
    # Сначала подключаемся к серверу PostgreSQL без указания конкретной базы
    engine = create_async_engine(POSTGRES_SERVER_URL, isolation_level="AUTOCOMMIT")
    try:
        # Проверяем существование базы данных и создаем если ее нет
        async with engine.connect() as conn:
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
            )
            database_exists = result.scalar() == 1

            if not database_exists: # если БД нет
                logging.info(f"Creating database {DB_NAME}...")
                await conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                logging.info(f"Database {DB_NAME} created successfully")
            else:
                logging.info(f"Database {DB_NAME} already exists")
    except Exception as e:
        logging.error(f"Error checking/creating database: {e}")
        raise
    finally:
        await engine.dispose()

    # создаем таблицы в целевой базе данных
    engine = create_async_engine(SQL_DB_URL)
    try:
        async with engine.begin() as conn:
            logging.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()
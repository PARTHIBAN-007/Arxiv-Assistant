from src.config import get_settings
from src.db.interfaces.base import baseDatabase
from src.db.interfaces.postgresql import PostgreSQLDatabase
from src.schemas.database.config import PostgreSQLSettings


def make_database()-> baseDatabase:
    """Facotroy function to creata a  database instance"""

    settings = get_settings()

    config = PostgreSQLSettings(
        database_url = settings.postgres_database_url,
        echo_sql = settings.postgres_echo_sql,
        pool_size = settings.postgres_pool_size,
        max_overflow = settings.postgres_max_overflow,
    )

    database = PostgreSQLDatabase(config = config)
    database.startup()
    return database
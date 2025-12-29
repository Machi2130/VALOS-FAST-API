from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
import time
import logging
from app.config import get_settings

settings = get_settings()

# Setup query timing logger
query_logger = logging.getLogger("db.queries")
query_logger.setLevel(logging.DEBUG if settings.debug else logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("⏱️  %(message)s"))
query_logger.addHandler(handler)

# Async engine for application with SSL support for Neon
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_size=10,           # Number of connections to keep open
    max_overflow=20,        # Additional connections allowed beyond pool_size
    pool_recycle=300,       # Recycle connections after 5 minutes (prevents stale connections)
    pool_timeout=30,        # Timeout waiting for a connection from pool
    connect_args={
        "ssl": True,  # This is how asyncpg handles SSL
    }
)

# ============================================
# QUERY TIMING EVENTS (for debugging)
# ============================================
if settings.debug:
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info["query_start_time"] = time.perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        elapsed = (time.perf_counter() - conn.info["query_start_time"]) * 1000
        # Truncate long queries for readability
        short_stmt = statement[:100].replace('\n', ' ') + ('...' if len(statement) > 100 else '')
        query_logger.debug(f"[{elapsed:.2f}ms] {short_stmt}")


# Session factory
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI routes
async def get_db():
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()


# Function to create all tables in Neon DB
async def create_db_and_tables():
    """
    Create all tables in Neon database if they don't exist.
    This runs on application startup.
    """
    async with engine.begin() as conn:
        # Import all models to register them with Base
        from app.models import (
            User, SalesLead, PackagingOption, 
            Costing, CostingPackaging, Quotation, QuotationLine
        )
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")


# Function to drop all tables (use with caution!)
async def drop_db_and_tables():
    """
    Drop all tables - USE WITH CAUTION!
    Only for development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("⚠️  All tables dropped!")

from datetime import datetime
from typing import List, Any

import ormar
from databases import Database
from sqlalchemy import Enum, MetaData

from core import settings

database = Database(settings.DATABASE_URL, pool_recycle=300)


async def init_db_pool():
    await database.connect()
    return database


metadata = MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class ValueEnum(ormar.Enum):
    """Custom FieldType with overriden enum value"""

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        """overriden to use enum values for storage"""
        enum_cls = kwargs.get("enum_class")
        return Enum(enum_cls, values_callable=lambda x: [e.value for e in x])


class Model(ormar.Model):
    """Custom Model with update overriden"""

    async def update(self, _columns: List[str] = None, **kwargs: Any):
        """overriden to set mtime as datetime.now()"""
        # Allow setting mtime with kwargs
        # Overwrite mtime set in the model
        if hasattr(self, "mtime") and "mtime" not in kwargs:
            kwargs["mtime"] = datetime.now()
        return await super().update(_columns, **kwargs)

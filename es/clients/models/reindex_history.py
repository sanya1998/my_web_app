from datetime import datetime

from pydantic import BaseModel


class ReindexHistory(BaseModel):
    task_id: str
    base_alias: str
    dest_index: str
    source_index: str
    started_at: datetime

from pydantic import BaseModel


class EvidMetadata(BaseModel):
    """Metadata model for evid format YAML."""

    authors: str
    dates: str
    label: str
    original_name: str
    tags: list[str]
    time_added: str
    title: str
    url: str
    uuid: str

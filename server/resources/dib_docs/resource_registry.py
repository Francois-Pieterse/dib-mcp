from dataclasses import dataclass
from typing import Any


@dataclass
class DocResourceMeta:
    """
    Metadata for a documentation resource.

    Attributes:
    - name (str): The name of the resource.
    - title (str): The title of the resource.
    - uri (str): The URI of the resource.
    - topic_id (str): The topic identifier the resource belongs to.
    - enabled (bool): Whether the resource is enabled.
    - description (str): A brief description of the resource.
    - endpoint (str): The endpoint from which to fetch the resource content.
    - payload (dict[str, Any]): The payload to send when fetching the resource content.
    """

    name: str
    title: str
    uri: str
    topic_id: str
    enabled: bool
    description: str
    endpoint: str
    payload: dict[str, Any]


DOCS_BY_NAME: dict[str, DocResourceMeta] = {}

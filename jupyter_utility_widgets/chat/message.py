from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid
import numpy as np


class ContentType(Enum):
    TEXT=0
    RAW_AUDIO=1


@dataclass
class Message:
    content: Any
    source: str
    type: ContentType
    uid: uuid.UUID = field(default_factory=uuid.uuid4)

    
@dataclass
class TextMessage(Message):
    content: str
    type: ContentType = ContentType.TEXT

@dataclass
class RawAudioContent:
    data: np.ndarray
    sample_rate: int

@dataclass
class RawAudioMessage(Message):
    content: RawAudioContent
    type: ContentType = ContentType.RAW_AUDIO

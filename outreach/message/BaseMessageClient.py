from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from outreach.models.party import Party


class BaseMessageClient(ABC):
    @abstractmethod
    def send_message(
        self,
        recipient: Party,
        message: str,
        subject: str = "",
        img_paths: Optional[List[Path]] = None,
    ):
        pass

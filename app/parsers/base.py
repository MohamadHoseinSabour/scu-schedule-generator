from abc import ABC, abstractmethod
from typing import Any
from app.domain.models import ScheduleReport

class ReportParser(ABC):
    @abstractmethod
    def can_parse(self, workbook: Any) -> bool:
        pass
    
    @abstractmethod  
    def parse(self, workbook: Any) -> ScheduleReport:
        pass

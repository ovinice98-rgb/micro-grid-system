from abc import ABC, abstractmethod
from datetime import datetime

class GridFaultError(RuntimeError):
    def __init__(self, source_id: str, fault_type: str, detail: str):
        super().__init__(f"[{source_id}] {fault_type}: {detail}")
        self.source_id = source_id

class EnergySource(ABC):
    def __init__(self, source_id: str, rated_capacity_w: float):
        self.source_id = source_id
        self.rated_capacity_w = rated_capacity_w
        
    @abstractmethod
    def generate(self, conditions: dict):
        pass
class SolarSource(EnergySource):
    def generate(self, conditions: dict):
        irradiance = conditions.get("irradiance", 0.0)
        if irradiance < 0 or irradiance > 1.0:
            raise GridFaultError(self.source_id, "InverterFault", "Irradiance out of safe bounds")
        return self.rated_capacity_w * irradiance

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
        # Co-authored by [Olaleye Bethel Bolutife CPE/2023/1084]
class SolarSource(EnergySource):
def generate(self, conditions: dict):
        irradiance = conditions.get("irradiance", 0.0)
        if irradiance < 0 or irradiance > 1.0:
            raise GridFaultError(self.source_id, "InverterFault", "Solar iradiance out of safe limit")
        return self.rated_capacity_w * irradiance
# Solar asset verified by [Oguntade Oluwasikemi Oluwadarasimi CPE/2023/1078]
# By [Olayele Bethel]
# Co-authored by [OGBOYE DIVINE AYOMIDE CPE/2023/1074]
classclass WindSource(EnergySource):
def generate(self, conditions: dict):
        speed = conditions.get("wind_speed", 0.0)
        if speed > 25.0:
            raise GridFaultError(self.source_id, "HighWindCutOut", "Wind speed exceeds safety limits")
        if speed < 3.0:
            return 0.0
        return self.rated_capacity_w * (speed / 12.0)
   # Wind asset verified by [Oladunjoye Olamiposi Caleb Cpe/2023/1082]
class MicrogridController:
    def __init__(self):
        self.sources = []
        self.storage = None
def add_source(self, source: EnergySource):
        self.sources.append(source)

    def balance_grid(self, conditions: dict, total_load_w: float):
        total_gen = sum(s.generate(conditions) for s in self.sources)
        net_power = total_gen - total_load_w
        return {"generation": total_gen, "load": total_load_w, "net": net_power}

# Grid controller verified by [Ogheneyorehme Ovie Favour CPE/2023/1075]

# System Control Module 
class MicrogridController:
    def __init__(self):
        self.sources = []
        self.storage = None
        
    def add_source(self, source: EnergySource):
        self.sources.append(source)
        
    def balance_grid(self, conditions: dict, total_load_w: float):
        total_gen = sum(s.generate(conditions) for s in self.sources)
        net_power = total_gen - total_load_w
        return {"generation": total_gen, "load": total_load_w, "net": net_power, "net_balance": net_power}


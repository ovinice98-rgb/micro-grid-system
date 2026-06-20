class GridFaultError(Exception):
    def __init__(self, asset_id: str, fault_type: str, message: str):
        self.asset_id = asset_id
        self.fault_type = fault_type
        self.message = message
        super().__init__(f"[{fault_type}] Asset {asset_id}: {message}")

class EnergySource:
    def __init__(self, source_id: str, rated_capacity_w: float):
        self.source_id = source_id
        self.rated_capacity_w = rated_capacity_w

    def generate(self, conditions: dict) -> float:
        raise NotImplementedError("Subclasses must implement generate method")

class SolarSource(EnergySource):
    def generate(self, conditions: dict) -> float:
        irradiance = conditions.get("irradiance", 0.0)
        if irradiance < 0 or irradiance > 1.0:
            raise GridFaultError(self.source_id, "InverterFault", "Solar irradiance out of safe limits")
        return self.rated_capacity_w * irradiance

class WindSource(EnergySource):
    def generate(self, conditions: dict) -> float:
        speed = conditions.get("wind_speed", 0.0)
        if speed > 25.0:
            raise GridFaultError(self.source_id, "HighWindCutOut", "Wind speed exceeds safety limits")
        if speed < 3.0:
            return 0.0
        return self.rated_capacity_w * (speed / 12.0)

class BatteryStorage:
    def __init__(self, battery_id: str, max_capacity_kwh: float):
        self.battery_id = battery_id
        self.max_capacity_kwh = max_capacity_kwh
        self.current_charge_kwh = max_capacity_kwh * 0.5
        
    def charge(self, energy_kwh: float):
        self.current_charge_kwh = min(self.max_capacity_kwh, self.current_charge_kwh + energy_kwh)
        
    def discharge(self, energy_kwh: float):
        if self.current_charge_kwh < energy_kwh:
            raise GridFaultError(self.battery_id, "LowBattery", "Battery storage depleted")
        self.current_charge_kwh -= energy_kwh

class MicrogridController:
    def __init__(self):
        self.sources = []
        self.storage = None
        
    def add_source(self, source: EnergySource):
        self.sources.append(source)
        
    def balance_grid(self, conditions: dict, total_load_w: float) -> dict:
        total_gen = sum(s.generate(conditions) for s in self.sources)
        net_power = total_gen - total_load_w
        return {
            "generation": total_gen, 
            "load": total_load_w, 
            "net": net_power,
            "net_balance": net_power
        }

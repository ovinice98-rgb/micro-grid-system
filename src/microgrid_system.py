# MICROGRID SIMULATION SYSTEM - CORE MODULE

class GridFaultError(Exception):
    """Custom exception raised when grid parameters exceed safe operations."""
    def __init__(self, asset_id: str, fault_type: str, message: str):
        self.asset_id = asset_id
        self.fault_type = fault_type
        self.message = message
        super().__init__(f"[{fault_type}] Asset {asset_id}: {message}")


class EnergySource:
    """Base class for all energy generation assets."""
    def __init__(self, source_id: str, rated_capacity_w: float):
        self.source_id = source_id
        self.rated_capacity_w = rated_capacity_w

    def generate(self, conditions: dict) -> float:
        raise NotImplementedError("Subclasses must implement generate method")


# SOLAR MODULE
class SolarSource(EnergySource):
    def generate(self, conditions: dict) -> float:
        irradiance = conditions.get("irradiance", 0.0)
        if irradiance < 0 or irradiance > 1.0:
            raise GridFaultError(self.source_id, "InverterFault", "Solar irradiance out of safe limits")
        return self.rated_capacity_w * irradiance





# WIND MODULE
class WindSource(EnergySource):
    def generate(self, conditions: dict) -> float:
        speed = conditions.get("wind_speed", 0.0)
        if speed > 25.0:
            raise GridFaultError(self.source_id, "HighWindCutOut", "Wind speed exceeds safety limits")
        if speed < 3.0:
            return 0.0
        return self.rated_capacity_w * (speed / 12.0)






# BATTERY STORAGE
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




# SYSTEM CONTROL
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


# MICROGRID SYSTEM - COMPLETE TEST SUITE
import pytest
from src.microgrid_system import GridFaultError, SolarSource, WindSource, BatteryStorage, MicrogridController

# SOLAR TESTS
def test_solar_generation_normal():
    solar = SolarSource("SOL_01", 1000.0)
    assert solar.generate({"irradiance": 0.5}) == 500.0

def test_solar_generation_fault():
    solar = SolarSource("SOL_01", 1000.0)
    with pytest.raises(GridFaultError):
        solar.generate({"irradiance": 1.5})


# WIND TESTS
def test_wind_generation_normal():
    wind = WindSource("WIND_01", 12000.0)
    assert wind.generate({"wind_speed": 12.0}) == 12000.0

def test_wind_cutoff_fault():
    wind = WindSource("WIND_01", 12000.0)
    with pytest.raises(GridFaultError):
        wind.generate({"wind_speed": 30.0})


# BATTERY TESTS
def test_battery_charge():
    bat = BatteryStorage("BAT_01", 100.0)
    bat.charge(20.0)
    assert bat.current_charge_kwh == 70.0 

def test_battery_discharging_empty_error():
    bat = BatteryStorage("BAT_01", 100.0)
    with pytest.raises(GridFaultError):
        bat.discharge(60.0)


# CONTROLLER AND INTEGRATION TESTS
def test_controller_empty_sources():
    ctrl = MicrogridController()
    res = ctrl.balance_grid({"irradiance": 1.0}, 1000.0)
    assert res["generation"] == 0.0

def test_controller_with_solar():
    ctrl = MicrogridController()
    solar = SolarSource("SOL_01", 2000.0)
    ctrl.add_source(solar)
    res = ctrl.balance_grid({"irradiance": 0.5}, 500.0)
    assert res["generation"] == 1000.0

def test_controller_with_multiple_sources():
    ctrl = MicrogridController()
    solar = SolarSource("SOL_01", 2000.0)
    wind = WindSource("WIND_01", 12000.0)
    ctrl.add_source(solar)
    ctrl.add_source(wind)
    conditions = {"irradiance": 0.5, "wind_speed": 12.0}
    res = ctrl.balance_grid(conditions, 5000.0)
    assert res["generation"] == 13000.0

def test_controller_perfect_balance():
    ctrl = MicrogridController()
    solar = SolarSource("SOL_01", 2000.0)
    ctrl.add_source(solar)
    res = ctrl.balance_grid({"irradiance": 0.5}, 1000.0)
    assert res["net"] == 0.0 or res.get("net_balance") == 0.0

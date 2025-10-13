from pydantic import BaseModel
from typing import Optional
from abc import ABC, abstractmethod

from globals_app import SAC, SIC


class VelocityData(BaseModel):
    speed:  int
    track: float
    vertical_rate: int
    speed_type: str

class AircraftData(BaseModel):
    icao: str
    sac: int = SAC
    sic: int = SIC
    lat: Optional[float] = None
    lon: Optional[float] = None
    altitude_ft: Optional[int] = None
    velocity: Optional[VelocityData] = None
    callsign: Optional[str] = None
    emitter_category: Optional[int] = None
    squawk: Optional[int] = None
    flight_status_code: Optional[int] = None


class IAircraftMessage(ABC):
    def __init__(self):
        self.aircraft_data = None
        self.sac = SAC
        self.sic = SIC

    @abstractmethod
    def encode(self) -> bytes | str:
        pass

    @abstractmethod
    def decode(self, data: bytes | str) -> AircraftData | None:
        pass
    
    def update(self, aircraft_data: AircraftData):
        self.aircraft_data = aircraft_data
        return self
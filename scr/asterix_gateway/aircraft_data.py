from pydantic import BaseModel
from typing import Optional


class VelocityData(BaseModel):
    speed: int                
    track: float
    vertical_rate: int
    speed_type: str


class AircraftData(BaseModel):
    icao: str
    sac: int = 0
    sic: int = 0
    lat: Optional[float] = None
    lon: Optional[float] = None
    altitude_ft: Optional[int] = None
    velocity: Optional[VelocityData] = None
    callsign: Optional[str] = None
    emitter_category: Optional[int] = None
    squawk: Optional[int] = None
    flight_status_code: Optional[int] = None

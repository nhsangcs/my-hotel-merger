from dataclasses import dataclass
from typing import List

@dataclass
class Location:
    lat: float
    lng: float
    address: str
    city: str
    country: str

@dataclass
class Image:
    link: str
    description: str

@dataclass
class Images:
    rooms: List[Image]
    site: List[Image]
    amenities: List[Image]

@dataclass
class Amenities:
    general: List[str]
    room: List[str]

@dataclass
class Hotel:
    id: str
    destination_id: int
    name: str
    location: Location
    description: str
    amenities: Amenities
    images: Images
    booking_conditions: List[str]
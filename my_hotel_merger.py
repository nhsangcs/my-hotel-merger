from dataclasses import dataclass, asdict
import json
import argparse
import requests
import re
from typing import List, Dict

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

class BaseSupplier:
    @staticmethod
    def endpoint():
        """URL to fetch supplier data"""

    @staticmethod
    def parse(obj: Dict) -> Hotel:
        """Parse supplier-provided data into Hotel object"""

    def fetch(self) -> List[Hotel]:
        url = self.endpoint()
        resp = requests.get(url)
        resp.raise_for_status()
        return [self.parse(dto) for dto in resp.json()]

class Acme(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme'

    @staticmethod
    def parse(dto: Dict) -> Hotel:
        return Hotel(
            id = dto['Id'],
            destination_id = dto['DestinationId'],
            name = dto['Name'].strip(),
            location = Location(
                lat = dto['Latitude'],
                lng = dto['Longitude'],
                address = dto['Address'].strip(),
                city = dto['City'],
                country = dto['Country']
            ),
            description = dto['Description'].strip(),
            amenities=Amenities(
                general = dto.get("Facilities", []),
                room = dto.get("RoomFacilities", [])
            ),
            images=Images(
                rooms = [Image(link=img['link'], description=img['description']) for img in dto.get("Images", [])],
                site = [Image(link=img['link'], description=img['description']) for img in dto.get("Images", [])],
                amenities = [Image(link=img['link'], description=img['description']) for img in dto.get("Images", [])]
            ),
            booking_conditions=dto.get("BookingConditions", [])
        )

class Paperflies(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies'

    @staticmethod
    def parse(dto: Dict) -> Hotel:
        return Hotel(
            id=dto['hotel_id'],
            destination_id=dto['destination_id'],
            name=dto['hotel_name'],
            description=dto['details'],
            location=Location(
                lat=None,
                lng=None,
                address=dto.get('location', {}).get('address', ''),
                city=None,
                country=dto.get('location', {}).get('country', '')
            ),
            amenities=Amenities(
                general=dto['amenities']['general'],
                room=dto['amenities']['room']
            ),
            images=Images(
                rooms=[
                    Image(link=img['link'], description=img['caption'])
                    for img in dto.get('images', {}).get('rooms', [])
                ],
                site=[
                    Image(link=img['link'], description=img['caption'])
                    for img in dto.get('images', {}).get('site', [])
                ], 
                amenities=[
                    Image(link=img['link'], description=img['caption'])
                    for img in dto.get('images', {}).get('amenities', [])
                ]
            ),
            booking_conditions=dto['booking_conditions']
        )

class Patagonia(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia'

    @staticmethod
    def parse(dto: Dict) -> Hotel:
        return Hotel(
            id = dto['id'],
            destination_id = dto['destination'],
            name = dto['name'].strip(),
            description = (dto.get("info") or "").strip(),  
            location=Location(
                lat=dto.get("lat", None),
                lng=dto.get("lng", None),
                address = (dto.get("address") or "").strip(),
                city=dto.get("city", ""),
                country=dto.get("country", "")
            ),
            amenities=Amenities(
                general=dto.get("General", []),  # General amenities are not explicitly listed
                room=dto.get("amenities", [])  # Use the 'amenities' field for room amenities
            ),
            images=Images(
                rooms=[
                    Image(link=img['url'], description=img['description'])
                    for img in dto.get('images', {}).get('rooms', [])
                ],
                site=[
                    Image(link=img['url'], description=img['description'])
                    for img in dto.get('images', {}).get('site', [])
                ], 
                amenities=[
                    Image(link=img['url'], description=img['description'])
                    for img in dto.get('images', {}).get('amenities', [])
                ]
            ),
            booking_conditions=[]  # Booking conditions are not provided; set to an empty list
        )



class HotelsService:
    def __init__(self):
        self.hotels = {}

    @staticmethod
    def normalize_amenity(amenity: str) -> str:
        """
        Normalize an amenity by:
        - Converting to lowercase
        - Converting camelCase to space-separated
        - Stripping extra spaces
        """
        # Convert camelCase or PascalCase to space-separated words
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', amenity)
        # Convert to lowercase and remove extra spaces
        return ' '.join(spaced.lower().split())

    @staticmethod
    def merge_amenities(existing: List[str], new: List[str]) -> List[str]:
        """
        Merges two lists of amenities with case-insensitive and spacing-normalized deduplication.
        """
        existing = existing or []  
        existing = [HotelsService.normalize_amenity(amenity) for amenity in existing]
        
        new = new or []
        new = [HotelsService.normalize_amenity(amenity) for amenity in new]

        # Normalize amenities and deduplicate
        normalized = {HotelsService.normalize_amenity(amenity): amenity for amenity in existing + new}
        return list(normalized.values())

    def merge_and_save(self, hotel_list: List[Hotel]):
        for hotel in hotel_list:
            if hotel.id not in self.hotels:
                # Initialize hotel if it's the first time seeing it
                self.hotels[hotel.id] = hotel
            else:
                # Merge the data for the existing hotel
                existing = self.hotels[hotel.id]

                # Merge amenities
                existing.amenities.general = self.merge_amenities(existing.amenities.general, hotel.amenities.general)
                existing.amenities.room = self.merge_amenities(existing.amenities.room, hotel.amenities.room)

                # Merge other attributes (you can expand this as needed)
                existing.description = existing.description or hotel.description
                existing.location = existing.location or hotel.location
                existing.images.rooms = list({img.link: img for img in (existing.images.rooms + hotel.images.rooms)}.values())
                existing.images.site = list({img.link: img for img in (existing.images.site + hotel.images.site)}.values())
                existing.images.amenities = list({img.link: img for img in (existing.images.amenities + hotel.images.amenities)}.values())
                existing.booking_conditions = list(set(existing.booking_conditions + hotel.booking_conditions))

    def find(self, hotel_ids: List[str], destination_ids: List[str]) -> List[Hotel]:
        # If no hotel_ids or destination_ids are provided, return all hotels
        if not hotel_ids or not destination_ids:
            return list(self.hotels.values())
        result = []
        for hotel in self.hotels.values():
            if (hotel.id in hotel_ids) and (str(hotel.destination_id) in destination_ids):
                result.append(hotel)
        return result

def fetch_hotels(hotel_ids: str, destination_ids: str) -> str:
    # Parse input arguments
    hotel_ids = hotel_ids.split(',') if hotel_ids != 'none' else None
    destination_ids = destination_ids.split(',') if destination_ids != 'none' else None

    # Initialize suppliers
    suppliers = [Acme(), Paperflies(), Patagonia()]

    # Fetch data from suppliers
    all_supplier_data = []
    for supplier in suppliers:
        all_supplier_data.extend(supplier.fetch())

    # Merge data
    svc = HotelsService()
    svc.merge_and_save(all_supplier_data)

    # Filter data
    filtered_hotels = svc.find(hotel_ids, destination_ids)

    # Convert to JSON
    return json.dumps([asdict(hotel) for hotel in filtered_hotels], indent=4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hotel_ids", type=str, help="Hotel IDs (comma-separated or 'none')")
    parser.add_argument("destination_ids", type=str, help="Destination IDs (comma-separated or 'none')")
    args = parser.parse_args()

    result = fetch_hotels(args.hotel_ids, args.destination_ids)
    print(result)

if __name__ == "__main__":
    main()

from dataclasses import dataclass, asdict
import json
import argparse
import requests
import re
import logging
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


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("hotel-data-fetch.log"),
        logging.StreamHandler()
    ]
)

class BaseSupplier:
    @staticmethod
    def endpoint():
        """URL to fetch supplier data"""

    @staticmethod
    def parse(obj: Dict) -> Hotel:
        """Parse supplier-provided data into Hotel object"""

    def fetch(self) -> List[Hotel]:
        url = self.endpoint()
        try:
            logging.info(f"Fetching data from {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()
            logging.info(f"Received {len(data)} records from {url}")
            return [self.parse(dto) for dto in data]
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP error from {url}: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error from {url}: {str(e)}")
            return []
        
class SupplierFactory:
    _suppliers = []

    @staticmethod
    def register_supplier(supplier_class):
        """Registers a supplier class."""
        SupplierFactory._suppliers.append(supplier_class)

    @staticmethod
    def get_suppliers():
        """Returns instances of all registered suppliers."""
        return [supplier() for supplier in SupplierFactory._suppliers]


class Acme(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme'

    @staticmethod
    def parse(dto: Dict) -> Hotel:
        return Hotel(
            id = dto['Id'],
            destination_id = dto['DestinationId'],
            name = (dto.get('Name') or '').strip(),
            location = Location(
                lat = dto.get('Latitude', None),
                lng = dto.get('Longitude', None),
                address = (dto.get('Address') or "").strip(),
                city = (dto.get('City') or "").strip(),
                country = (dto.get('Country') or '').strip()
            ),
            description = (dto.get('Description') or '').strip(),
            amenities = Amenities(
                general = dto.get('Facilities', []),
                room = dto.get('RoomFacilities', [])
            ),
            images = Images(
                rooms = [Image(link=img['link'], description=img['description']) for img in dto.get("Images", [])],
                site = [Image(link=img['link'], description=img['description']) for img in dto.get("Images", [])],
                amenities = [Image(link=img['link'], description=img['description']) for img in dto.get("Images", [])]
            ),
            booking_conditions = dto.get("BookingConditions", [])
        )

SupplierFactory.register_supplier(Acme)

class Paperflies(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies'

    @staticmethod
    def parse(dto: Dict) -> Hotel:
        return Hotel(
            id = dto['hotel_id'],
            destination_id = dto['destination_id'],
            name = (dto.get('hotel_name') or '').strip(),
            description = (dto.get('details') or '').strip(),
            location = Location(
                lat = dto.get('location', {}).get('lat', None),
                lng = dto.get('location', {}).get('lng', None),
                address = (dto.get('location', {}).get('address', '') or '').strip(),
                city = (dto.get('location', {}).get('city', '') or '').strip(),
                country = (dto.get('location', {}).get('country', '') or '').strip()
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
    
SupplierFactory.register_supplier(Paperflies)

class Patagonia(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia'

    @staticmethod
    def parse(dto: Dict) -> Hotel:
        return Hotel(
            id = dto['id'],
            destination_id = dto['destination'],
            name = (dto.get('name') or '').strip(),
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
            booking_conditions=dto.get("booking_conditions", [])
        )

SupplierFactory.register_supplier(Patagonia)


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
        if amenity.strip().lower() == 'wifi':
            return 'wifi'
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

        res = set(existing + new)
        return list(res)
    
    @staticmethod
    def merge_location(existing: Location, new: Location) -> Location:
        """
        Merge two Location objects, with preference for existing data.
        Specially for the address, .
        """
        lat = existing.lat or new.lat
        lng = existing.lng or new.lng
        existing_address = existing.address or ''
        new_address = new.address or ''
        city = existing.city or new.city
        if len(existing.country) > len(new.country):
            country = existing.country
        else:
            country = new.country

        existing_address_list = existing_address.split(', ')
        new_address_list = new_address.split(', ')
        
        if existing_address:
            address = existing_address
            for item in new_address_list:
                if item and item not in existing_address_list:
                    address += ', ' + item
        else:
            address = new_address

        return Location(lat=lat, lng=lng, address=address, city=city, country=country)


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
                existing.location = self.merge_location(existing.location, hotel.location)
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
    suppliers = SupplierFactory.get_suppliers()

    # Fetch data from suppliers
    all_supplier_data = []
    for supplier in suppliers:
        try:
            all_supplier_data.extend(supplier.fetch())
        except Exception as e:
            logging.error(f"Error fetching data from supplier {supplier.__class__.__name__}: {str(e)}")

    # Merge data
    svc = HotelsService()
    svc.merge_and_save(all_supplier_data)

    # Filter data
    filtered_hotels = svc.find(hotel_ids, destination_ids)
    logging.info(f"Found {len(filtered_hotels)} hotels matching the criteria")

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

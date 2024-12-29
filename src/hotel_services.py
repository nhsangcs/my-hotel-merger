from typing import List
import json
import re
import logging
from dataclasses import asdict
from .data_classes import Hotel, Location
from .suppliers import SupplierFactory


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
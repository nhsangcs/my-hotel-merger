from .base_supplier import BaseSupplier
from .data_classes import Hotel, Location, Amenities, Images, Image
from typing import Dict

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


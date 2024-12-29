from src.suppliers import SupplierFactory, Acme, Paperflies, Patagonia
import argparse
import logging
from src.hotel_services import fetch_hotels

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("hotel-data-fetch.log"),
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hotel_ids", type=str, help="Hotel IDs (comma-separated or 'none')")
    parser.add_argument("destination_ids", type=str, help="Destination IDs (comma-separated or 'none')")
    args = parser.parse_args()
    SUPPLIERS = [Acme, Paperflies, Patagonia]
    for supplier in SUPPLIERS:
        SupplierFactory.register_supplier(supplier)

    result = fetch_hotels(args.hotel_ids, args.destination_ids)
    print(result)

if __name__ == "__main__":
    main()

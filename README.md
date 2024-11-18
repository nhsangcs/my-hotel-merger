# My-Hotel-Merger
A Python-based Command Line Interface (CLI) tool for fetching, merging, and returning hotel data from multiple suppliers in a standardized JSON format. The tool supports filtering by hotel IDs and destination IDs.

## Features
- Fetches hotel data from multiple suppliers via APIs.
- Cleans and standardizes hotel attributes (e.g., amenities, images, descriptions).
- Merges hotel data across suppliers with conflict resolution for duplicate or inconsistent attributes.
- Filters results by hotel_ids and destination_ids.
- Outputs data in JSON format.

## Requirements
- Python 3.7+
- Virtualenv (optional but recommended)

## Installation
1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/nhsangcs/my-hotel-merger.git
```

2. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
Run the CLI tool with the desired arguments:
```bash
python my_hotel_merger.py <hotel_ids> <destination_ids>
```

Example:
```bash
python hotel_merger.py hotel_id_1,hotel_id_2 destination_id_1,destination_id_2
```

Note: if no hotel_id or destination_id is provided in the input, all hotels will be returned.

Alternatively, use the `runner` script:
```bash
bash runner <hotel_ids> <destination_ids>
```



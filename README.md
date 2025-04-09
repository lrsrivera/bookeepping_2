# Bookkeeping System

A Python-based system for processing and aggregating order data from XLSX files.

## Features

- Import XLSX files containing order data
- Process and aggregate orders by date
- Merge orders under 500 threshold
- Generate formatted output reports

## Project Structure

```
bookkeeping_system/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── file_processor.py    # Handles XLSX file reading and processing
│   ├── order_processor.py   # Contains order processing logic
│   ├── data_aggregator.py   # Handles data aggregation by date
│   └── output_generator.py  # Generates final output
├── tests/                   # Unit tests
├── requirements.txt         # Project dependencies
└── README.md               # Project documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your XLSX file in the appropriate directory
2. Run the main script:
```bash
python src/main.py
```

## Input File Format

The system expects an XLSX file with the following columns:
- ID Order (Column A)
- Paid Time (Column K)
- Variation Name (Column O)
- Quantity (Column R)
- Grand Total (Column AN)
- Username (Column AP) 
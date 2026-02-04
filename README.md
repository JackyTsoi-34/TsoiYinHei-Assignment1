# Data Cleaning and Validation Pipeline

## Overview
This project implements a robust data cleaning and validation pipeline for processing raw scraped web data. It transforms messy, inconsistent data into clean, structured output while providing comprehensive quality metrics.

## Features

### Data Cleaning (`cleaner.py`)
- **Whitespace & HTML Cleanup**: Removes extra spaces, tabs, newlines, and HTML tags/entities
- **Text Normalization**: Handles UTF-8 encoding and removes control characters  
- **Date Standardization**: Converts various date formats to ISO format (YYYY-MM-DD)
- **Special Character Handling**: Normalizes smart quotes, dashes, and other special characters

### Data Validation (`validator.py`)
- **Required Field Checks**: Ensures title, content, and URL are present and non-empty
- **URL Format Validation**: Verifies proper URL structure with scheme and domain
- **Content Length Validation**: Enforces minimum content length (default: 50 characters)
- **Comprehensive Error Reporting**: Flags invalid records with specific reasons

### Quality Reporting
- Total records processed with valid/invalid counts
- Field completeness percentages with visual progress bars
- Common validation failure categories
- Detailed error listings for each invalid record

## Project Structure
```
A1/
├── cleaner.py           # Data cleaning implementation
├── validator.py         # Validation rules and checks
├── pipeline.py          # Main pipeline orchestrator
├── sample_data.json     # Sample input data (11 records)
├── cleaned_output.json  # Cleaned output data
├── quality_report.txt   # Generated quality metrics
├── README.md           # This file
└── prompt-log.md       # AI-assisted development log
```

## Usage

### Running the Pipeline
```bash
python pipeline.py
```

The pipeline will:
1. Load data from `sample_data.json`
2. Clean all records using cleaning functions
3. Validate cleaned data against quality rules
4. Save results to `cleaned_output.json`
5. Generate quality report in `quality_report.txt`

### Using Individual Modules

**Cleaning data:**
```python
from cleaner import DataCleaner

cleaner = DataCleaner()
cleaned_record = cleaner.clean_record(raw_record)
```

**Validating data:**
```python
from validator import DataValidator

validator = DataValidator(min_content_length=50)
validation_result = validator.validate_record(record)
```

## Sample Results

**Input Data**: 11 records with various quality issues
- HTML artifacts and extra whitespace
- Multiple date formats (ISO, US, European)
- Smart quotes and special characters
- Missing required fields
- Invalid URLs

**Output Metrics**:
- Valid Records: 7 (63.6%)
- Invalid Records: 4 (36.4%)
- Field Completeness: Content (90.9%), URL (90.9%), Title (81.8%), Author/Date (63.6%)

## Configuration

### Customizing Validation Rules
Edit the pipeline configuration in `pipeline.py`:
```python
MIN_CONTENT_LENGTH = 50  # Minimum content length in characters
```

### Adding Custom Cleaning Rules
Extend the `DataCleaner` class in `cleaner.py`:
```python
def custom_cleaning_function(self, text):
    # Your custom logic here
    return cleaned_text
```

## Dependencies
- Python 3.7+
- Standard library only (no external packages required)

## Author
Tsoi Yin Hei (3036074825)
Created for IIMT3688 Assignment 1 - Data Pipeline

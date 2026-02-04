"""
Data Cleaning and Validation Pipeline
Main script to process scraped data through cleaning and validation.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from cleaner import DataCleaner
from validator import DataValidator


class DataPipeline:
    """Main pipeline for data cleaning and validation."""
    
    def __init__(self, min_content_length: int = 50):
        """
        Initialize the pipeline.
        
        Args:
            min_content_length: Minimum content length for validation
        """
        self.cleaner = DataCleaner()
        self.validator = DataValidator(min_content_length=min_content_length)
        self.stats = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'field_completeness': {},
            'validation_failures': {}
        }
    
    def load_data(self, input_file: str) -> List[Dict[str, Any]]:
        """
        Load data from JSON file.
        
        Args:
            input_file: Path to input JSON file
            
        Returns:
            List of data records
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data)} records from {input_file}")
            return data
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return []
    
    def save_data(self, data: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Save data to JSON file.
        
        Args:
            data: List of data records
            output_file: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(data)} records to {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving data: {e}")
            return False
    
    def calculate_field_completeness(self, records: List[Dict[str, Any]], 
                                    cleaned_records: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate completeness percentage for each field.
        
        Args:
            records: Original data records
            cleaned_records: Cleaned data records
            
        Returns:
            Dictionary with field completeness percentages
        """
        if not cleaned_records:
            return {}
        
        total = len(cleaned_records)
        fields = ['title', 'content', 'url', 'date', 'author']
        completeness = {}
        
        for field in fields:
            non_empty = sum(1 for record in cleaned_records 
                          if field in record and record[field] and str(record[field]).strip())
            completeness[field] = (non_empty / total) * 100
        
        return completeness
    
    def collect_validation_failures(self, validation_results: Dict[str, Any]) -> Dict[str, int]:
        """
        Collect and count common validation failures.
        
        Args:
            validation_results: Validation results from validator
            
        Returns:
            Dictionary with failure counts
        """
        failures = {}
        
        for record_result in validation_results['records']:
            if not record_result['is_valid']:
                for error in record_result['errors']:
                    # Categorize errors
                    if 'Missing required field' in error:
                        category = 'Missing Required Field'
                    elif 'empty' in error.lower():
                        category = 'Empty Field'
                    elif 'URL' in error:
                        category = 'Invalid URL'
                    elif 'Content too short' in error:
                        category = 'Content Too Short'
                    elif 'Title' in error:
                        category = 'Invalid Title'
                    else:
                        category = 'Other'
                    
                    failures[category] = failures.get(category, 0) + 1
        
        return failures
    
    def generate_quality_report(self, original_data: List[Dict[str, Any]], 
                               cleaned_data: List[Dict[str, Any]], 
                               validation_results: Dict[str, Any],
                               output_file: str) -> bool:
        """
        Generate quality metrics report.
        
        Args:
            original_data: Original input data
            cleaned_data: Cleaned data
            validation_results: Validation results
            output_file: Path to output report file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("DATA QUALITY REPORT\n")
                f.write("=" * 70 + "\n\n")
                
                # Timestamp
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Overview
                f.write("OVERVIEW\n")
                f.write("-" * 70 + "\n")
                f.write(f"Total Records Processed: {validation_results['total_records']}\n")
                f.write(f"Valid Records: {validation_results['valid_records']}\n")
                f.write(f"Invalid Records: {validation_results['invalid_records']}\n")
                
                if validation_results['total_records'] > 0:
                    valid_pct = (validation_results['valid_records'] / 
                               validation_results['total_records']) * 100
                    f.write(f"Validation Success Rate: {valid_pct:.1f}%\n")
                f.write("\n")
                
                # Field Completeness
                f.write("FIELD COMPLETENESS\n")
                f.write("-" * 70 + "\n")
                completeness = self.calculate_field_completeness(original_data, cleaned_data)
                for field, pct in sorted(completeness.items()):
                    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                    f.write(f"{field:15s} {bar} {pct:5.1f}%\n")
                f.write("\n")
                
                # Common Validation Failures
                f.write("COMMON VALIDATION FAILURES\n")
                f.write("-" * 70 + "\n")
                failures = self.collect_validation_failures(validation_results)
                if failures:
                    for category, count in sorted(failures.items(), 
                                                 key=lambda x: x[1], reverse=True):
                        f.write(f"{category:30s} {count:3d} occurrences\n")
                else:
                    f.write("No validation failures found!\n")
                f.write("\n")
                
                # Detailed Invalid Records
                if validation_results['invalid_records'] > 0:
                    f.write("DETAILED INVALID RECORDS\n")
                    f.write("-" * 70 + "\n")
                    for record_result in validation_results['records']:
                        if not record_result['is_valid']:
                            f.write(f"\nRecord #{record_result['record_index'] + 1}:\n")
                            for error in record_result['errors']:
                                f.write(f"  ✗ {error}\n")
                            if record_result['warnings']:
                                for warning in record_result['warnings']:
                                    f.write(f"  ⚠ {warning}\n")
                    f.write("\n")
                
                # Records with Warnings
                warnings_count = sum(1 for r in validation_results['records'] 
                                   if r['is_valid'] and r['warnings'])
                if warnings_count > 0:
                    f.write("VALID RECORDS WITH WARNINGS\n")
                    f.write("-" * 70 + "\n")
                    f.write(f"Total: {warnings_count} records\n\n")
                    for record_result in validation_results['records']:
                        if record_result['is_valid'] and record_result['warnings']:
                            f.write(f"Record #{record_result['record_index'] + 1}:\n")
                            for warning in record_result['warnings']:
                                f.write(f"  ⚠ {warning}\n")
                    f.write("\n")
                
                # Summary
                f.write("=" * 70 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 70 + "\n")
                if validation_results['valid_records'] == validation_results['total_records']:
                    f.write("✓ All records passed validation!\n")
                elif validation_results['valid_records'] > 0:
                    f.write(f"✓ {validation_results['valid_records']} records are ready for use\n")
                    f.write(f"✗ {validation_results['invalid_records']} records need attention\n")
                else:
                    f.write("✗ No valid records found. Please review the data quality.\n")
                
            print(f"✓ Quality report saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error generating report: {e}")
            return False
    
    def run(self, input_file: str, output_file: str, report_file: str) -> bool:
        """
        Run the complete pipeline.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file
            report_file: Path to quality report file
            
        Returns:
            True if successful, False otherwise
        """
        print("\n" + "=" * 70)
        print("DATA CLEANING AND VALIDATION PIPELINE")
        print("=" * 70 + "\n")
        
        # Step 1: Load data
        print("Step 1: Loading data...")
        raw_data = self.load_data(input_file)
        if not raw_data:
            return False
        
        # Step 2: Clean data
        print("\nStep 2: Cleaning data...")
        cleaned_data = self.cleaner.clean_dataset(raw_data)
        print(f"✓ Cleaned {len(cleaned_data)} records")
        
        # Step 3: Validate data
        print("\nStep 3: Validating data...")
        validation_results = self.validator.validate_dataset(cleaned_data)
        print(f"✓ Validated {validation_results['total_records']} records")
        print(f"  - Valid: {validation_results['valid_records']}")
        print(f"  - Invalid: {validation_results['invalid_records']}")
        
        # Step 4: Save cleaned data
        print("\nStep 4: Saving cleaned data...")
        # Save all cleaned records
        if not self.save_data(cleaned_data, output_file):
            return False
        
        # Step 5: Generate quality report
        print("\nStep 5: Generating quality report...")
        if not self.generate_quality_report(raw_data, cleaned_data, 
                                          validation_results, report_file):
            return False
        
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70 + "\n")
        
        return True


def main():
    """Main entry point."""
    # Configuration
    INPUT_FILE = "sample_data.json"
    OUTPUT_FILE = "cleaned_output.json"
    REPORT_FILE = "quality_report.txt"
    MIN_CONTENT_LENGTH = 50
    
    # Initialize and run pipeline
    pipeline = DataPipeline(min_content_length=MIN_CONTENT_LENGTH)
    success = pipeline.run(INPUT_FILE, OUTPUT_FILE, REPORT_FILE)
    
    if success:
        print("✓ All outputs generated successfully!")
        print(f"  - Cleaned data: {OUTPUT_FILE}")
        print(f"  - Quality report: {REPORT_FILE}")
    else:
        print("✗ Pipeline encountered errors")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

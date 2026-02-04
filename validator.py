"""
Data Validation Module
Implements validation rules to ensure data quality.
"""

import re
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse


class DataValidator:
    """Handles data validation operations for cleaned content."""
    
    def __init__(self, min_content_length: int = 50):
        """
        Initialize the DataValidator.
        
        Args:
            min_content_length: Minimum content length in characters
        """
        self.min_content_length = min_content_length
        self.required_fields = ['title', 'content', 'url']
    
    def validate_required_fields(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if all required fields are present and not empty.
        
        Args:
            record: Data record to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        for field in self.required_fields:
            if field not in record:
                errors.append(f"Missing required field: {field}")
            elif not record[field] or str(record[field]).strip() == "":
                errors.append(f"Required field is empty: {field}")
        
        return len(errors) == 0, errors
    
    def validate_url(self, url: str) -> Tuple[bool, List[str]]:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if not url or str(url).strip() == "":
            errors.append("URL is empty")
            return False, errors
        
        try:
            result = urlparse(url)
            
            # Check if scheme is present and valid
            if not result.scheme:
                errors.append("URL missing scheme (http/https)")
            elif result.scheme not in ['http', 'https']:
                errors.append(f"Invalid URL scheme: {result.scheme}")
            
            # Check if netloc (domain) is present
            if not result.netloc:
                errors.append("URL missing domain")
            
            # Basic domain validation
            if result.netloc and not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', result.netloc):
                errors.append(f"Invalid URL domain format: {result.netloc}")
        
        except Exception as e:
            errors.append(f"URL parsing error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def validate_content_length(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check if content meets minimum length requirement.
        
        Args:
            content: Content string to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if not content:
            errors.append("Content is empty")
            return False, errors
        
        content_length = len(str(content).strip())
        
        if content_length < self.min_content_length:
            errors.append(
                f"Content too short: {content_length} characters "
                f"(minimum: {self.min_content_length})"
            )
        
        return len(errors) == 0, errors
    
    def validate_title(self, title: str) -> Tuple[bool, List[str]]:
        """
        Validate title field.
        
        Args:
            title: Title string to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if not title or str(title).strip() == "":
            errors.append("Title is empty")
            return False, errors
        
        title = str(title).strip()
        
        # Check minimum length
        if len(title) < 3:
            errors.append(f"Title too short: {len(title)} characters (minimum: 3)")
        
        # Check maximum length
        if len(title) > 500:
            errors.append(f"Title too long: {len(title)} characters (maximum: 500)")
        
        return len(errors) == 0, errors
    
    def validate_date(self, date: str) -> Tuple[bool, List[str]]:
        """
        Validate date field (should be in ISO format after cleaning).
        
        Args:
            date: Date string to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Date is optional, so empty is acceptable
        if not date or str(date).strip() == "":
            return True, []
        
        # Check ISO format (YYYY-MM-DD)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(date)):
            errors.append(f"Date not in ISO format (YYYY-MM-DD): {date}")
        
        return len(errors) == 0, errors
    
    def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an entire data record.
        
        Args:
            record: Data record to validate
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        fields_valid, field_errors = self.validate_required_fields(record)
        if not fields_valid:
            validation_result['is_valid'] = False
            validation_result['errors'].extend(field_errors)
            # If required fields are missing, skip other validations
            return validation_result
        
        # Validate title
        title_valid, title_errors = self.validate_title(record.get('title', ''))
        if not title_valid:
            validation_result['is_valid'] = False
            validation_result['errors'].extend(title_errors)
        
        # Validate URL
        url_valid, url_errors = self.validate_url(record.get('url', ''))
        if not url_valid:
            validation_result['is_valid'] = False
            validation_result['errors'].extend(url_errors)
        
        # Validate content length
        content_valid, content_errors = self.validate_content_length(record.get('content', ''))
        if not content_valid:
            validation_result['is_valid'] = False
            validation_result['errors'].extend(content_errors)
        
        # Validate date (if present)
        if 'date' in record and record['date']:
            date_valid, date_errors = self.validate_date(record.get('date', ''))
            if not date_valid:
                validation_result['warnings'].extend(date_errors)
        
        # Check for author field (optional but recommended)
        if 'author' not in record or not record.get('author', '').strip():
            validation_result['warnings'].append("Author field is missing or empty")
        
        return validation_result
    
    def validate_dataset(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple records and generate summary statistics.
        
        Args:
            records: List of data records to validate
            
        Returns:
            Dictionary containing validation summary
        """
        results = {
            'total_records': len(records),
            'valid_records': 0,
            'invalid_records': 0,
            'records': []
        }
        
        for idx, record in enumerate(records):
            validation = self.validate_record(record)
            
            record_result = {
                'record_index': idx,
                'is_valid': validation['is_valid'],
                'errors': validation['errors'],
                'warnings': validation['warnings']
            }
            
            if validation['is_valid']:
                results['valid_records'] += 1
            else:
                results['invalid_records'] += 1
            
            results['records'].append(record_result)
        
        return results


if __name__ == "__main__":
    # Example usage
    validator = DataValidator(min_content_length=50)
    
    # Test valid record
    valid_record = {
        "title": "Test Article",
        "content": "This is a test article with sufficient content to meet the minimum length requirement.",
        "url": "https://example.com/article",
        "date": "2024-01-15",
        "author": "John Doe"
    }
    
    # Test invalid record
    invalid_record = {
        "title": "Short",
        "content": "Too short",
        "url": "not-a-valid-url"
    }
    
    print("Valid Record Validation:")
    print(validator.validate_record(valid_record))
    
    print("\nInvalid Record Validation:")
    print(validator.validate_record(invalid_record))

"""
Data Cleaning Module
Implements functions to clean and normalize scraped data.
"""

import re
import html
from datetime import datetime
from typing import Dict, Any, Optional


class DataCleaner:
    """Handles data cleaning operations for scraped content."""
    
    def __init__(self):
        """Initialize the DataCleaner."""
        pass
    
    def clean_text(self, text: Optional[str]) -> str:
        """
        Remove extra whitespace and HTML artifacts from text.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        if text is None or text == "":
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Decode HTML entities (e.g., &amp; -> &, &lt; -> <)
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace (multiple spaces, tabs, newlines)
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading and trailing whitespace
        text = text.strip()
        
        return text
    
    def normalize_encoding(self, text: Optional[str]) -> str:
        """
        Normalize text encoding to UTF-8.
        
        Args:
            text: Input text string
            
        Returns:
            Normalized text string
        """
        if text is None or text == "":
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Ensure proper UTF-8 encoding
        try:
            # Encode to UTF-8 and decode back to handle any encoding issues
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception:
            # If encoding fails, return as-is
            pass
        
        # Remove null bytes and other control characters
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def standardize_date(self, date_str: Optional[str]) -> str:
        """
        Convert various date formats to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Input date string in various formats
            
        Returns:
            ISO formatted date string or empty string if parsing fails
        """
        if date_str is None or date_str == "":
            return ""
        
        # Convert to string and clean
        date_str = str(date_str).strip()
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%d',           # 2024-01-15
            '%Y/%m/%d',           # 2024/01/15
            '%d-%m-%Y',           # 15-01-2024
            '%d/%m/%Y',           # 15/01/2024
            '%m-%d-%Y',           # 01-15-2024
            '%m/%d/%Y',           # 01/15/2024
            '%B %d, %Y',          # January 15, 2024
            '%b %d, %Y',          # Jan 15, 2024
            '%d %B %Y',           # 15 January 2024
            '%d %b %Y',           # 15 Jan 2024
            '%Y-%m-%dT%H:%M:%S',  # ISO 8601 with time
            '%Y-%m-%d %H:%M:%S',  # YYYY-MM-DD HH:MM:SS
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return empty string
        return ""
    
    def handle_special_characters(self, text: Optional[str]) -> str:
        """
        Handle special characters appropriately.
        
        Args:
            text: Input text string
            
        Returns:
            Text with properly handled special characters
        """
        if text is None or text == "":
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Replace common problematic characters
        replacements = {
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2026': '...',  # Ellipsis
            '\u00a0': ' ',  # Non-breaking space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def clean_url(self, url: Optional[str]) -> str:
        """
        Clean and normalize URL.
        
        Args:
            url: Input URL string
            
        Returns:
            Cleaned URL string
        """
        if url is None or url == "":
            return ""
        
        # Convert to string and strip whitespace
        url = str(url).strip()
        
        # Remove any whitespace within the URL
        url = re.sub(r'\s+', '', url)
        
        return url
    
    def clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean an entire data record.
        
        Args:
            record: Dictionary containing scraped data
            
        Returns:
            Dictionary with cleaned data
        """
        cleaned = {}
        
        # Clean title
        if 'title' in record:
            cleaned['title'] = self.handle_special_characters(
                self.normalize_encoding(
                    self.clean_text(record['title'])
                )
            )
        
        # Clean content
        if 'content' in record:
            cleaned['content'] = self.handle_special_characters(
                self.normalize_encoding(
                    self.clean_text(record['content'])
                )
            )
        
        # Clean URL
        if 'url' in record:
            cleaned['url'] = self.clean_url(record['url'])
        
        # Clean date
        if 'date' in record:
            cleaned['date'] = self.standardize_date(record['date'])
        
        # Clean author
        if 'author' in record:
            cleaned['author'] = self.handle_special_characters(
                self.normalize_encoding(
                    self.clean_text(record['author'])
                )
            )
        
        # Copy other fields as-is
        for key, value in record.items():
            if key not in cleaned:
                cleaned[key] = value
        
        return cleaned
    
    def clean_dataset(self, records: list) -> list:
        """
        Clean multiple records.
        
        Args:
            records: List of dictionaries containing scraped data
            
        Returns:
            List of cleaned data dictionaries
        """
        return [self.clean_record(record) for record in records]


if __name__ == "__main__":
    # Example usage
    cleaner = DataCleaner()
    
    # Test data
    test_record = {
        "title": "  Test Article   with   Extra    Spaces  ",
        "content": "<p>This has &lt;HTML&gt; entities &amp; tags</p>",
        "url": "  https://example.com/article  ",
        "date": "01/15/2024",
        "author": "John\u2019s Doe"
    }
    
    cleaned = cleaner.clean_record(test_record)
    print("Original:", test_record)
    print("\nCleaned:", cleaned)

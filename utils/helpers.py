"""
Helper utilities for LinkedIn Job Matcher.
"""

import re
import unicodedata
import logging
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime
import html
import json
import uuid

logger = logging.getLogger(__name__)


def format_date(date_obj: Union[datetime, str], format_str: str = "%d/%m/%Y") -> str:
    """
    Format a date object or string as a formatted string.

    Args:
        date_obj: Date object or string to format
        format_str: Format string for output

    Returns:
        Formatted date string
    """
    if isinstance(date_obj, str):
        try:
            # Try to parse the string as a date
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return date_obj

    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)

    return str(date_obj)


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to convert

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    text = text.lower()

    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

    # Replace non-word characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text).strip()

    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)

    return text


def clean_html(html_text: str) -> str:
    """
    Remove HTML tags and decode HTML entities.

    Args:
        html_text: HTML text to clean

    Returns:
        Cleaned text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace, converting to lowercase, etc.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing whitespace
    text = text.strip()

    return text


def extract_keywords(text: str, min_length: int = 3, max_words: int = 50) -> List[str]:
    """
    Extract important keywords from text.

    Args:
        text: Text to extract keywords from
        min_length: Minimum length of keywords
        max_words: Maximum number of keywords to return

    Returns:
        List of keywords
    """
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        # Tokenize the text
        tokens = word_tokenize(text.lower())

        # Remove stopwords and short words
        stop_words = set(stopwords.words('portuguese') + stopwords.words('english'))
        keywords = [word for word in tokens if word not in stop_words
                    and len(word) >= min_length
                    and word.isalpha()]

        # Get word frequencies
        from collections import Counter
        word_freq = Counter(keywords)

        # Return most common keywords
        return [word for word, _ in word_freq.most_common(max_words)]
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        # Fallback to simple word extraction
        words = re.findall(r'\b\w{%d,}\b' % min_length, text.lower())
        return list(set(words))[:max_words]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add to truncated text

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    # Find the last space before max_length
    last_space = text[:max_length].rfind(' ')

    if last_space > 0:
        return text[:last_space] + suffix
    else:
        return text[:max_length] + suffix


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique ID.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID
    """
    unique_id = str(uuid.uuid4())

    if prefix:
        return f"{prefix}_{unique_id}"

    return unique_id


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested dictionaries
        sep: Separator for keys

    Returns:
        Flattened dictionary
    """
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (values will override dict1 on conflicts)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def remove_duplicates(items: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.

    Args:
        items: List with potential duplicates

    Returns:
        List with duplicates removed
    """
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.

    Args:
        text: Text to extract URLs from

    Returns:
        List of URLs
    """
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text.

    Args:
        text: Text to extract email addresses from

    Returns:
        List of email addresses
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """
    Extract phone numbers from text.

    Args:
        text: Text to extract phone numbers from

    Returns:
        List of phone numbers
    """
    # Pattern for Brazilian phone numbers
    phone_pattern = r'(?:\+55|0)?(?:(?:(?:\(?[1-9][0-9]\)?)?(?:\s|-|\.)?)?)(?:9\d|[2-9])\d{3}(?:\s|-|\.)?(?:\d{4})'

    # Find all matches
    matches = re.findall(phone_pattern, text)

    # Clean matches
    cleaned_numbers = []
    for match in matches:
        # Remove non-digit characters
        cleaned = re.sub(r'\D', '', match)

        # If the number doesn't start with +55 (Brazil), add it
        if not cleaned.startswith('55') and len(cleaned) >= 10:
            cleaned = '55' + cleaned

        cleaned_numbers.append(cleaned)

    return cleaned_numbers


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load a JSON string.

    Args:
        json_str: JSON string to load
        default: Default value to return on error

    Returns:
        Parsed JSON or default value on error
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Error decoding JSON: {str(e)}")
        return default


def format_currency(amount: Union[float, int], currency: str = 'BRL') -> str:
    """
    Format a currency amount.

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted currency string
    """
    import locale

    # Set locale based on currency
    currency_locales = {
        'BRL': 'pt_BR.UTF-8',
        'USD': 'en_US.UTF-8',
        'EUR': 'fr_FR.UTF-8',
        'GBP': 'en_GB.UTF-8'
    }

    try:
        locale.setlocale(locale.LC_ALL, currency_locales.get(currency, 'pt_BR.UTF-8'))
    except locale.Error:
        # Fallback to C locale if the requested locale is not available
        locale.setlocale(locale.LC_ALL, 'C')

    # Format the amount
    if currency == 'BRL':
        return locale.currency(amount, grouping=True, symbol=True)
    elif currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    elif currency == 'GBP':
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_number(number: Union[float, int], decimal_places: int = 2) -> str:
    """
    Format a number with thousands separator and decimal places.

    Args:
        number: Number to format
        decimal_places: Number of decimal places

    Returns:
        Formatted number string
    """
    import locale

    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        # Fallback to C locale if the requested locale is not available
        locale.setlocale(locale.LC_ALL, 'C')

    # Format the number
    format_str = f"%.{decimal_places}f"
    formatted = locale.format_string(format_str, number, grouping=True)

    return formatted


def extract_linkedin_id(url: str) -> Optional[str]:
    """
    Extract LinkedIn ID from a URL.

    Args:
        url: LinkedIn URL

    Returns:
        LinkedIn ID or None if not found
    """
    # Pattern for job URLs
    job_pattern = r'linkedin\.com/jobs/view/([a-zA-Z0-9-]+)'
    job_match = re.search(job_pattern, url)

    if job_match:
        return job_match.group(1)

    # Pattern for company jobs pages
    company_pattern = r'linkedin\.com/company/([a-zA-Z0-9-]+)/jobs'
    company_match = re.search(company_pattern, url)

    if company_match:
        return f"company_{company_match.group(1)}"

    # Pattern for profiles
    profile_pattern = r'linkedin\.com/in/([a-zA-Z0-9-]+)'
    profile_match = re.search(profile_pattern, url)

    if profile_match:
        return f"profile_{profile_match.group(1)}"

    return None
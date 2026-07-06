import re

def normalize_vendor_name(vendor_name: str) -> str:
    """Normalize vendor names for consistent matching"""
    if not vendor_name:
        return ""
    
    # Convert to lowercase
    normalized = vendor_name.lower()
    
    # Remove special characters but preserve spaces
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    # Common replacements
    replacements = {
        'aws services': 'aws',
        'amazon web services': 'aws',
        'microsoft o365': 'microsoft office 365',
        'ms office': 'microsoft office 365',
        'google workspace': 'google',
        'g suite': 'google',
    }
    
    for old, new in replacements.items():
        if old in normalized:
            normalized = new
            break
    
    return normalized

# Vendor category mapping
VENDOR_CATEGORIES = {
    'aws': 'Cloud Infrastructure',
    'azure': 'Cloud Infrastructure',
    'google cloud': 'Cloud Infrastructure',
    'slack': 'Communication',
    'microsoft teams': 'Communication',
    'zoom': 'Communication',
    'google meet': 'Communication',
    'jira': 'Project Management',
    'asana': 'Project Management',
    'trello': 'Project Management',
    'monday': 'Project Management',
    'salesforce': 'CRM',
    'hubspot': 'CRM',
    'adobe': 'Design Tools',
    'figma': 'Design Tools',
    'canva': 'Design Tools',
    'datadog': 'Monitoring',
    'new relic': 'Monitoring',
    'grafana': 'Monitoring',
    'splunk': 'Monitoring',
}

def categorize_vendor(normalized_name: str) -> str:
    """Categorize vendor based on normalized name"""
    for vendor_key, category in VENDOR_CATEGORIES.items():
        if vendor_key in normalized_name:
            return category
    return 'Other'

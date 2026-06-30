# Navigation page identifiers - used throughout the application
# These are lowercase, hyphenless identifiers for reliable routing

NAV_ITEMS = [
    'mission_control',
    'collections',
    'business',
    'intelligence',
    'system'
]

# Map display labels to page identifiers
NAV_LABELS = {
    'mission_control': 'Mission Control',
    'collections': 'Collections',
    'business': 'Business',
    'intelligence': 'Intelligence',
    'system': 'System',
}

# Sidebar button configuration: label -> page identifier
SIDEBAR_PAGES = [
    ('Mission Control', 'mission_control'),
    ('Collections', 'collections'),
    ('Business', 'business'),
    ('Intelligence', 'intelligence'),
    ('System', 'system'),
]

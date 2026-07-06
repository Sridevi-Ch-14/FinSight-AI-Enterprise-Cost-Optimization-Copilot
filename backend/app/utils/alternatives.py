ALTERNATIVE_RECOMMENDATIONS = {
    'zoom': {
        'alternatives': [
            {
                'name': 'Microsoft Teams',
                'feature_parity': 'Full video conferencing, screen sharing, recording, breakout rooms. Better integration if Office365 licensed.',
                'risk_level': 'Low',
                'typical_savings_percent': 30
            },
            {
                'name': 'Google Meet',
                'feature_parity': 'Enterprise video conferencing with recording and live streaming. Ideal if Google Workspace licensed.',
                'risk_level': 'Low',
                'typical_savings_percent': 40
            }
        ]
    },
    'slack': {
        'alternatives': [
            {
                'name': 'Microsoft Teams',
                'feature_parity': 'Chat, channels, file sharing, integrations, video calls. Included with Office365.',
                'risk_level': 'Medium',
                'typical_savings_percent': 100
            }
        ]
    },
    'jira': {
        'alternatives': [
            {
                'name': 'Azure DevOps',
                'feature_parity': 'Boards, backlogs, sprints, CI/CD pipelines. Better for Microsoft ecosystem.',
                'risk_level': 'Medium',
                'typical_savings_percent': 25
            },
            {
                'name': 'Linear',
                'feature_parity': 'Modern issue tracking, sprints, roadmaps. Faster and cleaner UI.',
                'risk_level': 'Medium',
                'typical_savings_percent': 35
            }
        ]
    },
    'datadog': {
        'alternatives': [
            {
                'name': 'Grafana Cloud',
                'feature_parity': 'Metrics, logs, traces, dashboards. Open-source based with enterprise support.',
                'risk_level': 'Low',
                'typical_savings_percent': 50
            },
            {
                'name': 'New Relic',
                'feature_parity': 'APM, infrastructure monitoring, logs. Competitive pricing.',
                'risk_level': 'Low',
                'typical_savings_percent': 30
            }
        ]
    },
    'adobe': {
        'alternatives': [
            {
                'name': 'Figma',
                'feature_parity': 'Design, prototyping, collaboration. Better for UI/UX teams.',
                'risk_level': 'Low',
                'typical_savings_percent': 60
            },
            {
                'name': 'Canva Pro',
                'feature_parity': 'Design templates, brand kits. Ideal for marketing teams.',
                'risk_level': 'Low',
                'typical_savings_percent': 70
            }
        ]
    },
    'salesforce': {
        'alternatives': [
            {
                'name': 'HubSpot',
                'feature_parity': 'CRM, sales pipeline, marketing automation. More user-friendly.',
                'risk_level': 'High',
                'typical_savings_percent': 40
            }
        ]
    }
}

# Benchmark pricing (cost per seat per month in INR)
BENCHMARK_PRICING = {
    'zoom': 1200,
    'slack': 550,
    'microsoft teams': 0,  # Included with Office365
    'jira': 600,
    'asana': 800,
    'salesforce': 5000,
    'adobe': 3500,
    'datadog': 1000,
    'aws': None,  # Usage-based
    'google meet': 0,  # Included with Workspace
}

def get_alternatives(normalized_vendor: str):
    """Get alternative recommendations for a vendor"""
    for vendor_key, data in ALTERNATIVE_RECOMMENDATIONS.items():
        if vendor_key in normalized_vendor:
            return data['alternatives']
    return []

def get_benchmark_price(normalized_vendor: str):
    """Get benchmark price for a vendor"""
    for vendor_key, price in BENCHMARK_PRICING.items():
        if vendor_key in normalized_vendor:
            return price
    return None

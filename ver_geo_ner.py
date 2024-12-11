!pip install folium
!pip install spacy
!pip install geopy
!pip install chardet

import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def verify_location(name):
    """Verify if a name is actually a location using geocoding"""
    try:
        geolocator = Nominatim(user_agent="location_verifier")
        location = geolocator.geocode(name, timeout=5)
        return location is not None
    except GeocoderTimedOut:
        return False

def analyze_text(file_path):
    """Analyze text with improved location detection"""
    print("Loading model...")
    nlp = spacy.load("el_core_news_md")
    
    # Common Greek location indicators
    location_indicators = {
        'πόλη', 'χωριό', 'νησί', 'όρος', 'βουνό', 'ποταμός', 
        'λίμνη', 'χώρα', 'πολιτεία', 'περιοχή', 'δήμος'
    }
    
    # Known non-locations (customize this list based on your needs)
    non_locations = {
        'necromantia', 'varathron', 'rotting christ', 'septicflesh',
        # Add other known band names, terms, etc.
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    doc = nlp(text)
    
    locations = []
    uncertain = []
    
    for ent in doc.ents:
        if ent.label_ in ['LOC', 'GPE']:
            name = ent.text.lower()
            
            # Skip if in known non-locations
            if name in non_locations:
                continue
                
            # Check if preceded by location indicator
            has_indicator = any(indicator in ent.sent.text.lower() 
                              for indicator in location_indicators)
                
            if has_indicator or verify_location(ent.text):
                locations.append({
                    'text': ent.text,
                    'context': ent.sent.text,
                    'verified': True
                })
            else:
                uncertain.append({
                    'text': ent.text,
                    'context': ent.sent.text,
                    'verified': False
                })
    
    # Print results
    print("\n=== Verified Locations ===")
    for loc in locations:
        print(f"\nLocation: {loc['text']}")
        print(f"Context: {loc['context']}")
        
    if uncertain:
        print("\n=== Uncertain Entities (May Not Be Locations) ===")
        for unc in uncertain:
            print(f"\nEntity: {unc['text']}")
            print(f"Context: {unc['context']}")
    
    return {
        'verified_locations': locations,
        'uncertain': uncertain
    }

# Example usage:
results = analyze_text('your_text.txt')

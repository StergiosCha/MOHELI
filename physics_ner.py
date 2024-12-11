# Install required packages
!pip install pyvis pandas networkx spacy geopy
!python -m spacy download el_core_news_md

import spacy
import networkx as nx
from pyvis.network import Network
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Geocoding verification function
def verify_location(name):
    """Verify if a name is actually a location using geocoding"""
    try:
        geolocator = Nominatim(user_agent="location_verifier")
        location = geolocator.geocode(name, timeout=5)
        return location is not None
    except GeocoderTimedOut:
        return False

def create_metal_network(file_path):
    """Create and visualize network of metal bands, locations, and related entities with certainty categorization"""
    # Load SpaCy model
    nlp = spacy.load("el_core_news_md")
    
    # Known Greek metal bands
    greek_metal_bands = {
        'rotting christ', 'necromantia', 'varathron', 'septicflesh', 
        'thou art lord', 'astarte', 'zemial', 'kawir', 'naer mataron',
        'mortify', 'nightfall', 'horror of sadist', 'dark nova'
    }
    
    # Read and process text
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    doc = nlp(text)
    
    # Create interactive network
    net = Network(notebook=True, height='750px', width='100%', bgcolor='#222222', 
                  font_color='white')
    
    # Track entities and connections
    connections = []
    entities = {}
    certain_entities = []
    uncertain_entities = []
    
    # Process each sentence
    for sent in doc.sents:
        sentence_entities = []
        
        # Find bands in sentence
        for band in greek_metal_bands:
            if band.lower() in sent.text.lower():
                sentence_entities.append(('BAND', band.title()))
                certain_entities.append((band.title(), 'BAND'))
        
        # Find named entities
        for ent in sent.ents:
            if ent.label_ in ['LOC', 'GPE', 'ORG', 'PERSON', 'DATE']:
                if ent.text.lower() not in greek_metal_bands:
                    # Verify location or categorize as uncertain
                    if ent.label_ in ['LOC', 'GPE'] and verify_location(ent.text):
                        sentence_entities.append((ent.label_, ent.text))
                        certain_entities.append((ent.text, ent.label_))
                    else:
                        uncertain_entities.append((ent.text, ent.label_))
                        sentence_entities.append((ent.label_, ent.text))
        
        # Create connections between entities in the same sentence
        for i, (type1, ent1) in enumerate(sentence_entities):
            for type2, ent2 in sentence_entities[i+1:]:
                connections.append((ent1, ent2, type1, type2, sent.text))
                entities[ent1] = type1
                entities[ent2] = type2
    
    # Add nodes with different colors per type
    colors = {
        'BAND': '#ff4444',      # Red for bands
        'LOC': '#44ff44',       # Green for locations
        'GPE': '#44ff44',       # Green for geo-political entities
        'ORG': '#4444ff',       # Blue for organizations
        'PERSON': '#ffff44',    # Yellow for people
        'DATE': '#ff44ff',      # Purple for dates
    }
    
    # Add nodes with distinction between certain and uncertain
    for entity, type_ in entities.items():
        color = colors.get(type_, '#ffffff')
        if (entity, type_) in uncertain_entities:
            color = '#ff9900'  # Orange for uncertain entities
        net.add_node(entity, 
                     label=entity,
                     color=color,
                     title=f"Type: {type_}, Certain: {entity not in [e[0] for e in uncertain_entities]}")
    
    # Add edges
    for ent1, ent2, type1, type2, context in connections:
        net.add_edge(ent1, ent2, title=context)
    
    # Generate and display the network
    output_path = file_path.rsplit('.', 1)[0] + '_network.html'
    net.write_html(output_path)
    
    # Create summary DataFrame
    summary = pd.DataFrame(connections, 
                           columns=['Entity 1', 'Entity 2', 'Type 1', 'Type 2', 'Context'])
    
    # Save summary to CSV
    csv_path = file_path.rsplit('.', 1)[0] + '_connections.csv'
    summary.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"\nNetwork visualization saved to: {output_path}")
    print(f"Connections summary saved to: {csv_path}")
    
    # Print summary of entities found
    print("\nCertain Entities:")
    for entity_type in set([e[1] for e in certain_entities]):
        type_entities = [e[0] for e in certain_entities if e[1] == entity_type]
        if type_entities:
            print(f"\n{entity_type}:")
            for entity in type_entities:
                print(f"  - {entity}")
    
    print("\nUncertain Entities:")
    for entity_type in set([e[1] for e in uncertain_entities]):
        type_entities = [e[0] for e in uncertain_entities if e[1] == entity_type]
        if type_entities:
            print(f"\n{entity_type}:")
            for entity in type_entities:
                print(f"  - {entity}")
    
    return {
        'network': net,
        'connections': summary,
        'certain_entities': certain_entities,
        'uncertain_entities': uncertain_entities,
        'output_path': output_path,
        'csv_path': csv_path
    }

# Example Usage
result = create_metal_network('vatsnies.txt')

from IPython.display import IFrame
IFrame(src=result['output_path'], width=1000, height=800)

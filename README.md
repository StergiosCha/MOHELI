# MOHELI
Some simple models and visualisations for Modern Greek Literature. It processes Greek text to detect and analyze relationships between Greek metal bands (custom list), locations, and other entities. It uses SpaCy for named entity recognition (NER) and Pyvis for an interactive physics-based network visualization. Entities such as bands, locations, organizations, people, and dates are identified and categorized as either "Certain" (predefined bands or verified locations) or "Uncertain" (ambiguous entities not verified or lacking clear context). Connections between entities are established based on their co-occurrence within sentences.

The output includes an HTML file for network visualization, where nodes represent entities (color-coded by type) and edges indicate relationships, along with a CSV file summarizing the connections and context. The project allows for the exploration of cultural and textual relationships, with potential applications in digital humanities and Greek literature analysis.

"""
Persona management for AI Agents.
Loads personas from cs5740-personas repository.
"""
from pathlib import Path
from typing import Dict, List, Tuple


# Persona definitions - mapping display names to file paths
# Using specific named personas from cs5740-personas
# Requirement: At least 3 types × at least 3 personas each = 9+ personas
PERSONAS: Dict[str, Dict[str, str]] = {
    # Default option - no persona
    "None - Default Agent": {
        "path": None,
        "category": "Default",
        "description": "Standard AI agent without persona customization"
    },
    
    # Type 1: QA Engineers - 3 personas
    "Qa Engineers: Jack": {
        "path": "cs5740-personas/personas/quality_testing/qa_engineers/Jack.md",
        "category": "Quality & Testing",
        "description": "QA Engineer focused on systematic testing"
    },
    "Qa Engineers: Alex-QA": {
        "path": "cs5740-personas/personas/quality_testing/qa_engineers/Alex-QA.md",
        "category": "Quality & Testing",
        "description": "QA Engineer with automation expertise"
    },
    "Qa Engineers: Bob": {
        "path": "cs5740-personas/personas/quality_testing/qa_engineers/Bob.md",
        "category": "Quality & Testing",
        "description": "QA Engineer with test planning focus"
    },
    
    # Type 2: Software Engineers - 3 personas
    "Software Engineers: Ari": {
        "path": "cs5740-personas/personas/development/software_engineers/Ari.md",
        "category": "Development",
        "description": "Software Engineer focused on clean code"
    },
    "Software Engineers: Emily": {
        "path": "cs5740-personas/personas/development/software_engineers/Emily.md",
        "category": "Development",
        "description": "Software Engineer with full-stack expertise"
    },
    "Software Engineers: Bluey": {
        "path": "cs5740-personas/personas/development/software_engineers/Bluey.md",
        "category": "Development",
        "description": "Software Engineer focused on architecture"
    },
    
    # Type 3: Product Managers - 3 personas
    "Product Managers: Alex-Agile-PM": {
        "path": "cs5740-personas/personas/planning_requirements/product_managers/Alex-Agile-PM.md",
        "category": "Planning & Requirements",
        "description": "Agile Product Manager focused on user value"
    },
    "Product Managers: Jordan": {
        "path": "cs5740-personas/personas/planning_requirements/product_managers/Jordan.md",
        "category": "Planning & Requirements",
        "description": "Product Manager with strategic focus"
    },
    "Product Managers: Taylor": {
        "path": "cs5740-personas/personas/planning_requirements/product_managers/Taylor.md",
        "category": "Planning & Requirements",
        "description": "Product Manager focused on roadmap planning"
    }
}


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path object pointing to project root
    """
    # This file is in services/, so parent is project root
    return Path(__file__).parent.parent


def load_persona(persona_name: str) -> str:
    """
    Load a persona's content from the cs5740-personas repository.
    
    Args:
        persona_name: Name of the persona (key from PERSONAS dict)
        
    Returns:
        Persona content as string (empty string for "None - Default Agent")
        
    Raises:
        ValueError: If persona not found
        FileNotFoundError: If persona file doesn't exist
    """
    if persona_name not in PERSONAS:
        available = ", ".join(PERSONAS.keys())
        raise ValueError(f"Unknown persona: {persona_name}. Available: {available}")
    
    persona_info = PERSONAS[persona_name]
    
    # Handle "None - Default Agent" case
    if persona_info["path"] is None:
        return ""
    
    persona_path = get_project_root() / persona_info["path"]
    
    if not persona_path.exists():
        raise FileNotFoundError(f"Persona file not found: {persona_path}")
    
    return persona_path.read_text(encoding='utf-8')


def get_available_personas() -> List[str]:
    """
    Get list of available persona names.
    
    Returns:
        List of persona names
    """
    return list(PERSONAS.keys())


def get_persona_info(persona_name: str) -> Dict[str, str]:
    """
    Get information about a persona.
    
    Args:
        persona_name: Name of the persona
        
    Returns:
        Dictionary with persona info (category, description)
        
    Raises:
        ValueError: If persona not found
    """
    if persona_name not in PERSONAS:
        raise ValueError(f"Unknown persona: {persona_name}")
    
    return PERSONAS[persona_name]


def get_personas_by_category() -> Dict[str, List[Tuple[str, str]]]:
    """
    Get personas grouped by category.
    
    Returns:
        Dictionary mapping category to list of (name, description) tuples
    """
    by_category: Dict[str, List[Tuple[str, str]]] = {}
    
    for name, info in PERSONAS.items():
        category = info["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((name, info["description"]))
    
    return by_category

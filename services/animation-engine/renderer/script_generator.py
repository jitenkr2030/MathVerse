"""
MathVerse Animation Engine - Script Generator
Dynamically generates Manim scripts from request parameters.
"""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generates Manim scripts from configuration dictionaries"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self.jinja_env.filters['to_tex'] = self._to_latex
        self.jinja_env.filters['color_hex'] = self._color_to_manim
    
    def generate_script(
        self,
        scene_type: str,
        title: str,
        subtitle: Optional[str],
        equations: list,
        graph: Optional[Dict] = None,
        shapes: Optional[list] = None,
        proof_steps: Optional[list] = None,
        primary_color: str = "#3B82F6",
        secondary_color: str = "#10B981",
        text_color: str = "#1F2937",
        background_color: str = "#FFFFFF",
        level: str = "secondary",
        **kwargs
    ) -> str:
        """Generate complete Manim script content"""
        
        # Determine template based on scene type
        template_name = f"{scene_type}_scene.py.j2"
        
        if not (self.templates_dir / template_name).exists():
            template_name = "base_scene.py.j2"
        
        try:
            template = self.jinja_env.get_template(template_name)
        except Exception as e:
            logger.warning(f"Template {template_name} not found, using base template")
            template = self.jinja_env.get_template("base_scene.py.j2")
        
        # Prepare context
        context = {
            'job_id': str(uuid.uuid4())[:8],
            'title': title,
            'subtitle': subtitle,
            'equations': equations,
            'graph': graph,
            'shapes': shapes,
            'proof_steps': proof_steps,
            'colors': {
                'primary': primary_color,
                'secondary': secondary_color,
                'text': text_color,
                'background': background_color,
            },
            'level': level,
            'scene_name': self._generate_scene_name(scene_type, level),
        }
        
        # Add extra parameters
        context.update(kwargs)
        
        # Generate script
        script = template.render(**context)
        
        return script
    
    def save_script(
        self,
        script_content: str,
        output_dir: str = "temp"
    ) -> str:
        """Save generated script to file and return path"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        job_id = str(uuid.uuid4())[:8]
        filename = f"scene_{job_id}.py"
        file_path = output_path / filename
        
        # Write script
        with open(file_path, 'w') as f:
            f.write(script_content)
        
        logger.info(f"Generated script: {file_path}")
        return str(file_path)
    
    def _generate_scene_name(self, scene_type: str, level: str) -> str:
        """Generate valid Python class name for scene"""
        level_part = level.title().replace('_', '')
        type_part = scene_type.title()
        return f"{level_part}{type_part}Scene"
    
    def _to_latex(self, value: str) -> str:
        """Convert text to LaTeX format"""
        # Handle common math expressions
        replacements = {
            '^2': '²',
            '^3': '³',
            '/': ' / ',
            '*': ' \\cdot ',
            'sqrt': '\\sqrt',
            'sin': '\\sin',
            'cos': '\\cos',
            'tan': '\\tan',
            'log': '\\log',
            'ln': '\\ln',
            'dx': 'dx',
            'dy': 'dy',
        }
        
        result = value
        for pattern, replacement in replacements.items():
            result = result.replace(pattern, replacement)
        
        return result
    
    def _color_to_manim(self, color: str) -> str:
        """Convert hex color to Manim color string"""
        if color.startswith('#'):
            return f'"{color}"'
        return f'"{color}"'


def create_graph_scene_script(
    equation: str,
    x_range: list = [-10, 10],
    y_range: Optional[list] = None,
    title: str = "Graph",
    **kwargs
) -> str:
    """Create a graph scene script"""
    generator = ScriptGenerator()
    
    return generator.generate_script(
        scene_type='graph',
        title=title,
        subtitle=None,
        equations=[equation],
        graph={
            'equation': equation,
            'x_range': x_range,
            'y_range': y_range,
        },
        **kwargs
    )


def create_proof_scene_script(
    proof_steps: list,
    title: str = "Proof",
    **kwargs
) -> str:
    """Create a proof scene script"""
    generator = ScriptGenerator()
    
    return generator.generate_script(
        scene_type='proof',
        title=title,
        subtitle=None,
        equations=[],
        proof_steps=proof_steps,
        **kwargs
    )


def create_algebra_scene_script(
    equations: list,
    title: str = "Algebra",
    **kwargs
) -> str:
    """Create an algebra solution scene script"""
    generator = ScriptGenerator()
    
    return generator.generate_script(
        scene_type='algebra',
        title=title,
        subtitle=None,
        equations=equations,
        **kwargs
    )


def create_geometry_scene_script(
    shapes: list,
    title: str = "Geometry",
    **kwargs
) -> str:
    """Create a geometry scene script"""
    generator = ScriptGenerator()
    
    return generator.generate_script(
        scene_type='geometry',
        title=title,
        subtitle=None,
        equations=[],
        shapes=shapes,
        **kwargs
    )

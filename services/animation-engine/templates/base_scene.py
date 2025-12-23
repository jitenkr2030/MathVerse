from manim import *
import numpy as np

class MathVerseScene(Scene):
    """
    Base scene class for MathVerse animations.
    Provides consistent styling and utility methods for all math animations.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # MathVerse brand colors
        self.colors = {
            'primary': '#3B82F6',      # Blue
            'secondary': '#10B981',    # Green  
            'accent': '#F59E0B',       # Amber
            'background': '#FFFFFF',   # White
            'text': '#1F2937',         # Dark gray
            'highlight': '#EF4444',     # Red
        }
        
    def show_title(self, title: str, subtitle: str = None):
        """Display animated title and optional subtitle"""
        title_obj = Text(title, font_size=48, color=self.colors['primary'])
        title_obj.to_edge(UP)
        
        if subtitle:
            subtitle_obj = Text(subtitle, font_size=32, color=self.colors['text'])
            subtitle_obj.next_to(title_obj, DOWN, buff=0.5)
            title_group = VGroup(title_obj, subtitle_obj)
        else:
            title_group = title_obj
            
        self.play(Write(title_group))
        self.wait(1)
        return title_group
    
    def hide_title(self, title_group):
        """Fade out title"""
        self.play(FadeOut(title_group))
        
    def show_formula(self, formula: str, position=None):
        """Display mathematical formula with animation"""
        formula_obj = MathTex(formula, font_size=36, color=self.colors['text'])
        if position:
            formula_obj.move_to(position)
        self.play(Write(formula_obj))
        return formula_obj
    
    def highlight_element(self, element, color=None):
        """Highlight a mobject with color"""
        if color is None:
            color = self.colors['highlight']
        self.play(element.animate.set_color(color))
        
    def show_step_number(self, step: int):
        """Display step number for multi-step explanations"""
        step_obj = Text(f"Step {step}", font_size=24, color=self.colors['secondary'])
        step_obj.to_corner(UL)
        self.play(Write(step_obj))
        return step_obj
        
    def create_graph_background(self):
        """Create a coordinate system for graphing"""
        axes = Axes(
            x_range=[-10, 10, 1],
            y_range=[-10, 10, 1],
            axis_config={"color": self.colors['text']},
            tips=False
        )
        return axes
    
    def explain_concept(self, text: str, position=None):
        """Add explanatory text bubble"""
        explanation = Text(text, font_size=28, color=self.colors['text'])
        if position:
            explanation.move_to(position)
        else:
            explanation.to_edge(DOWN)
        
        # Create background rectangle
        bg = SurroundingRectangle(explanation, color=self.colors['primary'], fill_opacity=0.1)
        self.play(Create(bg), Write(explanation))
        return VGroup(bg, explanation)
        
    def transition_to_next(self):
        """Standard transition between concepts"""
        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)
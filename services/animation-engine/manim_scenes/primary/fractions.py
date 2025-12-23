from manim import *
from templates.base_scene import MathVerseScene
import numpy as np

class FractionBasics(MathVerseScene):
    """Introduction to fractions for primary school"""
    
    def construct(self):
        title = self.show_title("Understanding Fractions", "Parts of a Whole")
        
        # Create a circle to represent a whole
        circle = Circle(radius=2, color=self.colors['primary'], fill_opacity=0.3)
        self.play(Create(circle))
        
        # Divide into 4 parts
        lines = VGroup()
        for angle in [0, 90, 180, 270]:
            line = Line(circle.get_center(), circle.point_at_angle(angle * DEGREES))
            lines.add(line)
        
        self.play(Create(lines))
        
        # Highlight one quarter
        quarter_sector = Sector(
            outer_radius=2,
            angle=90 * DEGREES,
            color=self.colors['accent'],
            fill_opacity=0.7
        )
        self.play(Create(quarter_sector))
        
        # Show fraction notation
        fraction = MathTex(r"\frac{1}{4}", font_size=72, color=self.colors['text'])
        fraction.to_edge(DOWN)
        self.play(Write(fraction))
        
        # Explain
        explanation = Text("One part out of four equal parts", font_size=28, color=self.colors['secondary'])
        explanation.next_to(fraction, DOWN, buff=0.5)
        self.play(Write(explanation))
        
        self.wait(2)

class ShapeRecognition(MathVerseScene):
    """Basic geometry shapes recognition"""
    
    def construct(self):
        title = self.show_title("Basic Shapes", "Circle, Square, Triangle")
        
        # Create shapes
        circle = Circle(radius=1.5, color=self.colors['primary'], fill_opacity=0.5)
        square = Square(side_length=3, color=self.colors['secondary'], fill_opacity=0.5)
        triangle = Polygon(
            [0, 2, 0], [-1.5, -1, 0], [1.5, -1, 0],
            color=self.colors['accent'], fill_opacity=0.5
        )
        
        # Position shapes
        circle.shift(LEFT * 4)
        square.shift(UP * 1.5)
        triangle.shift(RIGHT * 4)
        
        # Animate shapes appearing
        self.play(Create(circle))
        self.play(Write(Text("Circle", font_size=24).next_to(circle, DOWN)))
        
        self.play(Create(square))
        self.play(Write(Text("Square", font_size=24).next_to(square, DOWN)))
        
        self.play(Create(triangle))
        self.play(Write(Text("Triangle", font_size=24).next_to(triangle, DOWN)))
        
        self.wait(2)
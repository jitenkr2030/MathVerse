from manim import *
from templates.base_scene import MathVerseScene
import numpy as np

class AlgebraBasics(MathVerseScene):
    """Introduction to algebraic expressions"""
    
    def construct(self):
        title = self.show_title("Introduction to Algebra", "Variables and Expressions")
        
        # Show simple equation
        equation = MathTex(r"x + 3 = 7", font_size=48, color=self.colors['text'])
        equation.to_edge(UP)
        self.play(Write(equation))
        
        # Visual representation with boxes
        x_box = Square(side_length=1.2, color=self.colors['primary'], fill_opacity=0.3)
        x_box.shift(LEFT * 3)
        
        three_dots = VGroup()
        for i in range(3):
            dot = Dot(radius=0.15, color=self.colors['secondary'])
            dot.shift(LEFT * 1 + RIGHT * i * 0.5)
            three_dots.add(dot)
        
        seven_dots = VGroup()
        for i in range(7):
            dot = Dot(radius=0.15, color=self.colors['accent'])
            dot.shift(RIGHT * 1 + RIGHT * i * 0.5)
            seven_dots.add(dot)
        
        self.play(Create(x_box))
        self.play(Create(three_dots))
        self.play(Create(seven_dots))
        
        # Show solving process
        step1 = MathTex(r"x = 7 - 3", font_size=36, color=self.colors['text'])
        step1.to_edge(DOWN)
        self.play(Write(step1))
        
        step2 = MathTex(r"x = 4", font_size=36, color=self.colors['accent'])
        step2.next_to(step1, DOWN, buff=0.5)
        self.play(Write(step2))
        
        # Fill in x box with 4 dots
        x_dots = VGroup()
        for i in range(4):
            dot = Dot(radius=0.15, color=self.colors['primary'])
            dot.move_to(x_box.get_center() + np.array([(-0.3 + i * 0.2), 0, 0]))
            x_dots.add(dot)
        
        self.play(FadeIn(x_dots))
        self.wait(2)

class LinearEquationGraph(MathVerseScene):
    """Graphing linear equations"""
    
    def construct(self):
        title = self.show_title("Graphing Linear Equations", "y = 2x + 1")
        
        # Create coordinate system
        axes = self.create_graph_background()
        self.play(Create(axes))
        
        # Plot the line
        def line_func(x):
            return 2 * x + 1
        
        line_graph = axes.plot(line_func, color=self.colors['primary'], x_range=[-5, 5])
        self.play(Create(line_graph))
        
        # Show key points
        points = VGroup()
        for x_val in [-2, -1, 0, 1, 2]:
            y_val = line_func(x_val)
            point = Dot(axes.coords_to_point(x_val, y_val), color=self.colors['accent'])
            points.add(point)
        
        self.play(Create(points))
        
        # Show equation
        equation = MathTex(r"y = 2x + 1", font_size=36, color=self.colors['text'])
        equation.to_corner(UR)
        self.play(Write(equation))
        
        # Show slope and y-intercept
        slope_text = Text("Slope = 2", font_size=24, color=self.colors['secondary'])
        slope_text.to_corner(DL)
        intercept_text = Text("Y-intercept = 1", font_size=24, color=self.colors['secondary'])
        intercept_text.next_to(slope_text, UP, buff=0.5)
        
        self.play(Write(slope_text), Write(intercept_text))
        self.wait(2)
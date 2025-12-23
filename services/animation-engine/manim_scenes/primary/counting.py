from manim import *
from templates.base_scene import MathVerseScene
import numpy as np

class CountingAnimation(MathVerseScene):
    """Basic counting animation for primary school"""
    
    def construct(self):
        # Show title
        title = self.show_title("Counting to 5", "Let's learn numbers!")
        
        # Create circles to represent numbers
        circles = VGroup()
        for i in range(5):
            circle = Circle(radius=0.5, color=self.colors['primary'], fill_opacity=0.7)
            circle.shift(LEFT * 2 + RIGHT * i)
            circles.add(circle)
        
        # Animate counting
        for i, circle in enumerate(circles):
            number = Text(str(i + 1), font_size=36).move_to(circle.get_center())
            self.play(Create(circle), Write(number))
            self.wait(0.5)
        
        # Show final count
        count_text = Text("Total: 5 circles!", font_size=32, color=self.colors['secondary'])
        count_text.to_edge(DOWN)
        self.play(Write(count_text))
        self.wait(2)

class BasicAddition(MathVerseScene):
    """Simple addition animation"""
    
    def construct(self):
        title = self.show_title("Basic Addition", "2 + 3 = ?")
        
        # Create first group
        group1 = VGroup()
        for i in range(2):
            square = Square(side_length=0.8, color=self.colors['primary'], fill_opacity=0.7)
            square.shift(LEFT * 2 + RIGHT * i * 1.2)
            group1.add(square)
        
        # Create second group
        group2 = VGroup()
        for i in range(3):
            square = Square(side_length=0.8, color=self.colors['secondary'], fill_opacity=0.7)
            square.shift(RIGHT * 0.5 + RIGHT * i * 1.2)
            group2.add(square)
        
        # Animate
        self.play(Create(group1))
        self.wait(1)
        self.play(Create(group2))
        self.wait(1)
        
        # Show addition symbol
        plus = Text("+", font_size=48, color=self.colors['text'])
        plus.move_to((group1.get_center() + group2.get_center()) / 2 + UP * 2)
        self.play(Write(plus))
        
        # Combine groups
        all_squares = VGroup(group1, group2)
        self.play(all_squares.animate.arrange(RIGHT, buff=0.3).shift(UP))
        
        # Show result
        equals = Text("=", font_size=48, color=self.colors['text'])
        equals.next_to(all_squares, RIGHT, buff=1)
        result = Text("5", font_size=48, color=self.colors['accent'])
        result.next_to(equals, RIGHT, buff=0.5)
        
        self.play(Write(equals), Write(result))
        self.wait(2)
"""
Content Seed Data Module

This module provides seed data for the MathVerse platform's content metadata,
populating the database with initial educational content across all levels.
"""

from datetime import datetime
from typing import List, Dict, Any

# Educational levels with descriptions
EDUCATIONAL_LEVELS = {
    "primary": {
        "name": "Primary Education",
        "age_range": "6-11 years",
        "description": "Foundational mathematics including counting, basic arithmetic, shapes, and introduction to fractions",
        "display_order": 1
    },
    "secondary": {
        "name": "Secondary Education",
        "age_range": "12-16 years",
        "description": "Algebra basics, trigonometry fundamentals, and geometry proofs",
        "display_order": 2
    },
    "senior_secondary": {
        "name": "Senior Secondary",
        "age_range": "17-18 years",
        "description": "Calculus, advanced functions, and vector mathematics",
        "display_order": 3
    },
    "undergraduate": {
        "name": "Undergraduate",
        "age_range": "18+ years",
        "description": "Linear algebra, probability & statistics, discrete mathematics",
        "display_order": 4
    },
    "postgraduate": {
        "name": "Postgraduate",
        "age_range": "21+ years",
        "description": "Abstract algebra, topology, real analysis",
        "display_order": 5
    }
}

# Subjects across all levels
SUBJECTS = [
    {
        "id": "arithmetic",
        "name": "Arithmetic",
        "description": "Basic operations and number theory",
        "icon": "calculator",
        "color": "#3B82F6"
    },
    {
        "id": "algebra",
        "name": "Algebra",
        "description": "Variables, expressions, equations, and functions",
        "icon": "function",
        "color": "#8B5CF6"
    },
    {
        "id": "geometry",
        "name": "Geometry",
        "description": "Shapes, spaces, and their properties",
        "icon": "shapes",
        "color": "#10B981"
    },
    {
        "id": "trigonometry",
        "name": "Trigonometry",
        "description": "Relationships between angles and sides",
        "icon": "triangle",
        "color": "#F59E0B"
    },
    {
        "id": "calculus",
        "name": "Calculus",
        "description": "Limits, derivatives, integrals, and series",
        "icon": "integral",
        "color": "#EF4444"
    },
    {
        "id": "statistics",
        "name": "Statistics & Probability",
        "description": "Data analysis and probability theory",
        "icon": "chart",
        "color": "#EC4899"
    },
    {
        "id": "linear_algebra",
        "name": "Linear Algebra",
        "description": "Vectors, matrices, and linear transformations",
        "icon": "grid",
        "color": "#6366F1"
    },
    {
        "id": "discrete_math",
        "name": "Discrete Mathematics",
        "description": "Logic, sets, combinatorics, and graph theory",
        "icon": "nodes",
        "color": "#14B8A6"
    }
]

# Sample concepts for each level and subject
CONCEPTS = [
    # Primary Level Concepts
    {
        "level_id": "primary",
        "subject_id": "arithmetic",
        "title": "Counting and Numbers",
        "description": "Learn to count, recognize numbers, and understand number sequences",
        "difficulty": "foundational",
        "estimated_minutes": 20,
        "learning_objectives": [
            "Count from 1 to 100",
            "Recognize number patterns",
            "Understand odd and even numbers"
        ],
        "topics": ["counting", "number recognition", "patterns"],
        "tags": ["basics", "numbers", "counting"],
        "prerequisites": []
    },
    {
        "level_id": "primary",
        "subject_id": "arithmetic",
        "title": "Basic Addition",
        "description": "Master addition of small numbers with visual representations",
        "difficulty": "beginner",
        "estimated_minutes": 25,
        "learning_objectives": [
            "Add single-digit numbers",
            "Use number lines for addition",
            "Solve word problems with addition"
        ],
        "topics": ["addition", "single-digit", "number lines"],
        "tags": ["arithmetic", "addition", "basics"],
        "prerequisites": ["counting-and-numbers"]
    },
    {
        "level_id": "primary",
        "subject_id": "arithmetic",
        "title": "Basic Subtraction",
        "description": "Learn subtraction as the inverse of addition",
        "difficulty": "beginner",
        "estimated_minutes": 25,
        "learning_objectives": [
            "Subtract single-digit numbers",
            "Understand subtraction as taking away",
            "Solve subtraction word problems"
        ],
        "topics": ["subtraction", "inverse operations", "word problems"],
        "tags": ["arithmetic", "subtraction", "basics"],
        "prerequisites": ["basic-addition"]
    },
    {
        "level_id": "primary",
        "subject_id": "arithmetic",
        "title": "Introduction to Multiplication",
        "description": "Understand multiplication as repeated addition",
        "difficulty": "beginner",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Understand multiplication as repeated addition",
            "Memorize multiplication tables 1-10",
            "Solve simple multiplication problems"
        ],
        "topics": ["multiplication", "times tables", "repeated addition"],
        "tags": ["arithmetic", "multiplication", "memory"],
        "prerequisites": ["basic-addition", "basic-subtraction"]
    },
    {
        "level_id": "primary",
        "subject_id": "arithmetic",
        "title": "Introduction to Division",
        "description": "Learn division as sharing and grouping",
        "difficulty": "beginner",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Understand division as sharing equally",
            "Divide single-digit numbers",
            "Relate division to multiplication"
        ],
        "topics": ["division", "sharing", "grouping"],
        "tags": ["arithmetic", "division", "basics"],
        "prerequisites": ["introduction-to-multiplication"]
    },
    {
        "level_id": "primary",
        "subject_id": "geometry",
        "title": "Basic Shapes",
        "description": "Identify and name common 2D and 3D shapes",
        "difficulty": "foundational",
        "estimated_minutes": 20,
        "learning_objectives": [
            "Identify circles, triangles, squares, rectangles",
            "Recognize basic 3D shapes",
            "Describe shape properties"
        ],
        "topics": ["2D shapes", "3D shapes", "shape properties"],
        "tags": ["geometry", "shapes", "visual"],
        "prerequisites": []
    },
    {
        "level_id": "primary",
        "subject_id": "geometry",
        "title": "Fractions Introduction",
        "description": "Visual introduction to fractions using shapes and objects",
        "difficulty": "beginner",
        "estimated_minutes": 25,
        "learning_objectives": [
            "Understand halves, thirds, quarters",
            "Compare simple fractions",
            "Identify fractions in everyday objects"
        ],
        "topics": ["fractions", "parts of a whole", "visual fractions"],
        "tags": ["fractions", "parts", "visual"],
        "prerequisites": ["basic-shapes"]
    },
    
    # Secondary Level Concepts
    {
        "level_id": "secondary",
        "subject_id": "algebra",
        "title": "Variables and Expressions",
        "description": "Introduction to algebraic variables and forming expressions",
        "difficulty": "foundational",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Understand the concept of variables",
            "Write algebraic expressions",
            "Evaluate expressions with given values"
        ],
        "topics": ["variables", "expressions", "evaluation"],
        "tags": ["algebra", "basics", "expressions"],
        "prerequisites": ["basic-arithmetic"]
    },
    {
        "level_id": "secondary",
        "subject_id": "algebra",
        "title": "Linear Equations",
        "description": "Solve one-step and two-step linear equations",
        "difficulty": "beginner",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Solve one-step equations",
            "Solve two-step equations",
            "Write equations from word problems"
        ],
        "topics": ["equations", "solving", "linear"],
        "tags": ["algebra", "equations", "problem-solving"],
        "prerequisites": ["variables-and-expressions"]
    },
    {
        "level_id": "secondary",
        "subject_id": "algebra",
        "title": "Inequalities",
        "description": "Understand and solve linear inequalities",
        "difficulty": "intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Understand inequality symbols",
            "Solve linear inequalities",
            "Graph inequalities on number lines"
        ],
        "topics": ["inequalities", "number lines", "graphs"],
        "tags": ["algebra", "inequalities", "graphs"],
        "prerequisites": ["linear-equations"]
    },
    {
        "level_id": "secondary",
        "subject_id": "geometry",
        "title": "Angle Relationships",
        "description": "Complementary, supplementary, and vertical angles",
        "difficulty": "beginner",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Identify complementary and supplementary angles",
            "Understand vertical angles",
            "Solve angle problems"
        ],
        "topics": ["angles", "relationships", "geometry"],
        "tags": ["geometry", "angles", "properties"],
        "prerequisites": ["basic-shapes"]
    },
    {
        "level_id": "secondary",
        "subject_id": "geometry",
        "title": "Triangle Properties",
        "description": "Types of triangles and their properties",
        "difficulty": "intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Classify triangles by sides and angles",
            "Understand triangle sum theorem",
            "Apply properties in problem solving"
        ],
        "topics": ["triangles", "classification", "theorems"],
        "tags": ["geometry", "triangles", "classification"],
        "prerequisites": ["angle-relationships"]
    },
    {
        "level_id": "secondary",
        "subject_id": "trigonometry",
        "title": "Introduction to Trigonometry",
        "description": "Sine, cosine, and tangent ratios in right triangles",
        "difficulty": "intermediate",
        "estimated_minutes": 40,
        "learning_objectives": [
            "Identify opposite, adjacent, and hypotenuse",
            "Calculate sine, cosine, and tangent",
            "Use trigonometry to find side lengths"
        ],
        "topics": ["trig ratios", "right triangles", "SOH CAH TOA"],
        "tags": ["trigonometry", "ratios", "right-triangles"],
        "prerequisites": ["triangle-properties", "basic-algebra"]
    },
    
    # Senior Secondary Concepts
    {
        "level_id": "senior_secondary",
        "subject_id": "calculus",
        "title": "Limits and Continuity",
        "description": "Understand the concept of limits and continuous functions",
        "difficulty": "intermediate",
        "estimated_minutes": 45,
        "learning_objectives": [
            "Understand limits intuitively",
            "Evaluate limits algebraically",
            "Determine continuity of functions"
        ],
        "topics": ["limits", "continuity", "function behavior"],
        "tags": ["calculus", "fundamentals", "limits"],
        "prerequisites": ["algebra", "functions"]
    },
    {
        "level_id": "senior_secondary",
        "subject_id": "calculus",
        "title": "Derivatives",
        "description": "Introduction to differentiation and rates of change",
        "difficulty": "advanced",
        "estimated_minutes": 50,
        "learning_objectives": [
            "Understand the derivative as a limit",
            "Apply differentiation rules",
            "Find slopes of curves at points"
        ],
        "topics": ["derivatives", "differentiation", "rates of change"],
        "tags": ["calculus", "derivatives", "differentiation"],
        "prerequisites": ["limits-and-continuity"]
    },
    {
        "level_id": "senior_secondary",
        "subject_id": "calculus",
        "title": "Integration",
        "description": "Antiderivatives and definite integrals",
        "difficulty": "advanced",
        "estimated_minutes": 50,
        "learning_objectives": [
            "Find antiderivatives",
            "Apply fundamental theorem of calculus",
            "Calculate definite integrals"
        ],
        "topics": ["integration", "antiderivatives", "area"],
        "tags": ["calculus", "integration", "area"],
        "prerequisites": ["derivatives"]
    },
    {
        "level_id": "senior_secondary",
        "subject_id": "trigonometry",
        "title": "Trigonometric Identities",
        "description": "Proving and using trigonometric identities",
        "difficulty": "advanced",
        "estimated_minutes": 45,
        "learning_objectives": [
            "Prove Pythagorean identities",
            "Use angle addition formulas",
            "Simplify trigonometric expressions"
        ],
        "topics": ["identities", "formulas", "proofs"],
        "tags": ["trigonometry", "identities", "formulas"],
        "prerequisites": ["introduction-to-trigonometry"]
    },
    {
        "level_id": "senior_secondary",
        "subject_id": "algebra",
        "title": "Polynomial Functions",
        "description": "Operations and graphs of polynomial functions",
        "difficulty": "intermediate",
        "estimated_minutes": 40,
        "learning_objectives": [
            "Perform polynomial operations",
            "Factor polynomials",
            "Graph polynomial functions"
        ],
        "topics": ["polynomials", "factoring", "graphs"],
        "tags": ["algebra", "polynomials", "functions"],
        "prerequisites": ["linear-equations", "functions"]
    },
    
    # Undergraduate Concepts
    {
        "level_id": "undergraduate",
        "subject_id": "linear_algebra",
        "title": "Vector Spaces",
        "description": "Introduction to vector spaces and subspaces",
        "difficulty": "intermediate",
        "estimated_minutes": 45,
        "learning_objectives": [
            "Understand vector space axioms",
            "Identify subspaces",
            "Find bases and dimension"
        ],
        "topics": ["vector spaces", "subspaces", "bases"],
        "tags": ["linear-algebra", "vectors", "abstract"],
        "prerequisites": ["linear-algebra-basics"]
    },
    {
        "level_id": "undergraduate",
        "subject_id": "linear_algebra",
        "title": "Matrix Operations",
        "description": "Matrix multiplication, inverses, and transformations",
        "difficulty": "intermediate",
        "estimated_minutes": 50,
        "learning_objectives": [
            "Perform matrix operations",
            "Find matrix inverses",
            "Understand linear transformations"
        ],
        "topics": ["matrices", "transformations", "inverses"],
        "tags": ["linear-algebra", "matrices", "transformations"],
        "prerequisites": ["vector-spaces"]
    },
    {
        "level_id": "undergraduate",
        "subject_id": "statistics",
        "title": "Probability Fundamentals",
        "description": "Basic probability theory and rules",
        "difficulty": "intermediate",
        "estimated_minutes": 40,
        "learning_objectives": [
            "Understand sample spaces and events",
            "Apply addition and multiplication rules",
            "Calculate conditional probability"
        ],
        "topics": ["probability", "conditional", "rules"],
        "tags": ["statistics", "probability", "fundamentals"],
        "prerequisites": ["basic-statistics"]
    },
    {
        "level_id": "undergraduate",
        "subject_id": "statistics",
        "title": "Probability Distributions",
        "description": "Discrete and continuous probability distributions",
        "difficulty": "advanced",
        "estimated_minutes": 50,
        "learning_objectives": [
            "Understand binomial distribution",
            "Work with normal distribution",
            "Calculate expected value and variance"
        ],
        "topics": ["distributions", "binomial", "normal"],
        "tags": ["statistics", "distributions", "probability"],
        "prerequisites": ["probability-fundamentals"]
    },
    {
        "level_id": "undergraduate",
        "subject_id": "discrete_math",
        "title": "Graph Theory Basics",
        "description": "Introduction to graphs, paths, and connectivity",
        "difficulty": "intermediate",
        "estimated_minutes": 45,
        "learning_objectives": [
            "Understand graph terminology",
            "Identify Eulerian and Hamiltonian paths",
            "Apply graph algorithms"
        ],
        "topics": ["graphs", "paths", "algorithms"],
        "tags": ["discrete-math", "graphs", "theory"],
        "prerequisites": ["logic-proofs"]
    },
    
    # Postgraduate Concepts
    {
        "level_id": "postgraduate",
        "subject_id": "linear_algebra",
        "title": "Eigenvalues and Eigenvectors",
        "description": "Understanding eigenvalues and their applications",
        "difficulty": "advanced",
        "estimated_minutes": 55,
        "learning_objectives": [
            "Find eigenvalues and eigenvectors",
            "Understand diagonalization",
            "Apply to differential equations"
        ],
        "topics": ["eigenvalues", "eigenvectors", "diagonalization"],
        "tags": ["linear-algebra", "advanced", "applications"],
        "prerequisites": ["matrix-operations", "vector-spaces"]
    },
    {
        "level_id": "postgraduate",
        "subject_id": "calculus",
        "title": "Real Analysis",
        "description": "Rigorous treatment of limits, continuity, and differentiation",
        "difficulty": "expert",
        "estimated_minutes": 60,
        "learning_objectives": [
            "Understand epsilon-delta proofs",
            "Prove theorems rigorously",
            "Work with sequences and series"
        ],
        "topics": ["analysis", "proofs", "rigor"],
        "tags": ["calculus", "analysis", "proofs"],
        "prerequisites": ["calculus-full", "mathematical-proofs"]
    },
    {
        "level_id": "postgraduate",
        "subject_id": "algebra",
        "title": "Abstract Algebra",
        "description": "Groups, rings, and fields",
        "difficulty": "expert",
        "estimated_minutes": 60,
        "learning_objectives": [
            "Understand group theory",
            "Work with rings and fields",
            "Apply algebraic structures"
        ],
        "topics": ["groups", "rings", "fields", "structures"],
        "tags": ["algebra", "abstract", "structures"],
        "prerequisites": ["linear-algebra", "mathematical-proofs"]
    },
    {
        "level_id": "postgraduate",
        "subject_id": "geometry",
        "title": "Topology",
        "description": "Introduction to topological spaces and continuity",
        "difficulty": "expert",
        "estimated_minutes": 60,
        "learning_objectives": [
            "Understand topological spaces",
            "Identify continuous functions",
            "Work with homeomorphisms"
        ],
        "topics": ["topology", "spaces", "continuity"],
        "tags": ["geometry", "topology", "abstract"],
        "prerequisites": ["real-analysis", "abstract-algebra"]
    }
]

# Sample courses combining multiple concepts
SAMPLE_COURSES = [
    {
        "title": "Mathematics Mastery: Primary Level",
        "description": "Complete primary school mathematics curriculum covering counting, arithmetic, shapes, and fractions with engaging animations and practice problems.",
        "level_id": "primary",
        "subject_ids": ["arithmetic", "geometry"],
        "concept_ids": [
            "counting-and-numbers",
            "basic-addition",
            "basic-subtraction",
            "introduction-to-multiplication",
            "introduction-to-division",
            "basic-shapes",
            "fractions-introduction"
        ],
        "estimated_hours": 15,
        "is_free": True,
        "price": 0.0
    },
    {
        "title": "Algebra Fundamentals",
        "description": "Build a strong foundation in algebra from variables through linear equations and inequalities.",
        "level_id": "secondary",
        "subject_ids": ["algebra"],
        "concept_ids": [
            "variables-and-expressions",
            "linear-equations",
            "inequalities"
        ],
        "estimated_hours": 10,
        "is_free": True,
        "price": 0.0
    },
    {
        "title": "Geometry Essentials",
        "description": "Master geometric concepts from basic shapes through triangle properties and angle relationships.",
        "level_id": "secondary",
        "subject_ids": ["geometry"],
        "concept_ids": [
            "basic-shapes",
            "angle-relationships",
            "triangle-properties"
        ],
        "estimated_hours": 8,
        "is_free": True,
        "price": 0.0
    },
    {
        "title": "Trigonometry Complete",
        "description": "From right triangle trigonometry through identities and applications.",
        "level_id": "secondary",
        "subject_ids": ["trigonometry"],
        "concept_ids": [
            "introduction-to-trigonometry",
            "trigonometric-identities"
        ],
        "estimated_hours": 12,
        "is_free": False,
        "price": 19.99
    },
    {
        "title": "Calculus Foundations",
        "description": "Master limits, derivatives, and integration with visual explanations and extensive practice.",
        "level_id": "senior_secondary",
        "subject_ids": ["calculus"],
        "concept_ids": [
            "limits-and-continuity",
            "derivatives",
            "integration"
        ],
        "estimated_hours": 25,
        "is_free": False,
        "price": 29.99
    },
    {
        "title": "Linear Algebra Deep Dive",
        "description": "Comprehensive exploration of vector spaces, matrices, and linear transformations.",
        "level_id": "undergraduate",
        "subject_ids": ["linear_algebra"],
        "concept_ids": [
            "vector-spaces",
            "matrix-operations",
            "eigenvalues-and-eigenvectors"
        ],
        "estimated_hours": 20,
        "is_free": False,
        "price": 34.99
    },
    {
        "title": "Probability and Statistics",
        "description": "From basic probability through distributions and statistical inference.",
        "level_id": "undergraduate",
        "subject_ids": ["statistics"],
        "concept_ids": [
            "probability-fundamentals",
            "probability-distributions"
        ],
        "estimated_hours": 18,
        "is_free": False,
        "price": 24.99
    },
    {
        "title": "Advanced Abstract Mathematics",
        "description": "Real analysis, abstract algebra, and topology for graduate students.",
        "level_id": "postgraduate",
        "subject_ids": ["algebra", "calculus", "geometry"],
        "concept_ids": [
            "real-analysis",
            "abstract-algebra",
            "topology"
        ],
        "estimated_hours": 40,
        "is_free": False,
        "price": 49.99
    }
]

# Learning paths combining courses
LEARNING_PATHS = [
    {
        "title": "Primary Mathematics Journey",
        "description": "Complete path from counting to fractions for young learners",
        "course_ids": ["primary-math-mastery"],
        "estimated_hours": 15,
        "difficulty": "foundational"
    },
    {
        "title": "Secondary Mathematics Foundation",
        "description": "Comprehensive secondary school mathematics preparation",
        "course_ids": ["algebra-fundamentals", "geometry-essentials", "trigonometry-complete"],
        "estimated_hours": 30,
        "difficulty": "intermediate"
    },
    {
        "title": "Calculus Mastery",
        "description": "From limits through integration for college preparation",
        "course_ids": ["calculus-foundations"],
        "estimated_hours": 25,
        "difficulty": "advanced"
    },
    {
        "title": "Data Science Pathway",
        "description": "Statistics and probability for data science careers",
        "course_ids": ["probability-and-statistics"],
        "estimated_hours": 18,
        "difficulty": "intermediate"
    }
]


def get_seed_data() -> Dict[str, Any]:
    """
    Get all seed data as a dictionary.
    
    Returns:
        Dictionary containing all seed data categories
    """
    return {
        "levels": EDUCATIONAL_LEVELS,
        "subjects": SUBJECTS,
        "concepts": CONCEPTS,
        "courses": SAMPLE_COURSES,
        "learning_paths": LEARNING_PATHS
    }


def get_concept_slugs() -> List[str]:
    """
    Get list of all concept slugs for reference.
    
    Returns:
        List of concept identifier strings
    """
    return [concept["id"] for concept in CONCEPTS]

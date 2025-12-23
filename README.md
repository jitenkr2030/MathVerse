# MathVerse 🧮✨

Animation-first Mathematics Learning Platform

MathVerse = Animation Engine + API + Web/Mobile Apps

## 🎯 Vision

Transform mathematics education through beautiful, interactive animations powered by Manim. Making complex mathematical concepts visual, engaging, and accessible to learners of all ages.

## 🏗️ Architecture

### Monorepo Structure
```
mathverse/
├── apps/                    # Frontend Applications
│   ├── backend/             # FastAPI Backend Service
│   ├── web/                 # Next.js Web Application  
│   ├── mobile/              # Flutter Mobile App
│   └── creator-portal/      # Teacher/Creator Platform
│
├── services/                # Microservices
│   ├── animation-engine/     # Manim-based Animation Service
│   ├── video-renderer/      # Video Processing Service
│   ├── content-metadata/    # Content Management
│   └── recommendation-engine/ # ML-based Recommendations
│
├── shared/                  # Shared Code
│   ├── schemas/            # Data Models & Schemas
│   ├── utils/              # Common Utilities
│   └── constants/          # Shared Constants
│
└── infra/                  # Infrastructure
    ├── docker/             # Docker Configurations
    ├── k8s/               # Kubernetes Manifests
    └── ci-cd/             # CI/CD Pipelines
```

## 🚀 Core Services

### 1. Animation Engine (Manim-powered)
- **Technology**: Python + Manim Community Edition
- **Purpose**: Create mathematical animations programmatically
- **Features**:
  - Educational level-specific scenes (Primary → Postgraduate)
  - Consistent MathVerse branding and styling
  - Reusable templates and components
  - Batch rendering capabilities

### 2. Video Renderer Service
- **Technology**: FastAPI + FFmpeg
- **Purpose**: Render Manim scenes to video format
- **Features**:
  - Asynchronous job processing
  - Multiple quality presets (480p → 4K)
  - Thumbnail generation
  - Progress tracking

### 3. Backend API
- **Technology**: FastAPI + SQLAlchemy + PostgreSQL
- **Purpose**: Core business logic and data management
- **Features**:
  - User authentication & authorization
  - Course & lesson management
  - Progress tracking
  - Payment processing (Stripe)
  - RESTful API design

### 4. Web Frontend
- **Technology**: Next.js 14 + TypeScript + Tailwind CSS
- **Purpose**: Primary web learning platform
- **Features**:
  - Responsive design
  - Video player integration
  - Interactive quizzes
  - Progress dashboard
  - Real-time updates

### 5. Mobile App
- **Technology**: Flutter + Dart
- **Purpose**: On-the-go learning experience
- **Features**:
  - Offline video downloads
  - Low-bandwidth mode
  - Progress sync
  - Push notifications

## 📚 Educational Content

### Content Levels
1. **Primary** (Ages 6-11)
   - Counting & basic arithmetic
   - Shapes & geometry fundamentals
   - Introduction to fractions

2. **Secondary** (Ages 12-16)
   - Algebra basics & equations
   - Trigonometry fundamentals
   - Geometry proofs

3. **Senior Secondary** (Ages 17-18)
   - Calculus (limits, derivatives, integrals)
   - Advanced functions
   - Vector mathematics

4. **Undergraduate**
   - Linear algebra
   - Probability & statistics
   - Discrete mathematics

5. **Postgraduate**
   - Abstract algebra
   - Topology
   - Real analysis

### Animation Types
- **Concept Introductions**: Visual explanations of new topics
- **Step-by-step Derivations**: Mathematical proofs animated
- **Graph Transformations**: Dynamic function visualization
- **Interactive Examples**: Problem-solving demonstrations

## 🎨 Design System

### Color Palette
- **Primary**: #3B82F6 (Blue)
- **Secondary**: #10B981 (Green)  
- **Accent**: #F59E0B (Amber)
- **Background**: #FFFFFF (White)
- **Text**: #1F2937 (Dark Gray)
- **Highlight**: #EF4444 (Red)

### Typography
- **Headings**: Inter, Bold
- **Body**: Inter, Regular
- **Code**: JetBrains Mono
- **Math**: Custom MathVerse Math Font

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Flutter 3.0+
- Docker & Docker Compose
- FFmpeg
- PostgreSQL (or use Docker)

### Quick Start

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd mathverse
   ```

2. **Setup Animation Engine**
   ```bash
   cd services/animation-engine
   pip install -r requirements.txt
   python -m manim --help  # Verify Manim installation
   ```

3. **Setup Video Renderer**
   ```bash
   cd services/video-renderer
   pip install -r requirements.txt
   python api.py  # Starts on port 8001
   ```

4. **Setup Backend**
   ```bash
   cd apps/backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload  # Starts on port 8000
   ```

5. **Setup Web Frontend**
   ```bash
   cd apps/web
   npm install
   npm run dev  # Starts on port 3000
   ```

6. **Setup Mobile App**
   ```bash
   cd apps/mobile
   flutter pub get
   flutter run  # Requires connected device/emulator
   ```

### Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 Key Features

### For Students
- **Animated Learning**: Visual explanations of complex concepts
- **Interactive Quizzes**: Test understanding with immediate feedback
- **Progress Tracking**: Monitor learning journey with detailed analytics
- **Offline Access**: Download videos for offline learning
- **Personalized Paths**: AI-driven course recommendations

### For Teachers/Creators
- **Scene Editor**: Write Manim code in browser-based editor
- **Template Library**: Pre-built educational animations
- **Revenue Sharing**: Earn from premium content
- **Analytics Dashboard**: Track student engagement
- **Version Control**: Manage lesson updates and iterations

### For Institutions
- **Classroom Management**: Student enrollment and progress monitoring
- **Custom Content**: Branded educational materials
- **Analytics Reports**: Institutional learning insights
- **LMS Integration**: Seamless integration with existing systems
- **Bulk Licensing**: Cost-effective institutional pricing

## 💰 Monetization

### Subscription Tiers
- **Free**: Basic courses, limited features
- **Premium** ($9.99/month): Full access, offline downloads
- **Institutional**: Custom pricing for schools/universities

### Creator Revenue
- **Content Sales**: 70% revenue share for creators
- **Premium Content**: Ability to sell advanced courses
- **Donations**: Support for favorite creators

## 🔮 Future Roadmap

### Phase 1 (Current)
- ✅ Basic animation engine
- ✅ Video rendering service
- ✅ Core API functionality
- ✅ Web and mobile apps

### Phase 2 (Next 3 months)
- 🔄 AI-powered explanations
- 🔄 Interactive problem solving
- 🔄 Real-time collaboration
- 🔄 Advanced analytics

### Phase 3 (6+ months)
- 📋 AR/VR math experiences
- 📋 Voice-guided learning
- 📋 Multilingual support
- 📋 Advanced ML recommendations

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Code review and merge

### Areas for Contribution
- **Animation Scenes**: New educational content
- **Frontend**: UI/UX improvements
- **Backend**: API enhancements
- **Mobile**: Native features
- **Documentation**: Guides and tutorials

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Manim Community**: For the amazing mathematical animation engine
- **3Blue1Brown**: Inspiration for mathematical visualization
- **Khan Academy**: Educational content philosophy
- **Open Source Community**: Tools and libraries that make this possible

## 📞 Contact

- **Website**: [mathverse.com](https://mathverse.com)
- **Email**: hello@mathverse.com
- **Discord**: [Join our community](https://discord.gg/mathverse)
- **Twitter**: [@MathVerseApp](https://twitter.com/mathverseapp)

---

**MathVerse** - Making Mathematics Beautiful 🧮✨
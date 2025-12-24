import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { courseService, Lesson } from '../../services/courses';
import { useAuthStore } from '../../store';
import Layout from '../../components/Layout';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import VideoPlayer from '../../components/VideoPlayer';
import QuizWidget from '../../components/QuizWidget';
import ProgressBar from '../../components/ProgressBar';

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

export default function LessonPage() {
  const router = useRouter();
  const { id } = router.query;
  const { isAuthenticated } = useAuthStore();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [nextLesson, setNextLesson] = useState<Lesson | null>(null);
  const [prevLesson, setPrevLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'video' | 'quiz' | 'notes'>('video');
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);

  useEffect(() => {
    const fetchLessonData = async () => {
      if (!id) return;

      setIsLoading(true);
      try {
        const lessonId = parseInt(id as string);
        const [lessonData, nextData, prevData] = await Promise.all([
          courseService.getLesson(lessonId),
          courseService.getNextLesson(lessonId),
          courseService.getPreviousLesson(lessonId),
        ]);
        setLesson(lessonData);
        setNextLesson(nextData);
        setPrevLesson(prevData);

        setQuizQuestions([
          {
            id: 1,
            question: 'What is the main concept covered in this lesson?',
            options: ['Concept A', 'Concept B', 'Concept C', 'Concept D'],
            correct_answer: 0,
            explanation: 'The correct answer is Concept A because...',
          },
          {
            id: 2,
            question: 'Which of the following is true about this topic?',
            options: ['Statement 1', 'Statement 2', 'Statement 3', 'Statement 4'],
            correct_answer: 1,
            explanation: 'Statement 2 is correct because...',
          },
          {
            id: 3,
            question: 'Solve for x in the given equation.',
            options: ['x = 1', 'x = 2', 'x = 3', 'x = 4'],
            correct_answer: 2,
            explanation: 'The solution is x = 3 because...',
          },
        ]);
      } catch (error) {
        console.error('Error fetching lesson data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLessonData();
  }, [id]);

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleVideoEnd = async () => {
    try {
      await courseService.completeLesson(parseInt(id as string));
    } catch (error) {
      console.error('Error completing lesson:', error);
    }
  };

  const handleQuizComplete = (score: number, answers: number[]) => {
    setQuizScore(score);
    setQuizCompleted(true);
  };

  if (isLoading) {
    return (
      <Layout title="Loading Lesson - MathVerse">
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </Layout>
    );
  }

  if (!lesson) {
    return (
      <Layout title="Lesson Not Found - MathVerse">
        <div className="min-h-screen flex items-center justify-center">
          <Card className="max-w-md text-center">
            <CardContent className="pt-6">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">Lesson not found</h3>
              <p className="mt-1 text-gray-500">The lesson you are looking for does not exist.</p>
              <div className="mt-6">
                <Link href="/courses">
                  <Button>Browse Courses</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={`${lesson.title} - MathVerse`}>
      <div className="bg-gray-100 min-h-screen">
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div>
                <Link href={`/course/${lesson.course_id}`} className="text-indigo-600 hover:text-indigo-800 text-sm">
                  ← Back to Course
                </Link>
                <h1 className="text-2xl font-bold text-gray-900 mt-1">{lesson.title}</h1>
              </div>
              <div className="flex items-center space-x-4">
                <ProgressBar value={45} size="sm" />
                <span className="text-sm text-gray-600">45% complete</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-3 space-y-6">
              <Card className="overflow-hidden">
                <VideoPlayer
                  url={lesson.video_url || 'https://example.com/sample-video.mp4'}
                  lessonId={lesson.id}
                  onEnded={handleVideoEnd}
                  onNext={() => nextLesson && router.push(`/lesson/${nextLesson.id}`)}
                  onPrev={() => prevLesson && router.push(`/lesson/${prevLesson.id}`)}
                />
              </Card>

              <Card>
                <div className="border-b border-gray-200">
                  <nav className="flex -mb-px">
                    {(['video', 'quiz', 'notes'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`py-4 px-6 font-medium text-sm border-b-2 transition-colors ${
                          activeTab === tab
                            ? 'border-indigo-600 text-indigo-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                      </button>
                    ))}
                  </nav>
                </div>
                <CardContent>
                  {activeTab === 'video' && (
                    <div className="prose max-w-none">
                      <h3>About This Lesson</h3>
                      <p>{lesson.description}</p>
                      <h4>Key Concepts</h4>
                      <ul>
                        <li>Understanding the fundamental principles</li>
                        <li>Applying concepts to solve problems</li>
                        <li>Building intuition through visualization</li>
                      </ul>
                    </div>
                  )}
                  {activeTab === 'quiz' && (
                    <QuizWidget
                      quiz={{
                        id: lesson.id,
                        title: 'Lesson Quiz',
                        lesson_id: lesson.id,
                        passing_score: 70,
                        questions: quizQuestions.map((q, index) => ({
                          id: q.id,
                          quiz_id: lesson.id,
                          question_text: q.question,
                          question_type: 'multiple_choice' as const,
                          options: q.options.map((opt, i) => ({
                            id: String(i),
                            text: opt,
                            is_correct: i === q.correct_answer
                          })),
                          explanation: q.explanation,
                          points: 1,
                          order_index: index
                        })),
                        created_at: new Date().toISOString()
                      }}
                      onComplete={(attempt) => {
                        setQuizScore(attempt.percentage);
                        setQuizCompleted(true);
                      }}
                    />
                  )}
                  {activeTab === 'notes' && (
                    <div>
                      <textarea
                        className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Take notes here... Your notes are saved automatically."
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="lg:col-span-1 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Lesson Navigation</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={!prevLesson}
                        onClick={() => prevLesson && router.push(`/lesson/${prevLesson.id}`)}
                      >
                        ← Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={!nextLesson}
                        onClick={() => nextLesson && router.push(`/lesson/${nextLesson.id}`)}
                      >
                        Next →
                      </Button>
                    </div>
                    <Button fullWidth onClick={() => courseService.completeLesson(lesson.id)}>
                      Mark as Complete
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Resources</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    <li>
                      <a href="#" className="flex items-center text-indigo-600 hover:text-indigo-800">
                        <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Download Notes
                      </a>
                    </li>
                    <li>
                      <a href="#" className="flex items-center text-indigo-600 hover:text-indigo-800">
                        <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download Video
                      </a>
                    </li>
                    <li>
                      <a href="#" className="flex items-center text-indigo-600 hover:text-indigo-800">
                        <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Practice Worksheet
                      </a>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Discussion</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-sm mb-4">
                    Have questions about this lesson? Ask the community.
                  </p>
                  <Button variant="outline" fullWidth>
                    View Discussions
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

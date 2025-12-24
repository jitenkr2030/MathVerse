import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Clock, Trophy, ArrowRight, RotateCcw } from 'lucide-react';
import { quizService } from '@/services/quiz';
import { Quiz, Question, QuizSubmission, QuizAttempt } from '@/types';

interface QuizWidgetProps {
  quiz: Quiz;
  onComplete?: (attempt: QuizAttempt) => void;
  onClose?: () => void;
}

export default function QuizWidget({ quiz, onComplete, onClose }: QuizWidgetProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [attempt, setAttempt] = useState<QuizAttempt | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(quiz.time_limit ? quiz.time_limit * 60 : null);
  const [showExplanation, setShowExplanation] = useState(false);

  const questions = quiz.questions;
  const totalQuestions = questions.length;
  const currentQ = questions[currentQuestion];

  // Timer effect
  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || showResults) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev === null || prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, showResults]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSelectAnswer = (questionId: string, answer: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion((prev) => prev + 1);
      setShowExplanation(false);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
      setShowExplanation(false);
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const submission: QuizSubmission = { answers: selectedAnswers };
      const result = await quizService.submitQuizAttempt(quiz.id, submission);
      setAttempt(result);
      setShowResults(true);
      setShowExplanation(true);
      
      if (onComplete) {
        onComplete(result);
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = () => {
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setShowResults(false);
    setAttempt(null);
    setTimeLeft(quiz.time_limit ? quiz.time_limit * 60 : null);
    setShowExplanation(false);
  };

  const getAnswerClass = (question: Question, optionId: string) => {
    if (!showResults) {
      return selectedAnswers[question.id] === optionId
        ? 'quiz-option-selected'
        : 'quiz-option';
    }

    const correctAnswer = question.options?.find(opt => opt.is_correct)?.id;
    const userAnswer = selectedAnswers[question.id];

    if (optionId === correctAnswer) {
      return 'quiz-option-correct';
    }
    if (optionId === userAnswer && optionId !== correctAnswer) {
      return 'quiz-option-incorrect';
    }
    return 'quiz-option';
  };

  // Results Screen
  if (showResults && attempt) {
    const passed = attempt.passed;
    
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card max-w-2xl mx-auto"
      >
        {/* Results Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
            className={`w-24 h-24 mx-auto mb-4 rounded-full flex items-center justify-center ${
              passed ? 'bg-green-100' : 'bg-red-100'
            }`}
          >
            {passed ? (
              <Trophy className="w-12 h-12 text-green-600" />
            ) : (
              <XCircle className="w-12 h-12 text-red-600" />
            )}
          </motion.div>
          
          <h2 className="text-2xl font-bold mb-2">
            {passed ? 'Congratulations!' : 'Keep Learning!'}
          </h2>
          <p className="text-dark-600">
            {passed
              ? 'You passed the quiz!'
              : `You need ${quiz.passing_score}% to pass. Try again!`}
          </p>
        </div>

        {/* Score Display */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="text-center p-4 bg-primary-50 rounded-lg">
            <p className="text-3xl font-bold text-primary-600">
              {Math.round(attempt.percentage)}%
            </p>
            <p className="text-sm text-dark-600">Your Score</p>
          </div>
          <div className="text-center p-4 bg-secondary-50 rounded-lg">
            <p className="text-3xl font-bold text-secondary-600">
              {attempt.score}/{attempt.total_points}
            </p>
            <p className="text-sm text-dark-600">Points</p>
          </div>
          <div className="text-center p-4 bg-accent-50 rounded-lg">
            <p className="text-3xl font-bold text-accent-600">
              {attempt.answers.filter((a) => a.is_correct).length}/{totalQuestions}
            </p>
            <p className="text-sm text-dark-600">Correct Answers</p>
          </div>
        </div>

        {/* Question Review */}
        <div className="mb-8">
          <h3 className="font-semibold mb-4">Review Answers</h3>
          <div className="space-y-4">
            {questions.map((question, index) => {
              const answer = attempt.answers.find((a) => a.question_id === String(question.id));
              return (
                <div
                  key={question.id}
                  className={`p-4 rounded-lg ${
                    answer?.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    {answer?.is_correct ? (
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="font-medium mb-2">
                        {index + 1}. {question.question_text}
                      </p>
                      {question.explanation && (
                        <p className="text-sm text-dark-600 bg-white/50 p-2 rounded mt-2">
                          {question.explanation}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <button onClick={handleRetry} className="btn-primary">
            <RotateCcw className="w-4 h-4 mr-2" />
            Try Again
          </button>
          {onClose && (
            <button onClick={onClose} className="btn-outline">
              Continue Learning
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  // Quiz Screen
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="card max-w-2xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">{quiz.title}</h2>
        {timeLeft !== null && (
          <div
            className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
              timeLeft < 60 ? 'bg-red-100 text-red-600' : 'bg-dark-100 text-dark-600'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span className="font-mono">{formatTime(timeLeft)}</span>
          </div>
        )}
      </div>

      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-dark-600 mb-2">
          <span>Question {currentQuestion + 1} of {totalQuestions}</span>
          <span>{Object.keys(selectedAnswers).length} answered</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-bar-fill bg-primary-600"
            style={{ width: `${((currentQuestion + 1) / totalQuestions) * 100}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          <h3 className="text-lg font-medium mb-4">{currentQ.question_text}</h3>

          {/* Options */}
          <div className="space-y-3 mb-6">
            {currentQ.options?.map((option) => (
              <button
                key={option.id}
                onClick={() => handleSelectAnswer(String(currentQ.id), option.id)}
                className={getAnswerClass(currentQ, option.id)}
              >
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                      selectedAnswers[currentQ.id] === option.id
                        ? 'border-primary-500 bg-primary-500 text-white'
                        : 'border-dark-300'
                    }`}
                  >
                    {selectedAnswers[currentQ.id] === option.id && (
                      <CheckCircle className="w-4 h-4" />
                    )}
                  </div>
                  <span>{option.text}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Explanation */}
          {showExplanation && currentQ.explanation && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Explanation:</strong> {currentQ.explanation}
              </p>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          className="btn-ghost disabled:opacity-50"
        >
          Previous
        </button>

        <div className="flex space-x-3">
          {currentQuestion < totalQuestions - 1 ? (
            <button onClick={handleNext} className="btn-primary">
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="btn-secondary"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Quiz'}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

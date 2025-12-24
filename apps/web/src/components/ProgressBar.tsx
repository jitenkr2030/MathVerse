import React from 'react';
import { motion } from 'framer-motion';

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
  striped?: boolean;
}

export default function ProgressBar({
  value,
  max = 100,
  size = 'md',
  color = 'primary',
  showLabel = false,
  label,
  animated = true,
  striped = false,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const colorClasses = {
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500',
  };

  const getColorBasedOnValue = () => {
    if (percentage < 33) return 'bg-red-500';
    if (percentage < 66) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full">
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-sm font-medium text-dark-700">{label}</span>}
          {showLabel && (
            <span className="text-sm text-dark-600">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className={`progress-bar ${sizeClasses[size]}`}>
        <motion.div
          className={`progress-bar-fill ${
            color === 'auto' ? getColorBasedOnValue() : colorClasses[color]
          } ${striped ? 'bg-opacity-50' : ''}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{
            duration: animated ? 0.5 : 0,
            ease: 'easeOut',
          }}
          style={{
            backgroundImage: striped
              ? 'linear-gradient(45deg,rgba(255,255,255,.15) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.15) 50%,rgba(255,255,255,.15) 75%,transparent 75%,transparent)'
              : undefined,
            backgroundSize: striped ? '1rem 1rem' : undefined,
          }}
        />
      </div>
    </div>
  );
}

interface CircularProgressProps {
  value: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  bgColor?: string;
  showLabel?: boolean;
  label?: string;
}

export function CircularProgress({
  value,
  size = 120,
  strokeWidth = 8,
  color = '#3b82f6',
  bgColor = '#e2e8f0',
  showLabel = false,
  label,
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={bgColor}
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>
      {(showLabel || label) && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {label && <span className="text-xs text-dark-500">{label}</span>}
          {showLabel && (
            <span className="text-2xl font-bold text-dark-800">{Math.round(value)}%</span>
          )}
        </div>
      )}
    </div>
  );
}

interface ProgressCardProps {
  title: string;
  current: number;
  total: number;
  unit?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success';
}

export function ProgressCard({
  title,
  current,
  total,
  unit = '',
  icon,
  color = 'primary',
}: ProgressCardProps) {
  const percentage = total > 0 ? (current / total) * 100 : 0;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-dark-700">{title}</h3>
        {icon && <span className="text-dark-400">{icon}</span>}
      </div>
      <div className="flex items-end justify-between mb-2">
        <span className="text-3xl font-bold text-dark-900">
          {current}
          <span className="text-lg font-normal text-dark-500">
            /{total}{unit}
          </span>
        </span>
      </div>
      <ProgressBar
        value={percentage}
        color={color === 'success' ? 'success' : color === 'secondary' ? 'secondary' : 'primary'}
        animated
      />
    </div>
  );
}

interface LearningStreakProps {
  currentStreak: number;
  longestStreak: number;
}

export function LearningStreak({ currentStreak, longestStreak }: LearningStreakProps) {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date().getDay();
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const dayIndex = (today - 6 + i + 7) % 7;
    return {
      day: days[dayIndex],
      active: i < currentStreak,
    };
  });

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-dark-700">Learning Streak</h3>
        <span className="text-2xl">🔥</span>
      </div>
      <div className="text-center mb-4">
        <span className="text-4xl font-bold text-primary-600">{currentStreak}</span>
        <span className="text-dark-600 ml-2">days</span>
      </div>
      <div className="flex justify-between">
        {last7Days.map((day, index) => (
          <div key={index} className="flex flex-col items-center">
            <span className="text-xs text-dark-500 mb-2">{day.day.charAt(0)}</span>
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                day.active
                  ? 'bg-primary-100 text-primary-600'
                  : 'bg-dark-100 text-dark-400'
              }`}
            >
              {day.active && '✓'}
            </div>
          </div>
        ))}
      </div>
      <p className="text-sm text-dark-500 mt-4 text-center">
        Longest streak: {longestStreak} days
      </p>
    </div>
  );
}

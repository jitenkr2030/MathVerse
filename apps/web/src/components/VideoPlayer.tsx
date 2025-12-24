import React, { useRef, useEffect, useState, useCallback } from 'react';
import ReactPlayer from 'react-player';
import { Play, Pause, Volume2, VolumeX, Maximize, Settings, SkipBack, SkipForward } from 'lucide-react';
import { courseService } from '@/services/courses';

interface VideoPlayerProps {
  url: string;
  lessonId: number;
  onProgress?: (progress: { played: number; playedSeconds: number }) => void;
  onComplete?: () => void;
  initialPosition?: number;
  autoPlay?: boolean;
}

export default function VideoPlayer({
  url,
  lessonId,
  onProgress,
  onComplete,
  initialPosition = 0,
  autoPlay = false,
}: VideoPlayerProps) {
  const playerRef = useRef<ReactPlayer>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [playing, setPlaying] = useState(autoPlay);
  const [volume, setVolume] = useState(0.8);
  const [muted, setMuted] = useState(false);
  const [played, setPlayed] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [loading, setLoading] = useState(true);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);

  const playbackRates = [0.5, 0.75, 1, 1.25, 1.5, 2];

  // Load saved position
  useEffect(() => {
    if (initialPosition > 0 && playerRef.current) {
      playerRef.current.seekTo(initialPosition, 'seconds');
    }
  }, [initialPosition]);

  // Hide controls after inactivity
  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    const handleMouseMove = () => {
      setShowControls(true);
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        if (playing) setShowControls(false);
      }, 3000);
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('mousemove', handleMouseMove);
      return () => {
        container.removeEventListener('mousemove', handleMouseMove);
        clearTimeout(timeout);
      };
    }
  }, [playing]);

  const handleProgress = useCallback((state: { played: number; playedSeconds: number }) => {
    setPlayed(state.played);
    
    if (onProgress) {
      onProgress(state);
    }

    // Auto-save progress every 10 seconds
    if (Math.floor(state.playedSeconds) % 10 === 0) {
      courseService.updateLessonProgress(lessonId, {
        last_position: Math.floor(state.playedSeconds),
        completion_percentage: state.played * 100,
      }).catch(console.error);
    }

    // Mark as complete when 90% watched
    if (state.played >= 0.9 && onComplete) {
      onComplete();
    }
  }, [lessonId, onProgress, onComplete]);

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const seekTo = parseFloat(e.target.value);
    setPlayed(seekTo);
    playerRef.current?.seekTo(seekTo);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    setMuted(newVolume === 0);
  };

  const toggleMute = () => {
    setMuted(!muted);
    if (muted && volume === 0) setVolume(0.8);
  };

  const skipForward = () => {
    const currentTime = playerRef.current?.getCurrentTime() || 0;
    playerRef.current?.seekTo(currentTime + 10, 'seconds');
  };

  const skipBackward = () => {
    const currentTime = playerRef.current?.getCurrentTime() || 0;
    playerRef.current?.seekTo(Math.max(0, currentTime - 10), 'seconds');
  };

  const toggleFullscreen = () => {
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        containerRef.current.requestFullscreen();
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div
      ref={containerRef}
      className="video-container group"
      onMouseLeave={() => playing && setShowControls(false)}
    >
      <ReactPlayer
        ref={playerRef}
        url={url}
        playing={playing}
        volume={volume}
        muted={muted}
        playbackRate={playbackRate}
        onProgress={handleProgress}
        onDuration={setDuration}
        onReady={() => setLoading(false)}
        width="100%"
        height="100%"
        controls={false}
      />

      {/* Custom Controls */}
      <div
        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 transition-opacity duration-300 ${
          showControls ? 'opacity-100' : 'opacity-0'
        }`}
      >
        {/* Progress Bar */}
        <div className="mb-3">
          <input
            type="range"
            min={0}
            max={1}
            step="0.001"
            value={played}
            onChange={handleSeek}
            className="w-full h-1 bg-white/30 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-primary-500 [&::-webkit-slider-thumb]:rounded-full"
          />
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Play/Pause */}
            <button
              onClick={() => setPlaying(!playing)}
              className="text-white hover:text-primary-400 transition-colors"
            >
              {playing ? <Pause size={24} /> : <Play size={24} />}
            </button>

            {/* Skip Buttons */}
            <button
              onClick={skipBackward}
              className="text-white/80 hover:text-white transition-colors"
            >
              <SkipBack size={20} />
            </button>
            <button
              onClick={skipForward}
              className="text-white/80 hover:text-white transition-colors"
            >
              <SkipForward size={20} />
            </button>

            {/* Volume */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className="text-white/80 hover:text-white transition-colors"
              >
                {muted || volume === 0 ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
              <input
                type="range"
                min={0}
                max={1}
                step="0.1"
                value={muted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-1 bg-white/30 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full"
              />
            </div>

            {/* Time */}
            <span className="text-white/80 text-sm">
              {formatTime(played * duration)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Playback Speed */}
            <div className="relative">
              <button
                onClick={() => setShowSpeedMenu(!showSpeedMenu)}
                className="text-white/80 hover:text-white text-sm font-medium transition-colors"
              >
                {playbackRate}x
              </button>
              {showSpeedMenu && (
                <div className="absolute bottom-full right-0 mb-2 bg-dark-800 rounded-lg shadow-xl py-2 min-w-[100px]">
                  {playbackRates.map((rate) => (
                    <button
                      key={rate}
                      onClick={() => {
                        setPlaybackRate(rate);
                        setShowSpeedMenu(false);
                      }}
                      className={`block w-full px-4 py-1 text-sm text-left hover:bg-dark-700 ${
                        rate === playbackRate ? 'text-primary-400' : 'text-white'
                      }`}
                    >
                      {rate}x
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="text-white/80 hover:text-white transition-colors"
            >
              <Maximize size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-dark-900/50">
          <div className="spinner w-12 h-12"></div>
        </div>
      )}
    </div>
  );
}

declare module 'react-player' {
  import React, { Component } from 'react';

  interface ReactPlayerProps {
    url?: string;
    playing?: boolean;
    loop?: boolean;
    controls?: boolean;
    light?: boolean | string;
    volume?: number;
    muted?: boolean;
    playbackRate?: number;
    width?: string | number;
    height?: string | number;
    style?: React.CSSProperties;
    progressInterval?: number;
    playsInline?: boolean;
    playIcon?: React.ReactNode;
    previewTabIndex?: number;
    onReady?: (player: any) => void;
    onStart?: () => void;
    onPlay?: () => void;
    onPause?: () => void;
    onEnded?: () => void;
    onError?: (error: any, data?: any, hlsInstance?: any, hlsGlobal?: any) => void;
    onProgress?: (state: { played: number; playedSeconds: number }) => void;
    onDuration?: (duration: number) => void;
    onSeek?: (seconds: number) => void;
  }

  export default class ReactPlayer extends Component<ReactPlayerProps> {
    seekTo: (amount: number, type?: 'seconds' | 'fraction') => void;
    getCurrentTime: () => number;
    getDuration: () => number;
    getInternalPlayer: (key?: string) => any;
  }
}

import { useEffect, useRef, useState } from 'react';

interface ProgressBarProps {
  audioRef: React.RefObject<HTMLAudioElement | null>;
  width?: number; // px, matches input width by default via CSS
  onSeek?: (fraction: number) => void;
}

/**
 * Thin horizontal progress line between the subject input and the controls.
 * Fill tracks speech playback; hovering reveals a small soft-edged square
 * cursor. Click to seek. No circles.
 */
export function ProgressBar({ audioRef, onSeek }: ProgressBarProps) {
  const [progress, setProgress] = useState(0);
  const [hoverX, setHoverX] = useState<number | null>(null);
  const lineRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const update = () => {
      if (audio.duration && Number.isFinite(audio.duration)) {
        setProgress(Math.min(1, Math.max(0, audio.currentTime / audio.duration)));
      }
    };
    const onLoaded = () => update();
    const onEnded = () => setProgress(1);

    audio.addEventListener('timeupdate', update);
    audio.addEventListener('loadedmetadata', onLoaded);
    audio.addEventListener('ended', onEnded);
    update();

    return () => {
      audio.removeEventListener('timeupdate', update);
      audio.removeEventListener('loadedmetadata', onLoaded);
      audio.removeEventListener('ended', onEnded);
    };
  }, [audioRef]);

  const fractionFromEvent = (clientX: number): number => {
    const line = lineRef.current;
    if (!line) return 0;
    const rect = line.getBoundingClientRect();
    return Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
  };

  return (
    <div
      className="progress-line"
      ref={lineRef}
      role="slider"
      aria-label="Story playback position"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(progress * 100)}
      tabIndex={0}
      onMouseMove={(e) => setHoverX(fractionFromEvent(e.clientX))}
      onMouseLeave={() => setHoverX(null)}
      onClick={(e) => onSeek?.(fractionFromEvent(e.clientX))}
      onKeyDown={(e) => {
        if (e.key === 'ArrowRight') onSeek?.(Math.min(1, progress + 0.05));
        if (e.key === 'ArrowLeft') onSeek?.(Math.max(0, progress - 0.05));
      }}
    >
      <div className="progress-line-fill" style={{ width: `${progress * 100}%` }} />
      {hoverX !== null && (
        <div
          className="progress-line-cursor"
          style={{ left: `${hoverX * 100}%` }}
        />
      )}
    </div>
  );
}

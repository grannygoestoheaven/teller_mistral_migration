import { useEffect, useRef, useState } from 'react';

interface ProgressBarProps {
  audioRef: React.RefObject<HTMLAudioElement | null>;
  backgroundRef: React.RefObject<HTMLAudioElement | null>;
  onSeek?: (fraction: number) => void;
}

/**
 * Thin horizontal progress line between the subject input and the controls.
 * Speech and music are linked (music starts at 0, speech joins at +5s), so
 * the combined experience is driven by the background track timeline:
 * progress = background.currentTime / background.duration. Falls back to
 * speech when the background track has no usable duration.
 *
 * Spotify-like scrub: while the user drags, the fill follows the pointer
 * and the cursor stays visible; playback seeks on release. Hover reveals
 * a small soft-edged square cursor. No circles.
 */
export function ProgressBar({ audioRef, backgroundRef, onSeek }: ProgressBarProps) {
  const [progress, setProgress] = useState(0);
  const [scrubFraction, setScrubFraction] = useState<number | null>(null);
  const [dragging, setDragging] = useState(false);
  const lineRef = useRef<HTMLDivElement | null>(null);

  const shown = scrubFraction ?? progress;

  useEffect(() => {
    const audio = audioRef.current;
    const background = backgroundRef.current;
    if (!audio && !background) return;

    const update = () => {
      // Linked playback: the background track is the master clock.
      const master = background && background.duration && Number.isFinite(background.duration)
        ? background
        : audio;
      if (master && master.duration && Number.isFinite(master.duration)) {
        setProgress(Math.min(1, Math.max(0, master.currentTime / master.duration)));
      }
    };
    const onEnded = () => setProgress(1);

    const targets = [audio, background].filter(Boolean) as HTMLAudioElement[];
    targets.forEach((el) => {
      el.addEventListener('timeupdate', update);
      el.addEventListener('loadedmetadata', update);
      el.addEventListener('ended', onEnded);
    });
    update();

    return () => {
      targets.forEach((el) => {
        el.removeEventListener('timeupdate', update);
        el.removeEventListener('loadedmetadata', update);
        el.removeEventListener('ended', onEnded);
      });
    };
  }, [audioRef, backgroundRef]);

  const fractionFromClientX = (clientX: number): number => {
    const line = lineRef.current;
    if (!line) return 0;
    const rect = line.getBoundingClientRect();
    return Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
  };

  const startDrag = (clientX: number) => {
    setDragging(true);
    setScrubFraction(fractionFromClientX(clientX));
  };

  const moveDrag = (clientX: number) => {
    if (dragging) setScrubFraction(fractionFromClientX(clientX));
  };

  const endDrag = (commit: boolean) => {
    if (!dragging) return;
    const fraction = scrubFraction;
    setDragging(false);
    setScrubFraction(null);
    if (commit && fraction !== null) onSeek?.(fraction);
  };

  // Global listeners so drags continue outside the thin line
  useEffect(() => {
    if (!dragging) return;
    const onMove = (e: MouseEvent) => moveDrag(e.clientX);
    const onUp = () => endDrag(true);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  });

  return (
    <div
      className={`progress-line${dragging ? ' dragging' : ''}`}
      ref={lineRef}
      role="slider"
      aria-label="Story playback position"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(shown * 100)}
      tabIndex={0}
      onMouseDown={(e) => startDrag(e.clientX)}
      onMouseMove={(e) => !dragging && setScrubFraction(fractionFromClientX(e.clientX))}
      onMouseLeave={() => !dragging && setScrubFraction(null)}
      onKeyDown={(e) => {
        if (e.key === 'ArrowRight') onSeek?.(Math.min(1, progress + 0.05));
        if (e.key === 'ArrowLeft') onSeek?.(Math.max(0, progress - 0.05));
      }}
    >
      <div className="progress-line-fill" style={{ width: `${shown * 100}%` }} />
      {scrubFraction !== null && (
        <div
          className="progress-line-cursor"
          style={{ left: `${shown * 100}%` }}
        />
      )}
    </div>
  );
}

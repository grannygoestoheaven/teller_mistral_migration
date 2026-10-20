import { useEffect, useRef, useState } from 'react';

interface ProgressBarProps {
  audioRef: React.RefObject<HTMLAudioElement | null>;
  backgroundRef: React.RefObject<HTMLAudioElement | null>;
  onSeek?: (fraction: number) => void;
  /** speech intro delay (s), outro hold (s), fade (s) — bar spans the whole experience */
  introSec?: number;
  outroHoldSec?: number;
  fadeSec?: number;
  /** true once the outro fade fully completed — bar resets to empty */
  outroDone?: boolean;
}

/**
 * Thin horizontal progress line between the subject input and the controls.
 * The bar length matches the PLAYBACK, not the music track: the story
 * timeline is speech.duration + SPEECH_START_DELAY (music starts at 0,
 * speech joins at +5s). Progress = bg.currentTime / that total, clamped
 * to 1 when the speech ends (the music outro afterwards is not "story").
 *
 * Spotify-like scrub: while the user drags, the fill follows the pointer
 * and the cursor stays visible; playback seeks on release. Hover reveals
 * a small soft-edged square cursor. No circles.
 */
export function ProgressBar({
  audioRef,
  backgroundRef,
  onSeek,
  introSec = 5,
  outroHoldSec = 30,
  fadeSec = 5,
  outroDone = false,
}: ProgressBarProps) {
  const [progress, setProgress] = useState(0);
  const [scrubFraction, setScrubFraction] = useState<number | null>(null);
  const [dragging, setDragging] = useState(false);
  const lineRef = useRef<HTMLDivElement | null>(null);

  // Fill follows the hover/scrub position in real time; the cursor does NOT. It
  // stays parked at the current playback position until a seek commits.
  const fillShown = outroDone ? 0 : scrubFraction ?? progress;
  const cursorShown = outroDone ? 0 : progress;

  useEffect(() => {
    if (outroDone) setProgress(0);
  }, [outroDone]);

  useEffect(() => {
    const audio = audioRef.current;
    const background = backgroundRef.current;
    if (!audio && !background) return;

    const update = () => {
      // The bar spans the WHOLE experience: intro (music alone), speech,
      // outro hold, fade. It fills fully exactly when the music fade ends.
      const speech = audio;
      if (
        speech &&
        speech.duration &&
        Number.isFinite(speech.duration) &&
        background &&
        Number.isFinite(background.currentTime)
      ) {
        const total = introSec + speech.duration + outroHoldSec + fadeSec;
        setProgress(Math.min(1, Math.max(0, background.currentTime / total)));
        return;
      }
      // Fallback: single-track mode (speech only)
      if (speech && speech.duration && Number.isFinite(speech.duration)) {
        setProgress(Math.min(1, Math.max(0, speech.currentTime / speech.duration)));
      }
    };
    // (Bar reset on fade completion is handled via the outroDone prop.)
    const onEnded = () => undefined;

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
      aria-valuenow={Math.round(cursorShown * 100)}
      tabIndex={0}
      onMouseDown={(e) => startDrag(e.clientX)}
      onMouseMove={(e) => !dragging && setScrubFraction(fractionFromClientX(e.clientX))}
      onMouseLeave={() => !dragging && setScrubFraction(null)}
      onKeyDown={(e) => {
        if (e.key === 'ArrowRight') onSeek?.(Math.min(1, progress + 0.05));
        if (e.key === 'ArrowLeft') onSeek?.(Math.max(0, progress - 0.05));
      }}
    >
      <div className="progress-line-fill" style={{ width: `${fillShown * 100}%` }} />
      {scrubFraction !== null && (
        <div
          className="progress-line-cursor"
          style={{ left: `${cursorShown * 100}%` }}
        />
      )}
    </div>
  );
}

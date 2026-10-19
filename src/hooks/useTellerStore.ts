import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AudioStateMachine, EventId, StateId, type StateMachineActions } from '../state/AudioStateMachine';
import { defaultFields } from '../fields/defaultFields';
import { fetchStory, sanitizeSubject } from '../services/api';
import type { StoryData, View, StorySettings } from '../types';
import { DEFAULT_SETTINGS } from '../types';

export const SQUARES_PER_WIDTH = 5;
const SPEECH_START_DELAY_MS = 5000;
const OUTRO_HOLD_MS = 10000; // hold music after speech ends
const FADE_OUT_MS = 5000; // fade music to silence

export interface Square {
  id: number;
  fullSubject: string | null;
  compactSubject: string | null;
  filledTitle: string | null;
}

export interface ButtonState {
  fromStartDisabled: boolean;
  playPauseDisabled: boolean;
  playPauseLabel: string;
}

export type DotColor = 'loading' | 'orange';

let squareIdCounter = 0;

function makeInitialSquares(): Square[] {
  const topics = Object.keys(defaultFields);
  const field = defaultFields[topics[0]];
  const count = SQUARES_PER_WIDTH * SQUARES_PER_WIDTH;
  return Array.from({ length: count }, (_, i) => ({
    id: squareIdCounter++,
    fullSubject: field.full[i] ?? null,
    compactSubject: field.compact[i] ?? null,
    filledTitle: null,
  }));
}

export function useTellerStore() {
  const [stateMachineState, setStateMachineState] = useState('IDLE');
  const [view, setView] = useState<View>('grid');
  const [inputValue, setInputValue] = useState('');
  const [squares, setSquares] = useState<Square[]>(makeInitialSquares);
  const [story, setStory] = useState<StoryData | null>(null);
  const [isStoryVisible, setIsStoryVisible] = useState(false);
  const [buttons, setButtons] = useState<ButtonState>({
    fromStartDisabled: true,
    playPauseDisabled: true,
    playPauseLabel: 'Start',
  });
  const [isBlurred, setIsBlurred] = useState(false);
  const [dotColor, setDotColor] = useState<DotColor>('loading');
  const [isMusicMuted, setIsMusicMuted] = useState(false);
  const [settings, setSettingsState] = useState<StorySettings>(() => {
    try {
      const raw = localStorage.getItem('teller_settings');
      return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  const setSettings = useCallback((next: StorySettings) => {
    setSettingsState(next);
    try {
      localStorage.setItem('teller_settings', JSON.stringify(next));
    } catch {
      /* storage unavailable */
    }
  }, []);
  const [activeSquareId, setActiveSquareId] = useState<number | null>(null);

  const speechRef = useRef<HTMLAudioElement | null>(null);
  const backgroundRef = useRef<HTMLAudioElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  // Set after clearOutroTimers is defined; lets earlier-declared callbacks
  // (resetAllAudio, abortProcess) cancel a pending outro.
  const clearOutroTimersRef = useRef<(() => void) | null>(null);
  const pendingSubjectRef = useRef<string | null>(null);
  const speechTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hasInitialSyncOccurredRef = useRef(false);
  const isPausedDuringDelayRef = useRef(false);
  const remainingDelayRef = useRef(0);

  const smRef = useRef<AudioStateMachine | null>(null);
  const [topicIndex, setTopicIndex] = useState(0);
  const topics = useMemo(() => Object.keys(defaultFields), []);

  const inputIsEmpty = useCallback(() => inputValue.trim().length === 0, [inputValue]);

  const abortProcess = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const pauseAllAudio = useCallback(() => {
    speechRef.current?.pause();
    backgroundRef.current?.pause();
    if (speechTimeoutRef.current && !hasInitialSyncOccurredRef.current) {
      clearTimeout(speechTimeoutRef.current);
      const musicPlayed = backgroundRef.current?.currentTime ?? 0;
      remainingDelayRef.current = Math.max(0, SPEECH_START_DELAY_MS - musicPlayed * 1000);
      isPausedDuringDelayRef.current = true;
    }
  }, []);

  const resumeAllAudio = useCallback(() => {
    backgroundRef.current?.play();
    if (isPausedDuringDelayRef.current) {
      delaySpeechStart(remainingDelayRef.current);
      isPausedDuringDelayRef.current = false;
    } else if (speechRef.current && !speechRef.current.ended) {
      speechRef.current.play();
    }
  }, []);

  const resetAllAudio = useCallback(() => {
    clearOutroTimersRef.current?.();
    if (speechRef.current) speechRef.current.currentTime = 0;
    if (backgroundRef.current) backgroundRef.current.currentTime = 0;
  }, []);

  const delaySpeechStart = useCallback((ms: number = SPEECH_START_DELAY_MS) => {
    if (speechTimeoutRef.current) clearTimeout(speechTimeoutRef.current);
    remainingDelayRef.current = ms;
    speechTimeoutRef.current = setTimeout(() => {
      if (backgroundRef.current && !backgroundRef.current.paused) {
        speechRef.current?.play();
        hasInitialSyncOccurredRef.current = true;
      } else {
        isPausedDuringDelayRef.current = true;
      }
    }, ms);
  }, []);

  const setUpAndStartAllAudio = useCallback(() => {
    if (backgroundRef.current) {
      backgroundRef.current.volume = 0.03;
      backgroundRef.current.play();
    }
    delaySpeechStart();
  }, [delaySpeechStart]);

  const fadeOutRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const outroTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearOutroTimers = useCallback(() => {
    if (fadeOutRef.current) {
      clearInterval(fadeOutRef.current);
      fadeOutRef.current = null;
    }
    if (outroTimeoutRef.current) {
      clearTimeout(outroTimeoutRef.current);
      outroTimeoutRef.current = null;
    }
    // restore music volume if a fade was in progress
    const bg = backgroundRef.current;
    if (bg && bg.paused && bg.volume === 0) {
      bg.volume = 0.03;
    }
  }, []);
  clearOutroTimersRef.current = clearOutroTimers;

  // Fade the background track to 0 over FADE_OUT_MS using a stepped ramp
  // (plain <audio> volume has no native ramp; Web Audio API is the future
  // pro path for this).
  const fadeOutBackground = useCallback((ms: number) => {
    const bg = backgroundRef.current;
    if (!bg) return;
    if (fadeOutRef.current) clearInterval(fadeOutRef.current);
    const startVolume = bg.volume;
    const steps = 20;
    const stepMs = ms / steps;
    let step = 0;
    fadeOutRef.current = setInterval(() => {
      step += 1;
      bg.volume = Math.max(0, startVolume * (1 - step / steps));
      if (step >= steps) {
        bg.pause();
        bg.volume = startVolume; // restore for next playback
        if (fadeOutRef.current) clearInterval(fadeOutRef.current);
        fadeOutRef.current = null;
      }
    }, stepMs);
  }, []);

  const beginOutro = useCallback(() => {
    // Playback ends 10s after speech ends: hold, then fade music 5s, then done.
    clearOutroTimers();
    outroTimeoutRef.current = setTimeout(() => {
      outroTimeoutRef.current = null;
      fadeOutBackground(FADE_OUT_MS);
      outroTimeoutRef.current = setTimeout(() => {
        outroTimeoutRef.current = null;
        smRef.current?.dispatchEvent(EventId.MUSIC_OVER);
      }, FADE_OUT_MS);
    }, OUTRO_HOLD_MS);
  }, [clearOutroTimers, fadeOutBackground]);

  const startNewStoryProcessForm = useCallback(async () => {
    const pending = pendingSubjectRef.current;
    pendingSubjectRef.current = null;
    let subject = (pending ?? inputValue).trim() || 'emptiness';
    subject = sanitizeSubject(subject);
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    try {
      const data = await fetchStory(subject, settings, abortRef.current.signal);
      setStory(data);
      const speechEl = speechRef.current;
      if (speechEl && data.speechUrl) {
        speechEl.src = data.speechUrl;
      }
      const bgEl = backgroundRef.current;
      if (bgEl && data.trackUrl) {
        bgEl.src = data.trackUrl;
        bgEl.loop = false;
      }
      setIsStoryVisible(false);
      hasInitialSyncOccurredRef.current = false;
      isPausedDuringDelayRef.current = false;
      setSquares((prev) => {
        const available = prev.filter((s) => s.filledTitle === null);
        if (available.length === 0 || !data.storyTitle) return prev;
        const target = available[Math.floor(Math.random() * available.length)];
        return prev.map((s) => (s.id === target.id ? { ...s, filledTitle: data.storyTitle } : s));
      });
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      console.error('Story process failed:', err);
      smRef.current?.dispatchEvent(EventId.CANCEL);
    }
  }, [inputValue, settings]);

  const actions: StateMachineActions = useMemo(
    () => ({
      abortProcess,
      gridView: () => setView('grid'),
      pauseAllAudio,
      resetAllAudio,
      uiIdleButtons: () =>
        setButtons({ fromStartDisabled: true, playPauseDisabled: true, playPauseLabel: 'Start' }),
      initInputAdjustments: () => {},
      uiLoadingButtons: () =>
        setButtons({ fromStartDisabled: true, playPauseDisabled: true, playPauseLabel: 'Loading' }),
      removeBlurr: () => setIsBlurred(false),
      dotsView: () => setView('dots'),
      loadingDots: () => setDotColor('loading'),
      addTitleToSquare: () => {},
      setUpAndStartAllAudio,
      displayStoryText: () => setIsStoryVisible(true),
      wrapWordsInSpans: () => {},
      uiPausedButtons: () =>
        setButtons({ fromStartDisabled: false, playPauseDisabled: false, playPauseLabel: 'Resume' }),
      addBlurr: () => {},
      resumeAllAudio,
      uiPlayingButtons: () =>
        setButtons({ fromStartDisabled: false, playPauseDisabled: false, playPauseLabel: 'Pause' }),
      orangeDots: () => setDotColor('orange'),
      beginOutro,
      clearOutroTimers,
      textView: () => setView('text'),
      uiReadyButtons: () =>
        setButtons({ fromStartDisabled: true, playPauseDisabled: false, playPauseLabel: 'Start' }),
      startNewStoryProcessForm: () => {
        void startNewStoryProcessForm();
      },
      inputIsEmpty,
    }),
    [
      abortProcess,
      pauseAllAudio,
      resetAllAudio,
      setUpAndStartAllAudio,
      resumeAllAudio,
      beginOutro,
      clearOutroTimers,
      startNewStoryProcessForm,
      inputIsEmpty,
      view,
    ]
  );

  if (!smRef.current) {
    const sm = new AudioStateMachine();
    sm.actions = actions;
    sm.start();
    smRef.current = sm;
  } else {
    smRef.current.actions = actions;
  }

  const dispatch = useCallback((eventId: EventId) => {
    const sm = smRef.current;
    if (!sm) return;
    sm.dispatchEvent(eventId);
    setStateMachineState(StateId[sm.stateId]);
  }, []);

  useEffect(() => {
    const speech = speechRef.current;
    if (!speech) return;
    const onCanPlayThrough = () => dispatch(EventId.SPEECH_READY);
    const onEnded = () => dispatch(EventId.SPEECH_OVER);
    speech.addEventListener('canplaythrough', onCanPlayThrough);
    speech.addEventListener('ended', onEnded);
    return () => {
      speech.removeEventListener('canplaythrough', onCanPlayThrough);
      speech.removeEventListener('ended', onEnded);
    };
  }, [dispatch, story]);

  useEffect(() => {
    const bg = backgroundRef.current;
    if (!bg) return;
    const onEnded = () => dispatch(EventId.MUSIC_OVER);
    bg.addEventListener('ended', onEnded);
    return () => bg.removeEventListener('ended', onEnded);
  }, [dispatch]);

  const seekToFraction = useCallback((fraction: number) => {
    const bg = backgroundRef.current;
    const speech = speechRef.current;
    // The story timeline is speech.duration + 5s intro (music starts at 0,
    // speech joins at +5s). fraction maps to that timeline, not the music
    // track length.
    if (
      speech &&
      speech.duration &&
      Number.isFinite(speech.duration) &&
      bg
    ) {
      const total = speech.duration + SPEECH_START_DELAY_MS / 1000;
      const t = fraction * total;
      bg.currentTime = Math.min(bg.duration, t);
      const speechT = t - SPEECH_START_DELAY_MS / 1000;
      speech.currentTime = speechT <= 0 ? 0 : Math.min(speech.duration, speechT);
      return;
    }
    // Fallback: seek speech only
    if (speech && speech.duration && Number.isFinite(speech.duration)) {
      speech.currentTime = fraction * speech.duration;
    }
  }, []);

  const rewind5Seconds = useCallback(() => {
    if (speechRef.current) {
      speechRef.current.currentTime = Math.max(0, speechRef.current.currentTime - 5);
    }
    if (backgroundRef.current) {
      backgroundRef.current.currentTime = Math.max(0, backgroundRef.current.currentTime - 5);
    }
  }, []);

  const forward5Seconds = useCallback(() => {
    if (speechRef.current && speechRef.current.duration) {
      speechRef.current.currentTime = Math.min(
        speechRef.current.duration,
        speechRef.current.currentTime + 5
      );
    }
    if (backgroundRef.current && backgroundRef.current.duration) {
      backgroundRef.current.currentTime = Math.min(
        backgroundRef.current.duration,
        backgroundRef.current.currentTime + 5
      );
    }
  }, []);

  const toggleMusicMute = useCallback(() => {
    if (backgroundRef.current) {
      backgroundRef.current.volume = isMusicMuted ? 0.03 : 0;
    }
    setIsMusicMuted(!isMusicMuted);
  }, [isMusicMuted]);

  const cycleTopic = useCallback(() => {
    setTopicIndex((prev) => {
      const next = (prev + 1) % topics.length;
      const field = defaultFields[topics[next]];
      setSquares((prevSquares) =>
        prevSquares.map((s, i) => ({
          ...s,
          fullSubject: field.full[i] ?? null,
          compactSubject: field.compact[i] ?? null,
        }))
      );
      return next;
    });
  }, [topics]);

  const handleSquareMouseDown = useCallback(
    (squareId: number) => {
      const square = squares.find((s) => s.id === squareId);
      if (!square) return;
      setActiveSquareId(squareId);
      if (square.filledTitle) {
        pendingSubjectRef.current = square.filledTitle;
        setInputValue(square.filledTitle);
        dispatch(EventId.SQUARE_CLICKED);
      }
    },
    [squares, dispatch]
  );

  const handleSquareMouseEnter = useCallback(
    (squareId: number) => {
      const square = squares.find((s) => s.id === squareId);
      if (!square) return;
      setActiveSquareId(squareId);
      if (square.filledTitle) {
        setInputValue(square.filledTitle);
        dispatch(EventId.INPUT_CHANGED);
      }
    },
    [squares, dispatch]
  );

  const toggleView = useCallback(() => {
    setView((prev) => {
      if (prev === 'grid') return 'dots';
      if (prev === 'dots') return 'text';
      return 'grid';
    });
  }, []);

  return {
    stateMachineState,
    view,
    inputValue,
    setInputValue,
    squares,
    story,
    isStoryVisible,
    buttons,
    isBlurred,
    dotColor,
    isMusicMuted,
    speechRef,
    backgroundRef,
    inputRef,
    dispatch,
    rewind5Seconds,
    forward5Seconds,
    seekToFraction,
    toggleMusicMute,
    toggleView,
    cycleTopic,
    topics,
    topicIndex,
    handleSquareMouseDown,
    handleSquareMouseEnter,
    settings,
    setSettings,
  };
}

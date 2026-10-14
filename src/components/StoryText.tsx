import { useCallback, useMemo, useRef, useState } from 'react';
import type { MouseEvent } from 'react';
import type { StoryData } from '../types';

interface StoryTextProps {
  story: StoryData | null;
  visible: boolean;
  blurred: boolean;
  onWordsSelected: (title: string) => void;
  wrapKey: string;
}

export function StoryText({ story, visible, blurred, onWordsSelected, wrapKey }: StoryTextProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const highlightedRef = useRef<Set<HTMLSpanElement>>(new Set());

  const words = useMemo(() => {
    if (!story) return [];
    return story.story
      .trim()
      .split(/([\s—–-]+)/)
      .filter((part) => !/^\s+$/.test(part));
  }, [story]);

  const clearHighlights = useCallback(() => {
    highlightedRef.current.forEach((span) => span.classList.remove('highlight-word'));
    highlightedRef.current.clear();
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent<HTMLDivElement>) => {
      const target = e.target as HTMLElement;
      if (!target.classList.contains('word')) {
        clearHighlights();
        return;
      }
      const span = target as HTMLSpanElement;
      clearHighlights();
      const rect = span.getBoundingClientRect();
      const mouseYRelative = e.clientY - rect.top;
      const zone = 10 - Math.floor((mouseYRelative / rect.height) * 10);
      let current: HTMLElement | null = span;
      for (let i = 0; i < zone && current; i++) {
        current.classList.add('highlight-word');
        highlightedRef.current.add(current as HTMLSpanElement);
        current = current.nextElementSibling as HTMLElement | null;
      }
    },
    [clearHighlights]
  );

  const handleMouseOut = useCallback(
    (e: MouseEvent<HTMLDivElement>) => {
      if (!e.relatedTarget || !containerRef.current?.contains(e.relatedTarget as Node)) {
        clearHighlights();
      }
    },
    [clearHighlights]
  );

  const handleClick = useCallback(
    (e: MouseEvent<HTMLDivElement>) => {
      const target = e.target as HTMLElement;
      if (!target.classList.contains('highlight-word')) return;
      const highlighted = Array.from(
        containerRef.current?.querySelectorAll('.highlight-word') ?? []
      ) as HTMLElement[];
      const cleanTitle = highlighted
        .map((span) => span.textContent?.trim() ?? '')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1).replace(/[.,"]/g, ''))
        .join(' ');
      if (cleanTitle) onWordsSelected(cleanTitle);
    },
    [onWordsSelected]
  );

  return (
    <div className="chat-history" id="chatHistory">
      <div
        ref={containerRef}
        key={wrapKey}
        id="story"
        className={`chat-inner caprasimo-regular ${visible ? 'visible' : 'hidden'} ${
          blurred ? 'blurred' : ''
        }`}
        onMouseMove={handleMouseMove}
        onMouseOut={handleMouseOut}
        onClick={handleClick}
      >
        {words.map((word, i) => (
          <span key={i} className="word">
            {word}
            {i < words.length - 1 ? ' ' : ''}
          </span>
        ))}
      </div>
    </div>
  );
}

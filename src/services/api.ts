import type { StoryCheckResponse, StoryData, StorySettings } from '../types';

export function sanitizeSubject(subject: string): string {
  return subject
    .toLowerCase()
    .trim()
    .replace(/[^\w\-_]/g, '_')
    .replace(/_{2,}/g, '_');
}

async function postJson<T>(url: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.error || errorData?.detail || `Error ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function checkStory(
  subject: string,
  settings: StorySettings,
  signal?: AbortSignal
): Promise<StoryCheckResponse> {
  return postJson<StoryCheckResponse>('/api/v1/stories/check_story', { subject, ...settings }, signal);
}

export function newStory(
  subject: string,
  settings: StorySettings,
  signal?: AbortSignal
): Promise<StoryData> {
  return postJson<StoryData>(
    '/api/v1/stories/new_story',
    { subject, ...settings },
    signal
  );
}

export async function fetchStory(
  subject: string,
  settings: StorySettings,
  signal?: AbortSignal
): Promise<StoryData> {
  const { exists, story } = await checkStory(subject, settings, signal);
  if (exists && story) return story;
  return newStory(subject, settings, signal);
}

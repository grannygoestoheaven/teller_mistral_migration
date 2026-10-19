export interface StoryData {
  storyFilename: string;
  storyTitle: string;
  story: string;
  speechUrl: string;
  trackUrl: string;
  trackTitle: string;
}

export interface StoryCheckResponse {
  exists: boolean;
  story: StoryData | null;
}

export type TopicField = {
  full: string[];
  compact: string[];
};

export type View = 'grid' | 'dots' | 'text';

export type SquareData = {
  id: number;
  fullSubject: string | null;
  compactSubject: string | null;
  filledTitle: string | null;
  isPlayed: boolean;
};

export type Approach =
  | 'dual_coding'
  | 'desirable_difficulty'
  | 'embodied_cognition'
  | 'caveman_teacher'
  | 'pne_no_tags';
export type Audience = 'kids' | 'grown-ups';
export type StoryLength = 'short' | 'long';

export interface StorySettings {
  approach: Approach;
  audience: Audience;
  length: StoryLength;
}

export const DEFAULT_SETTINGS: StorySettings = {
  approach: 'dual_coding',
  audience: 'grown-ups',
  length: 'long',
};

import type { Approach, Audience, StoryLength, StorySettings } from '../types';

interface SettingsPanelProps {
  settings: StorySettings;
  onChange: (next: StorySettings) => void;
}

function ShortTextIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
      <line x1="4" y1="6" x2="20" y2="6" stroke="currentColor" strokeWidth="2" />
      <line x1="4" y1="12" x2="14" y2="12" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

function LongTextIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
      <line x1="4" y1="4" x2="20" y2="4" stroke="currentColor" strokeWidth="2" />
      <line x1="4" y1="8" x2="20" y2="8" stroke="currentColor" strokeWidth="2" />
      <line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" strokeWidth="2" />
      <line x1="4" y1="16" x2="20" y2="16" stroke="currentColor" strokeWidth="2" />
      <line x1="4" y1="20" x2="14" y2="20" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

// dual_coding kept in backend (types + router) but hidden from the menu for now
const APPROACHES: { value: Approach; label: string }[] = [
  { value: 'caveman_teacher', label: 'Caveman Teacher' },
  { value: 'pne_no_tags', label: 'PNE no tags' },
  { value: 'desirable_difficulty', label: 'Desirable Difficulty' },
  { value: 'embodied_cognition', label: 'Embodied Cognition' },
];

const AUDIENCES: { value: Audience; label: string }[] = [
  { value: 'kids', label: 'kids' },
  { value: 'grown-ups', label: 'grown-ups' },
];

const LENGTHS: { value: StoryLength; label: string }[] = [
  { value: 'short', label: 'short' },
  { value: 'long', label: 'long' },
];

export function SettingsPanel({ settings, onChange }: SettingsPanelProps) {
  return (
    <div className="settings-panel" id="settingsPanel">
      <div className="settings-row">
        {LENGTHS.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            className={`settings-button ${settings.length === value ? 'lit' : ''}`}
            title={label}
            onClick={() => onChange({ ...settings, length: value })}
          >
            {value === 'short' ? <ShortTextIcon /> : <LongTextIcon />}
          </button>
        ))}
      </div>
      <div className="settings-row">
        {APPROACHES.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            className={`settings-button ${settings.approach === value ? 'lit' : ''}`}
            title={label}
            onClick={() => onChange({ ...settings, approach: value })}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="settings-row">
        {AUDIENCES.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            className={`settings-button ${settings.audience === value ? 'lit' : ''}`}
            title={label}
            onClick={() => onChange({ ...settings, audience: value })}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

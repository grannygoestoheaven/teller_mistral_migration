import { useEffect } from 'react';
import { EventId } from './state/AudioStateMachine';
import { useTellerStore } from './hooks/useTellerStore';
import { SubjectGrid } from './components/SubjectGrid';
import { LoadingDots } from './components/LoadingDots';
import { StoryText } from './components/StoryText';

export default function App() {
  const teller = useTellerStore();
  const {
    view,
    inputValue,
    setInputValue,
    squares,
    story,
    buttons,
    isBlurred,
    dotColor,
    isMusicMuted,
    speechRef,
    backgroundRef,
    dispatch,
    rewind5Seconds,
    forward5Seconds,
    toggleMusicMute,
    toggleView,
    cycleTopic,
    handleSquareMouseDown,
    handleSquareMouseEnter,
  } = teller;

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && document.activeElement?.tagName !== 'INPUT') {
        e.preventDefault();
        dispatch(EventId.TOGGLE_PAUSE_RESUME);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [dispatch]);

  return (
    <>
      <header className="chat-header">
        <h1 className="brand" id="teller-title" translate="no" onClick={cycleTopic}>
          teller
        </h1>
      </header>

      <div className="toggle-grid-text" id="toggleGridText">
        <button className="toggle-button" id="toggleBtn" onClick={toggleView}>
          ooo
        </button>
        <button className="music-button" id="musicBtn" onClick={toggleMusicMute}>
          {isMusicMuted ? 'music off' : 'music on'}
        </button>
      </div>

      <div className="toggle-container" id="toggleContainer">
        <SubjectGrid
          squares={squares}
          visible={view === 'grid'}
          onSquareEnter={handleSquareMouseEnter}
          onSquareDown={handleSquareMouseDown}
        />
        <LoadingDots visible={view === 'dots'} color={dotColor} />
        <StoryText
          story={story}
          visible={view === 'text'}
          blurred={isBlurred}
          wrapKey={story?.storyFilename ?? 'empty'}
          onWordsSelected={(title) => {
            setInputValue(title);
            dispatch(EventId.INPUT_CHANGED);
          }}
        />
      </div>

      <div className="audio-player-container" id="audioPlayerContainer">
        <audio id="speechAudio" preload="auto" crossOrigin="anonymous" ref={speechRef} />
        <audio id="backgroundAudio" preload="auto" loop ref={backgroundRef} />
        <div id="story-title-display" className="story-title-display"></div>
      </div>

      <footer className="chat-input-area">
        <form
          id="storyForm"
          onSubmit={(e) => {
            e.preventDefault();
            dispatch(EventId.FORM_SUBMITTED);
          }}
        >
          <div className="form-fields-container">
            <div className="form-group subject-input-group">
              <input
                type="text"
                id="subject"
                className="fill space"
                name="subject"
                placeholder="Enter a subject, ex: 'Quantum Physics'"
                required
                value={inputValue}
                onChange={(e) => {
                  setInputValue(e.target.value);
                  dispatch(EventId.INPUT_CHANGED);
                }}
                onBlur={() => dispatch(EventId.INPUT_DEFOCUSED)}
              />
            </div>
            <div className="controls">
              <button
                type="button"
                className="rewind-and-forward-buttons"
                onClick={rewind5Seconds}
              >
                -5SEC
              </button>
              <button
                type="button"
                className="send-button pixel-play"
                onClick={() => dispatch(EventId.FROM_START_CLICKED)}
              >
                Replay
              </button>
              <button
                type="button"
                className="send-button pixel-play"
                onClick={() => dispatch(EventId.TOGGLE_PAUSE_RESUME)}
              >
                {buttons.playPauseLabel}
              </button>
              <button
                type="button"
                className="rewind-and-forward-buttons"
                onClick={forward5Seconds}
              >
                +5SEC
              </button>
            </div>
          </div>
        </form>
      </footer>
    </>
  );
}

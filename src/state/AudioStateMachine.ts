export enum EventId {
  CANCEL = 0,
  FORM_SUBMITTED = 1,
  FROM_START_CLICKED = 2,
  INPUT_CHANGED = 3,
  INPUT_DEFOCUSED = 4,
  MUSIC_OVER = 5,
  SPEECH_OVER = 6,
  SPEECH_READY = 7,
  SQUARE_CLICKED = 8,
  TOGGLE_PAUSE_RESUME = 9,
}

export enum StateId {
  ROOT = 0,
  IDLE = 1,
  LOADING = 2,
  PAUSED = 3,
  PLAYING = 4,
  READY_DURING_IDLE = 5,
  READY_DURING_PAUSED = 6,
  READY_DURING_PLAYBACK = 7,
}

export interface StateMachineActions {
  abortProcess(): void;
  gridView(): void;
  pauseAllAudio(): void;
  resetAllAudio(): void;
  uiIdleButtons(): void;
  initInputAdjustments(): void;
  uiLoadingButtons(): void;
  removeBlurr(): void;
  dotsView(): void;
  loadingDots(): void;
  addTitleToSquare(): void;
  setUpAndStartAllAudio(): void;
  displayStoryText(): void;
  wrapWordsInSpans(): void;
  uiPausedButtons(): void;
  addBlurr(): void;
  resumeAllAudio(): void;
  uiPlayingButtons(): void;
  orangeDots(): void;
  bothTracksEnded(): boolean;
  textView(): void;
  uiReadyButtons(): void;
  startNewStoryProcessForm(): void;
  inputIsEmpty(): boolean;
}

export class AudioStateMachine {
  stateId: StateId = StateId.ROOT;
  actions!: StateMachineActions;

  start(): void {
    this.stateId = StateId.ROOT;
    this.transitionTo(StateId.IDLE);
  }

  dispatchEvent(eventId: EventId): void {
    switch (this.stateId) {
      case StateId.IDLE:
        if (eventId === EventId.INPUT_CHANGED) this.transitionTo(StateId.READY_DURING_IDLE);
        else if (eventId === EventId.FROM_START_CLICKED) {
          this.actions.resetAllAudio();
          this.actions.resumeAllAudio();
          this.transitionTo(StateId.PLAYING);
        }
        break;

      case StateId.LOADING:
        if (eventId === EventId.CANCEL) this.transitionTo(StateId.IDLE);
        else if (eventId === EventId.SPEECH_READY) {
          this.actions.addTitleToSquare();
          this.actions.setUpAndStartAllAudio();
          this.actions.displayStoryText();
          this.actions.wrapWordsInSpans();
          this.transitionTo(StateId.PLAYING);
        } else if (eventId === EventId.TOGGLE_PAUSE_RESUME) {
          this.actions.pauseAllAudio();
          this.transitionTo(StateId.PAUSED);
        }
        break;

      case StateId.PAUSED:
        if (eventId === EventId.INPUT_CHANGED) this.transitionTo(StateId.READY_DURING_PAUSED);
        else if (eventId === EventId.TOGGLE_PAUSE_RESUME) {
          this.actions.resumeAllAudio();
          this.transitionTo(StateId.PLAYING);
        } else if (eventId === EventId.FROM_START_CLICKED) {
          this.actions.resetAllAudio();
          this.actions.resumeAllAudio();
          this.transitionTo(StateId.PLAYING);
        } else if (eventId === EventId.CANCEL) this.transitionTo(StateId.IDLE);
        break;

      case StateId.PLAYING:
        if (eventId === EventId.SPEECH_OVER) this.actions.textView();
        else if (eventId === EventId.TOGGLE_PAUSE_RESUME) {
          this.actions.pauseAllAudio();
          this.transitionTo(StateId.PAUSED);
        } else if (eventId === EventId.FROM_START_CLICKED) {
          this.actions.resetAllAudio();
          this.actions.resumeAllAudio();
          this.transitionTo(StateId.PLAYING);
        } else if (eventId === EventId.INPUT_CHANGED) this.transitionTo(StateId.READY_DURING_PLAYBACK);
        else if (eventId === EventId.MUSIC_OVER) {
          if (this.actions.bothTracksEnded()) {
            this.actions.resetAllAudio();
            this.transitionTo(StateId.IDLE);
          }
        } else if (eventId === EventId.CANCEL) this.transitionTo(StateId.IDLE);
        break;

      case StateId.READY_DURING_IDLE:
        if (eventId === EventId.CANCEL) this.transitionTo(StateId.IDLE);
        else if (eventId === EventId.FORM_SUBMITTED || eventId === EventId.SQUARE_CLICKED) {
          this.actions.startNewStoryProcessForm();
          this.transitionTo(StateId.LOADING);
        } else if (eventId === EventId.FROM_START_CLICKED) {
          this.actions.resumeAllAudio();
          this.transitionTo(StateId.PLAYING);
        } else if (eventId === EventId.INPUT_DEFOCUSED) {
          this.transitionTo(StateId.IDLE);
        } else if (eventId === EventId.TOGGLE_PAUSE_RESUME) {
          if (!this.actions.inputIsEmpty()) {
            this.actions.startNewStoryProcessForm();
            this.transitionTo(StateId.LOADING);
          }
        }
        break;

      case StateId.READY_DURING_PAUSED:
        if (eventId === EventId.CANCEL) this.transitionTo(StateId.IDLE);
        else if (eventId === EventId.FORM_SUBMITTED || eventId === EventId.SQUARE_CLICKED) {
          this.actions.startNewStoryProcessForm();
          this.transitionTo(StateId.LOADING);
        } else if (eventId === EventId.INPUT_DEFOCUSED) this.transitionTo(StateId.PAUSED);
        else if (eventId === EventId.TOGGLE_PAUSE_RESUME) {
          if (!this.actions.inputIsEmpty()) {
            this.actions.startNewStoryProcessForm();
            this.transitionTo(StateId.LOADING);
          }
        }
        break;

      case StateId.READY_DURING_PLAYBACK:
        if (eventId === EventId.CANCEL) this.transitionTo(StateId.IDLE);
        else if (eventId === EventId.FORM_SUBMITTED || eventId === EventId.SQUARE_CLICKED) {
          this.actions.startNewStoryProcessForm();
          this.transitionTo(StateId.LOADING);
        } else if (eventId === EventId.INPUT_DEFOCUSED) this.transitionTo(StateId.PLAYING);
        else if (eventId === EventId.TOGGLE_PAUSE_RESUME) {
          if (!this.actions.inputIsEmpty()) {
            this.actions.startNewStoryProcessForm();
            this.transitionTo(StateId.LOADING);
          }
        }
        break;

      case StateId.ROOT:
        break;
    }
  }

  private transitionTo(target: StateId): void {
    this.stateId = target;
    switch (target) {
      case StateId.IDLE:
        this.actions.abortProcess();
        this.actions.gridView();
        this.actions.pauseAllAudio();
        this.actions.resetAllAudio();
        this.actions.uiIdleButtons();
        this.actions.initInputAdjustments();
        break;
      case StateId.LOADING:
        this.actions.uiLoadingButtons();
        this.actions.removeBlurr();
        this.actions.dotsView();
        this.actions.loadingDots();
        break;
      case StateId.PAUSED:
        this.actions.uiPausedButtons();
        this.actions.addBlurr();
        break;
      case StateId.PLAYING:
        this.actions.uiPlayingButtons();
        this.actions.removeBlurr();
        this.actions.orangeDots();
        break;
      case StateId.READY_DURING_IDLE:
      case StateId.READY_DURING_PAUSED:
      case StateId.READY_DURING_PLAYBACK:
        this.actions.uiReadyButtons();
        break;
      default:
        break;
    }
  }
}

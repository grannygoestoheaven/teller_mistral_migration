/**
 * Web Audio engine for the teller player.
 *
 * Both <audio> elements are routed through a single AudioContext via
 * createMediaElementSource. Each track gets a GainNode: all volume changes
 * and fades go through gain.value / linearRampToValueAtTime (sample-accurate,
 * no timers, no interval ramps, no mute locks).
 *
 * A gain of 0 is physically silent: after the music fade completes there is
 * no code path that can produce audible music, by construction.
 *
 * Constraints kept intentionally minimal:
 * - The <audio> elements remain the media clock (play/pause/currentTime).
 * - The engine owns gain only (volume, fade, mute).
 */

export const MUSIC_VOLUME = 0.03;
export const FADE_MS = 5000;

export class AudioEngine {
  private ctx: AudioContext | null = null;
  private speechGain: GainNode | null = null;
  private musicGain: GainNode | null = null;
  private sources = new WeakMap<HTMLMediaElement, MediaElementAudioSourceNode>();
  private connected = new WeakSet<HTMLMediaElement>();

  /**
   * Wire an audio element into the graph (idempotent per element).
   * Must be called after a user gesture (browser autoplay policy) — the
   * first play() click qualifies.
   *
   * IMPORTANT: elements feeding the graph MUST carry crossOrigin="anonymous"
   * in the JSX; a cross-origin resource without CORS yields silence when
   * routed through createMediaElementSource (tainted output).
   */
  attach(el: HTMLMediaElement): void {
    if (!this.ctx) {
      const Ctor: typeof AudioContext =
        window.AudioContext ??
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new Ctor();
      this.speechGain = this.ctx.createGain();
      this.musicGain = this.ctx.createGain();
      this.speechGain.connect(this.ctx.destination);
      this.musicGain.connect(this.ctx.destination);
    }
    if (this.ctx.state === 'suspended') {
      void this.ctx.resume();
    }
    if (this.sources.has(el) || this.connected.has(el)) return;
    const src = this.ctx.createMediaElementSource(el);
    const elId = el.id;
    src.connect(elId === 'backgroundAudio' ? this.musicGain! : this.speechGain!);
    this.sources.set(el, src);
    this.connected.add(el);
  }

  /** Resume the context (user gesture). Safe to call often. */
  unlock(): void {
    if (this.ctx && this.ctx.state === 'suspended') void this.ctx.resume();
  }

  private ramp(gain: GainNode, to: number, ms: number): void {
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const param = gain.gain;
    param.cancelScheduledValues(now);
    param.setValueAtTime(param.value, now);
    param.linearRampToValueAtTime(to, now + ms / 1000);
  }

  // ---- Music ----

  musicVolume(to: number): void {
    if (!this.musicGain || !this.ctx) return;
    const now = this.ctx.currentTime;
    const param = this.musicGain.gain;
    param.cancelScheduledValues(now);
    param.setValueAtTime(to, now);
  }

  /** Smooth fade of the music to the given volume over ms. */
  fadeMusic(to: number, ms: number): void {
    if (!this.musicGain) return;
    this.ramp(this.musicGain, to, ms);
  }

  // ---- Speech ----

  speechVolume(to: number): void {
    if (!this.speechGain || !this.ctx) return;
    const now = this.ctx.currentTime;
    const param = this.speechGain.gain;
    param.cancelScheduledValues(now);
    param.setValueAtTime(to, now);
  }

  /** Current music gain (0..1). */
  get musicGainValue(): number {
    return this.musicGain?.gain.value ?? MUSIC_VOLUME;
  }
}

export const audioEngine = new AudioEngine();

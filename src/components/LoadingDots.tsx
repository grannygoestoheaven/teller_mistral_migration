interface LoadingDotsProps {
  visible: boolean;
  color: 'loading' | 'orange';
}

export function LoadingDots({ visible, color }: LoadingDotsProps) {
  return (
    <div
      id="loadingAnimationContainer"
      className={`loading-animation-container ${visible ? 'visible' : 'hidden'}`}
    >
      <div id="loadingAnimation" className={`loading-animation dots-${color}`}>
        <span className="period period-1">.</span>
        <span className="period period-2">.</span>
        <span className="period period-3">.</span>
      </div>
    </div>
  );
}

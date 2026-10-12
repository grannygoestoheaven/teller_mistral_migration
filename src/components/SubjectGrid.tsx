import type { Square } from '../hooks/useTellerStore';

interface SubjectGridProps {
  squares: Square[];
  visible: boolean;
  onSquareEnter: (id: number) => void;
  onSquareDown: (id: number) => void;
}

export function SubjectGrid({ squares, visible, onSquareEnter, onSquareDown }: SubjectGridProps) {
  return (
    <div
      id="gridContainer"
      className={`grid-container ${visible ? 'visible' : 'hidden'}`}
    >
      {squares.map((square) => (
        <div
          key={square.id}
          className={`square ${square.filledTitle ? 'square-filled' : ''}`}
          tabIndex={0}
          onMouseEnter={() => onSquareEnter(square.id)}
          onMouseDown={() => onSquareDown(square.id)}
        />
      ))}
    </div>
  );
}

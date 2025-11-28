import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:3000');

function App() {
  const [gameState, setGameState] = useState({
    board: Array(9).fill(null),
    xIsNext: true,
  });

  useEffect(() => {
    socket.on('gameState', (state) => {
      setGameState(state);
    });

    return () => socket.off('gameState');
  }, []);

  const handleClick = (index) => {
    if (gameState.board[index] || calculateWinner(gameState.board)) return;
    socket.emit('makeMove', index);
  };

  const calculateWinner = (board) => {
    const lines = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8],
      [0, 3, 6], [1, 4, 7], [2, 5, 8],
      [0, 4, 8], [2, 4, 6]
    ];
    for (let [a, b, c] of lines) {
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }
    return null;
  };

  const winner = calculateWinner(gameState.board);
  const status = winner 
    ? `Winner: ${winner}` 
    : `Next player: ${gameState.xIsNext ? 'X' : 'O'}`;

  return (
    <div>
      <h1>Multiplayer Tic-Tac-Toe</h1>
      <div className="status">{status}</div>
      <div className="board">
        {gameState.board.map((cell, i) => (
          <button key={i} onClick={() => handleClick(i)}>
            {cell}
          </button>
        ))}
      </div>
      <button onClick={() => socket.emit('restartGame')}>Restart Game</button>
    </div>
  );
}

export default App;
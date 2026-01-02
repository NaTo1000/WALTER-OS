// Game state variables
let currentGame = null;

// Tic-Tac-Toe variables
let tttBoard = ['', '', '', '', '', '', '', '', ''];
let tttCurrentPlayer = 'X';
let tttGameActive = true;

// RPS variables
let rpsPlayerScore = 0;
let rpsWallyScore = 0;

// Guess variables
let guessTarget = 0;
let guessAttempts = 0;

// Coin Flip variables
let coinPlayerScore = 0;
let coinWallyScore = 0;

// Navigation functions
function loadGame(gameName) {
    document.getElementById('menu').style.display = 'none';
    document.getElementById(gameName).style.display = 'block';
    currentGame = gameName;
    
    // Initialize games
    if (gameName === 'tictactoe') {
        resetTicTacToe();
    } else if (gameName === 'guess') {
        resetGuess();
    }
}

function backToMenu() {
    if (currentGame) {
        document.getElementById(currentGame).style.display = 'none';
    }
    document.getElementById('menu').style.display = 'grid';
    currentGame = null;
}

// ============ TIC-TAC-TOE GAME ============

const tttWinningConditions = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
    [0, 4, 8], [2, 4, 6]              // Diagonals
];

function resetTicTacToe() {
    tttBoard = ['', '', '', '', '', '', '', '', ''];
    tttCurrentPlayer = 'X';
    tttGameActive = true;
    
    const cells = document.querySelectorAll('.ttt-cell');
    cells.forEach(cell => {
        cell.textContent = '';
        cell.classList.remove('taken');
        cell.onclick = handleTTTClick;
    });
    
    document.getElementById('ttt-status').textContent = 'Your turn! You are X';
}

function handleTTTClick(event) {
    const cell = event.target;
    const index = parseInt(cell.getAttribute('data-index'));
    
    if (tttBoard[index] !== '' || !tttGameActive || tttCurrentPlayer !== 'X') {
        return;
    }
    
    makeMove(index, 'X');
    
    if (tttGameActive) {
        setTimeout(() => {
            wallyTTTMove();
        }, 500);
    }
}

function makeMove(index, player) {
    tttBoard[index] = player;
    const cell = document.querySelector(`.ttt-cell[data-index="${index}"]`);
    cell.textContent = player;
    cell.classList.add('taken');
    
    checkTTTResult(player);
}

function wallyTTTMove() {
    if (!tttGameActive) return;
    
    document.getElementById('ttt-status').textContent = 'Wally is thinking...';
    
    // Smart AI: Try to win, then block, then take center, then random
    let move = findWinningMove('O') || findWinningMove('X') || 
               (tttBoard[4] === '' ? 4 : null) || getRandomEmptyCell();
    
    if (move !== null) {
        makeMove(move, 'O');
        tttCurrentPlayer = 'X';
        if (tttGameActive) {
            document.getElementById('ttt-status').textContent = 'Your turn!';
        }
    }
}

function findWinningMove(player) {
    for (let condition of tttWinningConditions) {
        const [a, b, c] = condition;
        const cells = [tttBoard[a], tttBoard[b], tttBoard[c]];
        const playerCells = cells.filter(cell => cell === player).length;
        const emptyCells = cells.filter(cell => cell === '').length;
        
        if (playerCells === 2 && emptyCells === 1) {
            if (tttBoard[a] === '') return a;
            if (tttBoard[b] === '') return b;
            if (tttBoard[c] === '') return c;
        }
    }
    return null;
}

function getRandomEmptyCell() {
    const emptyCells = tttBoard.map((cell, index) => cell === '' ? index : null).filter(i => i !== null);
    return emptyCells.length > 0 ? emptyCells[Math.floor(Math.random() * emptyCells.length)] : null;
}

function checkTTTResult(lastPlayer) {
    let roundWon = false;
    
    for (let condition of tttWinningConditions) {
        const [a, b, c] = condition;
        if (tttBoard[a] === '' || tttBoard[b] === '' || tttBoard[c] === '') {
            continue;
        }
        if (tttBoard[a] === tttBoard[b] && tttBoard[b] === tttBoard[c]) {
            roundWon = true;
            break;
        }
    }
    
    if (roundWon) {
        document.getElementById('ttt-status').textContent = 
            lastPlayer === 'X' ? '🎉 You won!' : '😔 Wally won!';
        tttGameActive = false;
        return;
    }
    
    if (!tttBoard.includes('')) {
        document.getElementById('ttt-status').textContent = "It's a tie!";
        tttGameActive = false;
        return;
    }
}

// ============ ROCK PAPER SCISSORS GAME ============

function playRPS(playerChoice) {
    const choices = ['rock', 'paper', 'scissors'];
    const wallyChoice = choices[Math.floor(Math.random() * choices.length)];
    
    const choiceEmojis = {
        'rock': '✊',
        'paper': '✋',
        'scissors': '✌️'
    };
    
    let result = '';
    let resultClass = '';
    
    if (playerChoice === wallyChoice) {
        result = `Tie! Both chose ${choiceEmojis[playerChoice]}`;
        resultClass = 'tie';
    } else if (
        (playerChoice === 'rock' && wallyChoice === 'scissors') ||
        (playerChoice === 'paper' && wallyChoice === 'rock') ||
        (playerChoice === 'scissors' && wallyChoice === 'paper')
    ) {
        rpsPlayerScore++;
        result = `You win! ${choiceEmojis[playerChoice]} beats ${choiceEmojis[wallyChoice]}`;
        resultClass = 'win';
    } else {
        rpsWallyScore++;
        result = `Wally wins! ${choiceEmojis[wallyChoice]} beats ${choiceEmojis[playerChoice]}`;
        resultClass = 'lose';
    }
    
    document.getElementById('rps-player-score').textContent = rpsPlayerScore;
    document.getElementById('rps-wally-score').textContent = rpsWallyScore;
    
    const resultDiv = document.getElementById('rps-result');
    resultDiv.textContent = result;
    resultDiv.className = 'result-display ' + resultClass;
}

// ============ NUMBER GUESSING GAME ============

function resetGuess() {
    guessTarget = Math.floor(Math.random() * 100) + 1;
    guessAttempts = 0;
    document.getElementById('guess-attempts').textContent = '0';
    document.getElementById('guess-hint').textContent = '';
    document.getElementById('guess-input').value = '';
    document.getElementById('guess-status').textContent = 'Guess a number between 1 and 100!';
}

function makeGuess() {
    const input = document.getElementById('guess-input');
    const guess = parseInt(input.value);
    
    if (isNaN(guess) || guess < 1 || guess > 100) {
        document.getElementById('guess-hint').textContent = 'Please enter a valid number between 1 and 100!';
        return;
    }
    
    guessAttempts++;
    document.getElementById('guess-attempts').textContent = guessAttempts;
    
    if (guess === guessTarget) {
        document.getElementById('guess-status').textContent = 
            `🎉 Correct! You guessed it in ${guessAttempts} attempts!`;
        document.getElementById('guess-hint').textContent = 
            `The number was ${guessTarget}. Wally is impressed! 🤖`;
        input.disabled = true;
    } else if (guess < guessTarget) {
        document.getElementById('guess-hint').textContent = 
            '📈 Too low! Wally says go higher!';
    } else {
        document.getElementById('guess-hint').textContent = 
            '📉 Too high! Wally says go lower!';
    }
    
    input.value = '';
}

// Allow Enter key to submit guess
document.addEventListener('DOMContentLoaded', function() {
    const guessInput = document.getElementById('guess-input');
    if (guessInput) {
        guessInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                makeGuess();
            }
        });
    }
});

// ============ COIN FLIP GAME ============

function flipCoin(playerCall) {
    const coin = document.getElementById('coin-display');
    coin.style.animation = 'none';
    setTimeout(() => {
        coin.style.animation = 'spin 0.5s ease-in-out';
    }, 10);
    
    setTimeout(() => {
        const result = Math.random() < 0.5 ? 'heads' : 'tails';
        coin.textContent = result === 'heads' ? '👑' : '🏛️';
        
        let message = '';
        let resultClass = '';
        
        if (playerCall === result) {
            coinPlayerScore++;
            message = `It's ${result}! You win! 🎉`;
            resultClass = 'win';
        } else {
            coinWallyScore++;
            message = `It's ${result}! Wally wins! 😔`;
            resultClass = 'lose';
        }
        
        document.getElementById('coin-player-score').textContent = coinPlayerScore;
        document.getElementById('coin-wally-score').textContent = coinWallyScore;
        
        const resultDiv = document.getElementById('coin-result');
        resultDiv.textContent = message;
        resultDiv.className = 'result-display ' + resultClass;
    }, 500);
}

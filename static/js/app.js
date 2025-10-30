let allPlayers = [];
let player1Data = null;
let player2Data = null;

// Load players on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadPlayers();
    setupEventListeners();
});

async function loadPlayers() {
    try {
        const response = await fetch('/api/players');
        allPlayers = await response.json();
        
        const player1List = document.getElementById('player1List');
        const player2List = document.getElementById('player2List');
        
        allPlayers.forEach(player => {
            const option1 = document.createElement('option');
            option1.value = player.full_name;
            option1.setAttribute('data-id', player.id);
            player1List.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = player.full_name;
            option2.setAttribute('data-id', player.id);
            player2List.appendChild(option2);
        });
    } catch (error) {
        console.error('Error loading players:', error);
        alert('Failed to load players. Please refresh the page.');
    }
}

function setupEventListeners() {
    const player1Input = document.getElementById('player1Input');
    const player2Input = document.getElementById('player2Input');
    const compareBtn = document.getElementById('compareBtn');
    
    player1Input.addEventListener('input', checkSelection);
    player2Input.addEventListener('input', checkSelection);
    compareBtn.addEventListener('click', comparePlayers);
}

function checkSelection() {
    const player1Input = document.getElementById('player1Input');
    const player2Input = document.getElementById('player2Input');
    const compareBtn = document.getElementById('compareBtn');
    
    const player1Valid = isValidPlayer(player1Input.value);
    const player2Valid = isValidPlayer(player2Input.value);
    
    if (player1Valid && player2Valid && player1Input.value !== player2Input.value) {
        compareBtn.disabled = false;
    } else {
        compareBtn.disabled = true;
    }
}

function isValidPlayer(playerName) {
    return allPlayers.some(p => p.full_name === playerName);
}

function getPlayerIdByName(playerName) {
    const player = allPlayers.find(p => p.full_name === playerName);
    return player ? player.id : null;
}

async function comparePlayers() {
    const player1Input = document.getElementById('player1Input');
    const player2Input = document.getElementById('player2Input');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // Hide results and show loading
    results.classList.add('hidden');
    loading.classList.remove('hidden');
    
    const player1Name = player1Input.value;
    const player2Name = player2Input.value;
    const player1Id = getPlayerIdByName(player1Name);
    const player2Id = getPlayerIdByName(player2Name);
    
    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                player1_id: player1Id,
                player2_id: player2Id,
                player1_name: player1Name,
                player2_name: player2Name
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Comparison failed');
        }
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error comparing players:', error);
        alert(`Error: ${error.message}`);
    } finally {
        loading.classList.add('hidden');
    }
}

function displayResults(data) {
    const results = document.getElementById('results');
    
    // Display winner
    document.getElementById('winnerName').textContent = data.winner;
    
    // Display player 1 data
    document.getElementById('player1Name').textContent = data.player1.name;
    document.getElementById('player1Score').textContent = data.player1.score;
    displayAccolades('player1Accolades', data.player1.stats);
    displayPlayerStats('player1StatsGrid', data.player1.stats, data.player2.stats);
    displayTicketImpact('player1Ticket', data.player1.ticket_impact);
    
    // Display player 2 data
    document.getElementById('player2Name').textContent = data.player2.name;
    document.getElementById('player2Score').textContent = data.player2.score;
    displayAccolades('player2Accolades', data.player2.stats);
    displayPlayerStats('player2StatsGrid', data.player2.stats, data.player1.stats);
    displayTicketImpact('player2Ticket', data.player2.ticket_impact);
    
    // Display analysis
    document.getElementById('analysisContent').innerHTML = data.analysis;
    
    // Show results
    results.classList.remove('hidden');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayAccolades(elementId, stats) {
    const container = document.getElementById(elementId);
    container.innerHTML = `
        <div class="accolade-item">
            🏆 <span class="label">Championships:</span> ${stats.championships}
        </div>
        <div class="accolade-item">
            🏅 <span class="label">MVP Awards:</span> ${stats.mvp_awards}
        </div>
        <div class="accolade-item">
            ⭐ <span class="label">Best Season:</span> ${stats.best_season}
        </div>
        <div class="accolade-item">
            🔥 <span class="label">Best Year PPG:</span> ${stats.best_season_ppg}
        </div>
        <div class="accolade-item">
            📈 <span class="label">Best Year Total Points:</span> ${stats.best_season_total_points}
        </div>
    `;
}

function displayTicketImpact(elementId, ticketData) {
    const container = document.getElementById(elementId);
    container.innerHTML = `
        <h4>🎟️ Ticket Price Impact</h4>
        <div class="ticket-rating">${ticketData.rating}</div>
        <div class="ticket-multiplier">${ticketData.multiplier}x Price Multiplier</div>
        <div class="ticket-description">${ticketData.description}</div>
    `;
}

function displayPlayerStats(elementId, stats, opponentStats) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';
    
    const statsToDisplay = [
        { label: 'Points Per Game', key: 'ppg' },
        { label: 'Rebounds Per Game', key: 'rpg' },
        { label: 'Assists Per Game', key: 'apg' },
        { label: 'Steals Per Game', key: 'spg' },
        { label: 'Blocks Per Game', key: 'bpg' },
        { label: 'Field Goal %', key: 'fg_pct', suffix: '%' },
        { label: '3-Point %', key: 'fg3_pct', suffix: '%' },
        { label: 'Free Throw %', key: 'ft_pct', suffix: '%' },
        { label: 'Minutes Per Game', key: 'mpg' },
        { label: 'Games Played', key: 'games_played' },
        { label: 'Seasons', key: 'seasons' },
        { label: 'Total Points', key: 'total_points' },
        { label: 'Total Rebounds', key: 'total_rebounds' },
        { label: 'Total Assists', key: 'total_assists' }
    ];
    
    statsToDisplay.forEach(stat => {
        const statRow = document.createElement('div');
        statRow.className = 'stat-row';
        
        // Highlight if this stat is better than opponent
        if (stats[stat.key] > opponentStats[stat.key]) {
            statRow.classList.add('highlight');
        }
        
        const label = document.createElement('span');
        label.className = 'stat-label';
        label.textContent = stat.label;
        
        const value = document.createElement('span');
        value.className = 'stat-value';
        value.textContent = stats[stat.key] + (stat.suffix || '');
        
        statRow.appendChild(label);
        statRow.appendChild(value);
        container.appendChild(statRow);
    });
}

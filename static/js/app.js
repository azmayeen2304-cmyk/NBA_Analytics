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
        
        const player1Select = document.getElementById('player1');
        const player2Select = document.getElementById('player2');
        
        allPlayers.forEach(player => {
            const option1 = new Option(player.full_name, player.id);
            const option2 = new Option(player.full_name, player.id);
            player1Select.add(option1);
            player2Select.add(option2);
        });
    } catch (error) {
        console.error('Error loading players:', error);
        alert('Failed to load players. Please refresh the page.');
    }
}

function setupEventListeners() {
    const player1Select = document.getElementById('player1');
    const player2Select = document.getElementById('player2');
    const compareBtn = document.getElementById('compareBtn');
    
    player1Select.addEventListener('change', checkSelection);
    player2Select.addEventListener('change', checkSelection);
    compareBtn.addEventListener('click', comparePlayers);
}

function checkSelection() {
    const player1Select = document.getElementById('player1');
    const player2Select = document.getElementById('player2');
    const compareBtn = document.getElementById('compareBtn');
    
    if (player1Select.value && player2Select.value && player1Select.value !== player2Select.value) {
        compareBtn.disabled = false;
    } else {
        compareBtn.disabled = true;
    }
}

async function comparePlayers() {
    const player1Select = document.getElementById('player1');
    const player2Select = document.getElementById('player2');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // Hide results and show loading
    results.classList.add('hidden');
    loading.classList.remove('hidden');
    
    const player1Id = player1Select.value;
    const player2Id = player2Select.value;
    const player1Name = player1Select.options[player1Select.selectedIndex].text;
    const player2Name = player2Select.options[player2Select.selectedIndex].text;
    
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
    
    // Display player 1 stats
    document.getElementById('player1Name').textContent = data.player1.name;
    document.getElementById('player1Score').textContent = data.player1.score;
    displayPlayerStats('player1StatsGrid', data.player1.stats, data.player2.stats);
    
    // Display player 2 stats
    document.getElementById('player2Name').textContent = data.player2.name;
    document.getElementById('player2Score').textContent = data.player2.score;
    displayPlayerStats('player2StatsGrid', data.player2.stats, data.player1.stats);
    
    // Display analysis
    document.getElementById('analysisContent').innerHTML = data.analysis;
    
    // Show results
    results.classList.remove('hidden');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
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

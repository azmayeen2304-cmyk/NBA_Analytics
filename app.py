from flask import Flask, render_template, jsonify, request
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo
import pandas as pd
import time
from datetime import datetime

app = Flask(__name__)

def get_all_players():
    """Get all NBA players and filter by years active between 1985-2024"""
    all_players = players.get_players()
    
    # Filter players who played between 1985-2024
    filtered_players = []
    for player in all_players:
        # We'll filter more accurately when we get career stats
        filtered_players.append({
            'id': player['id'],
            'full_name': player['full_name'],
            'is_active': player['is_active']
        })
    
    # Sort by full name
    filtered_players.sort(key=lambda x: x['full_name'])
    return filtered_players

def get_player_career_stats(player_id):
    """Get career statistics for a player"""
    try:
        time.sleep(0.6)  # Rate limiting for NBA API
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_df = career.get_data_frames()[0]
        
        # Filter seasons between 1985-2024
        career_df['SEASON_YEAR'] = career_df['SEASON_ID'].str[:4].astype(int)
        career_df = career_df[(career_df['SEASON_YEAR'] >= 1985) & (career_df['SEASON_YEAR'] <= 2024)]
        
        if career_df.empty:
            return None
            
        # Get regular season stats only
        regular_season = career_df[career_df['SEASON_ID'].str.contains('Regular')]
        
        if regular_season.empty:
            return None
        
        # Calculate career averages and totals
        total_games = regular_season['GP'].sum()
        total_minutes = regular_season['MIN'].sum()
        
        if total_games == 0:
            return None
        
        stats = {
            'games_played': int(total_games),
            'seasons': len(regular_season),
            'total_points': int(regular_season['PTS'].sum()),
            'total_rebounds': int(regular_season['REB'].sum()),
            'total_assists': int(regular_season['AST'].sum()),
            'total_steals': int(regular_season['STL'].sum()),
            'total_blocks': int(regular_season['BLK'].sum()),
            'ppg': round(regular_season['PTS'].sum() / total_games, 1),
            'rpg': round(regular_season['REB'].sum() / total_games, 1),
            'apg': round(regular_season['AST'].sum() / total_games, 1),
            'spg': round(regular_season['STL'].sum() / total_games, 1),
            'bpg': round(regular_season['BLK'].sum() / total_games, 1),
            'fg_pct': round(regular_season['FG_PCT'].mean() * 100, 1),
            'fg3_pct': round(regular_season['FG3_PCT'].mean() * 100, 1),
            'ft_pct': round(regular_season['FT_PCT'].mean() * 100, 1),
            'mpg': round(total_minutes / total_games, 1),
            'first_season': regular_season.iloc[0]['SEASON_ID'],
            'last_season': regular_season.iloc[-1]['SEASON_ID']
        }
        
        return stats
    except Exception as e:
        print(f"Error fetching stats for player {player_id}: {str(e)}")
        return None

def calculate_player_score(stats):
    """Calculate a comprehensive player score based on various metrics"""
    # Weighted scoring system
    weights = {
        'ppg': 3.0,      # Points are important
        'rpg': 2.0,      # Rebounds
        'apg': 2.5,      # Assists
        'spg': 1.5,      # Steals
        'bpg': 1.5,      # Blocks
        'fg_pct': 0.5,   # Field goal percentage
        'fg3_pct': 0.3,  # 3-point percentage
        'ft_pct': 0.2,   # Free throw percentage
        'games_played': 0.01,  # Longevity bonus
        'seasons': 2.0   # Career length
    }
    
    score = 0
    for key, weight in weights.items():
        if key in stats and stats[key] is not None:
            score += stats[key] * weight
    
    return round(score, 2)

def generate_comparison_analysis(player1_name, player2_name, stats1, stats2, score1, score2):
    """Generate a detailed comparison analysis"""
    winner = player1_name if score1 > score2 else player2_name
    score_diff = abs(score1 - score2)
    
    # Determine key strengths
    strengths1 = []
    strengths2 = []
    
    comparison_categories = [
        ('ppg', 'scoring', 'PPG'),
        ('rpg', 'rebounding', 'RPG'),
        ('apg', 'playmaking', 'APG'),
        ('fg_pct', 'shooting efficiency', 'FG%'),
        ('spg', 'defense (steals)', 'SPG'),
        ('bpg', 'defense (blocks)', 'BPG')
    ]
    
    for key, category, label in comparison_categories:
        if stats1[key] > stats2[key]:
            diff = stats1[key] - stats2[key]
            strengths1.append(f"{category} ({stats1[key]} vs {stats2[key]} {label})")
        elif stats2[key] > stats1[key]:
            diff = stats2[key] - stats1[key]
            strengths2.append(f"{category} ({stats2[key]} vs {stats1[key]} {label})")
    
    # Build analysis text
    analysis = f"<b>Winner: {winner}</b> (Score: {max(score1, score2)} vs {min(score1, score2)})<br><br>"
    
    if score_diff < 10:
        analysis += "This is an extremely close matchup! Both players have remarkably similar overall impact.<br><br>"
    elif score_diff < 30:
        analysis += "This is a competitive comparison with notable differences in their playing styles.<br><br>"
    else:
        analysis += f"{winner} has a clear statistical advantage in this comparison.<br><br>"
    
    analysis += f"<b>{player1_name}'s Strengths:</b><br>"
    if strengths1:
        analysis += "• " + "<br>• ".join(strengths1[:3]) + "<br><br>"
    else:
        analysis += "• More well-rounded across categories<br><br>"
    
    analysis += f"<b>{player2_name}'s Strengths:</b><br>"
    if strengths2:
        analysis += "• " + "<br>• ".join(strengths2[:3]) + "<br><br>"
    else:
        analysis += "• More well-rounded across categories<br><br>"
    
    # Career longevity comparison
    if stats1['games_played'] > stats2['games_played']:
        analysis += f"<b>Longevity:</b> {player1_name} played {stats1['games_played']} games over {stats1['seasons']} seasons, compared to {player2_name}'s {stats2['games_played']} games over {stats2['seasons']} seasons.<br><br>"
    else:
        analysis += f"<b>Longevity:</b> {player2_name} played {stats2['games_played']} games over {stats2['seasons']} seasons, compared to {player1_name}'s {stats1['games_played']} games over {stats1['seasons']} seasons.<br><br>"
    
    # Overall assessment
    analysis += "<b>Overall Assessment:</b><br>"
    if winner == player1_name and score1 > score2:
        analysis += f"{player1_name} edges out {player2_name} in this statistical comparison"
    else:
        analysis += f"{player2_name} edges out {player1_name} in this statistical comparison"
    
    if score_diff < 20:
        analysis += ", though both players would be considered elite performers with different strengths."
    else:
        analysis += " with stronger numbers across multiple categories."
    
    return analysis

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/players', methods=['GET'])
def api_get_players():
    """Get list of all players"""
    players_list = get_all_players()
    return jsonify(players_list)

@app.route('/api/compare', methods=['POST'])
def api_compare_players():
    """Compare two players"""
    data = request.json
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    player1_name = data.get('player1_name')
    player2_name = data.get('player2_name')
    
    if not all([player1_id, player2_id, player1_name, player2_name]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get stats for both players
    stats1 = get_player_career_stats(player1_id)
    stats2 = get_player_career_stats(player2_id)
    
    if not stats1:
        return jsonify({'error': f'No data available for {player1_name} in the 1985-2024 period'}), 404
    
    if not stats2:
        return jsonify({'error': f'No data available for {player2_name} in the 1985-2024 period'}), 404
    
    # Calculate scores
    score1 = calculate_player_score(stats1)
    score2 = calculate_player_score(stats2)
    
    # Generate analysis
    analysis = generate_comparison_analysis(player1_name, player2_name, stats1, stats2, score1, score2)
    
    return jsonify({
        'player1': {
            'name': player1_name,
            'stats': stats1,
            'score': score1
        },
        'player2': {
            'name': player2_name,
            'stats': stats2,
            'score': score2
        },
        'winner': player1_name if score1 > score2 else player2_name,
        'analysis': analysis
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, jsonify, request
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo
import pandas as pd
import time
from datetime import datetime

app = Flask(__name__)

# Championship data for notable players (manually maintained)
CHAMPIONSHIPS = {
    'Michael Jordan': 6, 'LeBron James': 4, 'Kobe Bryant': 5, 'Tim Duncan': 5,
    'Magic Johnson': 5, 'Larry Bird': 3, 'Shaquille O\'Neal': 4, 'Kareem Abdul-Jabbar': 6,
    'Stephen Curry': 4, 'Kevin Durant': 2, 'Kawhi Leonard': 2, 'Dwyane Wade': 3,
    'Hakeem Olajuwon': 2, 'Dirk Nowitzki': 1, 'Giannis Antetokounmpo': 1,
    'Bill Russell': 11, 'Wilt Chamberlain': 2, 'Julius Erving': 1, 'Isiah Thomas': 2,
    'Karl Malone': 0, 'Charles Barkley': 0, 'Patrick Ewing': 0, 'John Stockton': 0,
    'Allen Iverson': 0, 'Scottie Pippen': 6, 'Dennis Rodman': 5, 'Clyde Drexler': 1,
    'Gary Payton': 1, 'Ray Allen': 2, 'Paul Pierce': 1, 'Kevin Garnett': 1,
    'Tony Parker': 4, 'Manu Ginobili': 4, 'Chris Paul': 0, 'James Harden': 0,
    'Russell Westbrook': 0, 'Kyrie Irving': 1, 'Anthony Davis': 1, 'Damian Lillard': 0
}

# MVP Awards data for notable players
MVP_AWARDS = {
    'Michael Jordan': 5, 'LeBron James': 4, 'Kareem Abdul-Jabbar': 6, 'Bill Russell': 5,
    'Wilt Chamberlain': 4, 'Magic Johnson': 3, 'Larry Bird': 3, 'Moses Malone': 3,
    'Tim Duncan': 2, 'Steve Nash': 2, 'Stephen Curry': 2, 'Giannis Antetokounmpo': 2,
    'Karl Malone': 2, 'Kobe Bryant': 1, 'Shaquille O\'Neal': 1, 'Hakeem Olajuwon': 1,
    'David Robinson': 1, 'Allen Iverson': 1, 'Kevin Garnett': 1, 'Dirk Nowitzki': 1,
    'Derrick Rose': 1, 'Kevin Durant': 1, 'Russell Westbrook': 1, 'James Harden': 1,
    'Nikola Jokic': 2, 'Joel Embiid': 1, 'Charles Barkley': 1, 'Julius Erving': 1
}

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

def get_player_career_stats(player_id, player_name):
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
        
        # Calculate career averages and totals
        total_games = career_df['GP'].sum()
        total_minutes = career_df['MIN'].sum()
        
        if total_games == 0:
            return None
        
        # Find best season by total points scored
        best_season = career_df.loc[career_df['PTS'].idxmax()]
        best_year_ppg = round(best_season['PTS'] / best_season['GP'], 1) if best_season['GP'] > 0 else 0
        
        stats = {
            'games_played': int(total_games),
            'seasons': len(career_df),
            'total_points': int(career_df['PTS'].sum()),
            'total_rebounds': int(career_df['REB'].sum()),
            'total_assists': int(career_df['AST'].sum()),
            'total_steals': int(career_df['STL'].sum()),
            'total_blocks': int(career_df['BLK'].sum()),
            'ppg': round(career_df['PTS'].sum() / total_games, 1),
            'rpg': round(career_df['REB'].sum() / total_games, 1),
            'apg': round(career_df['AST'].sum() / total_games, 1),
            'spg': round(career_df['STL'].sum() / total_games, 1),
            'bpg': round(career_df['BLK'].sum() / total_games, 1),
            'fg_pct': round(career_df['FG_PCT'].mean() * 100, 1),
            'fg3_pct': round(career_df['FG3_PCT'].mean() * 100, 1),
            'ft_pct': round(career_df['FT_PCT'].mean() * 100, 1),
            'mpg': round(total_minutes / total_games, 1),
            'first_season': career_df.iloc[0]['SEASON_ID'],
            'last_season': career_df.iloc[-1]['SEASON_ID'],
            'best_season': best_season['SEASON_ID'],
            'best_season_total_points': int(best_season['PTS']),
            'best_season_ppg': best_year_ppg,
            'championships': CHAMPIONSHIPS.get(player_name, 0),
            'mvp_awards': MVP_AWARDS.get(player_name, 0)
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
        'seasons': 2.0,   # Career length
        'championships': 8.0,  # Championships are very important
        'mvp_awards': 10.0,  # MVP awards are crucial
        'best_season_ppg': 0.5  # Best season performance bonus
    }
    
    score = 0
    for key, weight in weights.items():
        if key in stats and stats[key] is not None:
            score += stats[key] * weight
    
    return round(score, 2)

def calculate_ticket_price_impact(best_season_ppg, championships, mvp_awards):
    """
    Calculate ticket price impact based on player's best season performance
    Returns a rating and multiplier for ticket prices
    """
    # Base price multiplier starts at 1.0x
    multiplier = 1.0
    
    # PPG impact (each point above 20 adds 2% to ticket price)
    if best_season_ppg > 20:
        multiplier += (best_season_ppg - 20) * 0.02
    
    # Championship bonus (each ring adds 10% to ticket price)
    multiplier += championships * 0.10
    
    # MVP bonus (each MVP adds 15% to ticket price)
    multiplier += mvp_awards * 0.15
    
    # Determine rating category
    if multiplier >= 2.5:
        rating = "SUPERSTAR ⭐⭐⭐⭐⭐"
        description = "Stadium would be PACKED! Tickets would be 2-3x normal price."
    elif multiplier >= 2.0:
        rating = "ELITE STAR ⭐⭐⭐⭐"
        description = "High demand! Tickets would be 2x normal price."
    elif multiplier >= 1.5:
        rating = "ALL-STAR ⭐⭐⭐"
        description = "Strong attendance boost! Tickets 1.5x normal price."
    elif multiplier >= 1.2:
        rating = "SOLID PLAYER ⭐⭐"
        description = "Good draw! Modest ticket price increase."
    else:
        rating = "ROLE PLAYER ⭐"
        description = "Standard pricing applies."
    
    return {
        'rating': rating,
        'multiplier': round(multiplier, 2),
        'description': description
    }

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
    stats1 = get_player_career_stats(player1_id, player1_name)
    stats2 = get_player_career_stats(player2_id, player2_name)
    
    if not stats1:
        return jsonify({'error': f'No data available for {player1_name} in the 1985-2024 period'}), 404
    
    if not stats2:
        return jsonify({'error': f'No data available for {player2_name} in the 1985-2024 period'}), 404
    
    # Calculate scores
    score1 = calculate_player_score(stats1)
    score2 = calculate_player_score(stats2)
    
    # Calculate ticket price impact
    ticket1 = calculate_ticket_price_impact(
        stats1['best_season_ppg'], 
        stats1['championships'], 
        stats1['mvp_awards']
    )
    ticket2 = calculate_ticket_price_impact(
        stats2['best_season_ppg'], 
        stats2['championships'], 
        stats2['mvp_awards']
    )
    
    # Generate analysis
    analysis = generate_comparison_analysis(player1_name, player2_name, stats1, stats2, score1, score2)
    
    return jsonify({
        'player1': {
            'name': player1_name,
            'stats': stats1,
            'score': score1,
            'ticket_impact': ticket1
        },
        'player2': {
            'name': player2_name,
            'stats': stats2,
            'score': score2,
            'ticket_impact': ticket2
        },
        'winner': player1_name if score1 > score2 else player2_name,
        'analysis': analysis
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

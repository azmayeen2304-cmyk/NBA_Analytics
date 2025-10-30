# NBA Player Comparison Tool (1985-2024)

A modern web application that allows you to compare NBA players from 1985 to 2024 based on their career statistics. The tool provides comprehensive metric comparisons, calculates an overall "who is better" score, and generates detailed analysis.

## Features

- 🏀 **Player Selection**: Choose from thousands of NBA players who played between 1985-2024
- 📊 **Comprehensive Stats**: Compare players across multiple metrics:
  - Points, Rebounds, Assists per game
  - Steals, Blocks per game
  - Field Goal %, 3-Point %, Free Throw %
  - Games played, Seasons, Total career stats
- 🏆 **Overall Score**: Advanced weighted scoring algorithm that determines who is better
- 📝 **Detailed Analysis**: Automatically generated comparison analysis highlighting:
  - Each player's strengths
  - Key statistical differences
  - Career longevity comparison
  - Overall assessment
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Data Source**: NBA API (nba_api library)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Processing**: Pandas, NumPy

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. Clone this repository:
```bash
git clone <repository-url>
cd workspace
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Select two NBA players from the dropdown menus and click "Compare Players"

## How It Works

### Scoring Algorithm

The app uses a weighted scoring system to determine overall player quality:

- **Points Per Game (PPG)**: Weight 3.0
- **Rebounds Per Game (RPG)**: Weight 2.0
- **Assists Per Game (APG)**: Weight 2.5
- **Steals Per Game (SPG)**: Weight 1.5
- **Blocks Per Game (BPG)**: Weight 1.5
- **Field Goal %**: Weight 0.5
- **3-Point %**: Weight 0.3
- **Free Throw %**: Weight 0.2
- **Games Played**: Weight 0.01 (longevity bonus)
- **Seasons**: Weight 2.0 (career length)

### Analysis Generation

The tool automatically generates analysis by:
1. Comparing key statistical categories
2. Identifying each player's strengths
3. Evaluating career longevity
4. Providing an overall assessment based on statistical differences

## API Endpoints

### GET `/api/players`
Returns a list of all NBA players available for comparison.

### POST `/api/compare`
Compares two players and returns comprehensive statistics and analysis.

**Request Body:**
```json
{
  "player1_id": "123",
  "player2_id": "456",
  "player1_name": "Player Name 1",
  "player2_name": "Player Name 2"
}
```

**Response:**
```json
{
  "player1": {
    "name": "Player Name 1",
    "stats": { ... },
    "score": 234.5
  },
  "player2": {
    "name": "Player Name 2",
    "stats": { ... },
    "score": 198.3
  },
  "winner": "Player Name 1",
  "analysis": "Detailed comparison text..."
}
```

## Example Comparisons

Try comparing:
- **Michael Jordan vs LeBron James** - The GOAT debate
- **Kobe Bryant vs Tim Duncan** - Different positions, similar excellence
- **Stephen Curry vs Magic Johnson** - Point guard evolution
- **Shaquille O'Neal vs Hakeem Olajuwon** - Dominant centers

## Notes

- The NBA API has rate limiting, so there's a 0.6-second delay between API calls
- Only regular season statistics are used for comparisons
- Players must have played at least some games between 1985-2024 to appear in results
- The scoring algorithm is designed to be position-agnostic, though guards may have advantages in certain categories

## Future Enhancements

Potential features to add:
- Advanced metrics (PER, Win Shares, VORP)
- Playoff statistics comparison
- Head-to-head game records
- Per-36-minute statistics
- Peak season comparison
- Position-specific scoring weights
- Visual charts and graphs
- Export comparison as PDF

## Contributing

Feel free to fork this project and submit pull requests for any enhancements!

## License

This project is open source and available under the MIT License.
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Optional
from config import RTANKS_BASE_URL, LEADERBOARD_CATEGORIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RTanksScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_leaderboard(self, category: str) -> List[Dict]:
        """Scrape leaderboard data for a specific category"""
        try:
            category_config = LEADERBOARD_CATEGORIES.get(category)
            if not category_config:
                logger.error(f"Unknown category: {category}")
                return []
            
            # All data is on the main page
            url = RTANKS_BASE_URL
            logger.info(f"Scraping {category} leaderboard from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse the specific category section from the main page
            players = self._parse_category_section(soup, category)
            
            logger.info(f"Successfully scraped {len(players)} players for {category}")
            return players
            
        except requests.RequestException as e:
            logger.error(f"Request error while scraping {category}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while scraping {category}: {e}")
            return []
    
    def _parse_leaderboard_table(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """Parse the HTML table containing leaderboard data"""
        players = []
        
        try:
            # Find the leaderboard table - looking for table rows with player data
            table_rows = soup.find_all('tr')
            
            # If no table rows found, try alternative selector based on the HTML structure
            if not table_rows:
                # Look for div elements that might contain player data
                player_divs = soup.find_all('div', class_=re.compile(r'player|rank|leaderboard'))
                logger.warning(f"No table rows found, trying alternative parsing. Found {len(player_divs)} potential elements")
            
            # Parse each row for player information
            rank = 1
            for row in table_rows:
                if rank > 100:  # Limit to top 100 players
                    break
                    
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # Ensure we have enough cells for rank, name, score
                    try:
                        # Extract rank (first column)
                        rank_text = cells[0].get_text(strip=True)
                        if not rank_text.isdigit():
                            continue
                        
                        # Extract player name (second column)
                        name_cell = cells[1]
                        player_name = self._extract_player_name(name_cell)
                        
                        # Extract score (third column)
                        score_text = cells[2].get_text(strip=True)
                        score = self._parse_score(score_text)
                        
                        # Extract rank icon/image if available
                        rank_icon = self._extract_rank_icon(name_cell)
                        
                        players.append({
                            'rank': int(rank_text),
                            'name': player_name,
                            'score': score,
                            'score_formatted': score_text,
                            'rank_icon': rank_icon,
                            'category': category
                        })
                        
                        rank += 1
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Error parsing row {rank}: {e}")
                        continue
            
            # If we didn't find players in table format, try parsing the actual HTML structure
            if not players:
                players = self._parse_alternative_format(soup, category)
                        
        except Exception as e:
            logger.error(f"Error parsing leaderboard table: {e}")
        
        return players
    
    def _parse_alternative_format(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """Alternative parser for the specific RTanks HTML structure"""
        players = []
        
        try:
            # Based on the provided HTML, look for the table structure
            # The data appears to be in a table with rank | player info | score format
            table = soup.find('table')
            if not table:
                logger.error("No table found in HTML")
                return []
            
            rows = table.find_all('tr')
            
            for i, row in enumerate(rows, 1):
                if i > 100:  # Limit to top 100
                    break
                
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        # Rank is in first cell
                        rank = int(cells[0].get_text(strip=True))
                        
                        # Player info is in second cell - contains image and link
                        player_cell = cells[1]
                        player_link = player_cell.find('a')
                        if player_link:
                            player_name = player_link.get_text(strip=True)
                        else:
                            player_name = player_cell.get_text(strip=True)
                        
                        # Extract rank icon
                        rank_icon = None
                        img = player_cell.find('img')
                        if img and img.get('src'):
                            rank_icon = img.get('src')
                        
                        # Score is in third cell
                        score_text = cells[2].get_text(strip=True)
                        score = self._parse_score(score_text)
                        
                        players.append({
                            'rank': rank,
                            'name': player_name,
                            'score': score,
                            'score_formatted': score_text,
                            'rank_icon': rank_icon,
                            'category': category
                        })
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Error parsing alternative format row {i}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in alternative parsing: {e}")
        
        return players
    
    def _parse_category_section(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """Parse the specific category section from the main page"""
        players = []
        
        try:
            category_config = LEADERBOARD_CATEGORIES.get(category)
            if not category_config:
                logger.error(f"Unknown category: {category}")
                return []
            
            # Find all tables on the page
            tables = soup.find_all('table')
            
            # Get the table for this specific category using section_index
            section_index = category_config['section_index']
            table = tables[section_index] if len(tables) > section_index else None
            
            if not table:
                logger.error(f"No table found for {category} at index {section_index}")
                return []
            
            rows = table.find_all('tr')
            
            for i, row in enumerate(rows, 1):
                if i > 100:  # Limit to top 100
                    break
                
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        # Rank is in first cell
                        rank = int(cells[0].get_text(strip=True))
                        
                        # Player info is in second cell - contains image and link
                        player_cell = cells[1]
                        player_link = player_cell.find('a')
                        if player_link:
                            player_name = player_link.get_text(strip=True)
                        else:
                            player_name = player_cell.get_text(strip=True)
                        
                        # Extract rank icon
                        rank_icon = None
                        img = player_cell.find('img')
                        if img and img.get('src'):
                            rank_icon = img.get('src')
                        
                        # Score is in third cell
                        score_text = cells[2].get_text(strip=True)
                        score = self._parse_score(score_text)
                        
                        players.append({
                            'rank': rank,
                            'name': player_name,
                            'score': score,
                            'score_formatted': score_text,
                            'rank_icon': rank_icon,
                            'category': category
                        })
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Error parsing category section row {i}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in category section parsing: {e}")
        
        return players
    
    def _extract_player_name(self, cell) -> str:
        """Extract player name from table cell"""
        # Look for link first (most likely contains the name)
        link = cell.find('a')
        if link:
            return link.get_text(strip=True)
        
        # Otherwise get all text and clean it
        text = cell.get_text(strip=True)
        return text
    
    def _extract_rank_icon(self, cell) -> Optional[str]:
        """Extract rank icon URL from table cell"""
        img = cell.find('img')
        if img and img.get('src'):
            src = img.get('src')
            # Convert relative URLs to absolute
            if src.startswith('//'):
                return f"https:{src}"
            elif src.startswith('/'):
                return f"{RTANKS_BASE_URL}{src}"
            return src
        return None
    
    def _parse_score(self, score_text: str) -> int:
        """Parse score from text, handling various formats"""
        try:
            # Remove any non-digit characters except spaces
            cleaned = re.sub(r'[^\d\s]', '', score_text)
            # Remove spaces and convert to int
            score = int(cleaned.replace(' ', ''))
            return score
        except ValueError:
            logger.warning(f"Could not parse score: {score_text}")
            return 0
    
    def scrape_all_categories(self) -> Dict[str, List[Dict]]:
        """Scrape all leaderboard categories"""
        results = {}
        
        for category in LEADERBOARD_CATEGORIES.keys():
            results[category] = self.scrape_leaderboard(category)
        
        return results
    
    def get_reset_countdown(self) -> Optional[str]:
        """Get the countdown until next rating reset"""
        try:
            response = self.session.get(RTANKS_BASE_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for countdown text - based on the HTML it shows "Рейтинг обнулится через"
            countdown_elements = soup.find_all(text=re.compile(r'обнулится через|resets in'))
            
            for element in countdown_elements:
                parent = element.parent
                if parent:
                    # Get the next sibling or child that contains the time
                    countdown_text = parent.get_text(strip=True)
                    # Extract time pattern like "2д 4ч 2м"
                    time_match = re.search(r'(\d+д\s*\d+ч\s*\d+м|\d+d\s*\d+h\s*\d+m)', countdown_text)
                    if time_match:
                        return time_match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting reset countdown: {e}")
            return None

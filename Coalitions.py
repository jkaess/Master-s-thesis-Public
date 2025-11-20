def scrape_german_coalitions():
    import requests
    from bs4 import BeautifulSoup
    import re
    url = "https://en.wikipedia.org/wiki/List_of_Federal_Republic_of_Germany_governments"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    coalitions = []
    coalition_id = 0
    
    # Find all tables with class wikitable
    tables = soup.find_all('table', class_='wikitable')
    
    for table in tables:
        rows = table.find_all('tr')
        
        current_coalition = None
        
        # Process each row
        for row in rows:
            cells = row.find_all('td')
                        
            
            if len(cells) >= 6:  # Main row with Term, Chancellor, Vice Chancellor, Cabinet, Parties, Seats
                term_cell = cells[0]
                chancellor_cell = cells[1]
                parties_cell = cells[4]
                
                # Extract term
                term = term_cell.get_text(strip=True)
                
                # Extract chancellor name
                chancellor_links = chancellor_cell.find_all('a')

                chancellor = chancellor_links[0].get_text(strip=True) if chancellor_links else chancellor_cell.get_text(strip=True)
                
                # Extract parties - they are in separate rows within the parties cell
                parties = []
                party_rows = parties_cell.find_all('tr') if parties_cell.find('table') else [parties_cell]
                
                for party_row in party_rows:
                    party_links = party_row.find_all('a')
                    for link in party_links:
                        party_name = link.get_text(strip=True)
                        # Filter for actual party abbreviations (short names)
                        if party_name and len(party_name) <= 10 and party_name not in parties:
                            parties.append(party_name)
                
                # Create coalition entry if we have meaningful data
                if term and chancellor and parties and re.search(r'19[4-9]\d|20\d\d', term):
                    coalition_id += 1 
                    current_coalition = {
                        'id': coalition_id,
                        'term': term,
                        'chancellor': chancellor,
                        'parties': parties
                    }
                    coalitions.append(current_coalition)
                    
            elif len(cells) == 1 and current_coalition is not None:  
                # This is likely a continuation row with additional coalition partner
                party_cell = cells[0]
                party_links = party_cell.find_all('a')
                
                for link in party_links:
                    party_name = link.get_text(strip=True)
                    # Filter for actual party abbreviations and avoid duplicates
                    if (party_name and len(party_name) <= 10 and 
                        party_name not in current_coalition['parties']):
                        current_coalition['parties'].append(party_name)
                
                # Also check for plain text if no links
                if not party_links:
                    party_text = party_cell.get_text(strip=True)
                    if (party_text and len(party_text) <= 10 and 
                        party_text not in current_coalition['parties'] and
                        not party_text.isdigit() and
                        party_text not in ['–', '-', '—']):
                        current_coalition['parties'].append(party_text)
            else:
                # Reset current_coalition when we encounter a row that doesn't fit our patterns
                if len(cells) > 1:  # Only reset for substantial rows, not empty ones
                    current_coalition = None
    print(coalitions)
    return coalitions
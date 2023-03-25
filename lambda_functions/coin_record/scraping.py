import requests

from bs4 import BeautifulSoup


def coin_scraper(coin_list, base_url,price_class):
    # Define a list to return
    results = []
    
    for coin in coin_list:
        # Get page html and parse
        url = base_url+coin
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Scrape data
        current_price = float(soup.find(class_=price_class).text.strip("$")\
                                                           .replace(',',''))
    
        # Append to response list
        results.append({
            'coin_name':coin, 
            'current_price':current_price
        })
        
    return results
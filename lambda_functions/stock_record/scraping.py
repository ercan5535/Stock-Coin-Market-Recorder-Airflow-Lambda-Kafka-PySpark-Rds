import requests

from bs4 import BeautifulSoup


def stock_scraper(stock_list, base_url, name_class, close_class, price_class):
    # Define a list to return
    results = []
    
    for stock in stock_list:
        # Get page html and parse
        url = base_url+stock
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Scrape data 
        stock_name = soup.find(class_=name_class).text.strip() 
        previouse_close = soup.find(class_=close_class).text.strip()
        current_price = soup.find(class_=price_class).text.strip()
    
        # Append to response list
        results.append({
            'stock_name':stock_name, 
            'current_price':float(current_price), 
            'previous_close':float(previouse_close)
        })
        
    return results
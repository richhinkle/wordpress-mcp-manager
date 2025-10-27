#!/usr/bin/env python3
"""
Check available Apify actors
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('APIFY_API_TOKEN')

if api_token:
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {api_token}'})
    
    # Search for web scraper actors
    url = 'https://api.apify.com/v2/acts'
    params = {'my': 'false', 'limit': 20}
    
    response = session.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        actors = data.get('data', {}).get('items', [])
        
        print('Available actors:')
        for actor in actors:
            actor_id = actor.get('id')
            actor_name = actor.get('name', 'Unknown')
            if 'web' in actor_name.lower() or 'scraper' in actor_name.lower():
                print(f'  {actor_id}: {actor_name}')
    else:
        print(f'Error: {response.status_code} - {response.text}')
else:
    print('No API token found')
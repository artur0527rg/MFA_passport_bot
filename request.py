import os

from fake_headers import Headers
import cloudscraper


status_tag = {
    1:'Заявку подано',
    2:'Дані відправлено на перевірку',
    3:'Дані відправлено на персоналізацію',
    4:'Документ виготовлено',
    5:'Документ прибув до ЗДУ',
    6:'Документ видано'
}


class Scraper():
    def __init__(self):
        # Init scraper.
        self.scraper = cloudscraper.create_scraper() # Needed to bypass cloudflare
    
    def check(self, identifier):
        # Check valid and status.
        try:
            # Generate new headers every time when we call func.
            headers = Headers().generate() # Fake headers
            # Scraping
            r = self.scraper.get(f"http://passport.mfa.gov.ua/Home/CurrentSessionStatus?sessionId={identifier}", headers=headers)
            # r = self.scraper.get(f"http://127.0.0.1:8000/{identifier}", headers=headers)
            if r.content:
                jsn = r.json()
                max = len(jsn['StatusInfo'])
                return [status_tag[max], max]
            else:
                return [False]
        except:
            return [None]



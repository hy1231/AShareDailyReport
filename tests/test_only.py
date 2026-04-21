import requests
from requests.sessions import Session
import efinance as ef

df = ef.stock.get_realtime_quotes('沪深京A股')
a = 0


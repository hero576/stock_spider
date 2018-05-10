import re

import requests

response = requests.get('http://finance.ifeng.com/app/hq/stock/sh603168/index.shtml')

html = response.content.decode()
print(html)

ltg = re.search(r'ltg : (\d+)', html).group(1)
mgsy = re.search(r'mgsy : (\d+[.]\d+)', html).group(1)
mgjzc = re.search(r'mgjzc : (\d+[.]\d+)', html).group(1)
print(ltg, '+', mgsy, '+', mgjzc)
#228725000 + 0 + 6
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import re
from bs4 import BeautifulSoup
from tqdm import tqdm

df = pd.read_csv('crawlingdata.CSV',encoding='CP949')
df['naver_map_url'] = '' # 미리 url을 담을 column을 만들어줌

driver = webdriver.Chrome(executable_path=r'C:\Users\chromedriver.exe') # 웹드라이버가 설치된 경로를 지정해주시면 됩니다.

for i, keyword in enumerate(df['검색어'].tolist()):

    print("이번에 찾을 키워드 :", i, f"/ {df.shape[0]} 행", keyword)

    try:
        naver_map_search_url = f'https://map.naver.com/v5/search/{keyword}/place'  # 검색 url 만들기
        driver.get(naver_map_search_url)  # 검색 url 접속 = 검색하기
        time.sleep(4)  # 중요

        cu = driver.current_url  # 검색이 성공된 플레이스에 대한 개별 페이지
        res_code = re.findall(r"place/(\d+)", cu)
        final_url = 'https://pcmap.place.naver.com/restaurant/' + res_code[0] + '/review/visitor#'
        print(final_url)
        df['naver_map_url'][i] = final_url

    except IndexError:
        df['naver_map_url'][i] = ''
        print('none')

    df.to_csv('url_completed.csv', encoding='utf-8-sig')
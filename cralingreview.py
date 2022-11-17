import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

# 웹드라이버 접속
driver = webdriver.Chrome(executable_path=r'C:\Users\chromedriver.exe')

# 전처리 완료한 데이터 불러오기
# url이 없는 경우는 제거함
df = pd.read_csv('url_completed.csv')

# 수집할 정보들
rating_list = []    # rating
user_review_id = {} # user id
review_json = {} # 리뷰
image_json = {} # 리뷰 이미지

for i in range(len(df)):

    print('======================================================')
    print(str(i) + '번째 식당')

    # 식당 리뷰 개별 url 접속
    driver.get(df['naver_map_url'][i])
    thisurl = df['naver_map_url'][i]
    time.sleep(2)

    # 더보기 버튼 다 누를 것
    # 더보기 버튼은 10개 마다 나옴
    while True:
        try:
            time.sleep(1)
            driver.find_element()
            driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
            time.sleep(3)

            driver.find_element(By.CSS_SELECTOR,
                '#app-root > div > div.place_detail_wrapper > div:nth-child(5) > div:nth-child(4) > div:nth-child(4) > div._2kAri > a').click()
            time.sleep(3)
            driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
            time.sleep(1)

        except NoSuchElementException:
            print('-더보기 버튼 모두 클릭 완료-')
            break

            # 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    time.sleep(1)

    # 식당 구분
    restaurant_name = df['검색어'][i]
    print('식당 이름 : ' + restaurant_name)

    user_review_id[restaurant_name] = {}
    review_json[restaurant_name] = {}
    image_json[restaurant_name] = {}

    try:
        restaurant_classificaton = soup.find_all('span', attrs={'class': '_3ocDE'})[0].text

    except:
        restaurant_classificaton = 'none'

    print('식당 구분 : ' + restaurant_classificaton)
    print('----------------------------------------------')

    # 특정 식당에 대한 리뷰 수집
    try:
        # one_review = soup.find_all('div', attrs={'class': '_1Z_GL'})
        one_review = soup.find_all('li', attrs={'class': 'YeINN'})#zPfVt
        review_num = len(one_review)  # 특정 식당의 리뷰 총 개수
        print('리뷰 총 개수 : ' + str(review_num))

        # 모든 리뷰에 대해서 정보 수집
        for i in range(len(one_review)):

            # user url
            user_url = one_review[i].find('div', attrs={'class': 'Lia3P'}).find('a').get('href')
            print('user_url = ' + user_url)

            # user url로부터 user code 뽑아내기
            user_code = re.findall(r"my/(\w+)", user_url)[0]
            print('user_code = ' + user_code)

            # review 1개에 대한 id 만들기
            res_code = re.findall(r"restaurant/(\d+)", thisurl)[0]
            review_id = str(res_code) + "_" + user_code
            print('review_id = ' + review_id)

            # # rating, 별점
            # rating = one_review[i].find('span', attrs={'class': '_2tObC'}).text
            # print('rating = ' + rating)

            ## 주의
            ## 사진 리뷰 유무에 따라 날짜 파싱코드가 다르기 때문에
            ## case 별로 처리해줘야 함
            ## ('span', attrs = {'class':'_3WqoL'})
            ## 사진 없는 경우 : 총 6개 중 4번째
            ## 사진 있는 경우 : 총 5개 중 3번째

            # date
            # 사진 리뷰 없음
            # if len(one_review[i].find_all('span', attrs={'class': '_3WqoL'})) == 5:
            #     date = one_review[i].find_all('span', attrs={'class': '_3WqoL'})[2].text
            #
            # elif len(one_review[i].find_all('span', attrs={'class': '_3WqoL'})) == 6:
            #     date = one_review[i].find_all('span', attrs={'class': '_3WqoL'})[3].text
            #
            # else:
            #     date = ""
            #
            # print('date = ' + date)

            # review 내용
            try:
                review_content = one_review[i].find('span', attrs={'class': 'zPfVt'}).text
            except:  # 리뷰가 없다면
                review_content = "??"
            print('리뷰 내용 : ' + review_content)

            # image 내용
            sliced_soup = one_review[i].find('div', attrs={'class': '_1aFEL _2GO1Q'})

            if (sliced_soup != None):
                sliced_soup = sliced_soup.find('div', attrs={'class': 'dRZ2X'})

                try:
                    img_url = 'https://search.pstatic.net/common/?autoRotate=true&quality=95&type=l&size=800x800&src=' + \
                              re.findall(r'src=(.*jpeg)', str(sliced_soup))[0]

                except:
                    if (len(re.findall(r'src=(.*jpg)', str(sliced_soup))) != 0):
                        img_url = 'https://search.pstatic.net/common/?autoRotate=true&quality=95&type=l&size=800x800&src=' + \
                                  re.findall(r'src=(.*jpg)', str(sliced_soup))[0]
                    elif (len(re.findall(r'src=(.*png)', str(sliced_soup))) != 0):
                        img_url = 'https://search.pstatic.net/common/?autoRotate=true&quality=95&type=l&size=800x800&src=' + \
                                  re.findall(r'src=(.*png)', str(sliced_soup))[0]
                    else:
                        img_url = ""

            else:
                img_url = ""

            print('이미지 url : ' + img_url)
            print('----------------------------------------------')
            print('\n')

            # 리뷰정보
            # user_review_id
            user_review_id[restaurant_name][user_code] = review_id

            # review_json
            review_json[restaurant_name][review_id] = review_content

            # image_json
            image_json[restaurant_name][review_id] = img_url

            # rating_df_list
            #naver_review = user_code, restaurant_name, rating, date
            naver_review = user_code, restaurant_name,review_content #3개
            rating_list.append(naver_review)

            # 리뷰가 없는 경우
    except NoSuchElementException:
        none_review = "네이버 리뷰 없음"
        print(none_review)
        review_num = 0

        # 리뷰정보 = restaurant_name, restaurant_classification, review_num, none_review

        # rating_df_list
        naver_review = user_code, restaurant_name, none_review, none_review
        rating_list.append(naver_review)

print('\n')


# dataframe 저장 및 csv 저장
rating_df = pd.DataFrame(rating_list)
# rating_df.columns = ['UserID','ItemID','Rating','Timestamp']
rating_df.columns = ['UserID','ItemID',"review"]
rating_df.to_csv('rating9.csv', encoding='utf-8-sig')

file_path = "./user_review_id.json"
with open(file_path, 'w') as outfile:
    json.dump(user_review_id, outfile)

    file_path = "./review.json"
    with open(file_path, 'w') as outfile:
        json.dump(review_json, outfile)

    # file_path = "./image.json"
    # with open(file_path, 'w') as outfile:
    #     json.dump(image_json, outfile)
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def get_seoul_news():
    url = "https://media.naver.com/press/081"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    news_items = soup.select('.press_edit_news_item')
    content = "<h2>🗞️ 오늘의 서울신문 주요 뉴스</h2><br>"
    
    for item in news_items[:3]: # 주요 기사 3개
        title = item.select_one('.press_edit_news_title').text.strip()
        link = item.select_one('.press_edit_news_title').find_parent('a')['href']
        desc = item.select_one('.press_edit_news_text').text.strip() if item.select_one('.press_edit_news_text') else ""
        content += f"<b>{title}</b><br>{desc}<br><a href='{link}'>자세히 보기</a><br><br><hr>"
    return content

def send_mail(body):
    user = os.environ.get('NAVER_USER_ID')
    pw = os.environ.get('NAVER_USER_PW')
    
    # 환경 변수가 비어있는지 확인
    if not user or not pw:
        print("에러: NAVER_USER_ID 또는 NAVER_USER_PW가 설정되지 않았습니다.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = "⏰ 아침 7시 서울신문 뉴스 브리핑"
    msg['From'] = user
    msg['To'] = user
    msg.attach(MIMEText(body, 'html'))

    try:
        # SMTP_SSL을 사용하여 네이버 서버에 연결
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as s:
            # TypeError 방지를 위해 직접 인증 시도
            s.ehlo()
            s.login(user, pw)
            s.sendmail(user, user, msg.as_string())
            print("메일 발송 성공!")
    except Exception as e:
        print(f"메일 발송 중 에러 발생: {e}")

if __name__ == "__main__":
    send_mail(get_seoul_news())

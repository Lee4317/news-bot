import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def get_seoul_news():
    url = "https://media.naver.com/press/081"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        news_items = soup.select('.press_edit_news_item')
        
        content = "<h2>🗞️ 오늘의 서울신문 주요 뉴스</h2><br>"
        for item in news_items[:3]:
            title_tag = item.select_one('.press_edit_news_title')
            if not title_tag: continue
            title = title_tag.text.strip()
            link = title_tag.find_parent('a')['href']
            desc = item.select_one('.press_edit_news_text').text.strip() if item.select_one('.press_edit_news_text') else ""
            content += f"<b>{title}</b><br>{desc}<br><a href='{link}'>자세히 보기</a><br><br><hr>"
        return content
    except Exception as e:
        return f"뉴스 추출 중 오류 발생: {e}"

def send_mail(body):
    # 환경 변수 읽기
    user = os.environ.get('NAVER_USER_ID', '').strip()
    pw = os.environ.get('NAVER_USER_PW', '').strip()
    
    # 값이 비어있는지 체크
    if not user or not pw:
        print(f"❌ 설정 오류: NAVER_USER_ID 또는 NAVER_USER_PW가 비어있습니다.")
        print(f"현재 ID 상태: {'입력됨' if user else '비어있음'}")
        return

    msg = MIMEMultipart()
    msg['Subject'] = "⏰ 아침 뉴스 브리핑"
    msg['From'] = user
    msg['To'] = user
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as s:
            s.login(user, pw)
            s.sendmail(user, user, msg.as_string())
            print("✅ 메일 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    news_content = get_seoul_news()
    send_mail(news_content)

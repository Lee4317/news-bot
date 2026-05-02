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
        
        content = "<h2 style='color: #2e7d32;'>🗞️ 오늘의 서울신문 주요 뉴스</h2><br>"
        for item in news_items[:3]:
            title_tag = item.select_one('.press_edit_news_title')
            if not title_tag: continue
            title = title_tag.text.strip()
            link = title_tag.find_parent('a')['href']
            desc = item.select_one('.press_edit_news_text').text.strip() if item.select_one('.press_edit_news_text') else ""
            content += f"<b>{title}</b><br>{desc}<br><a href='{link}'>자세히 보기</a><br><br><hr>"
        return content
    except Exception as e:
        return f"서울신문 추출 중 오류: {e}<br>"

def get_bbc_news():
    # BBC 뉴스 기술/과학 섹션 혹은 메인 (원하시는 섹션으로 변경 가능)
    url = "https://www.bbc.com/news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # BBC의 최신 뉴스 카드 선택자 (사이트 구조에 따라 변경될 수 있음)
        # 현재 BBC 구조에 최적화된 선택자입니다.
        articles = soup.find_all('div', {'data-testid': 'promo'}, limit=3)
        
        content = "<h2 style='color: #b71c1c;'>🌍 BBC World News (Top 3)</h2><br>"
        for art in articles:
            title_tag = art.find('h2')
            link_tag = art.find('a')
            desc_tag = art.find('p')
            
            if not title_tag or not link_tag: continue
            
            title = title_tag.text.strip()
            link = "https://www.bbc.com" + link_tag['href'] if not link_tag['href'].startswith('http') else link_tag['href']
            desc = desc_tag.text.strip() if desc_tag else "No description available."
            
            content += f"<b>{title}</b><br>{desc}<br><a href='{link}'>Read More</a><br><br><hr>"
        return content
    except Exception as e:
        return f"BBC 뉴스 추출 중 오류: {e}<br>"

def send_mail(body):
    user = os.environ.get('NAVER_USER_ID', '').strip()
    pw = os.environ.get('NAVER_USER_PW', '').strip()
    
    if not user or not pw:
        print("❌ 설정 오류: ID/PW를 찾을 수 없습니다.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = "⏰ 글로벌 뉴스 브리핑 (서울신문 & BBC)"
    msg['From'] = user
    msg['To'] = user
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as s:
            s.login(user, pw)
            s.sendmail(user, user, msg.as_string())
            print("✅ 통합 뉴스 메일 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    # 두 뉴스 내용을 합칩니다.
    combined_content = get_seoul_news() + "<br><br>" + get_bbc_news()
    send_mail(combined_content)

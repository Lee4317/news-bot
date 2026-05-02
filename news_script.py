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
        return f"서울신문 추출 실패: {e}<br>"

def get_bbc_news():
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers)
        # 'lxml' 파서를 명시적으로 사용합니다.
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item', limit=3)
        
        content = "<h2 style='color: #b71c1c;'>🌍 BBC World News (Top 3)</h2><br>"
        if not items:
            return content + "BBC 뉴스를 찾을 수 없습니다. (데이터 없음)<br>"
            
        for item in items:
            title = item.title.text.strip() if item.title else "No Title"
            link = item.link.text.strip() if item.link else "#"
            desc = item.description.text.strip() if item.description else "No description"
            content += f"<b>{title}</b><br>{desc}<br><a href='{link}'>Read More</a><br><br><hr>"
        return content
    except Exception as e:
        # 에러가 나면 메일 내용에 에러 메시지를 포함시킵니다.
        return f"<h2 style='color: red;'>❌ BBC 추출 실패</h2> 원인: {e}<br>"

def send_mail(body):
    user = os.environ.get('NAVER_USER_ID', '').strip()
    pw = os.environ.get('NAVER_USER_PW', '').strip()
    
    if not user or not pw:
        print("❌ ID/PW 누락")
        return

    msg = MIMEMultipart()
    msg['Subject'] = "⏰ 글로벌 뉴스 (서울신문 & BBC)"
    msg['From'] = user
    msg['To'] = user
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as s:
            s.login(user, pw)
            s.sendmail(user, user, msg.as_string())
            print("✅ 발송 완료")
    except Exception as e:
        print(f"❌ 발송 에러: {e}")

if __name__ == "__main__":
    # 두 뉴스를 합쳐서 보냅니다.
    combined_content = get_seoul_news() + "<br><br>" + get_bbc_news()
    send_mail(combined_content)

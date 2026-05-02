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
    # 가장 안정적인 RSS 피드 방식 사용 (World 뉴스)
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers)
        # RSS는 XML 형식이므로 lxml이나 html.parser로 분석 가능
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item', limit=3)
        
        content = "<h2 style='color: #b71c1c;'>🌍 BBC World News (Top 3)</h2><br>"
        if not items:
            content += "현재 업데이트된 BBC 뉴스가 없습니다.<br>"
            
        for item in items:
            title = item.title.text.strip()
            link = item.link.text.strip()
            desc = item.description.text.strip()
            content += f"<b>{title}</b><br>{desc}<br><a href='{link}'>Read More</a><br><br><hr>"
        return content
    except Exception as e:
        return f"BBC 뉴스 추출 실패: {e}<br>"

def send_mail(body):
    user = os.environ.get('NAVER_USER_ID', '').strip()
    pw = os.environ.get('NAVER_USER_PW', '').strip()
    
    if not user or not pw:
        print("❌ 설정 오류: ID/PW가 비어있습니다.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = "⏰ 서울신문 & BBC 뉴스 브리핑"
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
    combined_content = get_seoul_news() + "<br><br>" + get_bbc_news()
    send_mail(combined_content)

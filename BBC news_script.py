import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_bbc_news():
    # BBC World 뉴스 RSS 피드
    rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    feed = feedparser.parse(rss_url)
    news_list = ""
    
    for entry in feed.entries[:5]:
        news_list += f"제목: {entry.title}\n링크: {entry.link}\n\n"
    return news_list

def send_naver_email(content):
    # 네이버 계정 정보
    naver_id = "내아이디" # @naver.com 제외한 아이디
    naver_pw = "네이버비밀번호" # 또는 애플리케이션 비밀번호
    
    send_addr = f"{naver_id}@naver.com"
    recv_addr = "받는사람@email.com" # 본인에게 보내려면 본인 메일 주소

    # 메일 객체 설정
    msg = MIMEMultipart()
    msg['Subject'] = "오늘의 BBC 뉴스 요약 (Naver 전송)"
    msg['From'] = send_addr
    msg['To'] = recv_addr
    msg.attach(MIMEText(content, 'plain'))

    try:
        # 네이버 SMTP 서버 정보: smtp.naver.com / 포트: 465
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(naver_id, naver_pw)
            server.send_message(msg)
        print("네이버 메일 발송 성공!")
    except Exception as e:
        print(f"발송 실패: {e}")

if __name__ == "__main__":
    news_data = get_bbc_news()
    if news_data:
        send_naver_email(news_data)
    else:
        print("뉴스를 가져오지 못했습니다.")

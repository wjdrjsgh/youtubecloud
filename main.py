from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse
import requests
from google.cloud import vision
import os

# FastAPI 앱 생성
app = FastAPI()

# Google Vision API 서비스 계정 키 경로 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\dhfkr\Downloads\youtube-summarizer-446510-4c670fb16c60.json"

# YouTube Data API 키
YOUTUBE_API_KEY = "AIzaSyDywyylijdQYwW1tM5MIM15r6McrGqXYyM"

def get_video_id(encoded_path: str) -> str:
    """유튜브 경로에서 YouTube ID 추출"""
    decoded_path = urllib.parse.unquote(encoded_path)  # URL 디코딩
    if "youtu.be" in decoded_path:
        video_id = decoded_path.split("youtu.be/")[1].split("?")[0]
    elif "watch" in decoded_path:
        video_id = decoded_path.split("v=")[-1].split("&")[0]
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 유튜브 경로 형식입니다.")
    return video_id

def get_video_info(video_id: str) -> dict:
    """YouTube Data API로 제목, 썸네일 URL, 유튜버 이름 가져오기"""
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="YouTube Data API 호출 실패")
    
    data = response.json()
    if "items" not in data or not data["items"]:
        raise HTTPException(status_code=404, detail="유효하지 않은 비디오 ID")

    snippet = data["items"][0]["snippet"]
    title = snippet.get("title", "제목 없음")
    channel_title = snippet.get("channelTitle", "채널 이름 없음")
    thumbnail_url = snippet["thumbnails"]["high"]["url"]  # 고해상도 썸네일
    return {"title": title, "channel_title": channel_title, "thumbnail_url": thumbnail_url}

def extract_text_from_thumbnail(thumbnail_url: str) -> str:
    """Google Vision API로 썸네일 이미지에서 텍스트 추출"""
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image()
        image.source.image_uri = thumbnail_url
        response = client.text_detection(image=image)
        if response.error.message:
            raise HTTPException(status_code=500, detail=f"Google Vision API 오류: {response.error.message}")
        texts = response.text_annotations
        if texts:
            return texts[0].description.strip()  # 가장 첫 번째(전체 텍스트)
        return "텍스트 없음"
    except Exception as e:
        return f"OCR 실패: {e}"

@app.get("/transcripts/")
def get_transcripts(
    youtube_path: str = Query(..., description="유튜브 비디오 경로, URL 인코딩 필요")
):
    """YouTube ID를 받고 '제목', '썸네일 텍스트', '유튜버 이름', '스크립트' 반환"""
    video_id = get_video_id(youtube_path)
    try:
        # 제목, 썸네일 URL, 유튜버 이름 가져오기
        video_info = get_video_info(video_id)
        title = video_info["title"]
        channel_title = video_info["channel_title"]
        thumbnail_url = video_info["thumbnail_url"]
        
        # 썸네일에서 텍스트 추출
        thumbnail_text = extract_text_from_thumbnail(thumbnail_url)

        # 자막 가져오기
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcripts = []
        for transcript in transcript_list:
            try:
                language_code = transcript.language_code
                transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
                combined_transcript = ' '.join(item['text'] for item in transcript_text)
                transcripts.append(combined_transcript)
            except:
                continue
        
        # 최종 응답 구성
        return {
            "title": title,
            "thumbnail_text": thumbnail_text,
            "channel_title": channel_title,
            "content": transcripts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {e}")

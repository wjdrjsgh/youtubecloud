from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse
import requests

app = FastAPI()

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
    """YouTube Data API로 제목, 유튜버 이름, 게시일, 썸네일 링크 가져오기"""
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
    published_at = snippet.get("publishedAt", "게시일 없음")  # 게시일 추가
    thumbnail_url = snippet["thumbnails"]["high"]["url"]  # 썸네일 링크
    return {"title": title, "channel_title": channel_title, "published_at": published_at, "thumbnail_url": thumbnail_url}

@app.get("/transcripts/")
def get_transcripts(
    youtube_path: str = Query(..., description="유튜브 비디오 경로, URL 인코딩 필요")
):
    """YouTube ID를 받고 '제목', '유튜버 이름', '게시일', '썸네일 링크', '스크립트' 반환"""
    video_id = get_video_id(youtube_path)
    try:
        # 제목, 유튜버 이름, 게시일, 썸네일 링크 가져오기
        video_info = get_video_info(video_id)
        title = video_info["title"]
        channel_title = video_info["channel_title"]
        published_at = video_info["published_at"]
        thumbnail_url = video_info["thumbnail_url"]

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
            "channel_title": channel_title,
            "published_at": published_at,
            "thumbnail_url": thumbnail_url,  # 썸네일 링크 포함
            "content": transcripts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {e}")

# FastAPI 실행 설정
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

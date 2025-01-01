from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse

app = FastAPI()

def get_video_id(encoded_path: str) -> str:
    """유튜브 경로에서 youtube ID 추출"""
    decoded_path = urllib.parse.unquote(encoded_path)  # URL 디코딩
    if "youtu.be" in decoded_path:
        video_id = decoded_path.split("youtu.be/")[1].split("?")[0]
    elif "watch" in decoded_path:
        video_id = decoded_path.split("v=")[-1].split("&")[0]
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 유튜브 경로 형식입니다.")
    return video_id

@app.get("/transcripts/")
def get_transcripts(
    youtube_path: str = Query(..., description="유튜브 비디오 경로, URL 인코딩 필요")
):
    """youtube id 를 받고 'script' key 로 반환"""
    video_id = get_video_id(youtube_path)
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcripts = []
        for transcript in transcript_list:
            language_code = transcript.language_code
            transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
            # 여러개의 String 배열을 단일 String 배열로
            combined_transcript = ' '.join(item['text'] for item in transcript_text)
            transcripts.append(combined_transcript)
        return {"script": transcripts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자막을 가져오는 중 오류 발생: {e}")
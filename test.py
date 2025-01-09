from youtube_transcript_api import YouTubeTranscriptApi

def test_youtube_transcript_korean(video_id):
    try:
        # 한국어('ko') 자막 가져오기
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        
        # 자막 출력
        print("한국어 자막 가져오기 성공!")
        for item in transcript:
            print(f"[{item['start']:.2f}s - {item['start'] + item['duration']:.2f}s]: {item['text']}")
    except Exception as e:
        print(f"자막 가져오기 실패: {e}")

# 테스트할 YouTube 비디오 ID
video_id = "Yr315ytR8Ro"  # 테스트할 비디오 ID
test_youtube_transcript_korean(video_id)

def get_maxres_thumbnail(youtube_url: str) -> str:
    import re

    # 유튜브 비디오 ID 추출
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
    if not match:
        return "Invalid YouTube URL"
    
    video_id = match.group(1)
    # maxres 썸네일 URL 생성
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

# 테스트
youtube_url = "https://www.youtube.com/watch?v=fxjCfPS6G2U"
thumbnail_url = get_maxres_thumbnail(youtube_url)
print(thumbnail_url)

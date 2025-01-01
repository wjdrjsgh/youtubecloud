from google.cloud import vision
import requests
from io import BytesIO

# Google Cloud Vision API 서비스 계정 키 경로 설정
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\dhfkr\Downloads\youtube-summarizer-446510-4c670fb16c60.json"

def extract_text_with_vision_api(image_url):
    """
    Google Vision API를 사용하여 이미지 URL에서 텍스트 추출
    """
    try:
        # Vision API 클라이언트 생성
        client = vision.ImageAnnotatorClient()

        # URL에서 이미지 데이터 가져오기
        response = requests.get(image_url)
        if response.status_code != 200:
            return f"이미지를 가져오지 못했습니다. 상태 코드: {response.status_code}"

        # Vision API에 이미지 데이터 전달
        image = vision.Image(content=response.content)
        response = client.text_detection(image=image)

        # 결과에서 텍스트 추출
        texts = response.text_annotations
        if not texts:
            return "텍스트를 감지하지 못했습니다."
        
        # 첫 번째 결과가 전체 텍스트
        full_text = texts[0].description.strip()
        return full_text
    except Exception as e:
        return f"오류 발생: {e}"

if __name__ == "__main__":
    # 테스트할 이미지 URL
    image_url = "https://img.youtube.com/vi/rzkXYXKWkvg/maxresdefault.jpg"
    
    # OCR 결과 출력
    extracted_text = extract_text_with_vision_api(image_url)
    print("추출된 텍스트:")
    print(extracted_text)

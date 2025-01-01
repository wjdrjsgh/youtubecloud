import requests
import easyocr
from PIL import Image, ImageEnhance, ImageOps
from io import BytesIO
import numpy as np

def preprocess_image(image):
    # Grayscale 변환
    image = image.convert("L")
    # 대비 증가
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    # 이진화 처리 (Thresholding)
    image = ImageOps.autocontrast(image)
    return image

def extract_text_from_url(image_url):
    try:
        # 이미지 다운로드
        response = requests.get(image_url)
        response.raise_for_status()
        
        # PIL 이미지 열기
        image = Image.open(BytesIO(response.content))
        
        # 이미지 전처리
        processed_image = preprocess_image(image)
        
        # 이미지 데이터를 numpy 배열로 변환
        image_np = np.array(processed_image)

        # EasyOCR 초기화 및 텍스트 추출
        reader = easyocr.Reader(['ko', 'en'], gpu=False)
        result = reader.readtext(image_np, detail=0)
        
        return "\n".join(result)
    except Exception as e:
        return f"텍스트 추출 실패: {e}"

if __name__ == "__main__":
    # 테스트할 썸네일 이미지 URL
    image_url = "https://img.youtube.com/vi/rzkXYXKWkvg/maxresdefault.jpg"
    
    # 텍스트 추출 및 출력
    extracted_text = extract_text_from_url(image_url)
    print(f"추출된 텍스트:\n{extracted_text}")

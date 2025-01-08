FROM python:3.11-slim-buster

ARG UID=1000
ARG GID=1000

# 그룹 및 사용자 생성
RUN groupadd -g "${GID}" appgroup && \
    useradd --create-home --no-log-init -u "${UID}" -g "${GID}" appuser

# 작업 디렉토리 설정
WORKDIR /app

# pip 업그레이드 및 패키지 설치
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

# requirements.txt 파일 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사 후 권한 변경
COPY . .
RUN chown -R appuser:appgroup /app
RUN chmod +x main.py

# 사용자 변경
USER appuser:appgroup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 80

# FastAPI 애플리케이션 실행
ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", "--port", "80"]

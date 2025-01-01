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
    pip install --upgrade pip

# requirements.txt 파일 복사 및 패키지 설치
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install -r requirements.txt

# 사용자 변경
USER appuser:appgroup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 애플리케이션 파일 복사
COPY --chown=appuser:appgroup . .

# 포트 노출
EXPOSE 8080

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
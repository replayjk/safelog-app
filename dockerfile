FROM python:3.11          # 파이썬 3.11 버전 준비
WORKDIR /app              # 요리할 장소 설정
COPY . .                  # 모든 재료 넣기
RUN pip install -r requirements.txt  # 필요한 재료 (패키지) 설치
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  # 도시락 완성

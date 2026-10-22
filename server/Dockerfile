# LFAI 등기 쿠폰 백엔드 — 이식용 컨테이너 (서버 PC 오면 그대로 docker compose up)
FROM python:3.12-slim

# adb(실기기 세션 adb_runner) + websocket-client(CDP) 만 추가. 나머지는 표준 라이브러리.
RUN apt-get update && apt-get install -y --no-install-recommends android-tools-adb \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir websocket-client

WORKDIR /app
COPY coupon_server.py adb_runner.py ./

ENV LFAI_COUPON_PORT=8787 \
    LFAI_COUPON_DB=/data/coupons.db \
    IROS_OUT=/data/sessions \
    IROS_CDP_PORT=9222
VOLUME /data
EXPOSE 8787

CMD ["python", "coupon_server.py"]

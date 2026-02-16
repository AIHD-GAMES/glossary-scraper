
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# サービスアカウントはSecret Managerから取得することを想定
# ここでは一旦、ローカルと同じようにスクリプトを実行する環境を構築
CMD ["python", "main.py"]

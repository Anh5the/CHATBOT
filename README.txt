Cấu trúc thư mục:
===================
backend: Chứa mã nguồn Python FastAPI backend
db: Chứa bản sao của cơ sở dữ liệu. Bạn cần import bản sao này vào cơ sở dữ liệu MySQL bằng công cụ MySQL Workbench
dialogflow_assets: Chứa các cụm từ huấn luyện v.v. cho các ý định của chúng ta
frontend: Mã nguồn trang web

Cài đặt các module:
======================
```
pip install mysql-connector
pip install "fastapi[all]"
```
HOẶC chạy lệnh:
```
pip install -r backend/requirements.txt
```
để cài đặt cả hai module cùng một lúc.

Khởi động máy chủ backend FastAPI:
====================================
1. Đi đến thư mục backend trong dòng lệnh của bạn
2. Chạy lệnh này: 
```
uvicorn main:app --reload
```

Sử dụng ngrok để tạo kênh https:
==================================
1. Để cài đặt ngrok, truy cập https://ngrok.com/download và cài đặt phiên bản ngrok phù hợp với hệ điều hành của bạn.
2. Giải nén tệp zip và đặt ngrok.exe trong một thư mục.
3. Mở command prompt trên Windows, đi đến thư mục đó và chạy lệnh:
```
ngrok http 8000
```

LƯU Ý: ngrok có thể hết thời gian. Bạn cần khởi động lại phiên nếu bạn nhìn thấy thông báo hết hạn phiên.
# AI Agent EXE

AI Agent EXE là ứng dụng chatbot AI được xây dựng bằng OpenAI API, hỗ trợ chạy dưới dạng ứng dụng độc lập hoặc triển khai bằng Docker.

## 🚀 Tính năng

- Chat với AI thông qua OpenAI API
- Giao diện thân thiện
- Hỗ trợ Docker Deployment
- Dễ dàng đóng gói thành file EXE
- Quản lý dữ liệu bằng Database
- Cấu hình linh hoạt bằng Environment Variables

## 🛠 Công nghệ sử dụng

- Python
- OpenAI API
- Docker
- FastAPI
- PostgreSQL / MySQL
- SQLAlchemy

## 📂 Cấu trúc dự án

```bash
AI_Agent_EXE/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   └── utils/
│
├── docker/
├── data/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## ⚙️ Cài đặt

### 1. Clone project

```bash
git clone https://github.com/Vinh0905/AI_Agent_EXE.git
cd AI_Agent_EXE
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Cấu hình API Key

Tạo file `.env`

```env
OPENAI_API_KEY=your_api_key
```

## ▶️ Chạy ứng dụng

```bash
python main.py
```

Hoặc:

```bash
uvicorn app.main:app --reload
```

## 🐳 Chạy bằng Docker

Build image:

```bash
docker build -t ai-agent .
```

Run container:

```bash
docker run -p 8000:8000 ai-agent
```

Hoặc sử dụng Docker Compose:

```bash
docker-compose up -d
```

## 📡 API Endpoint

### Chat

```http
POST /chat
```

Request:

```json
{
  "message": "Xin chào"
}
```

Response:

```json
{
  "response": "Chào bạn!"
}
```

## 📦 Đóng gói thành EXE

Cài PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --onefile main.py
```

File thực thi sẽ nằm trong thư mục:

```bash
dist/
```

## 🔒 Biến môi trường

| Variable | Description |
|-----------|------------|
| OPENAI_API_KEY | OpenAI API Key |
| QDRANT_API_KEY| Qdrant API Key |
| QDRANT_URL | Qdrant Url |

## 🤝 Đóng góp

Pull Request luôn được chào đón.

## 📄 License

MIT License

## 👨‍💻 Tác giả

**Vinh Trần**

GitHub: https://github.com/Vinh0905

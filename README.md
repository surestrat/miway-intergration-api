# MiWay Integration API

A FastAPI application for integrating with DTech External Sales API, featuring secure AWS Signature V4 authentication and Appwrite backend.

## 🚀 Features

- DTech External Sales API integration with AWS Signature V4 authentication
- Real-time call recording upload with progress tracking
- Session management with Redis
- Secure user authentication via Appwrite
- Modern web interface with responsive design
- Docker support for easy deployment

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Appwrite account
- DTech API credentials
- Redis (optional, falls back to in-memory storage)

## 🛠️ Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/miway-intergration-api.git
cd miway-intergration-api
```

2. **Set up environment variables**
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
- Appwrite credentials
- DTech API credentials
- AWS credentials (from DTech activation)

3. **Create Appwrite Collections**
   - Create a new project in [Appwrite Console](https://cloud.appwrite.io)
   - Create a database
   - Create two collections:
     - `sales_processes`
     - `recordings`
   - Note down the IDs and update your `.env` file:
     ```
     APPWRITE_DATABASE_ID="your_database_id"
     APPWRITE_SALES_COLLECTION_ID="your_sales_collection_id"
     APPWRITE_RECORDINGS_COLLECTION_ID="your_recordings_collection_id"
     ```

4. **Run the Appwrite setup script**
```bash
python scripts/setup_appwrite.py
```
This will create all necessary attributes and indexes in your collections.

5. **Build and run with Docker**
```bash
docker-compose up --build
```

Or run locally:
```bash
pip install -r requirements.txt
python run.py
```

The API will be available at http://localhost:4005

## 📌 API Endpoints

### Sales Process

- `POST /api/v1/sales/start` - Start a new sales process
- `POST /api/v1/sales/continue/{spid}` - Continue an existing process
- `GET /api/v1/sales/status/{spid}/{accountid}` - Check process status
- `POST /api/v1/sales/stop/{spid}` - Stop a process
- `POST /api/v1/sales/recording-url/{spid}` - Get recording upload URL

### Authentication

- `GET /api/v1/sales/login-form` - Get login form
- `POST /api/v1/sales/login` - Login user
- `POST /api/v1/sales/logout` - Logout user

## 🔒 Security Features

- AWS Signature V4 authentication for DTech API
- Secure session management
- HTTPS support
- CORS protection
- Input validation
- XSS protection

## 📁 Project Structure

```
.
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── schemas/      # Pydantic models
│   ├── services/     # Business logic
│   ├── static/       # Static files
│   ├── templates/    # HTML templates
│   └── utils/        # Utility functions
├── config/           # Configuration
├── docs/            # Documentation
└── scripts/         # Setup scripts
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📚 Documentation

- [DTech API Guide](docs/dtech_api_guide.md) - Detailed DTech API integration guide
- API documentation available at `/docs` or `/redoc` when running the application

## 🚀 Deployment

1. Update `.env` with production settings
2. Build the Docker image:
```bash
docker-compose -f docker-compose.prod.yml build
```

3. Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## ⚙️ Configuration

Key configuration options in `.env`:

- `APPWRITE_*` - Appwrite settings
- `DIFFERENT_API_*` - DTech API endpoints
- `AWS_*` - AWS credentials
- `REDIS_*` - Redis configuration

## 📝 License

[MIT License](LICENSE)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🐛 Known Issues

- None currently reported

## 📞 Support

- Create an issue in the repository
- Contact: support@example.com

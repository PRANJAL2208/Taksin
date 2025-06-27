# === Install Dependencies ===
install:
	pip install -r requirements.txt

# === Run Backend (FastAPI) ===
backend:
	uvicorn main:app --reload

# === Run Frontend (Streamlit) ===
frontend:
	streamlit run streamlit_app.py

# === Build Docker Image ===
docker-build:
	docker build -t llm-qa-app .

# === Run Docker Container ===
docker-run:
	docker run -p 8000:8000 --env-file .env llm-qa-app

# === Stop All Containers ===
docker-stop:
	docker stop $$(docker ps -q)

# === Clean Docker Images ===
docker-clean:
	docker system prune -af

# === Run Both Backend and Frontend Locally ===
run:
	start cmd /k "make backend"
	start cmd /k "make frontend"

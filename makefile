include .env
export

all: up

up:
	docker-compose up --build -d

down:
	docker-compose down

copy_env_linux:
	cat example.env .env

copy_env_windows:
	cp example.env .env

build_torch_image:
	docker build -t torch_image -f deploy/Dockerfile_torch .

build_index_image:
	docker build --env-file .env -t index_image -f deploy/Dockerfile_indexing .

build_db_image:
	docker build --env-file .env -t db_image -f deploy/Dockerfile_database .

index_service_start: build_torch_image build_emb_model_image
	docker-compose up --build -d indexing_service

qa_service_start: build_torch_image build_qa_model_image
	docker-compose up --build -d qa_service

first_full_start: build_torch_image
	docker-compose up --build -d

help:
	@echo "Доступные цели:"
	@echo "  all                  - (По умолчанию) Запускает сервисы с пересборкой."
	@echo "  up                   - Запускает сервисы с пересборкой."
	@echo "  down                 - Останавливает сервисы."
	@echo "  copy_env_linux       - Копирует example.env в .env."
	@echo "  copy_env_windows     - Копирует example.env в .env."	
	@echo "  build_*_image        - Собирает образ сервиса. Варианты *: torch, qa_model, emb_model, index, db"
	@echo "  index_service_start  - Запускает indexing_service."
	@echo "  qa_service_start     - Запускает qa_service."
	@echo "  first_full_start     - Запускает все сервисы."

.PHONY: all up down copy_env build_torch_image build_qa_model_image build_emb_model_image build_index_image build_db_image index_service_start qa_service_start full_start help
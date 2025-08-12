# GitHub Secrets 설정 가이드

GitHub Actions CI/CD 파이프라인을 위해 다음 환경변수들을 GitHub Repository Secrets에 등록해야 합니다.

## 🔐 GitHub Repository Secrets 등록 방법

1. GitHub 저장소로 이동
2. **Settings** 탭 클릭
3. 좌측 메뉴에서 **Secrets and variables** > **Actions** 클릭
4. **New repository secret** 버튼 클릭
5. 아래 목록의 변수들을 하나씩 추가

---

## 📋 필수 등록 환경변수 목록

### 🔑 AI Service API Keys (필수)
```bash
# OpenAI GPT API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Gemini API Key
GOOGLE_API_KEY=your-google-gemini-api-key-here

# Naver Clova API Credentials
CLOVA_API_KEY=your-clova-api-key-here
CLOVA_API_SECRET=your-clova-api-secret-here
```

### 🗄️ Database Configuration (필수)
```bash
# MySQL Database URL for production
DATABASE_URL=mysql+aiomysql://username:password@host:port/database_name

# MySQL Root Password
MYSQL_ROOT_PASSWORD=your-secure-mysql-password
```

### 🔴 Redis & Message Queue (필수)
```bash
# Redis Connection URL
REDIS_URL=redis://your-redis-host:6379

# Kafka Bootstrap Servers
KAFKA_BOOTSTRAP_SERVERS=your-kafka-host:9092
```

### 🔒 Application Security (필수)
```bash
# Secret key for JWT tokens and session encryption
SECRET_KEY=your-super-secret-key-for-jwt-and-sessions

# API Keys for application access
ADMIN_API_KEY=your-admin-api-key-here
USER_API_KEY=your-user-api-key-here
```

### 🐳 Azure Container Registry (필수)
```bash
# Azure Container Registry Credentials
ACR_USERNAME=your-acr-username
ACR_PASSWORD=your-acr-password

# Azure AKS Deployment
AZURE_CREDENTIALS='{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret", 
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}'

# GitHub Token (자동으로 제공됨 - 수동 등록 불필요)
GITHUB_TOKEN=automatically-provided-by-github
```

---

## 🔧 선택적 환경변수 (필요시 등록)

### ☁️ 클라우드 서비스 (선택사항)
```bash
# Azure Services (사용하는 경우)
AZURE_CONNECTION_STRING=your-azure-connection-string

# AWS Services (사용하는 경우)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

### 📊 모니터링 & 알림 (선택사항)
```bash
# Sentry Error Tracking
SENTRY_DSN=https://your-sentry-dsn-here

# Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#smart-factory-alerts

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 🎯 환경별 설정 방법

### Development Environment
로컬 개발을 위해서는 `.env` 파일을 생성하세요:
```bash
# 프로젝트 루트에서
cp .env.example .env
# .env 파일을 편집하여 실제 값들을 입력하세요
```

### Production Environment
GitHub Secrets에 등록된 값들이 자동으로 사용됩니다.

---

## ⚠️ 보안 주의사항

### 🚫 절대 하지 말아야 할 것들:
- **코드에 직접 API 키 하드코딩 금지**
- **`.env` 파일을 Git에 커밋 금지**
- **Secrets를 로그에 출력 금지**

### ✅ 권장사항:
- **강력한 SECRET_KEY 생성** (최소 32자, 랜덤 문자열)
- **정기적인 API 키 로테이션**
- **최소 권한 원칙 적용**
- **프로덕션과 개발 환경 분리**

---

## 🔍 설정 검증 방법

### 1. GitHub Actions에서 확인
GitHub Actions 실행 시 다음과 같은 로그가 나타나면 정상:
```
✅ Environment variables loaded successfully
✅ API keys validation passed
✅ Database connection established
```

### 2. 로컬에서 확인
```bash
# 프로젝트 루트에서
python -c "from config.settings import settings; print('✅ Settings loaded successfully')"
```

### 3. Health Check API 확인
```bash
# 서버 실행 후
curl http://localhost:8000/health
```

---

## 🚀 Azure Kubernetes Service (AKS) 배포 설정

### AKS 클러스터 생성
먼저 Azure CLI를 사용해 AKS 클러스터를 생성하세요:

```bash
# Azure CLI 로그인
az login

# 리소스 그룹 생성
az group create --name 23-rsrc --location koreacentral

# ACR (Azure Container Registry) 생성
az acr create --resource-group 23-rsrc --name 23acr --sku Standard

# AKS 클러스터 생성
az aks create \
  --resource-group 23-rsrc \
  --name 23-aks \
  --node-count 2 \
  --enable-addons monitoring \
  --attach-acr 23acr \
  --generate-ssh-keys

# kubectl 설정
az aks get-credentials --resource-group 23-rsrc --name 23-aks
```

### Azure Service Principal 생성
GitHub Actions가 AKS에 배포할 수 있도록 Service Principal을 생성하세요:

```bash
# Service Principal 생성
az ad sp create-for-rbac \
  --name "github-actions-smart-factory" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/23-rsrc \
  --sdk-auth

# ACR에 대한 권한 부여
az acr login --name 23acr
az role assignment create \
  --assignee {service-principal-client-id} \
  --role AcrPush \
  --scope /subscriptions/{subscription-id}/resourceGroups/23-rsrc/providers/Microsoft.ContainerRegistry/registries/23acr
```

### GitHub Secrets 등록
위에서 생성한 정보를 GitHub Secrets에 등록하세요:
- `AZURE_CREDENTIALS`: Service Principal JSON 출력 전체
- `ACR_USERNAME`: ACR 사용자명
- `ACR_PASSWORD`: ACR 비밀번호

### Production Server Access (필요시)
```bash
# SSH 키 (서버 배포용)
SSH_PRIVATE_KEY=your-ssh-private-key-for-deployment
SSH_HOST=your-production-server-ip
SSH_USER=deployment-user
```

---

## ❓ 문제 해결

### API 키가 작동하지 않는 경우:
1. 각 서비스의 API 키 형식 확인
2. API 키의 권한 및 할당량 확인
3. GitHub Secrets 이름 정확성 확인

### 데이터베이스 연결 실패:
1. DATABASE_URL 형식 검증
2. 네트워크 접근 권한 확인
3. 데이터베이스 서버 상태 확인

### Docker 빌드 실패:
1. GITHUB_TOKEN 권한 확인
2. Container Registry 접근 권한 확인
3. Dockerfile 구문 검증

---

## 📚 참고 자료

- [GitHub Secrets 공식 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Docker Build and Push Action](https://github.com/docker/build-push-action)
- [Python Environment Variables Best Practices](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1)

---

**💡 Tip**: 모든 환경변수를 한 번에 설정하지 말고, CI/CD 파이프라인을 단계별로 테스트하면서 필요한 것들을 점진적으로 추가하세요!
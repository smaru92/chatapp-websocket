# ChatApp WebSocket

실시간 다국어 번역을 지원하는 의료 상담 채팅 애플리케이션

## 프로젝트 소개

환자와 병원 간의 실시간 채팅을 지원하는 WebSocket 기반 서버리스 애플리케이션입니다. DeepL API를 활용한 자동 번역 기능으로 언어 장벽 없는 의료 상담이 가능합니다.

## 주요 기능

- **실시간 메시징**: WebSocket 기반 양방향 통신
- **다국어 자동 번역**: DeepL API를 활용한 20개 이상 언어 지원
- **채팅방 관리**: 환자-병원 간 1:1 상담방 생성 및 관리
- **채팅 기록 조회**: 과거 대화 내역 조회 및 검색
- **읽지 않은 메시지 추적**: 사용자별 안 읽은 메시지 카운트
- **상담 상태 관리**: 상담중/종료 등 상태 변경

## 기술 스택

| 분류 | 기술 |
|------|------|
| Language | Python 3.12 |
| Framework | AWS Lambda, asyncio |
| Database | AWS DynamoDB |
| Real-time | WebSocket (AWS API Gateway) |
| Translation | DeepL API |
| Auth | JWT |
| Deployment | Serverless Framework, Docker |

## 아키텍처

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Client    │────▶│  API Gateway    │────▶│    Lambda    │
│  WebSocket  │◀────│   (WebSocket)   │◀────│   Handler    │
└─────────────┘     └─────────────────┘     └──────┬───────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
                    ▼                              ▼                              ▼
            ┌──────────────┐              ┌──────────────┐              ┌──────────────┐
            │   DynamoDB   │              │   DynamoDB   │              │   DeepL API  │
            │  (Messages)  │              │   (Rooms)    │              │ (Translation)│
            └──────────────┘              └──────────────┘              └──────────────┘
```

## 프로젝트 구조

```
chatapp-websocket/
├── app.py                    # Lambda 핸들러 (라우팅)
├── server.py                 # 로컬 개발용 WebSocket 서버
├── requirements.txt          # Python 의존성
├── Dockerfile
├── docker-compose.yml
├── serverless.yml            # AWS 배포 설정
│
├── functions/                # 핵심 비즈니스 로직
│   ├── connect.py            # 연결 처리
│   ├── disconnect.py         # 연결 해제 처리
│   ├── send_message.py       # 메시지 전송 및 저장
│   ├── translate_message.py  # 메시지 번역
│   ├── set_translated_message.py
│   ├── get_chat_history.py   # 채팅 기록 조회
│   ├── get_room_list.py      # 채팅방 목록 조회
│   └── change_room_status.py # 상담 상태 변경
│
└── utils/                    # 유틸리티
    ├── auth.py               # JWT 인증
    ├── setting.py            # 설정 관리
    ├── aws/
    │   ├── dynamodb.py       # DynamoDB 작업
    │   └── websocket.py      # WebSocket 브로드캐스트
    └── external/
        └── deepl.py          # DeepL API 래퍼
```

## API Routes

| Route | 설명 |
|-------|------|
| `$connect` | WebSocket 연결, 인증 처리 |
| `$disconnect` | 연결 해제, 상태 저장 |
| `sendMessage` | 메시지 전송 + 자동 번역 |
| `getChatHistory` | 채팅 기록 조회 |
| `getRoomList` | 채팅방 목록 조회 |
| `changeRoomStatus` | 상담 상태 변경 |
| `translateMessage` | 메시지 번역 요청 |
| `setTranslatedMessage` | 번역 메시지 저장 |

## 데이터베이스 스키마

### chatapp-connection
| 필드 | 설명 |
|------|------|
| connection_id (PK) | WebSocket 연결 ID |
| room_id | 채팅방 ID |
| user_id | 사용자 ID |
| hospital_id | 병원 ID |
| user_type | 사용자 유형 (user/hospital) |

### chatapp-message
| 필드 | 설명 |
|------|------|
| room_id (PK) | 채팅방 ID |
| timestamp (SK) | 메시지 타임스탬프 |
| message | 원본 메시지 |
| user_translated_message | 사용자용 번역 메시지 |
| hospital_translated_message | 병원용 번역 메시지 |

### chatapp-room
| 필드 | 설명 |
|------|------|
| room_id (PK) | 채팅방 ID |
| last_message | 마지막 메시지 |
| user_unread_count | 사용자 안 읽은 메시지 수 |
| hospital_unread_count | 병원 안 읽은 메시지 수 |
| room_status | 상담 상태 |

## 설치 및 실행

### 환경 변수 설정

```bash
# .env 파일 생성
CHEONGDAM_SECRET_KEY=your_jwt_secret_key
CHEONGDAM_ALGORITHM=HS256
DEEPL_AUTH_KEY=your_deepl_api_key
```

### 로컬 개발

```bash
# Docker로 실행
docker-compose up

# 또는 직접 실행
pip install -r requirements.txt
python server.py
```

### AWS 배포

```bash
# Serverless Framework로 배포
serverless deploy
```

## 메시지 흐름

```
1. 클라이언트 → sendMessage 요청
2. Lambda → 메시지 DynamoDB 저장
3. Lambda → DeepL API 번역 요청 (옵션)
4. Lambda → 번역 결과 저장
5. Lambda → 연결된 클라이언트들에게 브로드캐스트
6. 클라이언트 ← 실시간 메시지 수신
```

## 라이선스

MIT License

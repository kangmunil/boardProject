graph TD
   subgraph "외부"
       Client("💻 Client / Browser")
   end
   subgraph "API Gateway Layer"
       Gateway("🌐 API Gateway<br/>- Routing<br/>- Authentication / Session Handling")
   end
   subgraph "Internal Service Layer"
       BoardService("Board Service<br/>- REST API<br/>- APScheduler")
       BlogService("Blog Service<br/>- REST API<br/>- APScheduler")
       UserService("👤 User Service")
   end
   subgraph "Data Store Layer"
       UserDB("User DB<br/>(MySQL)")
       BoardDB("Board DB<br/>(MySQL)")
       BlogDB("Blog DB<br/>(MySQL)")
       Redis("⚡ Redis<br/>- Session Store<br/>- Cache & Queue")
   end
   
   Client --> Gateway
   Gateway --> Redis
   Gateway --> BoardService
   Gateway --> BlogService
   Gateway --> UserService
   
   UserService --> UserDB
   BoardService --> UserService
   BlogService --> UserService
   BoardService --> BoardDB
   BlogService --> BlogDB
   BoardService --> Redis
   BlogService --> Redis

   %% 스타일링 (선택사항)
   classDef gateway fill:#f8f9fa,stroke:#6c757d
   classDef board fill:#e6f7ff,stroke:#007bff
   classDef blog fill:#d4edda,stroke:#155724
   classDef user fill:#fff7e6,stroke:#ffc107
   classDef redis fill:#fff0f1,stroke:#dc3545
   
   class Gateway gateway
   class BoardService board
   class BlogService blog
   class UserService user
   class Redis redis

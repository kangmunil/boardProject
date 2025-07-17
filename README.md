graph TD
   subgraph "외부"
       Client("💻 Client / Browser")
   end

   subgraph "API Gateway Layer"
       style Gateway fill:#f8f9fa,stroke:#6c757d
       Gateway("🌐 API Gateway\n- Routing\n- Authentication / Session Handling")
   end

   subgraph "Internal Service Layer"
       style BoardService fill:#e6f7ff,stroke:#007bff
       style BlogService fill:#d4edda,stroke:#155724
       style UserService fill:#fff7e6,stroke:#ffc107
       BoardService("Board Service\n- REST API\n- APScheduler")
       BlogService("Blog Service\n- REST API\n- APScheduler")
       UserService("👤 User Service")
   end

   subgraph "Data Store Layer"
       style UserDB fill:#fffbe6,stroke:#ffc107
       style BoardDB fill:#e6f7ff,stroke:#007bff
       style BlogDB fill:#d4edda,stroke:#155724
       style Redis fill:#fff0f1,stroke:#dc3545
       UserDB("User DB\n(MySQL)")
       BoardDB("Board DB\n(MySQL)")
       BlogDB("Blog DB\n(MySQL)")
       Redis("⚡ Redis\n- Session Store\n- Cache & Queue")
   end

   Client -- "REST API Calls" --> Gateway

   Gateway -- "Session Check" --> Redis
   Gateway -- "Route" --> BoardService
   Gateway -- "Route" --> BlogService
   Gateway -- "Route" --> UserService
   
   UserService -- CRUD --> UserDB
   BoardService -- "작성자 정보 조회 (API 호출)" --> UserService
   BlogService -- "작성자 정보 조회 (API 호출)" --> UserService

   BoardService -- "CRUD & Sync" --> BoardDB
   BlogService -- "CRUD & Sync" --> BlogDB

   BoardService -- "캐시/큐 처리" --> Redis
   BlogService -- "캐시/큐 처리" --> Redis

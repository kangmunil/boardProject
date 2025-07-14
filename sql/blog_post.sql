INSERT INTO blogarticle
    (id, title, content, create_at, onwer_id, tags)
VALUES
    (1 , 'FastAPI로 나만의 API 게이트웨이 만들기',
     'Docker Compose로 마이크로서비스를 묶고, nginx reverse-proxy까지 올려보았습니다...',
     '2025-07-14 09:12:33', 3, 'FastAPI,Docker,Microservices'),

    (2 , 'Llama3 vs Gemma3 벤치마킹 결과',
     'M1 Mac mini + 16 GB RAM 환경에서 두 모델의 추론 속도와 메모리 사용량을 비교한 결과는 다음과 같습니다...',
     '2025-07-14 11:45:02', 1, 'AI,LLM,Benchmark'),

    (3 , '건축설비기사 한 달 벼락치기 플랜',
     '문제집 회독 순서, 기출 분류표, 개념 정리 PDF 링크까지—all-in-one 가이드!',
     '2025-07-14 14:27:51', 4, '자격증,StudyPlan,건축설비'),

    (4 , '학생 때 해두면 좋은 금융 습관 5가지',
     '체크카드보다 신용카드를 먼저 쓰라는 말, 사실일까? ISA와 청년도약계좌 활용 팁까지 정리했습니다.',
     '2025-07-14 16:08:19', 2, 'Finance,Hacks,UniversityLife'),

    (5 , 'Plato Reading Club: ‘‘Meno’’ 1주차 후기',
     '소크라테스식 반문법이 이렇게 빡센 줄 몰랐다… 논리 구조를 그림으로 정리해 봤습니다.',
     '2025-07-14 18:55:07', 5, 'Philosophy,Plato,StudyGroup'),

    (6 , '중고 RTX 3090, 아직 살 만할까?',
     '3090 vs 4080 vs 5070 전력 대비 해시레이트, 발열, 리셀 가격까지 총정리.',
     '2025-07-13 10:33:44', 1, 'GPU,Hardware,리뷰'),

    (7 , '‘‘Friends’’로 영어 공부: 발음 코칭 팁',
     '‘‘Could I BE any more excited?’’ 문장 하나로 억양·강세·연결 발음 다 잡기!',
     '2025-07-13 12:18:05', 3, 'English,Pronunciation,Friends'),

    (8 , 'Vercel Edge + PlanetScale로 초경량 블로그 배포',
     'MySQL compatible Serverless DB 세팅부터 Preview Deployment 자동화까지 스텝-바이-스텝.',
     '2025-07-13 15:02:29', 2, 'Vercel,PlanetScale,DevOps'),

    (9 , '코코비 캐릭터 MD 제작 노하우',
     '국내 생산 vs 중국 선주문, MOQ와 단가 계산 예시, 그리고 아마존 FBA 진출 체크리스트.',
     '2025-07-13 18:21:17', 4, 'MD,Commerce,CharacterGoods'),

    (10, 'SAR ADC 동작 원리 초간단 정리',
     '멀티비트 비교, 샘플&홀드, 디지털 보정까지 한 장 슬라이드로 끝!',
     '2025-07-12 09:50:58', 5, 'Analog,ADC,Electronics'),

    (11, '‘‘Discipline and Punish’’를 다시 읽다',
     '푸코의 판옵티콘 개념을 ‘‘SKY Castle’’ 학원 시스템에 대입해 보면…',
     '2025-07-12 13:14:47', 2, 'Foucault,Sociology,BookReview'),

    (12, '타일기능사 실기: 재료 손질 꿀팁',
     '시멘트·모래 배합 비율부터 줄눈 정리까지 시험장에서 바로 써먹는 팁 7가지.',
     '2025-07-12 16:32:22', 3, '타일기능사,HandsOn,DIY'),

    (13, 'Redis Pub/Sub vs Stream, 언제 써야 할까?',
     '실시간 채팅, 이벤트 브로커, 워커 큐 세팅 예제 포함.',
     '2025-07-11 10:05:13', 1, 'Redis,Backend,Architecture'),

    (14, '유통기한 지난 계란, 먹어도 되나?',
     '살모넬라 감염 확률과 안전하게 먹는 방법을 과학적으로 파헤쳐 봤습니다.',
     '2025-07-11 12:44:39', 5, 'FoodSafety,KitchenTips'),

    (15, 'ML Ops 파이프라인을 Poetry + Docker로 간단히',
     'Poetry로 의존성 잠그고, GitHub Actions에서 도커 빌드 → AWS ECR까지 푸시 자동화.',
     '2025-07-11 15:56:02', 4, 'MLOps,Poetry,Docker'),

    (16, 'ANOVA 문제 푸는 두 가지 ALEKS 방식',
     '표본 평균 기반 vs 표본 분산 기반—각 방법의 수식 유도와 예제 문제 해결 과정.',
     '2025-07-10 09:41:28', 2, 'Statistics,ANOVA,ALEKS'),

    (17, '런닝머신 러닝 폼 체크리스트',
     '무릎 통증을 줄이는 착지 방법과 상체 밸런스, 스트라이드 교정 영상 포함.',
     '2025-07-10 13:19:54', 3, 'Running,Health,Fitness'),

    (18, 'Firebase Auth + FastAPI 세션 통합',
     '프론트는 Firebase, 백엔드는 자체 JWT를 써야 할 때 bridging 하는 패턴.',
     '2025-07-10 17:02:40', 1, 'Auth,JWT,FullStack'),

    (19, '서울-암스테르담 왕복 2개월 배낭여행 예산표',
     '항공권, 유스호스텔, 시내 교통패스, 러닝코스 추천까지 총정리.',
     '2025-07-09 11:27:11', 4, 'Travel,Budget,Europe'),

    (20, 'BasisOS 화이트페이퍼 요약',
     '메인넷 구조, 모듈형 설계, 토큰 경제학과 파트너십 로드맵을 10분 컷으로 정리.',
     '2025-07-09 15:48:36', 2, 'Blockchain,Whitepaper,Summarize');

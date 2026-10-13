# 오픈소스 코드 구조 분석을 위한 Coding Agent 활용 가이드 – mini-swe-agent 경우를 중심으로

Coding Agent 프롬프트 설계 · Antigravity에서 `AGENTS.md` 배치 · 파일명 대소문자 주의사항

작성일: 2026-10-12

Q. 오픈 소스 코드를 설치하고 난 후에, SWE 관점에서 해당 오픈 소스 코드 동작 구조 파악을 위해, Coding Agent 에게 어떤 요청 (프롬프트)을 하는 게 좋은 가?

# 1. 오픈소스 동작 구조 파악을 위한 프롬프트 설계

한 번에 "이 코드를 설명해 줘"라고 묻기보다, 요청을 단계로 나누는 편이 결과가 훨씬 좋습니다. 그리고 단계마다 **근거(파일:라인)**, **실제 실행 확인**, **파일로 남기기**를 요구하세요. 그래야 에이전트가 그럴듯하게 추측하는 대신 코드를 실제로 읽고 돌려 보고 답합니다.

## 사전 준비 1: Antigravity IDE 다운로드, 설치 및 사용 방법

**■ Antigravity IDE 개요:** Antigravity IDE는 Google DeepMind에서 개발한 AI 에이전트 기반의 차세대 소프트웨어 개발 환경(IDE)입니다. 단순한 코드 자동완성 수준을 넘어, 파일 탐색, 소스 코드 분석, 터미널 명령 실행, 웹 검색 등 강력한 도구(Tool)를 자율적으로 사용하는 Coding Agent와 페어 프로그래밍을 진행할 수 있도록 설계되었습니다.

**■ 다운로드 및 설치:** 1) Antigravity 공식 배포 웹사이트(또는 조직 내 제공 포털)에 접속하여 운영체제(Windows / macOS / Linux)에 맞는 설치 프로그램을 다운로드합니다.  
2) 다운로드된 인스톨러(예: Windows의 경우 Setup 실행 파일)를 실행하여 안내에 따라 설치를 완료합니다.  
3) 설치 완료 후 IDE를 처음 실행하면 Google 계정 로그인 및 초기 환경 설정 마법사가 진행되며, 인증이 완료되면 메인 화면이 활성화됩니다.

**■ Antigravity IDE 주요 인터페이스 구성:** Antigravity IDE는 개발자가 편리하게 에이전트와 협업할 수 있도록 다음과 같은 3대 핵심 영역으로 구성되어 있습니다:  
• 코드 에디터 & 파일 탐색기 (좌측/중앙): 프로젝트 파일 트리 확인, 소스 코드 열람 및 편집  
• 통합 터미널 (하단/Terminal): 빌드, 테스트, CLI 명령어 실행 상태 확인  
• ★ Agent Manager 대화창 (우측 대화 패널): Coding Agent와 실시간으로 대화하며 분석 및 개발 작업을 지시하는 메인 창구

**■ Agent Manager 대화창 사용 방법:** 1) 대화 세션 시작: 우측 상단의 '+ New Conversation' 버튼을 클릭하여 새로운 작업 세션을 생성합니다.  
2) 자연어 프롬프트 입력: 하단 입력창에 분석 목표나 작업 요구사항을 자연어로 입력하여 전송합니다.  
3) 에이전트 자율 실행 및 관찰: 에이전트가 지시에 따라 파일을 읽고, 관련 도구를 자율적으로 호출하며 결과를 대화창에 보고합니다.  
4) 도구/명령 실행 승인(Human-in-the-Loop): 에이전트가 셸 명령어 실행이나 파일 수정을 제안할 때, 대화창에 승인 요청 카드가 표시됩니다. 내용을 확인한 후 'Approve' 또는 'Always Allow'를 클릭하여 안전하게 실행을 통제할 수 있습니다.

## 사전 준비 2: mini-swe-agent 오픈소스 저장소 클론 및 워크스페이스 열기 (mini-swe-agent)

**■ 1단계 - 대상 저장소 로컬 클론:** 분석을 시작하기 위해, 분석 대상인 `mini-swe-agent` 오픈소스 저장소를 로컬 머신에 클론(clone)합니다. 터미널(PowerShell 또는 Bash)을 열고 다음 명령을 실행합니다:

```text
# 1. mini-swe-agent 오픈소스 저장소 클론
git clone https://github.com/SWE-agent/mini-swe-agent.git

# 2. 클론된 저장소 디렉터리로 이동 확인
cd mini-swe-agent
```

**■ 2단계 - Antigravity IDE에서 'mini-swe-agent' 폴더 열기:** 저장소 클론이 완료되면 Antigravity IDE를 실행하고 다음 순서로 작업 환경을 준비합니다:  
1) 폴더 열기: 상단 메뉴의 File > Open Folder... (단축키: Windows Ctrl+K, Ctrl+O / Mac Cmd+O)를 클릭하고, 방금 클론한 `mini-swe-agent` (또는 로컬 mini-swe-agent 디렉터리) 폴더를 선택하여 엽니다.  
2) 프로젝트 루트 확인: 좌측 탐색기(Explorer)에 mini-swe-agent의 폴더 구조(`src/minisweagent`, `tests`, `docs`, `pyproject.toml` 등)가 정상적으로 표시되는지 확인합니다.

**■ 3단계 - Agent Manager 대화창에서 분석 작업 수행:** Antigravity IDE에서 `mini-swe-agent` 폴더를 열었다면, 실제 분석 작업은 우측의 Agent Manager 대화창에서 진행합니다:  
1) 작업 규칙(`AGENTS.md`) 확인: 프로젝트 루트 디렉터리에 이미 존재하는 `AGENTS.md` 파일(프로젝트 개요, 5대 레이어 구조, 코딩 스타일 가이드 등)을 확인하고, 분석 원칙(소스코드 수정 금지, 경로:라인 명시, [확인]/[추정] 구분)을 유지합니다.  
2) Agent Manager 대화창 활성화: 우측 Agent Manager 패널에서 '+ New Conversation'을 시작합니다.  
3) 대화형 단계별 분석 진행: Agent Manager 대화창의 메시지 입력란에 아래의 '0단계 프롬프트'부터 '8단계 프롬프트 및 보너스'까지 순서대로 하나씩 입력하여 Coding Agent에게 분석을 요청합니다. 에이전트는 규칙을 엄수하며 파일 분석, 빌드/테스트, 아키텍처 다이어그램 작성을 수행하고 그 결과를 보고합니다.

## 0단계: 작업 규칙 먼저 주기

처음에 한 번 주거나, `CLAUDE.md` / `AGENTS.md`에 넣어 둡니다.

```text
이 저장소(mini-swe-agent)의 동작 구조를 분석하려고 한다. 다음 규칙을 지켜라.
- 분석 단계에서는 소스 코드를 수정하지 마라 (읽기·실행만).
- 모든 주장에는 근거를 `경로:라인` 형식으로 붙여라.
- 코드로 확인한 것과 추측한 것을 [확인]/[추정]으로 구분하라.
- 결과는 docs/analysis/ 아래 마크다운 파일로 누적 저장하라.
```

## 1단계: 전체 지형 파악 (Orientation)

```text
1단계; 저장소 전체를 훑어보고 다음을 정리해 docs/analysis/01_overview.md에 저장해 줘.
1. 이 프로젝트가 해결하는 문제 (README와 실제 코드가 다르면 차이 표시)
2. 최상위 디렉터리별 역할 (src/minisweagent, tests, docs 등 한 줄씩)
3. 진입점(entry point): CLI 엔트리포인트(mini, mini-swe-agent), run 스크립트(run.mini, run.hello_world) 등
4. 빌드·설치·테스트 명령(uv, pip, pytest)과 주요 외부 의존성(litellm, typer, jinja2 등)
5. 핵심 모듈 상위 5~7개(Agent, Environment, Model, Run 등)와 그렇게 판단한 이유
```

## 2단계: 실제로 돌려 보기 (Dynamic Check)

```text
2단계; 설치된 가상환경(.venv)에서 pytest 단위 테스트를 실행해 보고, 가장 간단한 실행 예제(예: python -m minisweagent.run.hello_world 또는 mini --help)를 실행하라. 실행한 명령, 결과, 실패 원인을 기록하고, 1단계 분석에서 틀린 부분이 있으면 수정하라. 이상의 실행결과를 ‘docs/analysis/02_build_test_execution.md’ 에 저장해줘.
```

정적 분석만 하면 문서와 실제 동작이 어긋나는 부분을 놓칩니다.

## 3단계: 미설치 도구 설치 및 실패한 실행을 성공적 수행 실행 (Fix failures)

```text
3단계; 2단계 실행 결과 ‘docs/analysis/02_build_test_execution.md’ 에서 누락된 의존성 패키지나 환경 설정(.env 파일의 API 키 등)을 확인하고 테스트 및 실행이 성공하도록 조치하라. 다시 설치된 환경에서 빌드/테스트 및 hello_world 예제를 재실행하여 결과를 검증하고 기록하라.
```

## 4단계: 아키텍처 뷰 (Structure)

```text
4단계; mini-swe-agent의 모듈 간 의존 관계 및 인터페이스 구조를 분석해 줘.
- 계층 구조(interfaces/protocols in __init__.py → agents, environments, models → run)와 의존 방향
- Agent, Environment, Model 간의 다형성(Polymorphism) 구현 방식
- 순환 의존이나 계층 위반 사례
- Mermaid로 컴포넌트 다이어그램 작성 (C4의 Container/Component 수준)
결과는 ‘docs/analysis/04_SW_structure.md’ 에 저장.
```

## 5단계: 핵심 흐름 하나를 끝까지 추적 (End-to-End Trace)

분석에서 가장 가치가 큰 단계입니다.

```text
5단계; 대표 유스케이스 "사용자가 mini-swe-agent 실행 스크립트(run.hello_world 또는 run.mini)를 실행했을 때"의 전체 흐름을 진입점부터 최종 출력까지 추적해 줘.
- 호출 체인을 순서대로: CLI 파싱 → 설정 병합 → Model/Environment/Agent 인스턴스화 → Agent.run() 루프(LLM 질의 → 셸 명령 실행 → 관측 반환) → Trajectory 저장 (함수명 + 경로:라인)
- 각 단계에서 바뀌는 데이터·상태 (AgentState, Trajectory 등)
- 예외(비용 초과, 스텝 초과, 구문 에러 등) 발생 시 에러 처리 및 복구 경로
- Mermaid sequence diagram 작성
그다음 실제로 간단한 실행 로그를 확인하여 추적 결과가 맞는지 검증하라.
(검증용으로 임시 코드를 넣었다면 끝나면 원래대로 되돌릴 것)
```

## 6단계: 데이터 모델·설정·확장 지점

```text
6단계; mini-swe-agent의 데이터 모델, 설정 및 확장 지점을 정리해줘.
1. 핵심 데이터 구조/엔티티(AgentConfig, EnvironmentConfig, ModelConfig, Trajectory, Message 등)와 그 생명주기
2. 설정이 로드되는 순서와 우선순위 (mini.yaml 기본값 → 사용자 지정 config YAML → 환경변수/.env → CLI 인자)
3. 확장 지점: 새로운 Model 어댑터, 새로운 Environment(Local, Docker, Singularity 등), 커스텀 Agent 서브클래싱
4. 코드에서 보이는 설계 패턴 (Protocol 기반 Strategy 패턴, Factory 패턴, Dataclass 설정 관리 등)과 사용 위치
```

## 7단계: 이해를 테스트로 고정하기 (Characterization Test)

```text
7단계;
지금까지 분석한 mini-swe-agent의 핵심 동작 3가지(예: 모델 호출 인터페이스, 환경 커맨드 실행, 에이전트 1스텝 실행 루프)를 현재 동작 그대로 검증하는 테스트 코드를 pytest 기반으로 작성해 줘 (characterization test). 이 테스트들이 통과하면 우리 이해가 맞다는 뜻이다.
```

## 8단계: 정리와 남은 질문

```text
8단계 (최종 단계);
docs/analysis/의 내용을 종합해 ARCHITECTURE.md를 작성해 줘
(한 페이지 요약 + 다이어그램 + 핵심 흐름 + mini-swe-agent의 핵심 설계 철학: 단순성과 가독성).
마지막에 "아직 확인하지 못한 것 / 의문점" 목록을 넣어라.
```

## 보너스: 코딩 에이전트(mini-swe-agent) 심층 해부

mini-swe-agent는 가장 단순하고 가독성 높은 오픈소스 SWE 코딩 에이전트 구현체입니다. 이 코딩 에이전트를 "모델 + 하네스(Harness)" 관점에서 집중 해부하려면 다음과 같이 요청합니다:

```text
mini-swe-agent를 "모델 + 하네스" 관점에서 해부해 줘. 다음 각 항목의 구현 위치(경로:라인)와 동작을 설명하라.
1. 에이전트 루프: Agent.run() 및 step()의 한 턴(LLM 호출 → 도구/액션 추출 → 환경 실행 → 관측 반환) 흐름과 종료 조건(COMPLETE, 스텝/비용 초과)
2. 도구/실행 인터페이스: Environment 프로토콜(execute 메서드) 및 로컬/도커 환경 격리, 타임아웃, 출력 캡처 메커니즘
3. 컨텍스트 및 프롬프트 관리: Jinja2 템플릿(system, instance prompt) 기반 메시지 렌더링, 대화 히스토리 관리 방식
4. 통제 메커니즘: cost_limit, step_limit, 인터랙티브 확인 모드(human-in-the-loop)
5. 모델 인터페이스: LiteLLM 기반 Model 프로토콜 추상화, 다중 공급자 지원, 재시도(tenacity) 메커니즘
6. 확장성 및 다형성: 프로토콜 기반의 Agent / Environment / Model 플러그인 구조
마지막에 mini-swe-agent(초경량 미니멀 에이전트)의 아키텍처가 SWE-agent(기존 대형 프레임워크)나 OpenHands 대비 차별화되는 장단점과 설계 원칙을 표로 정리하라.
```

## 운영 팁

- **한 세션에 한 단계씩** 진행하세요. 결과를 파일로 남겨 두면 다음 세션은 그 파일을 읽고 이어 가면 되므로, 컨텍스트가 넘쳐도 분석이 끊기지 않습니다.

- **큰 저장소는 탐색을 병렬로** 나누세요. 서브에이전트 기능이 있으면 "디렉터리별로 나눠서 병렬 탐색 후 종합"을 요청하면 됩니다.

- **결과는 교차 검증**하세요. 에이전트 설명을 그대로 믿지 말고, 2단계와 5단계처럼 직접 실행해서 확인하는 단계를 꼭 넣습니다.

# 2. Antigravity IDE에서 AGENTS.md 위치

Antigravity에서 **연 폴더의 최상위(워크스페이스 루트)**에 두면 됩니다. Antigravity 공식 문서상 `AGENTS.md`는 프런트매터 없이 그 위치에서 항상 적용되는 워크스페이스 규칙으로 읽힙니다.

```text
mini-swe-agent/               ← Antigravity에서 "Open Folder"로 연 폴더
├── AGENTS.md                ← 여기에 둡니다 (저장소 전체에 적용, 아키텍처 개요 및 코딩/테스트 규칙)
├── README.md
├── pyproject.toml
├── src/
│   └── minisweagent/        ← mini-swe-agent 소스 코드 디렉터리
│       ├── __init__.py      ← 기본 인터페이스/프로토콜 정의
│       ├── agents/          ← 에이전트 제어 흐름
│       ├── environments/    ← 환경 실행 로직
│       ├── models/          ← LLM 인터페이스
│       └── run/             ← 실행 진입점 스크립트
├── tests/
└── docs/analysis/           ← 분석 결과 저장 위치
```

## 위치별 적용 범위

| **위치**                    | **적용 범위**                                                                                                                      |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| 워크스페이스 루트 `AGENTS.md` | 저장소 전체 (mini-swe-agent 루트에 이미 포함되어 코딩 스타일 및 설계 원칙 제공)                                                      |
| 하위 폴더 `AGENTS.md`         | 그 폴더 안의 파일을 다룰 때만 적용. 작업 파일의 폴더부터 루트까지 거슬러 올라가며 모두 읽고, 충돌하면 더 가까운 폴더의 규칙이 우선 |
| `~/.gemini/AGENTS.md`         | 모든 프로젝트 공통 전역 규칙 (Windows: `C:\Users\<사용자>\.gemini\AGENTS.md`)                                                       |
| `.agents/rules/*.md`         | 규칙을 여러 파일로 나눌 때 사용. YAML 프런트매터 필요, 하위 폴더는 읽지 않으므로 `rules/` 바로 아래에 둘 것                          |

## 주의할 점

- **연 폴더 확인:** 저장소의 상위 폴더를 열었다면, 그 폴더가 워크스페이스 루트가 됩니다. 저장소 폴더 자체(`mini-swe-agent`)를 여는 것이 가장 확실합니다.

- **새 대화에서 시작:** 파일을 수정한 뒤에는 새 대화를 시작하세요. 이전 대화를 이어 가면 규칙이 반영되지 않을 수 있습니다.

- **적용 여부 확인:** "현재 적용 중인 규칙을 요약해 줘"라고 물어보면 됩니다.

- **인식되지 않을 때:** 버전에 따라 `AGENTS.md`를 바로 읽지 않는다는 제3자 보고도 있습니다. 이 경우 `.agents/rules/` 폴더에 규칙 파일을 만들고, 그 안에서 루트의 `AGENTS.md`를 참조하게 하면 됩니다.

- **원본 저장소 관리:** `docs/analysis/` 등을 `.git/info/exclude`에 추가하면 Git 커밋 대상에서 깔끔하게 제외됩니다.

# 3. 파일명 대소문자: AGENTS.md vs agents.md

`AGENTS.md`(대문자)로 만드세요. 표준 파일명은 대문자이고, 대소문자를 구분하는 도구도 있습니다. `agents.md`가 인식되는지는 운영체제와 도구가 파일을 찾는 방식에 따라 달라서, 인식될 수도 있고 안 될 수도 있습니다.

| **환경**                    | **`agents.md`도 인식되나?**                                |
|-----------------------------|----------------------------------------------------------|
| Windows (NTFS)              | 대개 인식됨. 파일 시스템이 대소문자를 구분하지 않기 때문 |
| macOS (기본 APFS)           | 대개 인식됨. Windows와 같은 이유                         |
| Linux, WSL, Docker 컨테이너 | 인식 안 됨. 서로 다른 파일로 취급                        |

## Windows에서도 문제가 생길 수 있는 경우

- **목록 비교 방식:** 도구가 경로로 파일을 바로 여는 대신 폴더 목록을 읽어 문자열을 비교하면, `agents.md`는 `AGENTS.md`와 다른 이름으로 보고 건너뜁니다.

- **다른 환경으로 옮길 때:** Git으로 커밋하거나 원격 서버, WSL, CI에서 같은 저장소를 열면 Linux 규칙이 적용되어 인식되지 않습니다.

- **두 파일이 섞일 때:** Windows에서는 두 파일이 한 폴더에 공존할 수 없습니다. Linux에서 만든 저장소에 두 파일이 모두 있으면, Windows로 클론할 때 하나가 덮어써집니다.

## 이미 agents.md로 만들었다면

Windows에서는 대소문자만 바꾸는 이름 변경이 잘 반영되지 않으니, 두 번에 나눠 바꾸세요.

```text
ren agents.md tmp.md
ren tmp.md AGENTS.md
```

Git으로 관리 중이라면 `git mv agents.md AGENTS.md` 한 줄로 바꾸면 됩니다.

# 참고 자료

- [mini-swe-agent GitHub 저장소](https://github.com/SWE-agent/mini-swe-agent)
- [mini-swe-agent 공식 문서](https://mini-swe-agent.com/latest/)
- [Antigravity Docs: Rules](https://www.antigravity.google/docs/rules/)
- [Agentpedia: Antigravity AGENTS.md not working fix](https://agentpedia.codes/blog/antigravity-agents-md-not-working-fix)
- [The Prompt Shelf: Antigravity AGENTS.md rules guide](https://thepromptshelf.dev/blog/google-antigravity-agents-md-rules-guide-2026)

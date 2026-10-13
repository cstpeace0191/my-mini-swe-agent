# mini-swe-agent 심층 해부: "모델 + 하네스(Model + Harness)" 관점 분석

본 문서는 `mini-swe-agent`를 코딩 에이전트의 핵심 구성 요소인 **"지능을 담당하는 파운데이션 모델(Model)"**과 **"모델이 현실 세계(코드베이스, 셸 환경)와 상호작용하도록 제어하는 하네스(Harness/Scaffolding)"** 관점에서 체계적으로 분해하여 분석한 보고서입니다.

- **원칙 준수**: 모든 분석 내용은 소스 코드 상의 정확한 위치(`경로:라인`)와 (Verified) / (Inferred) 태그를 명시합니다.

---

## 1. 에이전트 루프 (Agent Loop)

에이전트 루프는 하네스의 심장이자 LLM과 환경을 연결하는 주기적 실행 루틴입니다.

### 1.1 루프 제어 흐름 및 한 턴(Single Turn)의 라이프사이클
- **진입 및 메인 루프 구현**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L88-L124") `DefaultAgent.run()`
- **스텝 실행 분할**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L126-L128") `DefaultAgent.step()`
  ```python
  def step(self) -> list[dict]:
      return self.execute_actions(self.query())
  ```
- **한 턴의 세부 흐름**:
  1. **한도 검사 (Pre-check)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L132-L147") `query()` 내부에서 `step_limit`, `cost_limit`, `wall_time_limit_seconds`를 LLM 호출 전에 검사.
  2. **LLM 호출 (Query)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L149") `self.model.query(self.messages)`를 통해 모델에 이전 대화 이력을 전달하고 생각(thought) 및 액션(bash command)을 수신.
  3. **비용 및 카운트 누적**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L148") `self.n_calls += 1`, `self.cost += message["extra"]["cost"]`.
  4. **도구/액션 추출 (Action Extraction)**: (".../mini-swe-agent/src/minisweagent/models/litellm_model.py#L89") `_parse_actions()` 및 (".../mini-swe-agent/src/minisweagent/models/utils/actions_toolcall.py#L30-L73")에서 OpenAI 호환 tool_call 인자 파싱 (또는 텍스트 기반 모델의 경우 마크다운 코드블록 정규식 파싱).
  5. **환경 실행 (Environment Execution)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L156") `[self.env.execute(action) for action in actions]`를 통해 서브셸 또는 컨테이너에서 셸 명령 실행.
  6. **관측 반환 (Observation Feedback)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L157") 실행 결과(`output`, `returncode`)를 모델의 관측값 템플릿(`<returncode>`, `<output>`)으로 변환하여 `self.messages`에 추가.
  7. **증분 저장**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L121") `finally: self.save(self.config.output_path)`로 매 스텝 종료 즉시 디스크에 직렬화.

### 1.2 종료 조건 (Termination Conditions)

| 종료 사유 | 발생 위치 | 트리거 조건 | 후속 처리 및 exit_status |
| :--- | :--- | :--- | :--- |
| **작업 정상 완료** | (".../mini-swe-agent/src/minisweagent/environments/local.py#L48-L56")<br>(".../mini-swe-agent/src/minisweagent/environments/docker.py#L146-L154") | 명령 실행 출력의 첫 줄이 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`이고 returncode가 0일 때 | `Submitted` 예외 발생 → `role: "exit"`, `exit_status: "Submitted"` 메시지 주입 후 루프 탈출 |
| **비용/스텝 한도 초과** | (".../mini-swe-agent/src/minisweagent/agents/default.py#L132-L139") | `self.n_calls >= step_limit` 또는 `self.cost >= cost_limit` | `LimitsExceeded` 발생 → `exit_status: "LimitsExceeded"`. (`InteractiveAgent`는 대화형 터미널에서 연장 여부 프롬프트) |
| **벽시계 시간 초과** | (".../mini-swe-agent/src/minisweagent/agents/default.py#L140-L147") | `elapsed_seconds >= wall_time_limit_seconds` | `TimeExceeded` 발생 → `exit_status: "TimeExceeded"` |
| **연속 구문 오류** | (".../mini-swe-agent/src/minisweagent/agents/default.py#L100-L114") | 모델이 올바른 도구 호출이나 형식을 연속 `max_consecutive_format_errors`(기본 3)회 이상 어겼을 때 | `role: "exit"`, `exit_status: "RepeatedFormatError"` 주입 후 강제 중단 |

---

## 2. 도구 및 실행 인터페이스 (Tool & Execution Interface)

mini-swe-agent는 전용 파일 편집기나 커스텀 파이썬 API를 복잡하게 노출하는 대신, **"표준 Bash 인터페이스 단 하나(Universal Bash Tool)"**만을 노출하고 환경 계층에서 이를 격리 실행합니다.

### 2.1 도구 정의 (Tool Definition)
- **위치**: (".../mini-swe-agent/src/minisweagent/models/utils/actions_toolcall.py#L11-L27")
- **정의**: OpenAI Function Calling 규격의 `BASH_TOOL`
  ```python
  BASH_TOOL = {
      "type": "function",
      "function": {
          "name": "bash",
          "description": "Execute a bash command",
          "parameters": {
              "type": "object",
              "properties": {"command": {"type": "string", "description": "The bash command to execute"}},
              "required": ["command"],
          },
      },
  }
  ```
- **특징**: 모델은 모든 작업(파일 탐색, 파일 생성 `cat <<EOF`, `sed`, `pytest`, `git diff`)을 표준 bash 명령어로 완수하도록 프롬프트됩니다.

### 2.2 환경 격리 및 실행 메커니즘
- **Environment 프로토콜**: (".../mini-swe-agent/src/minisweagent/__init__.py#L61-L70")
- **Local 실행 격리 및 프로세스 관리**:
  - (".../mini-swe-agent/src/minisweagent/environments/local.py#L72-L92") `_run()`
  - POSIX 환경에서는 `start_new_session=True`로 별도 프로세스 세션을 할당.
  - 타임아웃 발생 시 자식 프로세스가 고아(orphan)로 남지 않도록 `os.killpg(process.pid, signal.SIGKILL)`를 호출하여 프로세스 그룹 전체를 사살.
- **Docker 컨테이너 격리**:
  - (".../mini-swe-agent/src/minisweagent/environments/docker.py#L61-L82") `_start_container()`
  - 호스트에서 `docker run -d --rm <run_args> <image> sleep <container_timeout>`으로 데몬 컨테이너 기동.
  - (".../mini-swe-agent/src/minisweagent/environments/docker.py#L84-L141") `execute()`에서 `docker exec`를 통해 컨테이너 내부에서 지정된 인터프리터(`["bash", "-lc"]`)로 격리 실행.
- **출력 캡처 및 긴 출력 생략(Truncation)**:
  - `stderr`는 `stderr=subprocess.STDOUT`로 통합 캡처.
  - 인코딩 에러 방지를 위해 `encoding="utf-8"`, `errors="replace"` 설정.
  - (".../mini-swe-agent/src/minisweagent/config/mini.yaml#L120-L128") 관측 템플릿에서 출력이 너무 길 경우 앞 5,000자(`output_head`) + 뒤 5,000자(`output_tail`)만 남기고 생략(`elided_chars`) 경고 주입 `[확인]`.

---

## 3. 컨텍스트 및 프롬프트 관리 (Context & Prompt Engineering)

하네스의 주 역할 중 하나는 LLM이 정확하고 일관되게 동작하도록 시스템 상태를 프롬프트에 주입하고, 대화 컨텍스트를 규격에 맞게 유지하는 것입니다.

### 3.1 Jinja2 템플릿 기반 동적 렌더링
- **렌더링 구현**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L66-L67")
  ```python
  def _render_template(self, template: str) -> str:
      return Template(template, undefined=StrictUndefined).render(**self.get_template_vars())
  ```
  `StrictUndefined`를 사용하여 템플릿 변수가 하나라도 누락되면 런타임 에러를 발생시켜 조기 발견 유도.
- **주입 변수 취합 (`get_template_vars`)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L52-L64")
  1. `AgentConfig` 설정 덤프
  2. `Environment` 템플릿 변수: `platform.uname()` (OS 이름, 커널, 머신 아키텍처) 및 `os.environ`
  3. `Model` 템플릿 변수
  4. 동적 런타임 통계: `n_model_calls` (현재 호출 수), `model_cost` (누적 비용), `elapsed_seconds` (경과 시간)
  5. `extra_template_vars`: 전달된 `task` (이슈 설명)

### 3.2 대화 히스토리 관리 및 API 전처리
- **내부 상태 저장**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L42") `self.messages: list[dict]`.
  - 각 메시지는 표준 `role`(`system`, `user`, `assistant`, `tool`, `exit`)과 `content` 외에 에이전트 내부 메타데이터인 `extra`를 포함.
- **API 전송 전 정제 (`_prepare_messages_for_api`)**:
  - (".../mini-swe-agent/src/minisweagent/models/litellm_model.py#L76-L79")
  ```python
  def _prepare_messages_for_api(self, messages: list[dict]) -> list[dict]:
      prepared = [{k: v for k, v in msg.items() if k != "extra"} for msg in messages]
      prepared = _reorder_anthropic_thinking_blocks(prepared)
      return set_cache_control(prepared, mode=self.config.set_cache_control)
  ```
  - 모델 API 호출 직전에 내부 메타데이터인 `extra` 필드를 전량 제거하여 공급자 API 에러 방지.
  - Anthropic Thinking 블록의 순서 조정 및 프롬프트 캐싱(`cache_control`) 마커 주입 `[확인]`.

---

## 4. 통제 및 안전 메커니즘 (Control & Safety Guardrails)

자율 코딩 에이전트의 폭주(무한 루프, 비용 폭증, 위험 명령어 실행)를 방지하는 다중 방어선이 구축되어 있습니다.

### 4.1 3중 한도 제어 (Triple Limits)
1. **스텝 한도 (`step_limit`)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L132") - 0보다 크고 호출 횟수가 도달하면 차단.
2. **단일 인스턴스 비용 한도 (`cost_limit`)**: (".../mini-swe-agent/src/minisweagent/agents/default.py#L132") - 기본 $3.00, 초과 즉시 중단.
3. **글로벌 누적 한도 (`GLOBAL_MODEL_STATS`)**: (".../mini-swe-agent/src/minisweagent/models/__init__.py#L13-L42")
   - 환경변수 `MSWEA_GLOBAL_COST_LIMIT`, `MSWEA_GLOBAL_CALL_LIMIT` 지원.
   - 멀티스레드 락(`threading.Lock`)을 통해 SWE-bench 등 배치 실행 시 전체 프로세스의 총비용을 상시 통제 `[확인]`.

### 4.2 인간 개입형 확인 모드 (Human-in-the-Loop)
(".../mini-swe-agent/src/minisweagent/agents/interactive.py")의 `InteractiveAgent`가 제공:
- **`confirm` 모드 (기본값)**: 모델이 제안한 bash 명령어를 실행하기 전 터미널에 출력하고 사용자의 승인(`y/n`)을 대기.
- **`whitelist_actions`**: 정규표현식 목록(".../mini-swe-agent/src/minisweagent/agents/interactive.py#L27")과 일치하는 안전한 읽기 명령(`ls`, `cat`, `git status` 등)은 사용자 확인 없이 자동 실행.
- **`human` 모드**: 모델 대신 사용자가 직접 bash 명령을 입력하여 실행하고 그 결과를 모델에게 관측값으로 전달.
- **슬래시 커맨드 즉시 전환**: 실행 도중 `/u`(human), `/c`(confirm), `/y`(yolo) 입력으로 모드 실시간 변경.

---

## 5. 모델 인터페이스 및 재시도 메커니즘 (Model Interface & Resilience)

### 5.1 LiteLLM 추상화
- (".../mini-swe-agent/src/minisweagent/models/litellm_model.py#L64-L75") `_query()`
- `litellm.completion(model=self.config.model_name, messages=messages, tools=[BASH_TOOL], ...)`
- LiteLLM 단일 라이브러리를 통해 Anthropic Claude, OpenAI GPT, Google Gemini, Mistral, Ollama 등 수백 개 모델을 동일한 인터페이스로 연결 `[확인]`.

### 5.2 Tenacity 기반 지능형 재시도 루프
- **구현 위치**: (".../mini-swe-agent/src/minisweagent/models/utils/retry.py#L9-L25") 및 (".../mini-swe-agent/src/minisweagent/models/litellm_model.py#L82")
- **백오프 전략**: `wait_exponential(multiplier=1, min=4, max=60)` (4초에서 최대 60초까지 지수 백오프)
- **최대 시도 횟수**: 환경변수 `MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT` (기본 10회)
- **즉시 중단 예외 (`abort_exceptions`)**: (".../mini-swe-agent/src/minisweagent/models/litellm_model.py#L50-L57")
  - `AuthenticationError` (잘못된 API 키)
  - `PermissionDeniedError` (권한 부족)
  - `NotFoundError` (존재하지 않는 모델명)
  - `ContextWindowExceededError` (컨텍스트 길이 초과)
  - `UnsupportedParamsError`
  - `KeyboardInterrupt`
  - 상기 예외는 재시도해도 성공할 수 없으므로 지연 없이 즉시 에러를 발생시키고 종료 `[확인]`.

---

## 6. 확장성 및 다형성 (Extensibility & Polymorphism)

`mini-swe-agent`는 모든 핵심 구성요소가 독립된 프로토콜 계약에 따라 동작하는 완전한 플러그인 구조를 갖추고 있습니다.

```
       CLI / Run Script
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
get_agent  get_model  get_environment
    │         │         │
    ▼         ▼         ▼
«Protocol» «Protocol» «Protocol»
  Agent      Model    Environment
```

- **덕 타이핑 기반 분리**: 상속이 강제되지 않으므로, 서드파티 패키지에서 생성한 클래스라도 필요한 메서드 시그니처만 갖추면 코어 엔진에 결합됨.
- **Dotted Dynamic Import**:
  - `--model-class my_corp.models.PrivateLLM`
  - `--environment-class my_corp.envs.K8sEnvironment`
  - `--agent-class my_corp.agents.PlanningAgent`
  - CLI 인자나 YAML 설정에서 완전한 모듈 경로를 명시하면 `importlib.import_module`을 통해 즉시 로드 (".../mini-swe-agent/src/minisweagent/models/__init__.py#L108", ".../mini-swe-agent/src/minisweagent/environments/__init__.py#L23", ".../mini-swe-agent/src/minisweagent/agents/__init__.py#L18") `[확인]`.

---

## 7. 프레임워크 비교 분석: mini-swe-agent vs SWE-agent vs OpenHands

mini-swe-agent의 아키텍처적 위치와 차별성을 기존 대표적인 SWE 에이전트들과 비교 정리한 결과는 다음과 같습니다:

| 비교 항목 | **mini-swe-agent** (본 프로젝트) | **SWE-agent** (원조 프레임워크) | **OpenHands** (대형 플랫폼) |
| :--- | :--- | :--- | :--- |
| **핵심 철학** | **극도의 단순성 & 가독성 (Minimalism)**<br>"가장 작고 읽기 쉬운 에이전트" | **도구 설계 및 연구 중심 (Research-first)**<br>ACID 인터페이스, 검색/편집 CLI 도구 최적화 | **전면적 범용 에이전트 플랫폼 (Full Platform)**<br>마이크로서비스, 웹 UI, 다중 런타임 |
| **코드베이스 규모** | **초경량 (< 1,500 LOC 코어)**<br>1~2시간 안에 전체 코드 파악 가능 | **중형 (~ 10,000+ LOC)**<br>복잡한 설정 YAML 및 커스텀 도구 스크립트 | **초대형 (50,000+ LOC)**<br>FastAPI 백엔드, React 프론트엔드, 도커 관리자 |
| **도구 세트 (Tooling)** | **Universal Bash 1개 (단순 셸)**<br>`bash` 도구 호출로 모든 파일 편집/실행 | **커스텀 파일/검색 도구 집합**<br>`open_file`, `scroll`, `edit_line` 등 특수 CLI | **다중 멀티모달 도구 세트**<br>터미널, 파일 에디터, 브라우저, 웹 검색기 |
| **환경 격리 방식** | **Local, Docker, Singularity, Swerex**<br>필요한 환경만 심플하게 주입 | **Docker 및 Swe-rex 중심**<br>SWE-bench 평가 전용 컨테이너에 강결합 | **Docker / All-in-one Container**<br>자체 이벤트 스트림 API 기반 컨테이너 제어 |
| **제어 흐름 구조** | **단일 35줄 `while True` 루프**<br>`step() = execute_actions(query())` | **상태 머신 및 다단계 훅**<br>Pre/Post hook, 복잡한 히스토리 프로세서 | **EventStream 비동기 이벤트 버스**<br>Action/Observation 비동기 이벤트 발행/구독 |
| **학습 및 포킹 용이성** | **극상 (최고)**: 누구나 쉽게 수정 및 실험 가능 | **보통**: 프롬프트 및 도구 설정 학습 필요 | **낮음**: 전체 인프라 및 아키텍처 이해 부담 큼 |
| **주요 장점** | - 버그 추적이 매우 쉽고 투명함<br>- 종속성이 적고 오버헤드가 없음<br>- 모델의 네이티브 코딩 능력을 가감 없이 측정 | - SWE-bench용 특화 도구로 토큰 효율 극대화<br>- 검증된 벤치마크 고득점 레퍼런스 | - 풍부한 기능, 웹 GUI 제공<br>- 대규모 엔터프라이즈 기능 및 팀 협업 지원 |
| **주요 한계점** | - 복잡한 대규모 브라우징/UI 조작 불가<br>- LLM이 bash 명령어 작성 능력이 떨어지면 불리 | - 프레임워크 학습 곡선이 가파름<br>- 코드 수정 시 부수 효과 추적 어려움 | - 설치 및 배포가 무겁고 리소스 소모 큼<br>- 연구용 빠른 프로토타이핑에 과도함 |

---

## 8. 결론: "Less is More"의 아키텍처 가치

`mini-swe-agent`는 현대 소프트웨어 엔지니어링 에이전트에서 **"에이전트 하네스가 복잡할수록 모델의 성능이 올라가는가?"**라는 질문에 대해 명쾌한 반례를 제시합니다.
- 복잡한 전용 편집기나 상태 머신 대신 **표준 Bash 도구**와 **Jinja2 템플릿**, 그리고 **엄격한 한도 제어와 예외 처리 루프**만으로도 최신 파운데이션 모델(Claude 3.7 Sonnet, GPT-4o 등)이 소프트웨어 이슈를 충분히 해결할 수 있음을 증명합니다.
- 따라서 코딩 에이전트의 내부 원리를 학습하거나, 새로운 프롬프트 기법 및 자율 에이전트 아이디어를 빠르게 프로토타이핑하고자 하는 연구자와 엔지니어에게 최적의 표준 기준점(Baseline)을 제공합니다.

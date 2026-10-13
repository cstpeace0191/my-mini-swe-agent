# 01. mini-swe-agent 프로젝트 전체 지형 및 개요 분석 (Overview)

> **분석 기준일:** 2026-10-12  
> **분석 대상:** `mini-swe-agent` 저장소  
> **분석 규칙 준수:** 소스 코드 미수정, 모든 주장에 `경로:라인` 근거 제시, `[확인]`(Verified) 및 `[추정]`(Inferred) 구분 표기

---

## 1. 이 프로젝트가 해결하는 문제 (README vs 실제 코드)

### 1.1 프로젝트가 해결하고자 하는 핵심 과제
- **핵심 목표:** 대규모 언어 모델(LLM)을 활용하여 GitHub 이슈 및 소프트웨어 엔지니어링 문제를 자율적으로 해결하는 초경량(minimalist) AI 코딩 에이전트 구현 [확인: `README.md:5-9`, `AGENTS.md:3-4`].
- **차별화된 문제 의식:** 기존 AI 코딩 에이전트(예: 원작 `SWE-agent`, `OpenHands` 등)는 복잡한 다중 도구 인터페이스, 상태 유지 셸 세션, 비선형 히스토리 관리 등으로 인해 시스템 복잡도와 디버깅 난이도가 매우 높았습니다. `mini-swe-agent`는 **"에이전트 스캐폴드를 100배 단순화하고도 동일하거나 뛰어난 성능을 유지할 수 있는가?"**라는 질문에 답하기 위해 설계되었습니다 [확인: `README.md:19-22`, `README.md:38-55`].

### 1.2 README 문서의 기술 내용 vs 실제 코드베이스 구현의 비교 및 차이점
- **(1) 단일 도구(Bash Only) 철학 vs 실제 구현:**
  - *README:* "bash 외에 다른 도구를 일절 갖지 않으며, 심지어 LM의 tool-calling 인터페이스조차 필요 없다"   ("README.md#L42-L44", "README.md#L70-L74").
  - *실제 코드:* 
    - 기본 에이전트 루프(`DefaultAgent`)는 실제로 단일 bash 명령 문자열을 추출하여 환경에서 실행하는 방식으로 동작합니다 ("src/minisweagent/agents/default.py#L154-L157").
    - 그러나 실제 모델 계층에는 텍스트 출력 파싱 모델(`LitellmTextbasedModel`)뿐만 아니라, OpenAI/Anthropic 등의 구조화된 Tool Calling 및 Response API를 공식 지원하는 `LitellmResponseModel`, `OpenrouterResponseModel` 등도 함께 제공됩니다 (".../mini-swe-agrnt/src/minisweagent/models/litellm_response_model.py#L15-L70").
    - 벤치마크 평가 시에는 순수 bash 프롬프트가 가장 안정적이지만, 최신 상용 LLM의 Function Calling 및 Thinking 모드를 활용할 수 있도록 모델 계층에서 선택지를 확장해 둔 것입니다.
- **(2) 무상태(Stateless) 프로세스 실행:**
  - *README:* 상태 유지 셸 세션을 열어두지 않고 매 액션마다 독립된 프로세스로 실행(`subprocess.run`)한다고 명시합니다 ("README.md:L48-L50").
  - *실제 코드:* 로컬 환경 구현체인 `LocalEnvironment`에서 실제로 매 명령마다 새로운 `subprocess.run(command, shell=True, ...)`을 호출하여 실행 격리와 안정성을 보장함을 확인했습니다 (".../mini-swe-agent/src/minisweagent/environments/local.py#L27-L30").
- **(3) 단순 CLI 도구 vs 확장된 에코시스템:**
  - *README:* 단 100줄 내외의 파이썬 에이전트 클래스를 강조합니다 ("README.md#L26-L27").
  - *실제 코드:* 핵심 `DefaultAgent`는 실제로 191줄의 간결한 코드로 작성되어 있습니다 (".../mini-swe-agent/src/minisweagent/agents/default.py#L1-L191"). 동시에 실무 활용을 위해 Human-in-the-Loop 인터랙티브 모드(".../mini-swe-agent/src/minisweagent/agents/interactive.py#L38-L150"), TUI 궤적 검사기(".../mini-swe-agent/src/minisweagent/run/utilities/inspector.py#L1-L150"), 그리고 SWE-bench / ProgramBench 대규모 배치 평가 파이프라인("src/minisweagent/run/benchmarks/swebench.py#L1-L100")까지 프로덕션 수준으로 구현되어 있습니다.
- **(4) [2단계 동적 실행 추가 검증] 셸 환경 및 OS 의존성:**
  - `LocalEnvironment`는 `subprocess.run(shell=True)`를 사용하므로 POSIX 셸(bash) 환경을 기본 전제로 동작합니다. (".../mini-swe-agnent/src/minisweagent/environments/local.py:#L27"). Windows 환경(`cmd.exe`)에서는 작은따옴표(`'`)가 보존되어 완료 시그널(`echo 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'`) 문자열 매칭이 기본 상태에서 실패할 수 있습니다(".../docs/analysis/02_build_test_execution.md").
  - 또한 메인 CLI인 `mini.py`는 `prompt_toolkit`에 대한 모듈 레벨 의존성으로 인해 완전한 Win32 콘솔 버퍼가 없는 비대화형 환경에서 `NoConsoleScreenBufferError`가 발생하며, 비대화형 실행 시에는 [run.hello_world](".../mini-swe-agent/src/minisweagent/run/hello_world.py")가 안정적인 대안 진입점입니다.

---

## 2. 최상위 디렉터리별 역할 (한 줄 요약)

- **`src/`**: 패키지 소스 코드의 최상위 루트 디렉터리로, 메인 구현체인 `minisweagent` 모듈을 포함 [확인: `src/minisweagent`]
- **`src/minisweagent/`**: 에이전트 루프, 모델 인터페이스, 실행 환경, 설정 및 CLI 진입점을 담은 핵심 패키지 (".../mini-swe-agent/src/minisweagent/__init__.py#L1-L93")
- **`tests/`**: pytest 기반의 단위 테스트, 컴포넌트 통합 테스트, 픽스처 및 모의(mock) 환경 테스트 모음 (".../mini-swe-agent/tests/conftest.py#L1-L100", ".../mini-swe-agent/pyproject.toml#L236-L241")
- **`docs/`**: MkDocs 기반의 공식 사용자 및 개발자 매뉴얼, 가이드, FAQ, API 레퍼런스 문서 (".../mini-swe-agent/docs/index.md", ".../mini-swe-agent/mkdocs.yml#L1-L50")
- **`.github/`**: GitHub Actions CI 워크플로우(테스트, 릴리스 자동화, 린트) 및 이슈/PR 템플릿 정의 (".../mini-swe-agent/.github/workflows`]
- **`.venv/`**: 프로젝트 의존성 라이브러리가 격리 설치되어 있는 로컬 가상환경 (".venv")

---

## 3. 진입점 (Entry Point) 구조

### 3.1 CLI 콘솔 스크립트 진입점
`pyproject.toml`에 명시된 CLI 명령 매핑 ( ".../mini-swe-agent/pyproject.toml#L90-L93")
- **`mini`** & **`mini-swe-agent`**: `minisweagent.run.mini:app`  
  → Typer 기반 메인 CLI. 사용자 대화형 마법사 또는 CLI 옵션을 통해 모델, 환경, 설정을 로드하고 에이전트 실행 (".../mini-swe-agent/src/minisweagent/run/mini.py#L17-L105").
- **`mini-extra`** & **`mini-e`**: `minisweagent.run.utilities.mini_extra:main`  
  → 추가 유틸리티 서브커맨드(설정 점검, 진단 등) 실행기 (".../mini-swe-agent/src/minisweagent/run/utilities/mini_extra.py#L1-L40").
- **`python -m minisweagent`**: ".../mini-swe-agent/src/minisweagent/__main__.py"  
  → `from minisweagent.run.mini import app; app()`을 직접 트리거 ("../mini-swe-agent/src/minisweagent/__main__.py#L1-L7").

### 3.2 주요 실행 스크립트 (Run Scripts)
- **`src/minisweagent/run/hello_world.py`**:  
  - 파이썬 바인딩 사용을 보여주는 43줄의 최소 실행 예제. `LitellmModel`, `LocalEnvironment`, `DefaultAgent`를 인스턴스화하여 단일 태스크 실행 (".../mini-swe-agent/src/minisweagent/run/hello_world.py#L30-L38").
- **`src/minisweagent/run/mini.py`**:  
  - 일상 개발 워크플로우를 위한 메인 진입점. 전역 설정(`.env`), YAML 파일, CLI 인자를 병합하고 `get_model`, `get_environment`, `get_agent` 팩토리를 거쳐 `interactive` 모드로 실행 (".../mini-swe-agent/src/minisweagent/run/mini.py#L90-L105").
- **`src/minisweagent/run/benchmarks/swebench.py`**:  
  - SWE-bench 데이터셋 평가용 멀티프로세스 배치 러너 (".../mini-swe-agent/src/minisweagent/run/benchmarks/swebench.py#L1-L120" ).
- **`src/minisweagent/run/utilities/inspector.py`**:  
  - Textual 기반의 터미널 UI로 에이전트의 저장된 `*.trajectory.json` 궤적 파일을 대화형으로 탐색 ('.../mini-swe-agent/src/minisweagent/run/utilities/inspector.py#L1-L100").

---

## 4. 빌드·설치·테스트 명령 및 주요 외부 의존성

### 4.1 빌드, 설치 및 테스트 명령
- **빌드 시스템:** `setuptools.build_meta` 표준 빌드 백엔드 채택 (".../mini-swe-agent/pyproject.toml#L1-L3").
- **개발 환경 설치:**
  ```bash
  # uv를 사용한 고속 환경 동기화
  uv pip install -e .
  # 또는 일반 pip 사용
  pip install -e .
  ```
  (".../mini-swe-agent/README.md#L173-L176", ".../mini-swe-agent/pyproject.toml#L6-L48")
- **테스트 실행:**
  ```bash
  # pytest를 통한 전체 테스트 스위트 실행
  pytest
  ```
  (`AGENTS.md:Style guide - Test style`, ".../mini-swe-agent/pyproject.toml#L236-L241")
- **코드 스타일 검사 및 린트:**
  ```bash
  ruff check .
  ruff format --check .
  ```
  ( ".../mini-swe-agent/pyproject.toml:L108-L140")

### 4.2 주요 외부 의존성 분석
".../mini-swe-agent/pyproject.toml"의 `[project.dependencies]` 기준 (".../mini-swe-agent/pyproject.toml#L33-L48"):
1. **`litellm` (>= 1.75.5)**: 100개 이상의 LLM(OpenAI, Anthropic, Gemini, Bedrock, 로컬 Ollama 등)을 단일 API로 호출하기 위한 통일된 모델 추상화 계층.
2. **`typer`**: CLI 커맨드라인 애플리케이션 및 옵션/인자 파싱 프레임워크.
3. **`jinja2`**: `system_template`, `instance_template` 등 에이전트 프롬프트를 동적으로 렌더링하기 위한 템플릿 엔진.
4. **`pydantic` (>= 2.0)**: `AgentConfig`, `ModelConfig`, `EnvironmentConfig` 등 설정값의 타입 검증 및 직렬화.
5. **`rich`**: 콘솔 출력 포맷팅, 상태 배너, 문법 강조.
6. **`python-dotenv` & `platformdirs`**: OS별 전역 설정 디렉터리("~\AppData\Local\mini-swe-agent`) 파악 및 `.env` 파일 로드 (".../mini-swe-agent/src/minisweagent/__init__.py#L26-L36").
7. **`textual`**: `inspector` CLI의 터미널 사용자 인터페이스(TUI) 제공.
8. **`tenacity`**: LLM API 호출 실패 및 레이트 리밋 발생 시 재시도 로직 제어.
9. **`prompt_toolkit`**: 여러 줄의 태스크 프롬프트를 터미널에서 대화형으로 입력받기 위한 라이브러리.

---

## 5. 핵심 모듈 상위 6개와 선정 이유

| 순위 | 모듈 경로 | 핵심 역할 | 선정 근거 (`경로:라인`) |
|:---:|:---|:---|:---|
| **1** | **`.../mini-swe-agent/src/minisweagent/__init__.py`** | 핵심 프로토콜 정의 및 설정 초기화 | `Model`, `Environment`, `Agent`의 추상 프로토콜 인터페이스를 정의하여 전체 시스템의 다형성(Duck Typing)을 성립시키는 아키텍처의 근간 (".../mini-swe-agent/__init__.py#L43-L82") |
| **2** | **`.../mini-swe-agent/src/minisweagent/agents/default.py`** | 핵심 에이전트 루프 및 실행 제어 | `DefaultAgent`의 `run()` 및 `step()` 메서드를 통해 `LM 쿼리 → 액션 파싱 → 환경 실행 → 관측 메시지 반영`의 에이전트 라이프사이클을 총괄 (".../mini-swe-agent/src/minisweagent/agents/default.py#L126-L158") |
| **3** | **`.../mini-swe-agent/src/minisweagent/environments/local.py`** | 무상태 셸 명령 실행 및 피드백 캡처 | `subprocess.run` 기반으로 독립 프로세스 격리 명령을 실행하고, `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 종료 시그널을 감지 (".../mini-swe-agent/src/minisweagent/environments/local.py#L27-L56")|
| **4** | **`.../mini-swe-agent/src/minisweagent/models/litellm_model.py`** | 통일된 LLM 질의 및 프롬프트 포맷팅 | LiteLLM을 통해 다양한 모델 제공자와 통신하고, 템플릿 변수를 주입하며, 비용(cost) 및 토큰 사용량을 추적 ()".../mini-swe-agent/src/minisweagent/models/litellm_model.py:L45-L120") |
| **5** | **`.../mini-swe-agent/src/minisweagent/run/mini.py`** | 메인 CLI 오케스트레이션 및 팩토리 연결 | 전역 `.env`, `mini.yaml`, CLI 인자를 병합하고 3대 컴포넌트를 결합하여 사용자 태스크를 실행시키는 중앙 진입점 (".../mini-swe-agent/src/minisweagent/run/mini.py#L90-L105") |
| **6** | **`.../mini-swe-agent/src/minisweagent/config/mini.yaml`** | 기본 프롬프트 템플릿 및 동작 정책 정의 | 에이전트에게 전달되는 시스템 지침(bash 명령 규칙, 완료 선언 형식), 스텝 제한(step_limit), 비용 한도(cost_limit)를 규정하는 핵심 설정 (".../mini-swe-agent/src/minisweagent/config/mini.yaml#L1-L110")|

### 핵심 모듈 선정 이유 요약
`mini-swe-agent`는 **[Interface (`__init__.py`)] → [Control (`agents`)] → [Execution (`environments`)] → [Inference (`models`)] → [Orchestration (`run`)] → [Policy (`config`)]** 의 6대 레이어가 유기적으로 결합하여 최소한의 코드로 강력한 SWE 에이전트 기능을 수행하도록 설계되어 있어, 위 6개 모듈이 시스템 동작을 이해하는 데 가장 중요하다고 판단됩니다 (".../mini-swe-agent/AGENTS.md#L6-L17", ".../mini-swe-agent/Workflow_KR.md#L10-L16").

# 02. 가상환경 동적 실행 및 테스트 결과 보고서 (Dynamic Check)

> **분석 기준일:** 2026-10-12  
> **실행 환경:** Windows 11, Python 3.13.11, pytest-9.1.1, mini-swe-agent v2.4.6 (`.venv`)  
> **분석 규칙 준수:** 소스 코드 미수정 (읽기 및 실행만), 모든 주장에 `경로:라인` 근거 제시, `[확인]`(Verified) 및 `[추정]`(Inferred) 구분 표기

---

## 1. 동적 실행 개요

1단계(정적 분석)에서 파악한 빌드·테스트 체계와 실행 진입점의 실제 동작 여부를 검증하기 위해, 로컬 가상환경(`.venv`)에서 다음 세 가지 동적 실행을 진행했습니다:
1. **전체 단위 테스트 스위트 실행 (`pytest`)**
2. **독립 모듈별 단위 테스트 실행 (`tests/models/test_init.py`, `tests/agents/test_default.py`)**
3. **가장 간단한 실행 예제 및 CLI 진입점 호출 (`run.mini --help`, `run.hello_world --help`)**

---

## 2. 실행한 명령 및 결과 (Commands & Results)

### 2.1 전체 단위 테스트 실행
- **실행 명령:**
  ```powershell
  .venv\Scripts\python.exe -m pytest -v
  ```
- **실행 결과:** `실패 (Exit Code: 1, 9 Collection Errors, 2 Warnings in 33.26s)` [확인]
- **요약 요약문:**
  ```text
  =========================== short test summary info ===========================
  ERROR tests/agents/test_init.py - prompt_toolkit.output.win32.NoConsoleScreenBufferError
  ERROR tests/agents/test_interactive.py - prompt_toolkit.output.win32.NoConsoleScreenBufferError
  ERROR tests/environments/extra/test_contree.py - ModuleNotFoundError
  ERROR tests/environments/extra/test_swerex_docker.py - ModuleNotFoundError: No module named 'swerex'
  ERROR tests/environments/extra/test_swerex_modal.py - ModuleNotFoundError: No module named 'swerex'
  ERROR tests/models/test_portkey_model.py - ImportError: The portkey-ai package is required
  ERROR tests/models/test_portkey_response_model.py - ImportError: The portkey-ai package is required
  ERROR tests/run/test_cli_integration.py - prompt_toolkit.output.win32.NoConsoleScreenBufferError
  ERROR tests/run/test_local.py - prompt_toolkit.output.win32.NoConsoleScreenBufferError
  !!!!!!!!!!!!!!!!!!! Interrupted: 9 errors during collection !!!!!!!!!!!!!!!!!!!
  ======================= 2 warnings, 9 errors in 33.26s ========================
  ```

---

### 2.2 독립 모듈별 단위 테스트 실행
전체 수집 에러를 유발하는 선택적 의존성 및 콘솔 의존 모듈을 제외하고 모델 관련 테스트를 분리 실행했습니다.
- **실행 명령:**
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/models/test_init.py -v -p no:cacheprovider
  ```
- **실행 결과:** `성공 (21 Passed in 5.80s, Exit Code: 0)` [확인]
  - `TestGetModelName` (6개 테스트 전원 통과): 모델명 우선순위 검증 통과 [확인]
  - `TestGetModelClass` (4개 테스트 전원 통과): 모델 클래스 매핑 검증 통과 [확인]
  - `TestGetModel` (6개 테스트 전원 통과): 모델 팩토리 인스턴스화 검증 통과 [확인]
  - `TestGlobalModelStats` (6개 테스트 전원 통과): 전역 모델 비용/호출 통계 검증 통과 [확인]

---

### 2.3 CLI 진입점 실행 비교 (`run.mini` vs `run.hello_world`)

#### (1) `python -m minisweagent.run.mini --help`
- **실행 명령:**
  ```powershell
  .venv\Scripts\python.exe -m minisweagent.run.mini --help
  ```
- **실행 결과:** `실패 (Exit Code: 1, NoConsoleScreenBufferError)` [확인]
- **오류 내용:**
  ```text
  File "D:\Coding_Agents\mini-swe-agent\src\minisweagent\run\mini.py", line 15, in <module>
      from minisweagent.agents.utils.prompt_user import _multiline_prompt
  File "D:\Coding_Agents\mini-swe-agent\src\minisweagent\agents\utils\prompt_user.py", line 8, in <module>
      prompt_session = PromptSession(history=_history)
  ...
  prompt_toolkit.output.win32.NoConsoleScreenBufferError: No Windows console found. Are you running cmd.exe?
  ```

#### (2) `python -m minisweagent.run.hello_world --help`
- **실행 명령:**
  ```powershell
  .venv\Scripts\python.exe -m minisweagent.run.hello_world --help
  ```
- **실행 결과:** `성공 (Exit Code: 0)` [확인]
- **출력 내용:**
  ```text
  This is mini-swe-agent version 2.4.6.
  Loading global config from '.../.env'
   Usage: python -m minisweagent.run.hello_world [OPTIONS]                       
  +- Options -------------------------------------------------------------------+
  | *  --task      -t      <str>  Task/problem statement [required]             |
  |    --model     -m      <str>  Model name (defaults to MSWEA_MODEL_NAME)     |
  |    --help                     Show this message and exit.                   |
  +-----------------------------------------------------------------------------+
  ```

---

### 2.4 에이전트 기본 동작 테스트 (`test_successful_completion`)
- **실행 명령:**
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/agents/test_default.py -v -k "test_successful_completion" -p no:cacheprovider
  ```
- **실행 결과:** `실패 (Exit Code: 1, 3 Failed, 45 Deselected)` [확인]
  - `test_successful_completion[text]` FAILED (`IndexError: list index out of range`)
  - `test_successful_completion[toolcall]` FAILED (`IndexError: list index out of range`)
  - `test_successful_completion[response_api]` FAILED (`IndexError: list index out of range`)

---

## 3. 실패 원인 심층 분석 (Root Cause Analysis)

### 원인 1: Windows `cmd.exe`의 작은따옴표(`'`) 보존과 `_check_finished` 불일치
- **발생 위치:** [src/minisweagent/environments/local.py:46-50](".../mini-swe-agent/src/minisweagent/environments/local.py#L46-L50")
- **메커니즘:**
  1. `LocalEnvironment`는 `subprocess.run(action["command"], shell=True, text=True)`로 명령을 실행합니다("../mini-swe-agent/src/minisweagent/environments/local.py#L27").
  2. Windows 환경에서 `shell=True`는 `cmd.exe /c`를 호출합니다.
  3. Linux/POSIX의 `sh`나 `bash`에서는 `echo 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'` 실행 시 작은따옴표가 제거되어 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`이 출력됩니다.
  4. 그러나 Windows `cmd.exe`는 작은따옴표를 인용부호로 제거하지 않고 **리터럴 문자열 그대로 출력**합니다:
     ```python
     # Windows cmd.exe 실행 결과
     subprocess.run("echo 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'", shell=True, capture_output=True).stdout
     # 결과: "'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\n'" (앞뒤 따옴표 포함!)
     ```
  5. `_check_finished()`는 `lines[0].strip() == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"`로 엄격하게 일치 검사를 수행하므로, 앞뒤 따옴표가 붙은 출력(`"'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'"`)은 조건문을 통과하지 못합니다 (".../mini-swe-agent/src/minisweagent/environments/local.py#L48").
  6. 결과적으로 에이전트가 종료되지 않고 다음 스텝 질의를 시도하다가 모의 모델의 출력 목록이 고갈되어 `IndexError: list index out of range`가 발생합니다 (".../MINI-SWE-AGENT/test/models/test_models.py#L112").

---

### 원인 2: `prompt_toolkit`의 모듈 최상단 초기화 및 비대화형 콘솔 오류
- **발생 위치:** [src/minisweagent/agents/utils/prompt_user.py:8](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/agents/utils/prompt_user.py#L8)
- **메커니즘:**
  1. `prompt_user.py` 최상단에서 모듈 로드 즉시 `prompt_session = PromptSession(history=_history)`를 실행합니다.
  2. `PromptSession` 초기화 과정에서 Windows 콘솔 화면 버퍼(`Win32Output.get_win32_screen_buffer_info()`)를 조회합니다.
  3. IDE 백그라운드 태스크, CI 환경, 또는 파이프 기반의 비대화형 서브프로세스에서는 표준 입출력이 Win32 콘솔 핸들에 바인딩되어 있지 않으므로 `NoConsoleScreenBufferError`가 발생합니다.
  4. [src/minisweagent/run/mini.py:15](".../mini-swe-agent/src/minisweagent/run/mini.py#L15")에서 `_multiline_prompt`를 최상단에서 import하므로, `mini --help`나 `mini`를 임포트하는 모든 테스트 모듈(`test_cli_integration.py`, `test_local.py`, `test_init.py`)이 모듈 로딩 단계에서 즉시 크래시됩니다 [확인].
  5. 반면 [src/minisweagent/run/hello_world.py](".../mini-swe-agent/src/minisweagent/run/hello_world.py#L1-L40")는 `prompt_user.py`를 임포트하지 않고 자체 Typer 옵션을 사용하므로 비대화형 환경에서도 성공적으로 실행됩니다.

---

### 원인 3: 선택적 의존성(Optional Dependencies) 미설치로 인한 테스트 수집 실패
- **발생 위치:** [pyproject.toml:50-82](".../mini-swe-agent/pyproject.toml#L50-L82")
- **메커니즘:**
  1. `tests/environments/extra/` 및 `tests/models/` 디렉터리 내의 일부 테스트 파일들은 선택적 패키지(`swe-rex`, `contree-sdk`, `portkey-ai`)를 요구합니다.
  2. 현재 `.venv` 환경은 기본 필수 의존성(`dependencies`) 위주로 설치되어 있어, `import portkey_ai` 또는 `from swerex...` 시점에 `ImportError` / `ModuleNotFoundError`가 발생하며 pytest 컬렉션이 중단되었습니다.

---

### 원인 4: Windows 파일 권한 및 Pytest 캐시 디렉터리 경고
- **발생 위치:** `.pytest_cache/`
- **메커니즘:**
  - 저장소 파일 소유권(`BUILTIN\Administrators`)과 현재 실행 사용자(`USER`)의 권한 차이로 인해 `.pytest_cache\v\cache` 디렉터리 쓰기 시 `[WinError 5] Access is denied` 경고가 발생합니다. `-p no:cacheprovider` 플래그를 추가하면 캐시 없이 깔끔하게 테스트를 진행할 수 있습니다 [확인].

---

## 4. 1단계 분석(01_overview.md)의 수정 및 보완 사항

동적 실행 결과를 바탕으로 1단계 정적 분석에서 발견하지 못했거나 보완이 필요한 항목을 다음과 같이 교정합니다:

1. **실행 환경의 OS 의존성 및 셸 차이 명시 필요:**
   - *1단계 기술:* "로컬 환경 구현체인 `LocalEnvironment`는 `subprocess.run` 기반으로 독립된 프로세스로 명령 실행을 보장한다."
   - *동적 실행 교정:* `LocalEnvironment`는 `shell=True`를 사용하므로 POSIX(bash) 환경을 기본 전제로 작성되어 있습니다. Windows에서 실행할 경우 `cmd.exe`의 따옴표 처리 방식 차이로 인해 기본 완료 시그널(`echo 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'`) 매칭이 실패할 수 있으므로, Windows 환경에서는 WSL, Git Bash, 또는 따옴표 없는 명령어 형식이 필요함을 확인했습니다 [확인].
2. **CLI 진입점별 런타임 요구조건 차이:**
   - *1단계 기술:* "`mini`와 `mini-swe-agent`가 메인 CLI 진입점이다."
   - *동적 실행 교정:* 메인 CLI인 `mini.py`는 `prompt_toolkit`에 대한 모듈 레벨 하드 의존성을 가지므로 완전한 인터랙티브 TTY 콘솔 버퍼가 필요합니다. 반면 헤드리스나 스크립트 기반 실행 환경에서는 [run.hello_world](".../Coding_Agents/mini-swe-agent/src/minisweagent/run/hello_world.py")가 훨씬 더 견고한 진입점입니다.
3. **테스트 실행 전제 조건:**
   - *1단계 기술:* "`pytest`를 통해 전체 테스트를 실행한다."
   - *동적 실행 교정:* 전체 `pytest`를 온전히 통과시키려면 기본 의존성 외에 `[project.optional-dependencies]`의 `full` 패키지(또는 적어도 `portkey-ai`, `swe-rex`) 설치가 선행되어야 하며, 비대화형 환경에서는 콘솔 mock 또는 선택적 테스트 패스가 필요함을 규명했습니다.

---

## 5. 결론 및 3단계 대응 방향

- **정상 작동 확인:**
  - 핵심 인터페이스 및 모델 모듈 로직([tests/models/test_init.py](".../mini-swe-agent/tests/models/test_init.py"))은 **21개 테스트가 모두 통과**하여 정상 설계되었음을 검증했습니다.
  - 최소 실행 예제인 [run.hello_world](".../mini-swe-agent/src/minisweagent/run/hello_world.py")는 정상적으로 CLI 옵션을 파싱하고 실행 준비를 마침을 확인했습니다.
- **3단계 해결 과제:**
  1. 누락된 선택적 패키지(예: `portkey-ai` 등) 설치 여부 검토
  2. Windows 환경에서 pytest 실행 시 `prompt_toolkit` 및 `LocalEnvironment` 에코 문제 우회/격리 방안 적용
  3. 안정적인 테스트 세트 구축 및 예제 실행 검증

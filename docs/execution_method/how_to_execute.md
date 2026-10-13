# mini-SWE-agent 실행 및 프로젝트 수행 가이드 (How to Execute)

본 문서는 `mini-swe-agent` 프로젝트의 설치, 환경 설정, 다양한 실행 모드(CLI 대화형, 최소 스크립트, 컨테이너 격리, SWE-bench 벤치마크 평가), 결과 분석, 테스트 검증 및 트러블슈팅에 이르는 전체 수행 방법을 상세히 정리한 가이드입니다.

- **원칙 준수**: 모든 실행 명령과 설정 옵션은 저장소의 실제 코드([src/minisweagent/run/](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/), [pyproject.toml](file:///d:/Coding_Agents/mini-swe-agent/pyproject.toml))를 기반으로 검증되었습니다 `[확인]`.

---

## 1. 사전 요구사항 및 환경 준비 (Prerequisites)

### 1.1 시스템 요구사항
- **Python**: 3.10 이상 (Python 3.10 ~ 3.13 지원) `[확인]`
- **OS**: Linux, macOS, Windows (크로스 플랫폼 지원)
- **컨테이너 런타임 (선택 사항)**: Docker 또는 Singularity/Apptainer (격리 실행 시 필요)

### 1.2 가상환경 생성 및 패키지 설치

1. **가상환경 생성 및 활성화**:
   ```bash
   # uv를 사용하는 경우 (권장)
   uv venv .venv
   .venv\Scripts\activate      # Windows
   # source .venv/bin/activate # Linux / macOS

   # 또는 표준 venv 사용
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   ```

2. **패키지 설치**:
   ```bash
   # 기본 의존성 설치 (개발/편집 가능 모드)
   pip install -e .

   # 개발 및 테스트 도구 포함 설치 (pytest, ruff 등)
   pip install -e ".[dev]"

   # 전체 기능 포함 설치 (Swe-rex, Docker, Modal 등)
   pip install -e ".[full]"
   ```

---

## 2. 모델 및 환경 설정 (Configuration Setup)

`mini-swe-agent`는 LiteLLM을 통해 100개 이상의 상용/오픈소스 LLM을 지원합니다. 모델 호출을 위해 API 키 및 기본 모델을 설정해야 합니다.

### 2.1 대화형 설정 도구 사용 (`mini-extra config`)
[src/minisweagent/run/utilities/config.py](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/utilities/config.py)에 구현된 CLI 도구를 통해 손쉽게 전역 설정을 완료할 수 있습니다:

```bash
# 최초 대화형 설정 마법사 실행 (기본 모델 및 API 키 입력)
mini-extra config setup
```

개별 키-값 설정 및 확인:
```bash
# 특정 API 키 영구 저장
mini-extra config set ANTHROPIC_API_KEY sk-ant-api03-...
mini-extra config set OPENAI_API_KEY sk-proj-...
mini-extra config set GEMINI_API_KEY AIzaSy...

# 기본 모델 지정
mini-extra config set MSWEA_MODEL_NAME anthropic/claude-3-7-sonnet

# 전역 설정 파일 직접 열기
mini-extra config edit
```

### 2.2 전역 `.env` 파일 직접 수정
설정 파일은 운영체제별 사용자 설정 디렉터리에 자동으로 위치합니다:
- **Windows**: `C:\Users\<USER>\AppData\Local\mini-swe-agent\.env`
- **Linux/macOS**: `~/.config/mini-swe-agent/.env`
- **커스텀 경로 지정**: 환경변수 `MSWEA_GLOBAL_CONFIG_DIR`로 변경 가능 `[확인]`

`.env` 파일 예시:
```env
MSWEA_MODEL_NAME=anthropic/claude-3-7-sonnet
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
MSWEA_CONFIGURED=true
```

> [!IMPORTANT]
> 모델 이름을 지정할 때는 공급자 접두사(예: `anthropic/`, `openai/`, `gemini/`, `openrouter/`)를 반드시 포함해야 올바른 공급자 API 엔드포인트로 라우팅됩니다.

---

## 3. 핵심 실행 방법 (How to Run)

### 방법 A: 기본 대화형 CLI (`mini` 또는 `python -m minisweagent.run.mini`)

[src/minisweagent/run/mini.py](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/mini.py)는 실무 개발 및 로컬 문제 해결에 가장 널리 사용되는 기본 진입점입니다.

#### 1) 기본 대화형 실행 (`confirm` 모드)
작업 지시문을 주고 실행하면, 모델이 제안한 bash 명령어를 실행하기 전 사용자에게 승인을 묻습니다:
```bash
mini -t "이 저장소의 버블 정렬 알고리즘 버그를 찾아 수정하고 테스트를 통과시켜 줘."
```

#### 2) 자율 실행 (`yolo` 모드)
사용자 확인 없이 모델이 작업을 완료할 때까지 전자동으로 명령을 실행합니다:
```bash
mini -t "fix: tests/test_init.py의 실패하는 테스트를 해결하라" -y
```

#### 3) 특정 모델 및 비용 한도 지정
```bash
mini -m openai/gpt-4o -t "웹 크롤러 에러 핸들링 리팩토링" -l 2.5 -o results/task1.traj.json
```
- `-m, --model`: 사용할 모델 이름 지정
- `-l, --cost-limit`: 최대 허용 비용 ($ 단위, 초과 시 즉시 안전 종료)
- `-o, --output`: Trajectory JSON 저장 경로 지정

#### 4) 런타임 인터랙티브 제어 (Slash Commands)
`mini` 실행 도중 프롬프트에서 모드를 실시간으로 전환할 수 있습니다:
- `/c`: **Confirm 모드** (명령 실행 전 사용자 승인 대기)
- `/y`: **Yolo 모드** (무확인 전자동 실행)
- `/u`: **Human 모드** (사용자가 직접 bash 명령을 입력하여 실행하고 모델에게 전달)

#### 5) YAML 설정 병합 및 인라인 파라미터 오버라이드
```bash
# 기본 mini.yaml에 모델 temperature 파라미터만 오버라이드
mini -c mini.yaml -c model.model_kwargs.temperature=0.2 -t "버그 수정"
```

---

### 방법 B: 최소형 파이썬 스크립트 실행 (`run.hello_world`)

[src/minisweagent/run/hello_world.py](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/hello_world.py)는 약 40줄로 작성된 최소형 파이썬 바인딩 예제입니다:

```bash
python -m minisweagent.run.hello_world -t "간단한 버그 수정" -m anthropic/claude-3-7-sonnet
```

파이썬 코드 내에서 직접 임포트하여 사용하는 방식:
```python
import yaml
from pathlib import Path
from minisweagent import package_dir
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.local import LocalEnvironment
from minisweagent.models.litellm_model import LitellmModel

model = LitellmModel(model_name="anthropic/claude-3-7-sonnet")
env = LocalEnvironment()
config = yaml.safe_load(Path(package_dir / "config" / "default.yaml").read_text())["agent"]

agent = DefaultAgent(model, env, **config)
result = agent.run("tests/test_foo.py의 실패 원인을 수정하라")
print(f"종료 상태: {result['exit_status']}")
```

---

### 방법 C: 컨테이너 격리 환경 실행 (Docker Environment)

호스트 시스템을 오염시키지 않고 격리된 컨테이너 내부에서 안전하게 실행하려면 Docker 환경을 지정합니다:

```bash
mini -t "취약점 패치 적용" \
  -c environment.environment_class=docker \
  -c environment.image=python:3.11-slim \
  -y
```
- 컨테이너 내부에서 명령이 실행되며 작업 완료 시 `--rm` 옵션에 의해 자동으로 컨테이너가 정리됩니다 ([src/minisweagent/environments/docker.py:30](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/environments/docker.py#L30)).

---

### 방법 D: SWE-bench 벤치마크 평가 실행

[src/minisweagent/run/benchmarks/swebench.py](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/benchmarks/swebench.py)를 사용하여 대규모 벤치마크 평가를 수행합니다.

#### 1) 단일 SWE-bench 인스턴스 실행
```bash
mini-extra swebench-single \
  --instance-id sympy__sympy-20590 \
  -m anthropic/claude-3-7-sonnet \
  -o results/sympy_20590.traj.json
```

#### 2) SWE-bench Lite/Verified 배치 평가
```bash
mini-extra swebench \
  -c swebench.yaml \
  -c model.model_name=anthropic/claude-3-7-sonnet \
  --split lite \
  --slice 0:10 \
  --workers 4
```
- `--workers`: 병렬 실행 워커 스레드 수 (기본 1)
- `--slice`: 평가할 인스턴스 인덱스 범위 지정 (예: 앞 10개)

---

## 4. 실행 결과 분석 및 Trajectory 뷰어 (`mini-extra inspector`)

에이전트가 실행을 마치면 모든 프롬프트, 도구 호출, 셸 실행 stdout, 소요 비용, 종료 상태가 담긴 `*.traj.json` 파일이 생성됩니다.

### 4.1 기본 저장 위치
- **`mini` CLI 기본값**: `~/.config/mini-swe-agent/last_mini_run.traj.json` ([src/minisweagent/run/mini.py:23](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/mini.py#L23))
- 사용자가 `-o <경로>`를 지정한 경우 해당 경로에 저장됨.

### 4.2 TUI 기반 Trajectory 인스펙터 실행
Textual 기반의 터미널 GUI([src/minisweagent/run/utilities/inspector.py](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/run/utilities/inspector.py))를 통해 대화 히스토리와 비용을 시각적으로 탐색할 수 있습니다:

```bash
# 특정 결과 파일 열람
mini-extra inspector results/task1.traj.json

# 단축 명령어
mini-extra i ~/.config/mini-swe-agent/last_mini_run.traj.json
```

---

## 5. 테스트 및 검증 실행 (Testing & Verification)

### 5.1 전체 단위 테스트 실행
```bash
# 기본 단위 테스트 실행 (86개 테스트 통과)
python -m pytest tests/test_init.py tests/agents/ tests/models/ tests/environments/ tests/utils/ -v
```

### 5.2 핵심 동작 특성화 테스트 실행 (Characterization Tests)
[tests/test_characterization.py](file:///d:/Coding_Agents/mini-swe-agent/tests/test_characterization.py)에 작성된 모델-환경-에이전트 루프 검증 테스트:
```bash
python -m pytest tests/test_characterization.py -v -p no:cacheprovider
```

### 5.3 오프라인 무비용 결정론적 실행 검증 (Deterministic Verification)
API 비용 지출 없이 에이전트 파이프라인의 정상 동작을 검증하려면 [DeterministicModel](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/models/test_models.py#L104)을 사용합니다:
```bash
python -c "
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.local import LocalEnvironment
from minisweagent.models.test_models import DeterministicModel, make_output
import yaml, pathlib, minisweagent

model = DeterministicModel(outputs=[
    make_output('Step 1', [{'command': 'echo Verified_Offline'}]),
    make_output('Step 2', [{'command': 'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'}])
])
env = LocalEnvironment()
cfg = yaml.safe_load(pathlib.Path(minisweagent.package_dir / 'config' / 'default.yaml').read_text())['agent']
agent = DefaultAgent(model, env, **cfg)
res = agent.run('오프라인 검증')
print('Offline run exit status:', res['exit_status'])
"
```

---

## 6. 트러블슈팅 및 팁 (Troubleshooting & Best Practices)

1. **Windows 환경 복수 셸 명령 연결**:
   - Windows cmd 환경에서 `\n` 대신 `&` 또는 `&&`로 연결해야 복수 명령이 정상 실행됩니다 (`echo command1 && echo command2`).
2. **Pytest 캐시 권한 에러 방지**:
   - 샌드박스 또는 권한 제한 환경에서 pytest 실행 시 `-p no:cacheprovider` 플래그를 추가하여 불필요한 캐시 쓰기 충돌을 방지합니다.
3. **API 재시도 한도 설정**:
   - 네트워크가 불안정한 환경에서는 환경변수 `MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT=15`를 지정하여 최대 재시도 횟수를 늘릴 수 있습니다 ([src/minisweagent/models/utils/retry.py:21](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/models/utils/retry.py#L21)).
4. **글로벌 비용 상한선 설정**:
   - SWE-bench 등 대규모 배치 작업 시 예기치 못한 비용 폭증을 방지하려면 `export MSWEA_GLOBAL_COST_LIMIT=50.0`을 설정하십시오 ([src/minisweagent/models/__init__.py:20](file:///d:/Coding_Agents/mini-swe-agent/src/minisweagent/models/__init__.py#L20)).

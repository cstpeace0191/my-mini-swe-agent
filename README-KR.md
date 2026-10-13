<div align="center">
<a href="https://mini-swe-agent.com/latest/"><img src="https://github.com/SWE-agent/mini-swe-agent/raw/main/docs/assets/mini-swe-agent-banner.svg" alt="mini-swe-agent banner" style="height: 7em"/></a>
</div>

# 가장 미니멀한 AI 소프트웨어 엔지니어링 에이전트

📣 [mini-swe-agent가 이제 Ramp SWE-Bench를 구동합니다](https://labs.ramp.com/swebench)<br/>
📣 [mini-swe-agent가 DeepSWE에서 Claude Code와 Codex를 능가했습니다](https://deepswe.datacurve.ai/blog#evaluation-harness)<br/>
📣 [새롭고 매우 까다로운 벤치마크인 ProgramBench에서 mini-swe-agent를 실행해보세요](https://mini-swe-agent.com/latest/usage/programbench/)<br/>
📣 [미니멀한 AI 에이전트 구축에 관한 새로운 튜토리얼](https://minimal-agent.com/)

[![Docs](https://img.shields.io/badge/Docs-green?style=for-the-badge&logo=materialformkdocs&logoColor=white)](https://mini-swe-agent.com/latest/)
[![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://join.slack.com/t/swe-bench/shared_invite/zt-36pj9bu5s-o3_yXPZbaH2wVnxnss1EkQ)
[![PyPI - Version](https://img.shields.io/pypi/v/mini-swe-agent?style=for-the-badge&logo=python&logoColor=white&labelColor=black&color=deeppink)](https://pypi.org/project/mini-swe-agent/)

> [!WARNING]
> 이것은 **mini-swe-agent v2**입니다. [마이그레이션 가이드](https://mini-swe-agent.com/latest/advanced/v2_migration/)를 확인하세요. 이전 버전은 [v1 브랜치](https://github.com/SWE-agent/mini-swe-agent/tree/v1)를 참고하시기 바랍니다.

2024년, 저희는 [SWE-bench](https://github.com/swe-bench/SWE-bench)와 [SWE-agent](https://github.com/swe-agent/swe-agent)를 개발하며 코딩 에이전트 혁명의 시작을 도왔습니다.

이제 질문을 던집니다: **에이전트가 100배 더 단순하면서도, 여전히 거의 똑같이 잘 작동한다면 어떨까요?**

`mini`는 다음과 같습니다:

- **광범위한 도입**: Meta, NVIDIA, Essential AI, IBM, Nebius, Anyscale, 프린스턴 대학교, 스탠퍼드 대학교 등에서 사용되고 있습니다.
- **미니멀함**: [에이전트 클래스](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/agents/default.py)는 단 100줄 남짓의 Python 코드에 불과합니다([환경](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/local.py), [모델](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/models/litellm_model.py), [실행 스크립트](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/run/hello_world.py)를 합쳐도 아주 조금 더 늘어날 뿐입니다). 복잡한 의존성이 전혀 없습니다!
- **우수한 성능:** [SWE-bench verified 벤치마크](https://www.swebench.com/)에서 74% 이상의 점수를 기록했으며, Claude Code보다 훨씬 빠르게 시작됩니다.
- **손쉬운 배포:** **로컬 환경**, **docker/podman**, **singularity/apptainer**, **bubblewrap**, **contree** 등을 지원합니다.
- **높은 호환성:** **litellm**, **openrouter**, **portkey** 등을 통해 모든 모델을 지원합니다. `/completion` 및 `/response` 엔드포인트 지원, 인터리브된 추론(interleaved thinking) 지원 등.
- [SWE-bench](https://swebench.com), [SWE-agent](https://swe-agent.com) 등을 개발한 프린스턴 및 스탠퍼드 팀이 제작
- **테스트 완료:** [![Codecov](https://img.shields.io/codecov/c/github/swe-agent/mini-swe-agent?style=flat-square)](https://codecov.io/gh/SWE-agent/mini-swe-agent)

<details>

<summary>개발 배경 및 동기 (연구 관점)</summary>

[SWE-agent](https://swe-agent.com/latest/)는 2024년 AI 에이전트 개발의 포문을 열었습니다. 당시 저희는 에이전트를 위한 도구와 특수 인터페이스에 많은 중점을 두었습니다.
하지만 1년이 지난 지금, 언어 모델(LM)들의 성능이 향상되면서 유용한 에이전트를 구축하는 데 이러한 요소들이 대부분 전혀 필요하지 않게 되었습니다!
실제로 `mini` 에이전트는:

- **Bash 외에는 다른 어떤 도구도 갖추고 있지 않습니다** — 언어 모델의 도구 호출(tool-calling) 인터페이스조차 사용할 필요가 없습니다.
  이는 말 그대로 어떤 모델과도 함께 실행할 수 있음을 의미합니다. 또한 샌드박스 환경에서 실행할 때 단 하나의 패키지도 설치할 필요가 없으며, 오직 bash만 있으면 됩니다.
- **완전히 선형적인 히스토리를 유지합니다** — 에이전트의 모든 단계는 메시지에 내용을 추가하기만 하면 끝납니다.
  따라서 궤적(trajectory)과 언어 모델에 전달하는 메시지 사이에 차이가 없습니다.
  디버깅과 파인 튜닝에 매우 이상적입니다.
- **`subprocess.run`으로 액션을 실행합니다** — 상태를 유지하는 셸 세션을 계속 실행해 두는 것과 달리, 모든 액션이 완전히 독립적입니다.
  이 덕분에 샌드박스에서 액션을 실행하기가 매우 쉬워지며(말 그대로 `subprocess.run`을 `docker exec`로 바꾸기만 하면 됨), 손쉽게 확장이 가능합니다. 솔직히 말씀드리면, 이는 [정말 중요한 부분](https://mini-swe-agent.com/latest/faq/#why-no-shell-session)입니다.

이러한 특징들 덕분에 에이전트 비계(scaffold)가 아닌 언어 모델 자체를 관심의 중심에 두는 시스템이자 베이스라인 시스템으로서 완벽합니다.
`mini`를 사용하여 다양한 언어 모델의 성능을 평가한 [SWE-bench (bash only)](https://www.swebench.com/) 리더보드에서 그 결과를 확인할 수 있습니다.

</details>

<details>
<summary>개발 배경 및 동기 (도구 관점)</summary>

어떤 에이전트들은 과적합된 연구 결과물에 불과합니다. 또 다른 에이전트들은 UI가 과도하게 무거운 프론트엔드 괴물입니다.

`mini` 에이전트는 블랙박스가 아닌, 자유롭게 수정할 수 있는(hackable) 도구를 지향합니다.

- 한눈에 이해할 수 있을 만큼 **단순함**
- 일상적인 작업 흐름에서 사용할 수 있을 만큼 **편리함**
- 확장할 수 있을 만큼 **유연함**

저희가 만든 [swe-agent](https://swe-agent.com/latest/)를 포함한 다른 에이전트들과 달리, 다음과 같은 이유로 근본적으로 더 단순합니다:

- **Bash 외에는 다른 도구가 없습니다** — 언어 모델의 도구 호출(tool-calling) 인터페이스조차 사용할 필요가 없습니다.
  에이전트가 수행할 수 있는 모든 개별 작업에 맞춰 커스텀 도구를 구현하는 대신, 언어 모델이 셸의 잠재력을 최대한 활용하도록 하는 데 완전히 집중합니다.
  PR 생성과 같은 특정 작업을 수행하고 싶으신가요?
  에이전트 내부 코드에 이를 구현하느라 시간을 쓰는 대신, 언어 모델이 스스로 방법을 찾아내도록 지시하기만 하면 됩니다.
- **`subprocess.run`으로 액션을 실행합니다** — 상태를 유지하는 셸 세션을 계속 켜두는 것과 달리, 모든 액션이 완전히 독립적입니다.
  이는 에이전트의 안정성에 있어 [정말 중요한 부분](https://mini-swe-agent.com/latest/faq/#why-no-shell-session)입니다.
- **완전히 선형적인 히스토리를 유지합니다** — 에이전트의 각 단계는 다음 단계에서 언어 모델에 전달되는 메시지에 내용을 덧붙이기만 하면 끝납니다.
  이는 디버깅과 언어 모델에 어떤 프롬프트가 전달되는지 파악하기에 매우 좋습니다.

</details>

<details>
<summary>SWE-agent와 mini-SWE-agent 중 무엇을 사용해야 할까요?</summary>

기본 선택지로 `mini-swe-agent`를 고려하시는 것을 권장합니다.
특히 다음과 같은 경우에 `mini-swe-agent`를 사용하는 것이 좋습니다:

- 로컬에서 빠르게 실행되는 커맨드 라인 도구를 원할 때
- 매우 단순한 제어 흐름(control flow)을 가진 에이전트를 원할 때
- 샌드박싱 및 벤치마크 평가를 훨씬 더 빠르고, 간단하며, 안정적으로 수행하고 싶을 때
- 특정 에이전트 구조에 과적합되지 않은 상태로 파인 튜닝(FT)이나 강화학습(RL)을 진행하고 싶을 때

다음과 같은 경우에는 `swe-agent`를 사용하는 것이 좋습니다:

- 각각 고유한 인터페이스를 가진 다양한 도구 세트를 실험해보고 싶을 때
- 다양한 히스토리 프로세서를 실험해보고 싶을 때

두 프로젝트 모두에서 제공되는 기능:

- SWE-Bench에서의 뛰어난 성능
- 궤적 브라우저 (Trajectory browser)

</details>

<table>
<tr>
<td width="50%">
<a href="https://mini-swe-agent.com/latest/usage/mini/"><strong>CLI</strong></a> (<code>mini</code>)
</td>
<td>
<a href="https://mini-swe-agent.com/latest/usage/swebench/"><strong>배치 추론 (Batch inference)</strong></a>
</td>
</tr>
<tr>
<td width="50%">

![mini](https://github.com/SWE-agent/swe-agent-media/blob/main/media/mini/gif/mini.gif?raw=true)

</td>
<td>

![swebench](https://github.com/SWE-agent/swe-agent-media/blob/main/media/mini/gif/swebench.gif?raw=true)

</td>
</tr>
<tr>
<td>
<a href="https://mini-swe-agent.com/latest/usage/inspector/"><strong>궤적 브라우저 (Trajectory browser)</strong></a>
</td>
<td>
<a href="https://mini-swe-agent.com/latest/advanced/cookbook/"><strong>파이썬 바인딩 (Python bindings)</strong></a>
</td>
</tr>
<tr>
<td>

![inspector](https://github.com/SWE-agent/swe-agent-media/blob/main/media/mini/gif/inspector.gif?raw=true)

</td>
<td>

```python
agent = DefaultAgent(
    LitellmModel(model_name=...),
    LocalEnvironment(),
)
agent.run("Write a sudoku game")
```

</td>
</tr>
</table>

## 시작하기

**옵션 1:** CLI만 간단히 사용해보고 싶은 경우 (격리된 가상 환경에 패키지 설치)

```bash
pip install uv && uvx mini-swe-agent
# 또는
pip install pipx && pipx ensurepath && pipx run mini-swe-agent
```

**옵션 2:** 현재 환경에 CLI 및 Python 바인딩 설치

```bash
pip install mini-swe-agent
mini  # CLI 실행
```

**옵션 3:** 소스 코드로부터 설치 (개발자용 설정)

```bash
git clone https://github.com/SWE-agent/mini-swe-agent.git
cd mini-swe-agent && pip install -e .
mini  # CLI 실행
```

자세한 내용은 [공식 문서](https://mini-swe-agent.com/latest/)를 참고하세요:

* [빠른 시작 가이드 (Quick start guide)](https://mini-swe-agent.com/latest/quickstart/)
* [`mini` CLI 사용법](https://mini-swe-agent.com/latest/usage/mini/)
* [글로벌 환경 설정 (Global configuration)](https://mini-swe-agent.com/latest/advanced/global_configuration/)
* [YAML 설정 파일 (Yaml configuration files)](https://mini-swe-agent.com/latest/advanced/yaml_configuration/)
* [쿡북으로 활용도 높이기 (Cookbook)](https://mini-swe-agent.com/latest/advanced/cookbook/)
* [자주 묻는 질문 (FAQ)](https://mini-swe-agent.com/latest/faq/)
* [기여하기 (Contribute!)](https://mini-swe-agent.com/latest/contributing/)

## 인용 (Attribution)

이 프로젝트가 도움이 되었다면, 연구 및 작업물에 [SWE-agent 논문](https://arxiv.org/abs/2405.15793)을 인용해 주시기 바랍니다:

```bibtex
@inproceedings{yang2024sweagent,
  title={{SWE}-agent: Agent-Computer Interfaces Enable Automated Software Engineering},
  author={John Yang and Carlos E Jimenez and Alexander Wettig and Kilian Lieret and Shunyu Yao and Karthik R Narasimhan and Ofir Press},
  booktitle={The Thirty-eighth Annual Conference on Neural Information Processing Systems},
  year={2024},
  url={https://arxiv.org/abs/2405.15793}
}
```

기타 프로젝트:

<div align="center">
  <a href="https://github.com/SWE-agent/SWE-agent"><img src="https://raw.githubusercontent.com/SWE-agent/swe-agent-media/refs/heads/main/media/logos_banners/sweagent_logo_text_below.svg" alt="SWE-agent" height="120px"></a>
   &nbsp;&nbsp;
  <a href="https://github.com/SWE-agent/SWE-ReX"><img src="https://raw.githubusercontent.com/SWE-agent/swe-agent-media/refs/heads/main/media/logos_banners/swerex_logo_text_below.svg" alt="SWE-ReX" height="120px"></a>
   &nbsp;&nbsp;
  <a href="https://github.com/SWE-bench/SWE-bench"><img src="https://raw.githubusercontent.com/SWE-bench/swe-bench-media/refs/heads/main/media/logos_banners/swebench_logo_text_below.svg" alt="SWE-bench" height="120px"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/SWE-bench/SWE-smith"><img src="https://raw.githubusercontent.com/SWE-agent/swe-agent-media/refs/heads/main/media/logos_banners/swesmith_logo_text_below.svg" alt="SWE-smith" height="120px"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/codeclash-ai/codeclash"><img src="https://raw.githubusercontent.com/SWE-agent/swe-agent-media/refs/heads/main/media/logos_banners/codeclash_logo_text_below.svg" alt="CodeClash" height="120px"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/SWE-bench/sb-cli"><img src="https://raw.githubusercontent.com/SWE-agent/swe-agent-media/refs/heads/main/media/logos_banners/sbcli_logo_text_below.svg" alt="sb-cli" height="120px"></a>
</div>

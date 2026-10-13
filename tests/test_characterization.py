from pathlib import Path

import pytest
import yaml

from minisweagent import package_dir
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.local import LocalEnvironment
from minisweagent.exceptions import Submitted
from minisweagent.models import GLOBAL_MODEL_STATS
from minisweagent.models.test_models import DeterministicModel, make_output


def test_model_interface(reset_global_stats):
    model = DeterministicModel(
        outputs=[make_output("Test thought", [{"command": "echo test"}], cost=1.25)],
        cost_per_call=1.25,
    )
    message = model.query([{"role": "user", "content": "hello"}])
    assert message["content"] == "Test thought"
    assert message["extra"]["actions"] == [{"command": "echo test"}]
    assert message["extra"]["cost"] == 1.25
    assert GLOBAL_MODEL_STATS.cost == 1.25
    obs = model.format_observation_messages(
        message,
        [{"output": "test output\n", "returncode": 0, "exception_info": ""}],
        {"task": "dummy"},
    )
    assert len(obs) == 1
    assert "<returncode>0</returncode>" in obs[0]["content"]
    assert "test output" in obs[0]["content"]


@pytest.mark.parametrize(
    ("command", "expected_token"),
    [
        ("echo char_test_1", "char_test_1"),
        ("echo line1 && echo line2", "line2"),
    ],
)
def test_environment_execution(command: str, expected_token: str):
    env = LocalEnvironment()
    res = env.execute({"command": command})
    assert res["returncode"] == 0
    assert expected_token in res["output"]


def test_environment_submission_signal():
    env = LocalEnvironment()
    with pytest.raises(Submitted) as exc_info:
        env.execute({"command": "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT& echo patch_content"})
    assert exc_info.value.messages[0]["extra"]["exit_status"] == "Submitted"
    assert "patch_content" in exc_info.value.messages[0]["extra"]["submission"]


def test_agent_single_step_loop():
    model = DeterministicModel(
        outputs=[make_output("Step thought", [{"command": "echo step_verified"}], cost=0.5)]
    )
    env = LocalEnvironment()
    config_dict = yaml.safe_load(Path(package_dir / "config" / "default.yaml").read_text())["agent"]
    agent = DefaultAgent(model, env, **config_dict)

    agent.add_messages(
        {"role": "system", "content": "You are a test assistant"},
        {"role": "user", "content": "Please verify step execution"},
    )
    assert agent.n_calls == 0
    assert agent.cost == 0.0

    agent.step()

    assert agent.n_calls == 1
    assert agent.cost == 0.5
    assert len(agent.messages) == 4
    assert agent.messages[2]["role"] == "assistant"
    assert agent.messages[2]["content"] == "Step thought"
    assert agent.messages[3]["role"] == "user"
    assert "<returncode>0</returncode>" in agent.messages[3]["content"]
    assert "step_verified" in agent.messages[3]["content"]

    serialized = agent.serialize()
    assert serialized["info"]["model_stats"]["api_calls"] == 1
    assert serialized["info"]["model_stats"]["instance_cost"] == 0.5
    assert serialized["trajectory_format"] == "mini-swe-agent-1.1"


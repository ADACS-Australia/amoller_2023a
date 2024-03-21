import os
from pathlib import Path
import shutil
from .test_utils import call_cmd
import pytest

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/dump/"


@pytest.fixture(scope="module")
def make_data():
    shutil.rmtree(dir_path, ignore_errors=True)
    cmd = "snn --data --dump_dir tests/dump --raw_dir tests/raw"
    call_cmd(cmd)
    yield
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.mark.parametrize("option", ["", "--nb_classes 2"])
def test_rnn_train(make_data, option):
    cmd = "snn --train_rnn --dump_dir tests/dump --nb_epoch=5 " + option

    call_cmd(cmd)

    model_dir = dir_path + "models/"
    files = [
        "*/*.pt",
        "*/PRED*",
        "*/METRICS*",
        "*/train_and_val_loss*",
        "*/training_log.json",
    ]
    for fi in files:
        assert len([e for e in (Path(model_dir)).glob(fi)]) == 1

    # clean up model folder
    shutil.rmtree(model_dir)


class TestValidation:
    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        shutil.rmtree(dir_path, ignore_errors=True)
        cmd1 = "snn --data --dump_dir tests/dump --raw_dir tests/raw"
        call_cmd(cmd1)
        cmd2 = "snn --train_rnn --dump_dir tests/dump --nb_epoch=5"
        call_cmd(cmd2)
        yield
        shutil.rmtree(dir_path, ignore_errors=True)

    def test_rnn_validate(self):
        """test fails if the line command exits with error"""
        cmd = "snn --validate_rnn --dump_dir tests/dump"

        call_cmd(cmd)

    def test_rnn_metrics(self):
        model_dir = dir_path + "models/"
        pred_files = [e for e in (Path(model_dir)).glob("*/PRED*")]

        for pf in pred_files:
            cmd = (
                f"snn --validate_rnn --metrics --dump_dir tests/dump "
                f"--prediction_files {pf}"
            )

            call_cmd(cmd)

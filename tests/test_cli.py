import json

from vinovatornik import __version__
from vinovatornik.cli import main


def test_cli_prints_verdict(capsys):
    assert main(["в", "меня", "врезался", "грузовик"]) == 0
    out = capsys.readouterr().out
    assert "Виноват:" in out
    assert "Уверенность:" in out


def test_cli_json_output(capsys):
    assert main(["--json", "упал", "прод"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"culprit", "category", "confidence", "reason", "level"}


def test_cli_level_option(capsys):
    assert main(["-l", "1", "--json", "сломался", "лифт"]) == 0
    assert json.loads(capsys.readouterr().out)["category"] == "Быт"


def test_cli_bad_level_returns_error(capsys):
    assert main(["-l", "9", "проблема"]) == 2
    assert "Ошибка" in capsys.readouterr().err


def test_cli_same_input_same_output(capsys):
    main(["проблема"])
    first = capsys.readouterr().out
    main(["проблема"])
    assert capsys.readouterr().out == first


def test_version(capsys):
    try:
        main(["--version"])
    except SystemExit as exit_info:
        assert exit_info.code == 0
    assert __version__ in capsys.readouterr().out

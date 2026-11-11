"""Bad input and clearer feedback (specs/bad-input-ux.md).

Assumed interface:
- accounts.account_name(target, player); accounts.log_in(..., now=seconds) with a limit of 5 wrong tries in 10 min
- browser_input.clean_action(value) -> {"id", "x", "code", "from"} or None
- app: an invite link ?sala=CODE joins the room as contacto
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import accounts
from accounts import AccountError, account_name, create_account, log_in
from browser_input import clean_action
from logic import apply_action, new_game
from rooms import create_room, join_room
from translations import tr

APP_PATH = str(Path(__file__).parent.parent / "app.py")
ALICE = "alice_aaaaaaaaaaaaaaaaaaaaaa"
BRUNO = "bruno_bbbbbbbbbbbbbbbbbbbbbb"
CARLA = "carla_cccccccccccccccccccccc"


@pytest.fixture
def store(tmp_path):
    path = tmp_path / "game.db"
    accounts.FAILED_LOGINS.clear()
    return path


# Done when 1
def test_the_account_name_comes_from_the_database(store):
    assert account_name(store, ALICE) is None
    create_account(store, "Alice", "secret1", ALICE)

    assert account_name(store, ALICE) == "alice"


@pytest.fixture
def online(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    accounts.FAILED_LOGINS.clear()
    return path


def open_app(player, **params):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.query_params["jogador"] = player
    for name, value in params.items():
        at.query_params[name] = value
    at.run()
    return at


def texts(at):
    parts = [el.value for el in at.markdown] + [el.value for el in at.caption] + [el.value for el in at.error]
    parts += [el.value for el in at.info] + [el.value for el in at.warning] + [el.value for el in at.code]
    return " ".join(str(part) for part in parts)


def test_a_name_in_the_link_does_not_log_you_in(online):
    at = open_app(ALICE, conta="admin")

    assert "admin" not in texts(at)
    assert "sair_conta" not in [b.key for b in at.button]


def test_the_real_account_is_shown(online):
    create_account(online, "alice", "secret1", ALICE)

    at = open_app(ALICE)

    assert "alice" in texts(at)
    assert "sair_conta" in [b.key for b in at.button]


# Done when 2
def test_one_account_per_player_code(store):
    create_account(store, "alice", "secret1", ALICE)

    with pytest.raises(AccountError, match="already have an account"):
        create_account(store, "other", "secret2", ALICE)
    assert log_in(store, "alice", "secret1") == ALICE


# Done when 3
def test_too_many_wrong_logins_lock_the_username_for_a_while(store):
    create_account(store, "alice", "secret1", ALICE)
    for _ in range(5):
        with pytest.raises(AccountError, match="Wrong"):
            log_in(store, "alice", "nope!!", now=1000)

    with pytest.raises(AccountError, match="Too many attempts"):
        log_in(store, "alice", "secret1", now=1001)
    assert log_in(store, "alice", "secret1", now=1000 + 601) == ALICE


def test_a_good_login_clears_the_count(store):
    create_account(store, "alice", "secret1", ALICE)
    for _ in range(4):
        with pytest.raises(AccountError):
            log_in(store, "alice", "nope!!", now=1000)
    log_in(store, "alice", "secret1", now=1000)

    for _ in range(4):
        with pytest.raises(AccountError, match="Wrong"):
            log_in(store, "alice", "nope!!", now=1001)
    assert log_in(store, "alice", "secret1", now=1001) == ALICE


def test_the_limit_is_per_username_and_unknown_names_count_too(store):
    create_account(store, "alice", "secret1", ALICE)
    for _ in range(5):
        with pytest.raises(AccountError):
            log_in(store, "ghost", "nope!!", now=1000)

    with pytest.raises(AccountError, match="Too many attempts"):
        log_in(store, "GHOST", "nope!!", now=1000)
    assert log_in(store, "alice", "secret1", now=1000) == ALICE


# Done when 4
def test_spaces_around_the_username_are_removed(store):
    create_account(store, "  alice ", "secret1", ALICE)

    assert log_in(store, " Alice  ", "secret1") == ALICE


def test_the_password_rule_says_6_to_128(store):
    for password in ("short", "x" * 129):
        with pytest.raises(AccountError, match="6 to 128"):
            create_account(store, "alice", password, ALICE)


# Done when 5
@pytest.mark.parametrize("code", ["", "   ", None])
def test_an_empty_code_asks_for_the_code(code):
    state = {"scene": "ministerio", "inventory": ["cartao_acesso"], "decisions": {}}

    accepted, after, message = apply_action(state, "ir_arquivo", code)

    assert not accepted and after == state
    assert message == "Type the code first."


@pytest.mark.parametrize("code", [1704, ["1704"], {"a": 1}, 17.04])
def test_a_code_that_is_not_text_is_a_wrong_code(code):
    state = {"scene": "ministerio", "inventory": ["cartao_acesso"], "decisions": {}}

    accepted, after, _ = apply_action(state, "ir_arquivo", code)

    assert not accepted and after == state


@pytest.mark.parametrize(
    "value",
    [None, "ir_arquivo", 42, [], {}, {"id": 5, "x": 10}, {"id": "ir_arquivo", "x": "left"}, {"x": 10}],
)
def test_malformed_actions_from_the_browser_are_ignored(value):
    assert clean_action(value) is None


def test_a_good_action_is_kept_and_its_code_is_capped():
    cleaned = clean_action({"id": "ir_arquivo", "x": 120.5, "code": "1" * 100, "from": "nowhere", "extra": 1})

    assert cleaned == {"id": "ir_arquivo", "x": 120.5, "code": "1" * 32, "from": None}
    assert clean_action({"id": "abrir", "x": 3, "code": 1704})["code"] is None


# Done when 6
def test_an_invite_link_joins_the_room_as_contact(online):
    code = create_room(online, ALICE)

    at = open_app(BRUNO, sala=code)

    assert at.title[0].value == "Ministry of Truth"
    assert "agent" in texts(at).lower() or "contact" in texts(at).lower()
    assert join_room(online, code, BRUNO) == "contacto"


def test_a_full_room_link_explains_why(online):
    code = create_room(online, ALICE)
    join_room(online, code, BRUNO)

    at = open_app(CARLA, sala=code)

    assert "full" in texts(at)
    assert "sala" not in at.query_params


def test_an_unknown_room_link_explains_why(online):
    at = open_app(CARLA, sala="ZZZZZZ")

    assert "not found" in texts(at)


def test_the_waiting_room_shows_an_invite_link_without_the_player_code(online):
    at = open_app(ALICE)
    at.button(key="criar_sala").click().run()

    shown = texts(at)
    assert "?sala=" in shown
    assert ALICE not in shown


# Done when 7
def test_new_texts_have_portuguese():
    for text in (
        "Type the code first.",
        "Too many attempts. Wait a few minutes and try again.",
        "A password has 6 to 128 characters.",
    ):
        assert tr(text, "pt") != text, text
    assert tr("You already have an account. Log out first to create another.", "pt") != (
        "You already have an account. Log out first to create another."
    )


def test_new_game_is_unchanged():
    assert new_game() == {"scene": "ministerio", "inventory": [], "decisions": {}}

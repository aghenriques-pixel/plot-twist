"""Levels map and accounts (specs/levels-dialogue-accounts.md)."""

import sqlite3

import pytest

from accounts import AccountError, create_account, log_in
from db import endings_reached, record_ending
from levels import COMING_SOON, LEVELS, level_for_chapter, level_status

ALICE = "alice_aaaaaaaaaaaaaaaaaaaaaa"


@pytest.fixture
def db(tmp_path):
    return tmp_path / "game.db"


# --- Levels -------------------------------------------------------------------------------


# Changed (specs/levels-2-and-3.md): levels 2 and 3 exist now, locked until the level before is done
def test_a_new_player_has_level_1_open():
    status = level_status(set())

    assert [(s["number"], s["unlocked"], s["completed"]) for s in status] == [(1, True, False), (2, False, False), (3, False, False)]
    assert COMING_SOON == []


@pytest.mark.parametrize("ending", ["final_entregue", "final_tiago"])
def test_submitting_completes_level_1(ending):
    assert level_status({ending})[0]["completed"]


def test_failing_endings_do_not_complete_the_level():
    status = level_status({"final_afogado", "final_seguranca"})

    assert not status[0]["completed"]
    assert status[0]["endings_found"] == 2
    assert status[0]["endings_total"] == 5


def test_levels_match_chapters():
    assert [level["chapter"] for level in LEVELS] == [1, 2, 3]  # changed: specs/levels-2-and-3.md
    assert level_for_chapter(1)["number"] == 1


def test_endings_are_recorded_once_per_player_and_survive_a_restart(db):
    record_ending(db, ALICE, "final_entregue")
    record_ending(db, ALICE, "final_entregue")
    record_ending(db, "someone_else_xxxxxxxxxxxxx", "final_afogado")

    assert endings_reached(db, ALICE) == {"final_entregue"}


# --- Accounts -----------------------------------------------------------------------------


def test_create_and_log_in_returns_the_same_player(db):
    player = create_account(db, "afonso", "segredo123", ALICE)

    assert player == ALICE
    assert log_in(db, "afonso", "segredo123") == ALICE
    assert log_in(db, "AFONSO", "segredo123") == ALICE  # usernames ignore case


def test_username_must_be_unique(db):
    create_account(db, "afonso", "segredo123", ALICE)

    with pytest.raises(AccountError):
        create_account(db, "Afonso", "outra-coisa", "other_player_xxxxxxxxxxxxx")


def test_wrong_password_or_unknown_user_gives_the_same_message(db):
    create_account(db, "afonso", "segredo123", ALICE)

    with pytest.raises(AccountError) as wrong_password:
        log_in(db, "afonso", "errada")
    with pytest.raises(AccountError) as unknown_user:
        log_in(db, "ninguem", "segredo123")
    assert str(wrong_password.value) == str(unknown_user.value)


@pytest.mark.parametrize("username, password", [("ab", "segredo123"), ("nome com espaços", "segredo123"), ("x" * 21, "segredo123"),
                                                ("afonso", "12345"), ("' OR 1=1 --", "segredo123")])
def test_invalid_usernames_and_short_passwords_are_refused(db, username, password):
    with pytest.raises(AccountError):
        create_account(db, username, password, ALICE)


def test_password_is_never_stored(db):
    create_account(db, "afonso", "segredo123", ALICE)

    with sqlite3.connect(db) as conn:
        dump = " ".join(str(value) for row in conn.execute("SELECT * FROM accounts") for value in row)
    conn.close()
    assert "segredo123" not in dump

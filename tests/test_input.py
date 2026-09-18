"""Check pygame keyboard translation at the application boundary."""

from random import Random

import pygame
import pytest

from snake_game.config import MIN_WINDOW_SIZE
from snake_game.game import Game, GameState
from snake_game.grid import Position
from snake_game.main import clamp_window_size, process_events
from snake_game.snake import Direction, Snake


@pytest.mark.parametrize(
    ("key", "direction"),
    [
        (pygame.K_UP, Direction.UP),
        (pygame.K_w, Direction.UP),
        (pygame.K_DOWN, Direction.DOWN),
        (pygame.K_s, Direction.DOWN),
        (pygame.K_LEFT, Direction.LEFT),
        (pygame.K_a, Direction.LEFT),
        (pygame.K_RIGHT, Direction.RIGHT),
        (pygame.K_d, Direction.RIGHT),
    ],
)
def test_keyboard_requests_domain_direction(
    monkeypatch: pytest.MonkeyPatch, key: int, direction: Direction
) -> None:
    snake = Snake([Position(5, 3), Position(5, 4), Position(5, 5)], Direction.UP)
    if direction in (Direction.UP, Direction.DOWN):
        snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=key)]
    )

    assert process_events(Game(snake, Random(0)))
    assert snake.requested_direction == direction
    snake.step()
    assert snake.direction == direction


def test_unrelated_events_do_not_change_direction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    events = [
        pygame.event.Event(pygame.KEYUP, key=pygame.K_UP),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        pygame.event.Event(pygame.USEREVENT),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    assert process_events(Game(snake, Random(0)))
    assert snake.requested_direction is None


@pytest.mark.parametrize("key", [pygame.K_r, pygame.K_RETURN])
@pytest.mark.parametrize("state", [GameState.RUNNING, GameState.GAME_OVER])
def test_restart_keys_only_reset_game_over(
    monkeypatch: pytest.MonkeyPatch, key: int, state: GameState
) -> None:
    snake = Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT)
    game = Game(snake, Random(0))
    game.score = 5
    game.accumulated_ms = 100
    if state is GameState.GAME_OVER:
        game.step()
    body = snake.body.copy()
    food = game.food
    rng_state = game.rng.getstate()
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=key)]
    )

    assert process_events(game)

    assert game.state is GameState.RUNNING
    if state is GameState.GAME_OVER:
        assert game.snake is not snake
        assert game.snake.body == [Position(16, 12), Position(15, 12), Position(14, 12)]
        assert game.snake.direction is Direction.RIGHT
        assert game.snake.requested_direction is None
        assert game.score == 0
        assert game.accumulated_ms == 0
        assert game.food is not None
        assert game.food not in game.snake.body
        assert game.rng.getstate() != rng_state
    else:
        assert game.snake is snake
        assert snake.body == body
        assert snake.direction is Direction.LEFT
        assert game.score == 5
        assert game.accumulated_ms == 100
        assert game.food == food
        assert game.rng.getstate() == rng_state


@pytest.mark.parametrize("key", [pygame.K_r, pygame.K_RETURN])
def test_releasing_restart_key_does_not_restart(
    monkeypatch: pytest.MonkeyPatch, key: int
) -> None:
    game = Game(
        Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT),
        Random(0),
    )
    game.step()
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYUP, key=key)]
    )

    assert process_events(game)
    assert game.state is GameState.GAME_OVER


def test_event_batch_cannot_reverse_snake(monkeypatch: pytest.MonkeyPatch) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    assert process_events(Game(snake, Random(0)))
    snake.step()
    assert snake.direction == Direction.UP


@pytest.mark.parametrize(
    "key",
    [
        pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_w,
        pygame.K_a,
        pygame.K_s,
        pygame.K_d,
    ],
)
def test_direction_keys_do_not_alter_game_over(
    monkeypatch: pytest.MonkeyPatch, key: int
) -> None:
    snake = Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT)
    game = Game(snake, Random(0))
    game.step()
    body = snake.body.copy()
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=key)]
    )

    assert process_events(game)
    game.step()

    assert game.state is GameState.GAME_OVER
    assert snake.body == body
    assert snake.direction is Direction.LEFT
    assert snake.requested_direction is None


def test_display_keys_return_requests_without_changing_game(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game = Game(rng=Random(0))
    body = game.snake.body.copy()
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    result = process_events(game)

    assert result.should_continue
    assert result.toggle_fullscreen
    assert result.leave_fullscreen
    assert result.resized_to is None
    assert game.snake.body == body
    assert game.accumulated_ms == 0


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ((1280, 720), (1280, 720)),
        ((400, 900), (MIN_WINDOW_SIZE[0], 900)),
        ((1200, 300), (1200, MIN_WINDOW_SIZE[1])),
    ],
)
def test_resize_events_are_clamped(
    monkeypatch: pytest.MonkeyPatch,
    requested: tuple[int, int],
    expected: tuple[int, int],
) -> None:
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.VIDEORESIZE, size=requested)],
    )

    result = process_events(Game(rng=Random(0)))

    assert result.resized_to == expected
    assert clamp_window_size(requested) == expected


def test_quit_event_returns_stop_request(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.QUIT)],
    )

    result = process_events(Game(rng=Random(0)))

    assert not result
    assert not result.should_continue

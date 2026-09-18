"""Check application startup and shutdown using SDL's dummy display."""

from random import Random
from unittest.mock import Mock, call

import pygame
import pytest

from snake_game import main as application
from snake_game.config import (
    COLUMNS,
    FOOD_COLOR,
    FPS,
    SNAKE_COLOR,
    WINDOW_TITLE,
    WINDOWED_SIZE,
)
from snake_game.game import Game, GameState
from snake_game.grid import Position
from snake_game.layout import GameLayout
from snake_game.main import main
from snake_game.rendering import to_pixel
from snake_game.snake import Direction


def test_window_runs_until_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    event_polls = 0
    set_mode = Mock(wraps=pygame.display.set_mode)

    def get_events() -> list[pygame.event.Event]:
        nonlocal event_polls
        event_polls += 1
        assert pygame.get_init()
        screen = pygame.display.get_surface()
        assert screen is not None
        assert screen.get_width() > 0
        assert screen.get_height() > 0
        assert pygame.display.get_caption()[0] == WINDOW_TITLE

        if event_polls == 1:
            return []
        return [pygame.event.Event(pygame.QUIT)]

    monkeypatch.setattr(pygame.event, "get", get_events)
    monkeypatch.setattr(pygame.display, "set_mode", set_mode)

    main()

    assert event_polls == 2
    set_mode.assert_called_once_with((0, 0), pygame.FULLSCREEN)
    assert not pygame.get_init()
    assert not pygame.display.get_init()


def test_loop_repeats_phases_until_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    phases: list[str] = []
    rendered_bodies: list[list[Position]] = []
    rendered_food: list[Position | None] = []
    batches = iter(
        [
            [],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)],
            [],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )

    def get_events() -> list[pygame.event.Event]:
        phases.append("events")
        return next(batches)

    def render(screen: pygame.Surface, layout: GameLayout) -> None:
        phases.append("grid")
        application_render(screen, layout)

    def render_snake(
        screen: pygame.Surface, body: list[Position], layout: GameLayout
    ) -> None:
        phases.append("snake")
        rendered_bodies.append(body.copy())
        application_render_snake(screen, body, layout)

    def render_food(
        screen: pygame.Surface,
        position: Position | None,
        layout: GameLayout,
    ) -> None:
        phases.append("food")
        rendered_food.append(position)
        application_render_food(screen, position, layout)
        assert position is not None
        x, y = to_pixel(position, layout)
        center = (x + layout.cell_size // 2, y + layout.cell_size // 2)
        assert screen.get_at(center)[:3] == FOOD_COLOR

    def update(game: Game, elapsed_ms: int) -> int:
        phases.append("update")
        return application_update(game, elapsed_ms)

    def tick(fps: int) -> int:
        phases.append("tick")
        return next(frame_times)

    def flip_frame() -> None:
        phases.append("flip")
        flip()

    application_render = application.render_grid
    application_render_snake = application.render_snake
    application_render_food = application.render_food
    application_update = application.update
    flip = pygame.display.flip
    frame_times = iter([0, 125, 250])
    clock = Mock()
    clock.tick.side_effect = tick
    rng = Random(0)
    placements = iter([Position(16, 11), Position(0, 0)])

    def choice(available: list[Position]) -> Position:
        position = next(placements)
        assert position in available
        return position

    monkeypatch.setattr(rng, "choice", choice)
    monkeypatch.setattr(application, "Random", lambda: rng)
    monkeypatch.setattr(pygame.event, "get", get_events)
    monkeypatch.setattr(application, "update", update)
    monkeypatch.setattr(application, "render_grid", render)
    monkeypatch.setattr(application, "render_snake", render_snake)
    monkeypatch.setattr(application, "render_food", render_food)
    monkeypatch.setattr(pygame.display, "flip", flip_frame)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)
    feedback = Mock()
    monkeypatch.setattr(application, "render_game_over", feedback)
    score_display = Mock(wraps=application.render_score)
    monkeypatch.setattr(application, "render_score", score_display)

    main()

    assert phases == [
        "events",
        "tick",
        "update",
        "grid",
        "food",
        "snake",
        "flip",
    ] * 3 + ["events"]
    assert rendered_bodies == [
        [Position(16, 12), Position(15, 12), Position(14, 12)],
        [Position(16, 11), Position(16, 12), Position(15, 12), Position(14, 12)],
        [Position(16, 9), Position(16, 10), Position(16, 11), Position(16, 12)],
    ]
    assert rendered_food == [Position(16, 11), Position(0, 0), Position(0, 0)]
    for food, body in zip(rendered_food, rendered_bodies, strict=True):
        assert food not in body
    assert clock.tick.call_args_list == [call(FPS)] * 3
    assert not pygame.get_init()
    feedback.assert_not_called()
    assert [entry.args[2] for entry in score_display.call_args_list] == [0, 1, 1]


def test_pygame_shuts_down_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def get_events() -> list[pygame.event.Event]:
        raise RuntimeError("Event processing failed")

    monkeypatch.setattr(pygame.event, "get", get_events)

    with pytest.raises(RuntimeError, match="Event processing failed"):
        main()

    assert not pygame.get_init()
    assert not pygame.display.get_init()


def test_windowed_display_is_resizable_and_clamped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screen = pygame.Surface((800, 600))
    set_mode = Mock(return_value=screen)
    monkeypatch.setattr(pygame.display, "set_mode", set_mode)

    created_screen, layout = application.create_display(False, (320, 240))

    assert created_screen is screen
    assert layout.screen_size == (800, 600)
    set_mode.assert_called_once_with((800, 600), pygame.RESIZABLE)


def test_display_changes_preserve_match_and_discard_transition_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = iter(
        [
            [],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)],
            [pygame.event.Event(pygame.VIDEORESIZE, size=(1000, 700))],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    display_requests: list[tuple[bool, tuple[int, int]]] = []
    games: list[Game] = []
    create_game = application.Game
    clock = Mock()
    clock.tick.side_effect = [124, 5000, 5000, 5000, 5000, 0]

    def create_display(
        fullscreen: bool, windowed_size: tuple[int, int]
    ) -> tuple[pygame.Surface, GameLayout]:
        display_requests.append((fullscreen, windowed_size))
        size = (1920, 1080) if fullscreen else windowed_size
        return pygame.Surface(size), GameLayout.from_size(size)

    def make_game(rng: Random) -> Game:
        game = create_game(rng=rng)
        games.append(game)
        return game

    monkeypatch.setattr(application, "create_display", create_display)
    monkeypatch.setattr(application, "Game", make_game)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert display_requests == [
        (True, WINDOWED_SIZE),
        (False, WINDOWED_SIZE),
        (False, (1000, 700)),
        (True, (1000, 700)),
        (False, (1000, 700)),
    ]
    assert len(games) == 1
    assert games[0].snake.body == [
        Position(16, 12),
        Position(15, 12),
        Position(14, 12),
    ]
    assert games[0].snake.direction is Direction.RIGHT
    assert games[0].score == 0
    assert games[0].state is GameState.RUNNING
    assert games[0].accumulated_ms == 124
    assert clock.tick.call_args_list == [call(FPS)] * 6


def test_game_over_keeps_rendering_frozen_board_and_allows_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = iter(
        [
            [],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)],
            [],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    frames: list[bytes] = []
    games: list[Game] = []
    create_game = application.Game
    feedback = application.render_game_over
    clock = Mock()
    clock.tick.side_effect = [2000, 1000, 1000]

    def make_game(rng: Random) -> Game:
        game = create_game(rng=rng)
        game.food = Position(0, 0)
        games.append(game)
        return game

    def render_game_over(
        screen: pygame.Surface,
        font: pygame.font.Font,
        layout: GameLayout,
    ) -> None:
        before = pygame.image.tobytes(screen, "RGB")
        feedback(screen, font, layout)
        after = pygame.image.tobytes(screen, "RGB")
        assert before != after
        food_x, food_y = to_pixel(Position(0, 0), layout)
        assert (
            screen.get_at(
                (
                    food_x + layout.cell_size // 2,
                    food_y + layout.cell_size // 2,
                )
            )[:3]
            == FOOD_COLOR
        )
        snake_x, snake_y = to_pixel(Position(COLUMNS - 1, 12), layout)
        assert (
            screen.get_at(
                (
                    snake_x + layout.cell_size // 2,
                    snake_y + layout.cell_size // 2,
                )
            )[:3]
            == SNAKE_COLOR
        )
        frames.append(after)

    monkeypatch.setattr(application, "Game", make_game)
    monkeypatch.setattr(application, "render_game_over", render_game_over)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert len(frames) == 3
    assert frames[0] == frames[1] == frames[2]
    assert games[0].snake.body == [Position(32, 12), Position(31, 12), Position(30, 12)]
    assert games[0].snake.direction is Direction.RIGHT
    assert games[0].snake.requested_direction is None
    assert games[0].food == Position(0, 0)
    assert not pygame.get_init()


@pytest.mark.parametrize("restart_key", [pygame.K_r, pygame.K_RETURN])
def test_restart_renders_reset_state_and_discards_old_frame_time(
    monkeypatch: pytest.MonkeyPatch, restart_key: int
) -> None:
    batches = iter(
        [
            [],
            [],
            [pygame.event.Event(pygame.KEYDOWN, key=restart_key)],
            [],
            [],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    rng = Random(0)
    placements = iter([Position(17, 12), Position(0, 0), Position(0, 1)])
    games: list[Game] = []
    bodies: list[list[Position]] = []
    scores: list[int] = []
    states: list[GameState] = []
    foods: list[Position | None] = []
    clock = Mock()
    clock.tick.side_effect = [125, 2000, 5000, 124, 1]
    create_game = application.Game
    draw_snake = application.render_snake
    draw_score = application.render_score

    def choice(available: list[Position]) -> Position:
        position = next(placements)
        assert position in available
        return position

    def make_game(rng: Random) -> Game:
        game = create_game(rng=rng)
        games.append(game)
        return game

    def render_snake(
        screen: pygame.Surface, body: list[Position], layout: GameLayout
    ) -> None:
        bodies.append(body.copy())
        foods.append(games[0].food)
        states.append(games[0].state)
        draw_snake(screen, body, layout)

    def render_score(
        screen: pygame.Surface,
        font: pygame.font.Font,
        score: int,
        layout: GameLayout,
    ) -> None:
        before = pygame.image.tobytes(screen, "RGB")
        draw_score(screen, font, score, layout)
        assert pygame.image.tobytes(screen, "RGB") != before
        assert games[0].score == score
        scores.append(score)

    feedback = Mock(wraps=application.render_game_over)
    monkeypatch.setattr(rng, "choice", choice)
    monkeypatch.setattr(application, "Random", lambda: rng)
    monkeypatch.setattr(application, "Game", make_game)
    monkeypatch.setattr(application, "render_snake", render_snake)
    monkeypatch.setattr(application, "render_score", render_score)
    monkeypatch.setattr(application, "render_game_over", feedback)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert len(games) == 1
    assert scores == [1, 1, 0, 0, 0]
    assert states == [
        GameState.RUNNING,
        GameState.GAME_OVER,
        GameState.RUNNING,
        GameState.RUNNING,
        GameState.RUNNING,
    ]
    assert bodies[0] == [
        Position(17, 12),
        Position(16, 12),
        Position(15, 12),
        Position(14, 12),
    ]
    assert bodies[1] == [
        Position(32, 12),
        Position(31, 12),
        Position(30, 12),
        Position(29, 12),
    ]
    assert (
        bodies[2] == bodies[3] == [Position(16, 12), Position(15, 12), Position(14, 12)]
    )
    assert bodies[4] == [Position(17, 12), Position(16, 12), Position(15, 12)]
    assert foods == [
        Position(0, 0),
        Position(0, 0),
        Position(0, 1),
        Position(0, 1),
        Position(0, 1),
    ]
    assert games[0].accumulated_ms == 0
    assert games[0].snake.direction is Direction.RIGHT
    assert games[0].snake.requested_direction is None
    assert feedback.call_count == 1
    assert not pygame.get_init()

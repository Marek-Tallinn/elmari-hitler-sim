import os
import time

import pygame
from ffpyplayer.player import MediaPlayer


def _play_video(screen, game_settings, video_path, min_skip_delay=0.0):
    if not os.path.exists(video_path):
        return

    player = MediaPlayer(video_path, ff_opts={"sync": "audio"})
    clock = pygame.time.Clock()
    target_size = (game_settings.screen_width, game_settings.screen_height)
    start_ts = time.time()
    allow_skip_at = start_ts + max(0.0, min_skip_delay)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    player.close_player()
                    pygame.event.post(event)
                    return
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    if time.time() < allow_skip_at:
                        continue
                    player.close_player()
                    pygame.event.clear()
                    return

            frame, val = player.get_frame()
            if val == "eof":
                break
            if frame is None:
                clock.tick(120)
                continue

            img, pts = frame
            if pts is not None:
                target_time = start_ts + pts
                delay = target_time - time.time()
                if delay > 0:
                    time.sleep(delay)

            w, h = img.get_size()
            data = img.to_bytearray()[0]

            surface = pygame.image.frombuffer(data, (w, h), "RGB")
            if (w, h) != target_size:
                surface = pygame.transform.smoothscale(surface, target_size)

            screen.blit(surface, (0, 0))
            pygame.display.flip()
            clock.tick(120)
    finally:
        player.close_player()
        pygame.event.clear()


def play_intro(screen, game_settings, video_path="intro.mp4"):
    """Play the intro video fullscreen until it ends or the user skips."""
    _play_video(screen, game_settings, video_path, min_skip_delay=3.0)


def play_boss_intro(screen, game_settings, video_path="intro_2.mp4"):
    """Play the second boss intro video if available."""
    _play_video(screen, game_settings, video_path, min_skip_delay=3.0)

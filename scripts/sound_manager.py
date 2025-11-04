# sound_manager.py (reemplaza todo el archivo con esto)
import pygame
import os
import array
import math
import sys

class SoundManager:
    """Gestor centralizado de sonidos y música (con debug)."""

    def __init__(self, asset_path="assets"):
        # No forzamos init si ya está hecho, pero intentamos iniciarlo de forma segura
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[SoundManager] Error inicializando mixer: {e}", file=sys.stderr)

        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.5
        self.asset_path = asset_path
        self.current_music = None

        try:
            # Asegurar suficientes canales
            pygame.mixer.set_num_channels(16)
        except Exception as e:
            print(f"[SoundManager] Error set_num_channels: {e}", file=sys.stderr)

        self.load_sounds()

    def load_sounds(self):
        """Carga sonidos desde assets/sounds si existen (no obligatorios)."""
        sound_files = {
            "shoot": "assets/sound/shoot.wav",
            "enemy_shoot": "sounds/enemy_shoot.wav",
            "explosion": "sounds/explosion.wav",
            "hit": "sounds/hit.wav",
        }

        for name, rel_path in sound_files.items():
            full_path = os.path.join(self.asset_path, rel_path)
            if os.path.exists(full_path):
                try:
                    snd = pygame.mixer.Sound(full_path)
                    snd.set_volume(self.sfx_volume)
                    self.sounds[name] = snd
                    print(f"[SoundManager] Cargado: {full_path}")
                except Exception as e:
                    print(f"[SoundManager] Error cargando {full_path}: {e}", file=sys.stderr)
            else:
                # no existe: no es un error, usaremos beep generado en play_sound
                print(f"[SoundManager] No encontrado (usará beep): {full_path}")

    def create_beep_sound(self, frequency=440, duration_ms=100, volume=0.5, sample_rate=44100):
        """Crea un Sound usando PCM 16-bit stereo y pygame.mixer.Sound(buffer=...)."""
        try:
            frames = int(sample_rate * (duration_ms / 1000.0))
            max_amp = int(32767 * volume)
            arr = array.array('h')  # signed short

            for i in range(frames):
                t = i / sample_rate
                sample = int(max_amp * math.sin(2 * math.pi * frequency * t))
                # stereo: duplicar sample (L,R)
                arr.append(sample)
                arr.append(sample)

            # convertir a bytes y crear Sound
            sound = pygame.mixer.Sound(buffer=arr.tobytes())
            return sound
        except Exception as e:
            print(f"[SoundManager] create_beep_sound error: {e}", file=sys.stderr)
            return None

    def play_sound(self, sound_name):
        """Reproduce un sonido, ya sea archivo cargado o beep generado."""
        try:
            if sound_name not in self.sounds:
                # Generar beeps por defecto si no hay archivo
                if sound_name == "shoot":
                    s = self.create_beep_sound(800, 50, volume=0.4)
                elif sound_name == "enemy_shoot":
                    s = self.create_beep_sound(600, 80, volume=0.4)
                elif sound_name == "explosion":
                    s = self.create_beep_sound(200, 200, volume=0.6)
                elif sound_name == "hit":
                    s = self.create_beep_sound(300, 120, volume=0.6)
                else:
                    print(f"[SoundManager] play_sound: sonido desconocido '{sound_name}'", file=sys.stderr)
                    return

                if s:
                    self.sounds[sound_name] = s
                else:
                    print(f"[SoundManager] No se pudo crear beep para '{sound_name}'", file=sys.stderr)
                    return

            # Reproducir usando find_channel o Sound.play()
            try:
                channel = pygame.mixer.find_channel()
                if channel:
                    channel.set_volume(self.sfx_volume)
                    channel.play(self.sounds[sound_name])
                else:
                    # sin canal disponible, usar play directo (pygame manejará)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                    self.sounds[sound_name].play()
            except Exception as e:
                print(f"[SoundManager] Error al reproducir '{sound_name}': {e}", file=sys.stderr)

        except Exception as e:
            print(f"[SoundManager] Error general en play_sound('{sound_name}'): {e}", file=sys.stderr)

    def play_music(self, music_name):
        """Reproduce música de fondo (si hay archivo -> assets/music/)."""
        try:
            music_path = os.path.join(self.asset_path, "music", music_name)
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # loop
                self.current_music = music_name
                print(f"[SoundManager] Reproduciendo música: {music_path}")
            else:
                print(f"[SoundManager] No se encontró música: {music_path}")
        except Exception as e:
            print(f"[SoundManager] play_music error: {e}", file=sys.stderr)

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"[SoundManager] stop_music error: {e}", file=sys.stderr)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        # actualizar volúmenes de sonidos ya cargados
        for s in self.sounds.values():
            try:
                s.set_volume(self.sfx_volume)
            except:
                pass

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception as e:
            print(f"[SoundManager] set_music_volume error: {e}", file=sys.stderr)

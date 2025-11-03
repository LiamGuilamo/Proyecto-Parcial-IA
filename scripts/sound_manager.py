# Sistema de gestión de sonidos y música
import pygame
import os

class SoundManager:
    """Gestor centralizado de sonidos y música"""
    
    def __init__(self, asset_path="assets"):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.5
        self.asset_path = asset_path
        self.current_music = None
        self.load_sounds()
    
    def load_sounds(self):
        """Carga todos los sonidos disponibles"""
        # Los sonidos se cargarán bajo demanda
        pass
    
    def create_beep_sound(self, frequency=440, duration=100):
        """Crea un sonido de beep simple sin archivos externos"""
        sample_rate = 22050
        frames = int(duration * sample_rate / 1000)
        
        # Generar onda senoidal
        import math
        sound_data = []
        for i in range(frames):
            phase = 2 * math.pi * frequency * i / sample_rate
            sample = int(32767 * 0.3 * math.sin(phase))
            sound_data.append(sample)
            sound_data.append(sample)
        
        import array
        arr = array.array('h', sound_data)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def play_sound(self, sound_name):
        """Reproduce un sonido"""
        try:
            if sound_name not in self.sounds:
                # Crear sonidos programáticamente
                if sound_name == "shoot":
                    self.sounds[sound_name] = self.create_beep_sound(800, 50)
                elif sound_name == "enemy_shoot":
                    self.sounds[sound_name] = self.create_beep_sound(600, 100)
                elif sound_name == "explosion":
                    self.sounds[sound_name] = self.create_beep_sound(200, 150)
                elif sound_name == "hit":
                    self.sounds[sound_name] = self.create_beep_sound(300, 200)
                else:
                    return
            
            channel = pygame.mixer.find_channel()
            if channel:
                channel.set_volume(self.sfx_volume)
                channel.play(self.sounds[sound_name])
        except:
            pass
    
    def play_music(self, music_name):
        """Reproduce música de fondo"""
        try:
            # En lugar de cargar archivos, generar música proceduralmente
            # Para el proyecto actual, simplemente no reproducimos música
            # Pero esta estructura permite agregar archivos de audio
            pass
        except:
            pass
    
    def stop_music(self):
        """Detiene la música actual"""
        try:
            pygame.mixer.music.stop()
        except:
            pass
    
    def set_sfx_volume(self, volume):
        """Ajusta el volumen de efectos de sonido (0.0 a 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """Ajusta el volumen de música (0.0 a 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass

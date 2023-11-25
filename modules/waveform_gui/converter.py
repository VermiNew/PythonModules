import os
from moviepy.editor import VideoFileClip

def convert_mp4_files_to_wav(input_folder, output_folder):
    # Upewnij się, że output_folder istnieje
    os.makedirs(output_folder, exist_ok=True)

    # Pętla przez wszystkie pliki w folderze input_folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_path = os.path.join(input_folder, filename)
            
            # Tworzymy nazwę pliku WAV, zamieniając rozszerzenie na ".wav"
            output_filename = os.path.splitext(filename)[0] + ".wav"
            output_path = os.path.join(output_folder, output_filename)

            # Wczytaj plik mp4
            clip = VideoFileClip(input_path)

            # Wyodrębnij ścieżkę dźwiękową
            audio = clip.audio

            # Zapisz plik wav
            audio.write_audiofile(output_path, codec='pcm_s16le', ffmpeg_params=['-ac', '2'])

# Przykład użycia
input_folder = "./mp4"
output_folder = "./wav"

convert_mp4_files_to_wav(input_folder, output_folder)

import os
import sys
import subprocess
import glob
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import imageio_ffmpeg

# Set up local .env path relative to this script
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Get FFmpeg path dynamically
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def extract_audio(video_path: Path, output_mp3: Path, duration_limit=None):
    """Extracts audio from video file using FFmpeg, optionally limited to duration_limit seconds."""
    print(f"-> Extraindo áudio do vídeo: {video_path.name}")
    cmd = [FFMPEG_EXE, "-y"]
    if duration_limit:
        cmd.extend(["-to", str(duration_limit)])
    
    cmd.extend([
        "-i", str(video_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "16000",
        "-ac", "1",
        "-ab", "64k",
        str(output_mp3)
    ])
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Erro no FFmpeg:")
        print(result.stderr)
        raise RuntimeError("Falha ao extrair áudio com o FFmpeg.")
    print(f"-> Áudio extraído com sucesso: {output_mp3.name} ({os.path.getsize(output_mp3) / 1024 / 1024:.2f} MB)")

def split_audio(audio_path: Path, chunk_pattern: str, segment_time_seconds=900):
    """Splits large audio file into segments to respect the API limits."""
    print(f"-> Dividindo o áudio em partes de {segment_time_seconds // 60} minutos...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", str(audio_path),
        "-f", "segment",
        "-segment_time", str(segment_time_seconds),
        "-c", "copy",
        chunk_pattern
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Erro no FFmpeg ao dividir áudio:")
        print(result.stderr)
        raise RuntimeError("Falha ao dividir áudio com o FFmpeg.")
    
    chunks = sorted(glob.glob(chunk_pattern.replace("%03d", "*")))
    print(f"-> Áudio dividido em {len(chunks)} partes.")
    return chunks

def transcribe_chunk(client: OpenAI, chunk_path: str, lang: str):
    """Transcribes a single audio chunk using OpenAI Whisper API."""
    print(f"-> Transcrevendo parte: {os.path.basename(chunk_path)} (Idioma: {lang})...")
    with open(chunk_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=lang
        )
    return transcription.text

def main():
    parser = argparse.ArgumentParser(description="Whisper Video Transcriber CLI - Automate transcription of large video files via OpenAI Whisper API.")
    parser.add_argument("-v", "--video", required=True, type=str, help="Caminho do arquivo de vídeo ou áudio de entrada.")
    parser.add_argument("-o", "--output", type=str, default=".", help="Caminho do arquivo ou diretório de saída para a transcrição. Padrão: diretório atual.")
    parser.add_argument("-l", "--lang", type=str, default="pt", help="Código de idioma da transcrição (ex: pt, en, es). Padrão: pt.")
    parser.add_argument("-t", "--test", action="store_true", help="Modo Teste: extrai e transcreve apenas os primeiros 30 segundos do vídeo.")
    
    args = parser.parse_args()

    # Verify OpenAI API Key
    global OPENAI_API_KEY
    if not OPENAI_API_KEY or OPENAI_API_KEY == "coloque_sua_chave_aqui":
        print("[ERRO] Chave de API da OpenAI não encontrada ou configurada incorretamente no arquivo .env!")
        print("Por favor, configure a variável OPENAI_API_KEY no arquivo .env.")
        sys.exit(1)

    # Initialize OpenAI Client
    client = OpenAI(api_key=OPENAI_API_KEY)

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"[ERRO] O arquivo de entrada não existe: {video_path}")
        sys.exit(1)

    output_path = Path(args.output)
    # Determine output file path
    if output_path.is_dir() or args.output == ".":
        output_file = output_path / f"{video_path.stem}-transcricao.txt"
    else:
        output_file = output_path
        # Ensure parent directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

    print("=== INICIANDO PIPELINE DE TRANSCRIÇÃO ===")
    print(f"Vídeo de Entrada: {video_path.name}")
    print(f"Destino da Transcrição: {output_file.resolve()}")
    print(f"Idioma: {args.lang}")
    
    if args.test:
        print("[MODO TESTE ATIVADO] Será transcrito apenas os primeiros 30 segundos do vídeo.")
        temp_audio = Path("test_audio.mp3")
        
        try:
            # 1. Extract first 30 seconds
            extract_audio(video_path, temp_audio, duration_limit=30)
            
            # 2. Transcribe
            text = transcribe_chunk(client, str(temp_audio), args.lang)
            
            # 3. Print test results
            print("\n--- Resultado do Teste ---")
            print(text)
            print("--------------------------\n")
            print("Teste concluído com sucesso!")
            
        except Exception as e:
            print(f"[ERRO] Ocorreu uma falha no teste: {e}")
            sys.exit(1)
        finally:
            if temp_audio.exists():
                os.remove(temp_audio)
    else:
        temp_audio = Path("full_audio.mp3")
        chunk_pattern = "chunk_%03d.mp3"
        chunks = []
        
        try:
            # 1. Extract audio
            extract_audio(video_path, temp_audio)
            
            # 2. Split audio into 15-minute segments (900 seconds)
            chunks = split_audio(temp_audio, chunk_pattern, segment_time_seconds=900)
            
            # 3. Transcribe each segment
            full_transcript = []
            for idx, chunk in enumerate(chunks):
                print(f"\n[Progresso: {idx + 1}/{len(chunks)}]")
                text = transcribe_chunk(client, chunk, args.lang)
                full_transcript.append(text)
            
            # 4. Consolidate and save
            final_text = "\n\n".join(full_transcript)
            output_file.write_text(final_text, encoding="utf-8")
            
            print(f"\n=== SUCESSO! ===")
            print(f"Transcrição completa salva em: {output_file.resolve()}")
            
        except Exception as e:
            print(f"[ERRO] Ocorreu uma falha na transcrição: {e}")
            sys.exit(1)
        finally:
            # Cleanup temporary files
            if temp_audio.exists():
                try:
                    os.remove(temp_audio)
                except:
                    pass
            for chunk in chunks:
                if os.path.exists(chunk):
                    try:
                        os.remove(chunk)
                    except:
                        pass

if __name__ == "__main__":
    main()

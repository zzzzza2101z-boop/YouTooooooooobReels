import os, subprocess
from pathlib import Path

def download_youtube(url, out_dir):
    out_file = os.path.join(out_dir, 'source.mp4')
    cmd = ['yt-dlp', '-f', 'bestvideo+bestaudio/best', '-o', out_file, url]
    subprocess.run(cmd, check=True)
    return out_file

def extract_audio(video_path, out_dir):
    audio_path = os.path.join(out_dir, 'audio.wav')
    cmd = ['ffmpeg', '-y', '-i', video_path, '-ac', '1', '-ar', '16000', audio_path]
    subprocess.run(cmd, check=True)
    return audio_path

def transcribe_audio(audio_path, out_dir):
    import openai, io
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    with open(audio_path, 'rb') as f:
        res = openai.Audio.transcriptions.create(file=f, model='whisper-1')
    text = res.get('text', '')
    txt_path = os.path.join(out_dir, 'transcript.txt')
    with open(txt_path, 'w', encoding='utf-8') as o:
        o.write(text)
    return txt_path, text

def detect_scenes(video_path):
    import ffmpeg
    probe = ffmpeg.probe(video_path)
    duration = float(probe['format']['duration'])
    scenes = []
    step = max(5, int(duration // 12))
    t = 0
    while t < duration:
        start = t
        end = min(t + step, duration)
        scenes.append({'start': start, 'end': end})
        t += step
    return scenes

def cut_clips(video_path, scenes, out_dir):
    list_file = os.path.join(out_dir, 'list.txt')
    with open(list_file, 'w') as L:
        for i, s in enumerate(scenes):
            out = os.path.join(out_dir, f'clip_{i}.mp4')
            cmd = ['ffmpeg','-y','-ss', str(s['start']), '-to', str(s['end']), '-i', video_path, '-c','copy', out]
            subprocess.run(cmd, check=True)
            L.write(f"file '{out}'\n")
    return [os.path.join(out_dir, f'clip_{i}.mp4') for i in range(len(scenes))]

def burn_subtitles(reel_path, transcript_path, out_dir):
    srt_path = os.path.join(out_dir, 'captions.srt')
    with open(transcript_path, 'r', encoding='utf-8') as f:
        text = f.read()
    words = text.split()
    chunks = []
    per_chunk = 12
    for i in range(0, len(words), per_chunk):
        chunk = ' '.join(words[i:i+per_chunk])
        chunks.append(chunk)
    with open(srt_path, 'w', encoding='utf-8') as s:
        t0 = 0
        for i, c in enumerate(chunks):
            t1 = t0 + 4
            s.write(f"{i+1}\n")
            s.write(f"00:00:{t0:02d},000 --> 00:00:{t1:02d},000\n")
            s.write(c + '\n\n')
            t0 = t1
    out = os.path.join(out_dir, 'reel_subtitled.mp4')
    cmd = ['ffmpeg', '-y', '-i', reel_path, '-vf', f"subtitles={srt_path}:force_style='FontName=Arial,Fontsize=24'", out]
    subprocess.run(cmd, check=True)
    return out

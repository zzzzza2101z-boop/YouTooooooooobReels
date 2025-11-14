from flask import Flask, request, jsonify, send_file
import os, subprocess, uuid
from utils import download_youtube, extract_audio, transcribe_audio, detect_scenes, cut_clips, burn_subtitles

app = Flask(__name__)
UPLOADS = 'work'
os.makedirs(UPLOADS, exist_ok=True)

PRIVATE_PASSWORD = os.environ.get('PRIVATE_PASSWORD', 'changeme')

@app.route('/api/process', methods=['POST'])
def process():
    data = request.json
    password = data.get('password')
    if password != PRIVATE_PASSWORD:
        return jsonify({'error':'unauthorized'}), 401

    youtube_url = data.get('youtube')
    job_id = str(uuid.uuid4())
    out_dir = os.path.join(UPLOADS, job_id)
    os.makedirs(out_dir, exist_ok=True)

    source_path = None
    if youtube_url:
        source_path = download_youtube(youtube_url, out_dir)
    else:
        return jsonify({'error':'no source provided'}), 400

    audio_path = extract_audio(source_path, out_dir)
    transcript_path, transcript_text = transcribe_audio(audio_path, out_dir)
    scenes = detect_scenes(source_path)
    highlights = scenes[:6]
    clips = cut_clips(source_path, highlights, out_dir)

    reel_path = os.path.join(out_dir, 'reel.mp4')
    concat_file = os.path.join(out_dir, 'list.txt')
    cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', reel_path]
    subprocess.run(cmd, check=True)

    subtitled = burn_subtitles(reel_path, transcript_path, out_dir)

    return jsonify({'job_id': job_id, 'reel': f'/api/download/{job_id}/reel'})

@app.route('/api/download/<job_id>/reel')
def download_reel(job_id):
    path = os.path.join(UPLOADS, job_id, 'reel_subtitled.mp4')
    if not os.path.exists(path):
        return jsonify({'error':'not found'}), 404
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

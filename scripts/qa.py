"""Control de calidad técnico del video final.

Uso: python3 scripts/qa.py [--sheets]
Comprueba formato, duración, fps, decodificación completa sin errores, tramos negros y congelados,
sonoridad del audio, y (con --sheets) genera hojas de contacto cada 2 s en build/qa/.
"""
import os
import re
import sys
import json
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scenes.meta import timeline  # noqa: E402

VIDEO = os.path.join(ROOT, 'output', 'kentukis_emilia_video_final.mp4')


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    rep = []
    pr = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', VIDEO]).stdout)
    v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]
    a = [s for s in pr['streams'] if s['codec_type'] == 'audio']
    dur = float(pr['format']['duration'])
    rep.append('archivo: %s (%.1f MB)' % (os.path.relpath(VIDEO, ROOT), os.path.getsize(VIDEO) / 1e6))
    rep.append('duración: %.2f s (%d:%05.2f)' % (dur, dur // 60, dur % 60))
    rep.append('video: %s %s, %sx%s, %s fps (avg %s), pix_fmt %s, %s fotogramas' % (
        v['codec_name'], v.get('profile'), v['width'], v['height'], v['r_frame_rate'], v['avg_frame_rate'],
        v['pix_fmt'], v.get('nb_frames')))
    if a:
        rep.append('audio: %s, %s Hz, %s canales, %.0f kb/s' % (a[0]['codec_name'], a[0]['sample_rate'], a[0]['channels'],
                                                                int(a[0].get('bit_rate', 0)) / 1000))
    # decodificación completa
    d = run(['ffmpeg', '-v', 'error', '-i', VIDEO, '-f', 'null', '-'])
    rep.append('decodificación completa: %s' % ('sin errores' if not d.stderr.strip() else d.stderr.strip()[:500]))
    # negros y congelados
    bd = run(['ffmpeg', '-i', VIDEO, '-vf', 'blackdetect=d=0.4:pix_th=0.08', '-an', '-f', 'null', '-'])
    blacks = re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', bd.stderr)
    rep.append('tramos negros (≥0,4 s): ' + (', '.join('%s–%s' % b for b in blacks) or 'ninguno'))
    fd = run(['ffmpeg', '-i', VIDEO, '-vf', 'freezedetect=n=0.0005:d=1.5', '-an', '-f', 'null', '-'])
    fr = re.findall(r'freeze_start: ([\d.]+).*?freeze_duration: ([\d.]+)', fd.stderr, re.S)
    rep.append('imágenes congeladas (≥1,5 s): ' + (', '.join('%s (+%s s)' % f for f in fr) or 'ninguna'))
    # sonoridad
    lo = run(['ffmpeg', '-i', VIDEO, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    m = re.search(r'Integrated loudness:\s+I:\s+([-\d.]+) LUFS.*?LRA:\s+([-\d.]+) LU.*?True peak:\s+Peak:\s+([-\d.]+) dBFS',
                  lo.stderr, re.S)
    if m:
        rep.append('audio: sonoridad integrada %s LUFS, rango %s LU, pico verdadero %s dBFS' % m.groups())
    print('\n'.join(rep))
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    open(os.path.join(ROOT, 'build', 'qa_report.txt'), 'w').write('\n'.join(rep) + '\n')
    if '--sheets' in sys.argv:
        sheets(dur)


def sheets(dur, step=2.0, per=24):
    from PIL import Image, ImageDraw
    out = os.path.join(ROOT, 'build', 'qa')
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, 'f')
    os.makedirs(tmp, exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', VIDEO, '-vf', 'fps=1/%g,scale=320:180' % step,
                    os.path.join(tmp, 'f_%04d.png')], check=True)
    files = sorted(os.listdir(tmp))
    for p in range(0, len(files), per):
        im = Image.new('RGB', (320 * 6, 180 * 4), (0, 0, 0))
        for k, f in enumerate(files[p:p + per]):
            fr = Image.open(os.path.join(tmp, f)).convert('RGB')
            dr = ImageDraw.Draw(fr)
            dr.text((4, 2), '%.0fs' % ((p + k) * step), fill=(255, 255, 0))
            im.paste(fr, ((k % 6) * 320, (k // 6) * 180))
        im.save(os.path.join(out, 'hoja_%02d.png' % (p // per)))
    print('hojas de contacto en', out)


if __name__ == '__main__':
    main()

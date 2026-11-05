"""動画に読み上げ音声と BGM を入れる（すべて無料・オフライン）。

- 読み上げ：Open JTalk（pyopenjtalk-plus。pip で入る。声のデータは同梱）
- BGM：このファイルで和音とリズムを合成して作る（素材を使わないので権利の心配がない）

使い方（動画を作ったあと）:
  from tools.audio import add_voice_and_bgm
  add_voice_and_bgm("out/xxx.mp4", [(0.1, "読み上げる文"), (3.0, "次の文"), ...])
文は読み間違いを防ぐため、数字や「1人」はひらがなで書く（例：ひとり、ななわり）。
文が重なるときは、前の文の終わりから0.15秒あけて後ろにずらす。動画より音声が長くなったら、最後の画面をのばす。
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 48000


def _write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def narrate(lines, speed=1.3, half_tone=1.0):
    """[(開始秒, 文), ...] ➔ (音声の配列, 長さ秒)。重なりは後ろにずらす。"""
    import pyopenjtalk
    clips, t_end = [], 0.0
    for start, text in lines:
        x, sr = pyopenjtalk.tts(text, speed=speed, half_tone=half_tone)
        x = x.astype(np.float32) / 32768.0
        if sr != SR:
            x = np.interp(np.linspace(0, len(x), int(len(x) * SR / sr), endpoint=False), np.arange(len(x)), x)
        start = max(start, t_end + 0.15)
        clips.append((start, x)); t_end = start + len(x) / SR
    out = np.zeros(int((t_end + 0.3) * SR), dtype=np.float32)
    for start, x in clips:
        i = int(start * SR); out[i:i + len(x)] += x
    peak = np.abs(out).max() or 1
    return out / peak * 0.9, t_end


def bgm(seconds, bpm=118, seed=7):
    """明るいポップ調の BGM（I–V–vi–IV の和音＋分散和音＋軽いリズム）。"""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR); t = np.arange(n) / SR
    beat = 60 / bpm; bar = beat * 4
    root = {"C": 261.63, "G": 196.00, "Am": 220.00, "F": 174.61}
    chords = [("C", [0, 4, 7]), ("G", [0, 4, 7]), ("Am", [0, 3, 7]), ("F", [0, 4, 7])]
    out = np.zeros(n, dtype=np.float32)

    def tone(f, length, decay, harm=(1, .5, .25)):
        tt = np.arange(int(length * SR)) / SR
        w = sum(a * np.sin(2 * np.pi * f * k * tt) for k, a in enumerate(harm, 1))
        env = np.minimum(1, tt / 0.01) * np.exp(-tt / decay)
        return (w * env).astype(np.float32)

    for b in range(int(seconds / bar) + 1):
        name, iv = chords[b % 4]; f0 = root[name]; t0 = b * bar
        for k in iv:  # パッド（やわらかい和音）
            seg = tone(f0 * 2 ** (k / 12), bar, 1.2, harm=(1, .3)) * 0.10
            i = int(t0 * SR); out[i:i + len(seg)] += seg[:max(0, n - i)]
        for s in range(8):  # 8分音符の分散和音
            k = iv[s % 3] + (12 if s % 4 == 3 else 0)
            seg = tone(f0 * 2 * 2 ** (k / 12), beat / 2, 0.18) * 0.08
            i = int((t0 + s * beat / 2) * SR); out[i:i + len(seg)] += seg[:max(0, n - i)]
        bass = tone(f0 / 2, bar, 0.9, harm=(1, .2)) * 0.16
        i = int(t0 * SR); out[i:i + len(bass)] += bass[:max(0, n - i)]
        for q in range(4):  # キック（1・3拍）とハイハット（裏拍）
            i = int((t0 + q * beat) * SR)
            if q % 2 == 0:
                kt = np.arange(int(0.25 * SR)) / SR
                kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt / 0.03)) * kt) * np.exp(-kt / 0.09) * 0.35
                out[i:i + len(kick)] += kick[:max(0, n - i)]
            j = int((t0 + (q + .5) * beat) * SR)
            hat = rng.standard_normal(int(0.04 * SR)) * np.exp(-np.arange(int(0.04 * SR)) / SR / 0.01) * 0.04
            out[j:j + len(hat)] += hat[:max(0, n - j)]
    fade = np.ones(n); f = int(1.0 * SR)
    fade[:f] = np.linspace(0, 1, f); fade[-f:] = np.linspace(1, 0, f)
    out *= fade
    return out / (np.abs(out).max() or 1) * 0.9


def add_voice_and_bgm(video, lines, bgm_level=0.22, out=None, speed=1.3):
    """動画に読み上げと BGM を入れた版を書き出す（元の動画はそのまま）。"""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    voice, v_end = narrate(lines, speed=speed)
    total = max(dur, v_end + 0.8)
    mix = bgm(total) * bgm_level
    duck = np.ones(len(mix), dtype=np.float32)  # 声が出ている間は BGM を少し下げる
    env = np.convolve(np.abs(voice) > 0.02, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")[:len(mix)]
    duck[:len(env)] -= 0.45 * np.clip(env * 4, 0, 1)
    mix *= duck
    mix[:len(voice)] += voice[:len(mix)]
    out = out or video.replace(".mp4", "_音声BGM.mp4")
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav"); _write(wav, mix / (np.abs(mix).max() or 1) * 0.95)
        pad = max(0.0, total - dur)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav,
                        "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={pad:.2f}[v]",
                        "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                       check=True)
    return out

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


# 音楽制作AI（No.33）が選ぶ雰囲気。和音の進行・速さ・調をそれぞれ変える（すべて自作の音なので無料・権利の心配なし）
MOODS = {
    "pop":    dict(bpm=118, prog=["C", "G", "Am", "F"]),    # いつもの明るいポップ（今までのBGM）
    "happy":  dict(bpm=128, prog=["F", "G", "Em", "Am"]),   # わくわく：告知・当日募集
    "gentle": dict(bpm=96,  prog=["C", "Am", "F", "G"]),    # やさしい：Q&A・1人参加の安心材料
    "fresh":  dict(bpm=110, prog=["G", "D", "Em", "C"]),    # さわやか：振り返り・レポート
    # v3.0（11/11）：垢抜けた空気感。7th・9th の和音、スウィング、テープの揺れ、ノイズで「打ち込みっぽさ」を消す
    "citypop": dict(bpm=104, prog=["F", "Em", "Am", "G"], ext=[0, 4, 7, 11], swing=.08, wow=.003),  # シティポップ：告知・夜の雰囲気
    "lofi":    dict(bpm=82,  prog=["F", "Em", "Am", "C"], ext=[0, 4, 7, 11], swing=.16, wow=.006, noise=.012, lp=.6),  # ローファイ：Q&A・落ち着き
    "ambient": dict(bpm=70,  prog=["C", "Am", "F", "G"], ext=[0, 7, 14], drums=False, noise=.004, lp=.5),  # アンビエント：余韻・振り返り
    "indie":   dict(bpm=138, prog=["C", "G", "Am", "F"], ext=[0, 7, 12], swing=.03, drive=1.6),  # インディーロック：当日募集・勢い
}
_ROOT = {"C": 261.63, "D": 293.66, "Em": 329.63, "F": 174.61, "G": 196.00, "Am": 220.00}


def bgm(seconds, bpm=None, seed=7, mood="pop", rests=()):
    """自作の BGM。mood で雰囲気（pop／happy／gentle／fresh／citypop／lofi／ambient／indie）、seed で曲の番号を変える。
    rests=[(開始秒, 終了秒), ...] の間は音を抜く（「間」の演出。前後0.15秒でなめらかに）。"""
    m = MOODS.get(mood, MOODS["pop"]); bpm = bpm or m["bpm"]
    rng = np.random.default_rng(seed)
    n = int(seconds * SR); t = np.arange(n) / SR
    beat = 60 / bpm; bar = beat * 4
    vary = mood != "pop"  # pop は今までと同じ音のまま。ほかの雰囲気は seed ごとに調と進行の始まりを変える
    shift = 2 ** (int(np.random.default_rng(seed + 100).integers(-2, 3)) / 12) if vary else 1
    root = {k: v * shift for k, v in _ROOT.items()}
    def _iv(c):
        if "ext" in m:  # 7th などの響き（短調は3度を下げる）
            return [k - 1 if c.endswith("m") and k in (4, 11) else k for k in m["ext"]]
        return [0, 3, 7] if c.endswith("m") else [0, 4, 7]
    chords = [(c, _iv(c)) for c in m["prog"]]
    if vary and seed % 2: chords = chords[2:] + chords[:2]
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
            k = iv[s % len(iv)] + (12 if s % 4 == 3 else 0)
            seg = tone(f0 * 2 * 2 ** (k / 12), beat / 2, 0.18) * 0.08
            sw = m.get("swing", 0) * beat if s % 2 else 0  # 裏の8分を少し遅らせる（人が弾いた揺れ）
            i = int((t0 + s * beat / 2 + sw) * SR); out[i:i + len(seg)] += seg[:max(0, n - i)]
        bass = tone(f0 / 2, bar, 0.9, harm=(1, .2)) * 0.16
        i = int(t0 * SR); out[i:i + len(bass)] += bass[:max(0, n - i)]
        for q in (range(4) if m.get("drums", True) else ()):  # キック（1・3拍）とハイハット（裏拍）
            i = int((t0 + q * beat) * SR)
            if q % 2 == 0:
                kt = np.arange(int(0.25 * SR)) / SR
                kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt / 0.03)) * kt) * np.exp(-kt / 0.09) * 0.35
                out[i:i + len(kick)] += kick[:max(0, n - i)]
            j = int((t0 + (q + .5 + m.get("swing", 0)) * beat) * SR)
            hat = rng.standard_normal(int(0.04 * SR)) * np.exp(-np.arange(int(0.04 * SR)) / SR / 0.01) * 0.04
            out[j:j + len(hat)] += hat[:max(0, n - j)]
    if "drive" in m:  # ギターのような歪み（インディー）
        out = np.tanh(out * m["drive"] / (np.abs(out).max() or 1)).astype(np.float32)
    if "lp" in m:  # こもった音（ローファイ・アンビエント）：移動平均で高い音を落とす（numpy だけで動く）
        w = max(2, int(m["lp"] * 20)); c = np.cumsum(np.concatenate([[0], out]))
        out = ((c[w:] - c[:-w]) / w).astype(np.float32); out = np.concatenate([out, np.zeros(n - len(out), np.float32)])
    if "wow" in m:  # テープの揺れ（音量がゆっくり波打つ）
        out *= (1 + m["wow"] * 10 * np.sin(2 * np.pi * 0.7 * t)).astype(np.float32)
    if "noise" in m:  # レコードのサーッという音とプチッという音
        out += (rng.standard_normal(n) * m["noise"]).astype(np.float32)
        for c in rng.integers(0, n, size=int(seconds * 3)):
            out[c:c + 40] += (rng.standard_normal(min(40, n - c)) * m["noise"] * 8).astype(np.float32)
    fade = np.ones(n); f = int(1.0 * SR)
    fade[:f] = np.linspace(0, 1, f); fade[-f:] = np.linspace(1, 0, f)
    for a0, a1 in rests:  # 「間」：その区間だけ音を抜く
        i0, i1, r = int(a0 * SR), int(a1 * SR), int(0.15 * SR)
        fade[i0:i1] = 0
        fade[max(0, i0 - r):i0] = np.minimum(fade[max(0, i0 - r):i0], np.linspace(1, 0, i0 - max(0, i0 - r)))
        fade[i1:i1 + r] = np.minimum(fade[i1:i1 + r], np.linspace(0, 1, len(fade[i1:i1 + r])))
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

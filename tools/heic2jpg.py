"""iPhone の HEIC を JPG にする（pillow_heif も libheif の HEVC も無い作業場向け。ffmpeg だけで動く）。
HEIC の中のタイル（HEVC）を1枚ずつ ffmpeg で読み、グリッドに並べて回転を戻す。
使い方: python3 tools/heic2jpg.py 入力.heic 出力.jpg
"""
import io, struct, subprocess, sys
from PIL import Image


def boxes(b, off=0, end=None):
    end = len(b) if end is None else end
    while off + 8 <= end:
        size, typ = struct.unpack(">I4s", b[off:off + 8]); hdr = 8
        if size == 1: size = struct.unpack(">Q", b[off + 8:off + 16])[0]; hdr = 16
        elif size == 0: size = end - off
        yield typ.decode("latin1"), off + hdr, off + size
        off += size


def child(b, s, e, name, full=False):
    s = s + 4 if full else s
    for t, cs, ce in boxes(b, s, e):
        if t == name: return cs, ce
    return None


def parse(b):
    ms, me = child(b, 0, len(b), "meta")
    ms += 4  # meta は FullBox
    sub = {t: (s, e) for t, s, e in boxes(b, ms, me)}
    # pitm
    s, _ = sub["pitm"]; v = b[s]; primary = struct.unpack(">H" if v == 0 else ">I", b[s + 4:s + (6 if v == 0 else 8)])[0]
    # iinf → item type
    s, e = sub["iinf"]; v = b[s]; n = struct.unpack(">H" if v == 0 else ">I", b[s + 4:s + (6 if v == 0 else 8)])[0]
    itype = {}
    for t, cs, ce in boxes(b, s + (6 if v == 0 else 8), e):
        iv = b[cs]; p = cs + 4
        if iv >= 2:
            iid = struct.unpack(">H" if iv == 2 else ">I", b[p:p + (2 if iv == 2 else 4)])[0]; p += 2 if iv == 2 else 4
            p += 2; itype[iid] = b[p:p + 4].decode("latin1")
    # iloc
    s, e = sub["iloc"]; v = b[s]; p = s + 4
    a, c = b[p], b[p + 1]; p += 2
    osz, lsz, bsz, isz = a >> 4, a & 15, c >> 4, (c & 15 if v in (1, 2) else 0)
    cnt = struct.unpack(">H" if v < 2 else ">I", b[p:p + (2 if v < 2 else 4)])[0]; p += 2 if v < 2 else 4
    rd = lambda n, p: (int.from_bytes(b[p:p + n], "big") if n else 0, p + n)
    loc = {}
    for _ in range(cnt):
        iid, p = rd(2 if v < 2 else 4, p)
        cm = 0
        if v in (1, 2): cm = int.from_bytes(b[p:p + 2], "big") & 15; p += 2
        p += 2  # data_reference_index
        base, p = rd(bsz, p)
        ec, p = rd(2, p); data = b""
        for _ in range(ec):
            if v in (1, 2) and isz: _, p = rd(isz, p)
            eo, p = rd(osz, p); el, p = rd(lsz, p)
            src0 = sub["idat"][0] if cm == 1 else 0  # construction_method 1 = idat の中
            data += b[src0 + base + eo:src0 + base + eo + el]
        loc[iid] = data
    # iref dimg
    dimg = {}
    if "iref" in sub:
        s, e = sub["iref"]; v = b[s]
        for t, cs, ce in boxes(b, s + 4, e):
            w = 2 if v == 0 else 4
            frm = int.from_bytes(b[cs:cs + w], "big"); k = int.from_bytes(b[cs + w:cs + w + 2], "big")
            refs = [int.from_bytes(b[cs + w + 2 + i * w:cs + w + 2 + (i + 1) * w], "big") for i in range(k)]
            if t == "dimg": dimg[frm] = refs
    # iprp: ipco と ipma
    s, e = sub["iprp"]; props = [None]
    pc = child(b, s, e, "ipco")
    for t, cs, ce in boxes(b, pc[0], pc[1]): props.append((t, cs, ce))
    assoc = {}
    for t, cs, ce in boxes(b, s, e):
        if t != "ipma": continue
        v, fl = b[cs], int.from_bytes(b[cs + 1:cs + 4], "big"); p = cs + 4
        n = struct.unpack(">I", b[p:p + 4])[0]; p += 4
        for _ in range(n):
            iid = int.from_bytes(b[p:p + (2 if v < 1 else 4)], "big"); p += 2 if v < 1 else 4
            k = b[p]; p += 1; lst = []
            for _ in range(k):
                if fl & 1: idx = int.from_bytes(b[p:p + 2], "big") & 0x7FFF; p += 2
                else: idx = b[p] & 0x7F; p += 1
                lst.append(idx)
            assoc[iid] = lst
    return primary, itype, loc, dimg, props, assoc


def hvcc_to_annexb(b, s, e):
    p = s + 22; n = b[p]; p += 1; out = b""
    for _ in range(n):
        p += 1; k = struct.unpack(">H", b[p:p + 2])[0]; p += 2
        for _ in range(k):
            ln = struct.unpack(">H", b[p:p + 2])[0]; p += 2
            out += b"\0\0\0\1" + b[p:p + ln]; p += ln
    return out


def sample_to_annexb(d):
    out, p = b"", 0
    while p + 4 <= len(d):
        ln = struct.unpack(">I", d[p:p + 4])[0]; out += b"\0\0\0\1" + d[p + 4:p + 4 + ln]; p += 4 + ln
    return out


def decode_item(b, iid, loc, props, assoc):
    hv = next(props[i] for i in assoc[iid] if props[i][0] == "hvcC")
    stream = hvcc_to_annexb(b, hv[1], hv[2]) + sample_to_annexb(loc[iid])
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "hevc", "-i", "-", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       input=stream, capture_output=True, check=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def convert(src, dst):
    b = open(src, "rb").read()
    primary, itype, loc, dimg, props, assoc = parse(b)
    if itype.get(primary) == "grid":
        g = loc[primary]; big = g[1] & 1; rows, cols = g[2] + 1, g[3] + 1
        W, H = (struct.unpack(">II", g[4:12]) if big else struct.unpack(">HH", g[4:8]))
        tiles = [decode_item(b, t, loc, props, assoc) for t in dimg[primary]]
        tw, th = tiles[0].size; img = Image.new("RGB", (cols * tw, rows * th))
        for i, t in enumerate(tiles): img.paste(t, ((i % cols) * tw, (i // cols) * th))
        img = img.crop((0, 0, W, H))
    else:
        img = decode_item(b, primary, loc, props, assoc)
    for i in assoc.get(primary, []):
        t, cs, ce = props[i]
        if t == "irot": img = img.rotate(90 * (b[cs] & 3), expand=True)  # 反時計回り
        if t == "imir": img = img.transpose(Image.FLIP_TOP_BOTTOM if b[cs] & 1 == 0 else Image.FLIP_LEFT_RIGHT)
    img.save(dst, quality=92)


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])

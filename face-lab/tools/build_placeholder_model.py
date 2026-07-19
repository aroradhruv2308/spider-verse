"""Build a procedural parametric head as a stand-in for Google's GNM head model.

Writes the same gnm_web.bin format that face-lab/index.html loads (and that
export_gnm_web.py will produce from real GNM data once available), so the web
app is identical either way — only the data file changes.

The head is a deformed UV sphere. Identity/expression controls are analytic
displacement fields: smooth Gaussian bumps anchored at facial landmarks.

Usage:  python build_placeholder_model.py --out ../model/gnm_web.bin
"""

import argparse
import json
import struct

import numpy as np

LAT, LON = 128, 192  # sphere resolution -> ~24k vertices


def sphere_grid():
    """Unit sphere as a lat/lon grid. Returns (verts [N,3], tris [T,3], units [N,3])."""
    lat = np.linspace(0.004 * np.pi, 0.996 * np.pi, LAT)  # avoid degenerate poles
    lon = np.linspace(-np.pi, np.pi, LON, endpoint=False)
    th, ph = np.meshgrid(lat, lon, indexing="ij")
    units = np.stack([np.sin(th) * np.sin(ph),      # x: left-right
                      np.cos(th),                   # y: up-down
                      np.sin(th) * np.cos(ph)],     # z: back-front (+z = face)
                     axis=-1).reshape(-1, 3)
    idx = np.arange(LAT * LON).reshape(LAT, LON)
    a, b = idx[:-1, :], idx[1:, :]
    c, d = np.roll(idx[:-1, :], -1, axis=1), np.roll(idx[1:, :], -1, axis=1)
    tris = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3),
                           np.stack([c, b, d], -1).reshape(-1, 3)])
    return units.copy(), tris.astype(np.uint32), units


def bump(units, center, sigma):
    """Smooth radial falloff [N] around a landmark direction on the sphere."""
    c = np.asarray(center, float)
    c /= np.linalg.norm(c)
    ang = np.arccos(np.clip(units @ c, -1, 1))
    return np.exp(-0.5 * (ang / sigma) ** 2)


def normals_of(units):
    return units  # for a star-shaped surface, the sphere direction is a fine push axis


def build():
    units, tris, _ = sphere_grid()
    n = normals_of(units)
    x, y, z = units[:, 0], units[:, 1], units[:, 2]

    # ---- template: sculpt the average head ----
    v = units * np.array([0.80, 1.0, 0.80])                     # skull ellipsoid
    taper = 1.0 - 0.33 * np.clip(-y, 0, 1) ** 1.5               # narrower toward chin
    v[:, 0] *= taper
    v[:, 2] *= 1.0 - 0.12 * np.clip(-y, 0, 1) ** 2              # jaw sits back a bit
    front = np.clip(z, 0, 1)

    def push(center, sigma, vec, amt):
        v[:] += np.outer(bump(units, center, sigma) * amt, np.asarray(vec, float))

    # flatten the frontal cap into a face plate: real faces are nearly planar,
    # with features only ~20-25 degrees off the central axis
    push([0.0, -0.05, 1.0], 0.55, [0, 0, -1], 0.22)             # flatten front pole
    push([0.0, -0.75, 0.75], 0.50, [0, -0.4, 0.9], 0.13)        # chin/jaw forward
    push([0.0, 0.00, 1.0], 0.15, [0, 0, 1], 0.30)               # nose ridge
    push([0.0, -0.18, 1.0], 0.09, [0, -0.25, 1], 0.16)          # nose tip
    for s in (+1, -1):
        push([s * 0.42, 0.28, 0.95], 0.17, [0, 0, -1], 0.09)    # eye sockets (in)
        push([s * 0.40, 0.26, 0.97], 0.09, [s * 0.1, 0, 1], 0.05)   # eyeball bulge
        push([s * 0.68, -0.05, 0.65], 0.28, [s * 0.3, 0, 0.6], 0.08)  # cheekbones
    push([0.0, 0.48, 0.92], 0.40, [0, 0.1, 1], 0.10)            # brow/forehead
    push([0.0, -0.46, 0.92], 0.13, [0, 0, 1], 0.07)             # lips
    push([0.0, -0.62, 0.86], 0.10, [0, 0, -1], 0.035)           # under-lip crease

    template = v.astype(np.float32)

    # ---- per-vertex colors: eyes, brows, lips make the face readable ----
    skin = np.array([225.0, 178.0, 155.0])
    colors = np.tile(skin, (len(units), 1))

    def paint(center, sigma, rgb, strength=1.0, sharp=1.0):
        m = np.clip(bump(units, center, sigma) ** sharp * strength, 0, 1)[:, None]
        colors[:] = colors * (1 - m) + np.asarray(rgb, float) * m

    for s in (+1, -1):
        paint([s * 0.42, 0.50, 0.85], 0.11, [70, 52, 45], 1.0, 2.0)     # eyebrow
        paint([s * 0.42, 0.28, 0.93], 0.11, [248, 246, 242], 1.0, 2.2)  # eye white
        paint([s * 0.40, 0.27, 0.95], 0.062, [96, 122, 168], 1.0, 1.3)  # iris
        paint([s * 0.40, 0.27, 0.96], 0.03, [22, 22, 26], 1.0, 1.0)     # pupil
    paint([0.0, -0.46, 0.95], 0.12, [176, 92, 92], 1.0, 1.5)            # lips
    for s in (+1, -1):
        paint([s * 0.60, -0.18, 0.70], 0.24, [222, 152, 138], 0.35)     # blush
    colors_u8 = np.clip(colors, 0, 255).astype(np.uint8)

    # ---- identity directions: (name, displacement field [N,3]) ----
    def field(center, sigma, vec):
        return np.outer(bump(units, center, sigma), np.asarray(vec, float))

    sym = lambda cx, cy, cz, s, vec: (field([cx, cy, cz], s, vec)
                                      + field([-cx, cy, cz], s, [-vec[0], vec[1], vec[2]]))

    identity = [
        ("Head width",     np.outer(np.abs(x) * 0.5, [0, 0, 0]) + units * [0.10, 0, 0] * np.sign(x)[:, None] ** 2),
        ("Head length",    units * [0, 0.12, 0]),
        ("Jaw width",      sym(0.55, -0.45, 0.45, 0.35, [0.09, 0, 0])),
        ("Chin length",    field([0, -0.85, 0.55], 0.30, [0, -0.11, 0.02])),
        ("Nose size",      field([0, -0.02, 1.0], 0.14, [0, 0, 0.10])),
        ("Nose width",     sym(0.10, -0.10, 1.0, 0.07, [0.05, 0, 0])),
        ("Eye size",       sym(0.42, 0.28, 0.95, 0.14, [0, 0, -0.05])),
        ("Cheek fullness", sym(0.60, -0.12, 0.62, 0.25, [0.06, -0.01, 0.05])),
        ("Brow ridge",     field([0, 0.38, 0.95], 0.22, [0, 0.02, 0.07])),
        ("Lip fullness",   field([0, -0.42, 0.92], 0.12, [0, 0, 0.06])),
        ("Face roundness", np.outer(np.clip(-y, 0, 1) * front, [0, 0, 0]) + units * [0.06, -0.04, 0.02] * np.clip(-y, 0, 1)[:, None]),
        ("Forehead slope", field([0, 0.62, 0.75], 0.35, [0, 0.03, -0.08])),
    ]

    lower_face = bump(units, [0, -0.6, 0.7], 0.5)
    expression = [
        ("Jaw open",    np.outer(lower_face, [0, -0.14, -0.03])),
        ("Smile",       sym(0.35, -0.38, 0.85, 0.12, [0.05, 0.05, 0.01])),
        ("Frown",       sym(0.35, -0.38, 0.85, 0.12, [0.02, -0.05, 0.0])),
        ("Brow raise",  field([0, 0.44, 0.90], 0.28, [0, 0.06, 0.01])),
        ("Pucker",      field([0, -0.42, 0.93], 0.12, [0, 0, 0.07]) + sym(0.20, -0.42, 0.90, 0.09, [-0.04, 0, 0])),
        ("Cheek puff",  sym(0.65, -0.20, 0.62, 0.22, [0.06, 0, 0.03])),
    ]

    id_names = [nm for nm, _ in identity]
    ex_names = [nm for nm, _ in expression]
    id_basis = np.stack([f.reshape(-1) for _, f in identity]).astype(np.float32)
    ex_basis = np.stack([f.reshape(-1) for _, f in expression]).astype(np.float32)
    id_std = np.ones(len(identity), np.float32)
    ex_std = np.ones(len(expression), np.float32)

    return (template.reshape(-1), tris.reshape(-1), id_basis, ex_basis,
            id_std, ex_std, id_names, ex_names, colors_u8.reshape(-1))


def quantize_int16(a):
    scale = float(np.abs(a).max()) / 32767.0 or 1.0
    return np.round(a / scale).astype(np.int16), scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../model/gnm_web.bin")
    args = ap.parse_args()

    template, tris, id_b, ex_b, id_std, ex_std, id_names, ex_names, colors = build()
    id_q, id_scale = quantize_int16(id_b)
    ex_q, ex_scale = quantize_int16(ex_b)

    payload = bytearray()
    header = {"source": "placeholder", "idScale": id_scale, "exScale": ex_scale,
              "idNames": id_names, "exNames": ex_names}

    def add(name, arr, components=None):
        header[name] = {"offset": len(payload), "length": int(arr.size)}
        if components is not None:
            header[name]["components"] = components
        payload.extend(np.ascontiguousarray(arr).tobytes())

    add("template", template)
    add("triangles", tris)
    add("idBasis", id_q, id_q.shape[0])
    add("exBasis", ex_q, ex_q.shape[0])
    add("idStd", id_std)
    add("exStd", ex_std)
    add("colors", colors)

    hb = json.dumps(header).encode()
    with open(args.out, "wb") as f:
        f.write(struct.pack("<I", len(hb)))
        f.write(hb)
        f.write(payload)
    print(f"wrote {args.out}: {(4 + len(hb) + len(payload)) / 1e6:.2f} MB, "
          f"{template.size // 3} verts, {tris.size // 3} tris")


if __name__ == "__main__":
    main()

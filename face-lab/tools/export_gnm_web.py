"""Bake Google's GNM head model into a compact binary for the Face Lab web app.

Usage (needs the google/GNM repo installed: `pip install ./gnm/shape` from a clone):

    python export_gnm_web.py --out ../model/gnm_web.bin

Output layout (read by index.html):
    [uint32 little-endian: JSON header length][JSON header][payload bytes]

The web app evaluates:  vertices = template + idBasis.T @ id + exBasis.T @ ex
with the basis rows quantized to int16 (dequantized via idScale/exScale).
Truncating to the top-N components keeps the download small while preserving
most of the variance of the full 253-identity / 383-expression model.
"""

import argparse
import json
import struct

import numpy as np

N_IDENTITY = 40    # top identity components kept for the web
N_EXPRESSION = 30  # top expression components kept for the web


def quantize_int16(a: np.ndarray) -> tuple[np.ndarray, float]:
    scale = float(np.abs(a).max()) / 32767.0 or 1.0
    return np.round(a / scale).astype(np.int16), scale


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../model/gnm_web.bin")
    args = ap.parse_args()

    from gnm.shape import gnm_numpy  # noqa: PLC0415 — heavyweight import

    gnm = gnm_numpy.GNM.from_local(
        version=gnm_numpy.GNMMajorVersion.V3,
        variant=gnm_numpy.GNMVariant.HEAD,
    )

    template = np.asarray(gnm.template_vertex_positions, np.float32).reshape(-1)
    triangles = np.asarray(gnm.triangles, np.uint32).reshape(-1)

    # NOTE: attribute names below are adapted to the installed GNM release;
    # they expose the linear identity/expression bases and their stddevs.
    id_basis = np.asarray(gnm.identity_basis, np.float32)[:N_IDENTITY]
    ex_basis = np.asarray(gnm.expression_basis, np.float32)[:N_EXPRESSION]
    id_std = np.asarray(gnm.identity_stddev, np.float32)[:N_IDENTITY]
    ex_std = np.asarray(gnm.expression_stddev, np.float32)[:N_EXPRESSION]

    id_q, id_scale = quantize_int16(id_basis.reshape(N_IDENTITY, -1))
    ex_q, ex_scale = quantize_int16(ex_basis.reshape(N_EXPRESSION, -1))

    payload = bytearray()
    header: dict = {"idScale": id_scale, "exScale": ex_scale}

    def add(name: str, arr: np.ndarray, components: int | None = None) -> None:
        header[name] = {"offset": len(payload), "length": arr.size}
        if components is not None:
            header[name]["components"] = components
        payload.extend(arr.tobytes())

    add("template", template)
    add("triangles", triangles)
    add("idBasis", id_q, N_IDENTITY)
    add("exBasis", ex_q, N_EXPRESSION)
    add("idStd", id_std)
    add("exStd", ex_std)

    header_bytes = json.dumps(header).encode()
    with open(args.out, "wb") as f:
        f.write(struct.pack("<I", len(header_bytes)))
        f.write(header_bytes)
        f.write(payload)

    size_mb = (4 + len(header_bytes) + len(payload)) / 1e6
    print(f"wrote {args.out}: {size_mb:.1f} MB, "
          f"{template.size // 3} verts, {triangles.size // 3} tris")


if __name__ == "__main__":
    main()

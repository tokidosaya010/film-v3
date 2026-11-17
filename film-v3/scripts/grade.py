"""Apply the Film v3 color grade to a photograph."""
import argparse
from io import BytesIO
from pathlib import Path
from zlib import crc32

import numpy as np
from PIL import Image, ImageCms, ImageOps

RAW_EXTENSIONS = {".cr2", ".cr3", ".nef", ".arw", ".raf", ".orf", ".rw2", ".dng"}
SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))


def read_rgb(path):
    if path.suffix.lower() in RAW_EXTENSIONS:
        try:
            import rawpy
        except ImportError as error:
            raise ValueError("RAW input requires rawpy or a developed RGB export.") from error
        with rawpy.imread(str(path)) as raw:
            pixels = raw.postprocess(use_camera_wb=True, output_bps=16)
        return pixels.astype(np.float32) / 65535

    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        profile = source.info.get("icc_profile")
        if profile:
            image = ImageCms.profileToProfile(
                image, ImageCms.ImageCmsProfile(BytesIO(profile)), SRGB, outputMode="RGB"
            )
        else:
            image = image.convert("RGB")
        return np.asarray(image, dtype=np.float32) / 255


def smoothstep(low, high, value):
    normalized = np.clip((value - low) / (high - low), 0, 1)
    return normalized**2 * (3 - 2 * normalized)


def grade(rgb, seed):
    weights = np.array([.2126, .7152, .0722], dtype=np.float32)
    y = rgb @ weights
    hsv = np.asarray(Image.fromarray(np.rint(rgb * 255).astype(np.uint8)).convert("HSV"))
    hue = hsv[..., 0].astype(np.float32) * (360 / 255)
    chroma = rgb.max(axis=-1) - rgb.min(axis=-1)

    def band(a, b, c, d):
        return smoothstep(a,b,hue) * (1-smoothstep(c,d,hue))

    skin = band(5,17,39,54) * smoothstep(.21,.42,y) * (1-smoothstep(.30,.48,chroma))
    foliage = band(48,76,145,171)
    blues = band(164,188,232,264)
    red = 1-smoothstep(7,22,np.minimum(hue,360-hue))
    active = smoothstep(.025,.14,chroma)
    sat = 1 - active * (.27 + .18*smoothstep(.26,.70,chroma) + .32*foliage + .10*blues - .21*skin - .22*red)
    color = (rgb-y[...,None])*sat[...,None]

    def shift(mask, offsets):
        offsets = np.array(offsets, dtype=np.float32)
        color[:] += mask[...,None] * (offsets-offsets@weights)

    shift(foliage*active, [.101,.012,-.028])
    shift(blues*active, [-.042,.055,.004])
    shadows = smoothstep(.01,.075,y) * (1-smoothstep(.15,.45,y)) * (1-.76*skin)
    shift(shadows, [-.059,.018,.053])
    highlights = smoothstep(.51,.92,y) * (1-.83*skin)
    shift(highlights, [.045,.013,-.054])
    tone = np.interp(y,[0,.06,.18,.36,.55,.72,.88,1],
                      [.019,.051,.137,.302,.569,.767,.886,.959]).astype(np.float32)
    tone += .012 * skin
    rng = np.random.default_rng(seed)
    grain = rng.standard_normal(y.shape, dtype=np.float32)
    tone += grain * .024 * smoothstep(.018,.12,y) * (1-.70*smoothstep(.60,.99,y))
    tone = np.clip(tone,0,1)
    fit = np.minimum(1,np.minimum((1-tone)/np.maximum(color.max(axis=-1),1e-6),
                                tone/np.maximum(-color.min(axis=-1),1e-6)))
    return np.rint(255*np.clip(tone[...,None]+color*fit[...,None],0,1)).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preview", action="store_true", help="export an ungraded, oriented preview")
    args = parser.parse_args()
    formats = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".tif": "TIFF", ".tiff": "TIFF"}
    fmt = formats.get(args.output.suffix.lower())
    if fmt is None:
        parser.error("output must be JPEG, PNG or TIFF")
    try:
        rgb = read_rgb(args.input)
        suffix = args.input.stem.rsplit("_", 1)[-1]
        seed = int(suffix) if suffix.isascii() and suffix.isdecimal() else crc32(args.input.stem.encode("utf-8"))
        if args.preview:
            image = Image.fromarray(np.rint(rgb * 255).astype(np.uint8))
            image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        else:
            image = Image.fromarray(grade(rgb, seed))
        options = {"quality": 96, "subsampling": 0} if fmt == "JPEG" else {}
        with args.output.open("xb") as output:
            image.save(output, format=fmt, icc_profile=SRGB.tobytes(), **options)
    except (OSError, ValueError, ImageCms.PyCMSError) as error:
        parser.exit(1, f"Grade failed: {error}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Simula variações de captura em selfies com Pillow e NumPy.

Instalação: python -m pip install "Pillow>=9.2" "numpy>=1.24"
Exemplo: python main.py dataset/ output/ \
    --perfil misto --variantes 3 --seed 42

A saída preserva a proporção e a estrutura de pastas da entrada. A pasta
de saída deve ser nova. O manifesto CSV registra a origem e os parâmetros
de cada JPEG. Os perfis são aproximações manuais de capturas de celular.
"""

import argparse
import csv
import hashlib
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from constants import EXTENSIONS, LUMA, PIXEL_COUNTS, PROFILES




def rng_for(seed, relative_path, stream):
    key = f"{seed}\0{relative_path}\0{stream}".encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=16).digest()
    return np.random.default_rng(int.from_bytes(digest, "little"))


def sample_settings(profile, rng):
    settings = {
        name: float(rng.uniform(*bounds))
        for name, bounds in PROFILES[profile].items()
        if name not in {"lado_curto", "qualidade_jpeg"}
    }
    minimum, maximum = PROFILES[profile]["lado_curto"]
    settings["lado_curto"] = int(rng.choice([n for n in PIXEL_COUNTS if minimum <= n <= maximum]))
    minimum, maximum = PROFILES[profile]["qualidade_jpeg"]
    settings["qualidade_jpeg"] = int(rng.integers(minimum, maximum + 1))
    settings["luz_lateral_ev"] *= int(rng.choice((-1, 1)))
    return settings


def simulate_capture(image, settings, rng):
    width, height = image.size
    scale = min(1.0, settings["lado_curto"] / min(width, height))
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    image = image.filter(ImageFilter.GaussianBlur(settings["desfoque_px"]))

    rgb = np.asarray(image, dtype=np.float32) / 255.0
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    lateral = np.linspace(-0.5, 0.5, size[0], dtype=np.float32)
    exposure = settings["exposicao_ev"] + settings["luz_lateral_ev"] * lateral
    warmth = settings["dominante"]
    channel_gain = np.exp2(np.array([warmth, 0.0, -warmth], dtype=np.float32))
    linear *= np.exp2(exposure)[None, :, None] * channel_gain
    rgb = np.where(linear <= 0.0031308, 12.92 * linear, 1.055 * linear ** (1 / 2.4) - 0.055)

    luma = rgb @ LUMA
    rgb = luma[..., None] + settings["saturacao"] * (rgb - luma[..., None])
    # Um pivô mais baixo evita clarear demais as sombras no perfil de baixa luz.
    pivot = 0.25
    rgb = pivot + settings["contraste"] * (rgb - pivot)

    # Ruído correlacionado entre canais, mais aparente nas regiões escuras.
    shadows = np.sqrt(1 - np.clip(luma, 0, 1))
    grain = rng.standard_normal(luma.shape, dtype=np.float32)
    rgb += (settings["ruido_luma"] * (0.45 + 0.75 * shadows) * grain)[..., None]

    # O ruído de cor tem resolução menor para formar manchas discretas.
    chroma_size = (max(1, (size[0] + 1) // 2), max(1, (size[1] + 1) // 2))
    for channel in (0, 2):
        chroma = rng.standard_normal(chroma_size[::-1], dtype=np.float32)
        chroma = Image.fromarray(chroma).resize(size, Image.Resampling.BILINEAR)
        rgb[..., channel] += settings["ruido_cor"] * np.asarray(chroma)

    pixels = np.rint(np.clip(rgb, 0.0, 1.0) * 255).astype(np.uint8)
    return Image.fromarray(pixels)


def process_folder(source, output, profile, variants, seed):
    if not source.is_dir():
        raise ValueError(f"Pasta de entrada inválida: {source}")
    if output.exists() or output.is_relative_to(source):
        raise ValueError("Use uma pasta de saída nova, fora da pasta de entrada.")
    sources = sorted(
        path for path in source.rglob("*")
        if path.is_file() and not path.is_symlink() and path.suffix.lower() in EXTENSIONS
    )
    if not sources:
        raise ValueError("Nenhuma imagem compatível encontrada na pasta de entrada.")

    fields = ["origem", "saida", "variante", "perfil", "seed", "largura", "altura", *PROFILES["interno"]]
    output.mkdir(parents=True, exist_ok=False)
    try:
        with (output / "manifesto.csv").open("w", newline="", encoding="utf-8") as file:
            manifest = csv.DictWriter(file, fieldnames=fields)
            manifest.writeheader()
            for path in sources:
                relative = path.relative_to(source)
                try:
                    with Image.open(path) as opened:
                        image = ImageOps.exif_transpose(opened).convert("RGB")
                except OSError as error:
                    raise ValueError(f"Falha ao abrir {relative}: {error}") from error

                order = rng_for(seed, relative.as_posix(), "perfis").permutation(tuple(PROFILES))
                for index in range(1, variants + 1):
                    selected = str(order[(index - 1) % len(order)]) if profile == "misto" else profile
                    rng = rng_for(seed, relative.as_posix(), index)
                    settings = sample_settings(selected, rng)
                    simulated = simulate_capture(image, settings, rng)
                    name = f"{relative.name}__v{index:02d}_{selected}.jpg"
                    target = relative.with_name(name)
                    destination = output / target
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    simulated.save(destination, "JPEG", quality=settings["qualidade_jpeg"], subsampling=2)
                    manifest.writerow({
                        "origem": relative.as_posix(),
                        "saida": target.as_posix(),
                        "variante": index,
                        "perfil": selected,
                        "seed": seed,
                        "largura": simulated.width,
                        "altura": simulated.height,
                        **settings,
                    })
    except (Exception, KeyboardInterrupt):
        shutil.rmtree(output)
        raise
    return len(sources)



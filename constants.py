
import numpy as np

PROFILES = {
    "interno": {
        "exposicao_ev": (-0.45, 0.20),
        "contraste": (0.87, 1.00),
        "saturacao": (0.80, 1.02),
        "dominante": (-0.08, 0.13),
        "luz_lateral_ev": (0.00, 0.30),
        "desfoque_px": (0.25, 0.80),
        "ruido_luma": (0.003, 0.010),
        "ruido_cor": (0.001, 0.004),
        "lado_curto": (480, 720),
        "qualidade_jpeg": (65, 87),
    },
    "baixa_luz": {
        "exposicao_ev": (-2.15, -1.10),
        "contraste": (0.96, 1.19),
        "saturacao": (0.71, 0.98),
        "dominante": (-0.10, 0.19),
        "luz_lateral_ev": (0.15, 0.70),
        "desfoque_px": (0.55, 1.20),
        "ruido_luma": (0.012, 0.027),
        "ruido_cor": (0.007, 0.016),
        "lado_curto": (360, 720),
        "qualidade_jpeg": (52, 78),
    },
    "suave": {
        "exposicao_ev": (-0.30, 0.35),
        "contraste": (0.70, 0.87),
        "saturacao": (0.69, 0.94),
        "dominante": (-0.15, 0.09),
        "luz_lateral_ev": (0.00, 0.24),
        "desfoque_px": (0.90, 1.70),
        "ruido_luma": (0.003, 0.012),
        "ruido_cor": (0.001, 0.005),
        "lado_curto": (360, 600),
        "qualidade_jpeg": (57, 82),
    },
}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
PIXEL_COUNTS = (360, 480, 540, 600, 640, 720) # sorteio de resolução
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32) # é uma medida de quão claro ou escuro um pixel parece
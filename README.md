# Simulação de captura em selfies sintéticas

![Python 3.9 ou superior](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Pillow 9.2 ou superior](https://img.shields.io/badge/Pillow-9.2%2B-764ABC)
![NumPy 1.24 ou superior](https://img.shields.io/badge/NumPy-1.24%2B-013243?logo=numpy&logoColor=white)

Script de linha de comando para gerar variações de captura de celular a partir de um lote de selfies. O processamento aproxima características observadas em frames de referência, como exposição baixa, perda de detalhe fino, variação de cor e compressão. Cada imagem gerada vem acompanhada de um registro dos parâmetros usados.

## Estrutura do projeto

```text
face-synthetic-data/
├── main.py          # CLI: argumentos e execução do processamento
├── functions.py     # Leitura das imagens, transformações e gravação dos resultados
├── constants.py     # Perfis, extensões aceitas, resoluções e pesos de luminância
├── dataset/         # Imagens de entrada, organizadas em subpastas
│   ├── pessoa_01/
│   │   └── foto_01.jpg
│   └── pessoa_02/
│       └── foto_01.png
├── output/          # Criada na execução: imagens geradas e manifesto.csv
└── README.md
```

`main.py` chama `process_folder`, em `functions.py`, que percorre a entrada, aplica as transformações e salva as variantes e o manifesto. Os parâmetros dos perfis ficam em `constants.py`.

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Define os argumentos da CLI, valida o número de variantes e inicia o processamento. |
| `functions.py` | `process_folder` encontra as imagens e grava os resultados; `rng_for` gera sorteios reproduzíveis; `sample_settings` sorteia os parâmetros; `simulate_capture` aplica as transformações. |
| `constants.py` | Define os perfis em `PROFILES`, as extensões em `EXTENSIONS`, as resoluções em `PIXEL_COUNTS` e os pesos de luminância em `LUMA`. |

## Instalação

Em Linux ou macOS, abra o terminal na pasta que contém o script e crie um ambiente virtual:

```bash
conda create -n <venv name> python==3.13
conda activate <venv name>

python -m pip install "Pillow>=9.2" "numpy>=1.24"
```

## Uso rápido

1. Remova de `dataset/` as imagens sintéticas de exemplo do repositório.
2. Coloque suas próprias imagens dentro de `dataset/`, organizadas em subpastas por pessoa ou categoria, como na estrutura acima.
3. Execute o comando abaixo na raiz do projeto. As imagens geradas ficarão em `output/`, com a mesma organização de subpastas da entrada.

O script percorre `dataset/` recursivamente e aceita JPEG, PNG, WebP, BMP e TIFF. Todas as imagens compatíveis presentes nessa pasta entram no processamento.

Execute na raiz do projeto. Por padrão, o script lê `dataset/` e grava as imagens geradas e o manifesto em `output/`:

```bash
python main.py --perfil misto --variantes 3 --seed 42
```

A pasta `output/` é criada automaticamente e não deve existir antes da execução. Para executar novamente, mova a saída anterior ou informe outra pasta de saída nova, fora de `dataset/`. Com 30 fotos de entrada, esse comando gera 90 JPEGs, com uma imagem de cada perfil por foto. A proporção das imagens é preservada, com arredondamento para dimensões inteiras, e a resolução é reduzida até o lado curto sorteado quando a imagem original é maior.

Os caminhos também podem ser informados explicitamente: `python main.py dataset/ output/`.

### Parâmetros da linha de comando


| Argumento     | Padrão      | Função                                                |
| ------------- | ------------ | ------------------------------------------------------- |
| `entrada`     | `dataset/`   | Pasta com as imagens de origem.                         |
| `saida`       | `output/`    | Nova pasta para os JPEGs e o manifesto.                 |
| `--perfil`    | `misto`      | Seleciona `misto`, `interno`, `baixa_luz` ou `suave`.    |
| `--variantes` | `3`          | Número de versões geradas por imagem. O mínimo é 1. |
| `--seed`      | `42`         | Semente usada para sortear parâmetros e gerar ruído.  |
| `--help`      |              | Exibe a ajuda do script.                                |

Para gerar uma versão de baixa luz por foto:

```bash
python main.py dataset/ output/ \
  --perfil baixa_luz --variantes 1 --seed 42
```

## Perfis de captura


| Perfil      | Aparência                                                                        | Exposição (EV) | Desfoque gaussiano (px) | Qualidade JPEG |
| ----------- | --------------------------------------------------------------------------------- | ---------------: | ----------------------: | -------------: |
| `interno`   | Variações discretas de cor e exposição, com suavização leve.                |   −0,45 a +0,20 |              0,25–0,80 |         65–87 |
| `baixa_luz` | Exposição reduzida, iluminação lateral mais variável e ruído mais visível. |  −2,15 a −1,10 |              0,55–1,20 |         52–78 |
| `suave`     | Contraste reduzido e perda de detalhe fino mais acentuada.                        |   −0,30 a +0,35 |              0,90–1,70 |         57–82 |

Cada perfil sorteia parâmetros dentro de intervalos definidos em `PROFILES`, no arquivo `constants.py`. O modo `misto` sorteia a ordem dos três perfis por arquivo e percorre essa ordem ciclicamente. Com uma ou duas variantes, entram apenas os primeiros perfis da ordem sorteada para aquela foto.

O processamento primeiro corrige a orientação EXIF. Em seguida, reduz a resolução e aplica desfoque. A exposição e a dominante de cor são ajustadas em RGB linear. Após a conversão para sRGB, o script ajusta saturação e contraste, adiciona ruído de luminância e cor e exporta em JPEG com subamostragem de crominância 4:2:0.

## Arquivos gerados

O script reproduz a hierarquia da entrada na pasta de saída. O nome de cada JPEG combina o nome original, incluindo a extensão, com o número da variante e o perfil.

```text
output/
├── manifesto.csv
└── pessoa_01/
    ├── A_ponto_de_onibus.png__v01_interno.jpg
    ├── A_ponto_de_onibus.png__v02_baixa_luz.jpg
    └── A_ponto_de_onibus.png__v03_suave.jpg
```

O `manifesto.csv` tem uma linha por JPEG. Use `origem` para identificar todas as variantes da mesma foto e `saida` para localizar cada arquivo. Os dois caminhos são relativos às respectivas pastas.


| Campos                                          | Significado                                                                                                                       |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `origem`, `saida`, `variante`, `perfil`, `seed` | Proveniência da imagem e parâmetros de execução.                                                                              |
| `largura`, `altura`, `lado_curto`               | Dimensões reais do JPEG e lado curto sorteado, em pixels. Uma entrada menor pode resultar em dimensões abaixo do alvo sorteado. |
| `exposicao_ev`, `luz_lateral_ev`, `dominante`   | Deslocamento global de exposição, gradiente horizontal de exposição e ajuste relativo dos canais vermelho e azul.             |
| `contraste`, `saturacao`, `desfoque_px`         | Multiplicadores de contraste e saturação e raio do desfoque gaussiano em pixels da imagem redimensionada.                       |
| `ruido_luma`, `ruido_cor`, `qualidade_jpeg`     | Escalas de intensidade do ruído em valores normalizados e parâmetro de qualidade do codificador JPEG.                           |

## Reprodutibilidade e avaliação

A semente é combinada com o caminho relativo do original e o índice da variante. Para repetir uma execução, mantenha os arquivos de entrada, os caminhos relativos, a versão do script, as opções e o ambiente de execução. Use outra pasta de saída. Na checagem deste projeto, duas execuções com a mesma semente produziram manifestos e 90 JPEGs idênticos byte a byte no mesmo ambiente.

Os perfis foram definidos por inspeção visual dos exemplos fornecidos. A similaridade com o dataset público ainda precisa ser medida. A simulação opera em imagens individuais e cobre características espaciais da captura. Para avaliar o impacto em detecção de apresentação, compare o desempenho com e sem dados sintéticos em um conjunto real separado. Mantenha todas as variantes de uma mesma identidade na mesma partição e verifique se formato, resolução ou compressão acabam ligados a uma única classe.

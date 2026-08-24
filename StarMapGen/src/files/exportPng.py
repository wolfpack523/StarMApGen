from pathlib import Path

import resvg_py


def exportPng(
        svgFile,
        pngFile=None,
        scale=2.0,
):
    """Render an SVG file to PNG."""

    svgPath = Path(svgFile)

    if pngFile is None:
        pngPath = svgPath.with_suffix(".png")
    else:
        pngPath = Path(pngFile)

    svgData = svgPath.read_text(
        encoding="utf-8",
    )

    pngData = resvg_py.svg_to_bytes(
        svg_string=svgData,
        zoom=scale,
        font_dirs=[
            r"C:\Windows\Fonts",
        ],
    )

    pngPath.write_bytes(
        pngData
    )

    return pngPath
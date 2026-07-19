import re
from html import escape
from pathlib import Path

import wx
import wx.html2


class SMGMapPanel(wx.Panel):
    """Display the generated map using a browser-based SVG renderer."""

    def __init__(self, parent, w=20, h=20):
        super().__init__(parent)

        ratio = w / h
        self.SetMinSize(
            wx.Size(
                round(400 * ratio),
                400,
            )
        )

        self.webView = wx.html2.WebView.New(self)

        if self.webView is None:
            raise RuntimeError(
                "No WebView backend is available. "
                "On Windows, make sure the Microsoft Edge "
                "WebView2 Runtime is installed."
            )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(
            self.webView,
            1,
            wx.EXPAND,
        )

        self.SetSizer(sizer)

        # Delay the initial load until the native WebView exists.
        wx.CallAfter(
            self.setMap,
            "BannerMap.svg",
        )

    def setMap(self, file):
        """Load and display an SVG file."""

        svgPath = Path(file).resolve()

        if not svgPath.is_file():
            self.showError(
                f"SVG file not found:\n{svgPath}"
            )
            return

        try:
            svg = svgPath.read_text(
                encoding="utf-8-sig"
            )
        except OSError as error:
            self.showError(
                f"Could not read SVG file:\n{error}"
            )
            return

        # The XML declaration is valid in a standalone SVG file,
        # but not when the SVG is inserted into an HTML document.
        svg = re.sub(
            r"^\s*<\?xml[^>]*\?>",
            "",
            svg,
            count=1,
            flags=re.IGNORECASE,
        )

        html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">

    <style>
        html,
        body {{
            width: 100%;
            height: 100%;
            margin: 0;
            overflow: hidden;
            background: #000;
        }}

        body {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        svg {{
            display: block;
            width: 100%;
            height: 100%;
        }}
    </style>
</head>

<body>
{svg}
</body>
</html>
"""

        self.webView.SetPage(
            html,
            svgPath.parent.as_uri() + "/",
        )

    def showError(self, message):
        """Display an error inside the preview area."""

        self.webView.SetPage(
            f"""<!doctype html>
<html>
<body style="
    margin: 0;
    padding: 20px;
    background: #000;
    color: #fff;
    font-family: sans-serif;
">
    {escape(message)}
</body>
</html>
""",
            "",
        )

import re
from html import escape
from pathlib import Path

import wx
import wx.html2


class SMGMapPanel(wx.Panel):
    """Panel used to display the generated SVG map."""

    def __init__(self, parent, w=20, h=20):
        super().__init__(parent)

        self.SetBackgroundColour(wx.BLACK)

        self.webViewReady = False
        self.pendingDocument = None

        backend = wx.html2.WebViewBackendDefault

        if (
            hasattr(wx.html2, "WebViewBackendEdge")
            and wx.html2.WebView.IsBackendAvailable(
                wx.html2.WebViewBackendEdge
            )
        ):
            backend = wx.html2.WebViewBackendEdge

        self.webView = wx.html2.WebView.New(
            self,
            backend=backend,
        )

        if self.webView is None:
            raise RuntimeError(
                "No compatible WebView backend is available."
            )

        self.webView.Bind(
            wx.html2.EVT_WEBVIEW_LOADED,
            self.onWebViewLoaded,
        )

        self.webView.Bind(
            wx.html2.EVT_WEBVIEW_ERROR,
            self.onWebViewError,
        )

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(
            self.webView,
            1,
            wx.EXPAND,
        )

        self.SetSizer(sizer)

        # Explicitly load an initial page. SetPage() will only be used
        # after EVT_WEBVIEW_LOADED confirms that the WebView is ready.
        self.webView.LoadURL("about:blank")

        # Preserve the original startup behaviour.
        wx.CallAfter(
            self.setMap,
            "BannerMap.svg",
        )

    def setMap(self, fileName):
        """Load and display an SVG file."""

        filePath = (
            Path(fileName)
            .expanduser()
            .resolve()
        )

        if not filePath.is_file():
            self.showError(
                f"SVG file not found:\n{filePath}"
            )
            return

        try:
            svgContent = filePath.read_text(
                encoding="utf-8",
            )
        except (OSError, UnicodeError) as error:
            self.showError(
                f"Unable to read SVG file:\n{error}"
            )
            return

        svgContent = self.prepareSvg(
            svgContent
        )

        document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">

    <style>
        html,
        body {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: auto;
            background: #000000;
        }}

        #viewport {{
            position: relative;
            width: max-content;
            height: max-content;
            min-width: 100%;
            min-height: 100%;
            transform-origin: 0 0;
        }}

        #map {{
            display: block;
            transform-origin: 0 0;
        }}

        #map svg {{
            display: block;
            max-width: none;
            max-height: none;
        }}

        #zoomIndicator {{
            position: fixed;
            right: 12px;
            bottom: 12px;

            padding: 5px 9px;

            color: #ffffff;
            background: rgba(0, 0, 0, 0.7);

            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 4px;

            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;

            pointer-events: none;
            user-select: none;
        }}
    </style>
</head>

<body>

<div id="viewport">
    <div id="map">
        {svgContent}
    </div>
</div>

<div id="zoomIndicator">
    100 %
</div>

<script>
    const map = document.getElementById("map");
    const viewport = document.getElementById("viewport");
    const indicator = document.getElementById("zoomIndicator");

    let zoom = 1.0;

    const minZoom = 0.1;
    const maxZoom = 8.0;
    const zoomStep = 1.15;

    function clamp(value, minimum, maximum) {{
        return Math.min(
            maximum,
            Math.max(
                minimum,
                value
            )
        );
    }}

    function updateZoom() {{
        map.style.transform =
            `scale(${{zoom}})`;

        const svg = map.querySelector("svg");

        if (svg) {{
            const width =
                svg.viewBox.baseVal.width
                || svg.width.baseVal.value;

            const height =
                svg.viewBox.baseVal.height
                || svg.height.baseVal.value;

            viewport.style.width =
                `${{width * zoom}}px`;

            viewport.style.height =
                `${{height * zoom}}px`;
        }}

        indicator.textContent =
            `${{Math.round(zoom * 100)}} %`;
    }}

    function setZoom(newZoom) {{
        zoom = clamp(
            newZoom,
            minZoom,
            maxZoom
        );

        updateZoom();
    }}

    document.addEventListener(
        "wheel",
        event => {{
            if (!event.ctrlKey) {{
                return;
            }}

            event.preventDefault();

            if (event.deltaY < 0) {{
                setZoom(
                    zoom * zoomStep
                );
            }}
            else {{
                setZoom(
                    zoom / zoomStep
                );
            }}
        }},
        {{
            passive: false
        }}
    );

    document.addEventListener(
        "keydown",
        event => {{
            if (
                event.key === "+"
                || event.key === "="
            ) {{
                event.preventDefault();

                setZoom(
                    zoom * zoomStep
                );

                return;
            }}

            if (event.key === "-") {{
                event.preventDefault();

                setZoom(
                    zoom / zoomStep
                );

                return;
            }}

            if (event.key === "0") {{
                event.preventDefault();

                setZoom(1.0);
            }}
        }}
    );

    document.body.tabIndex = 0;
    document.body.focus();

    updateZoom();
</script>

</body>
</html>
"""

        baseUrl = (
            filePath.parent.as_uri()
            + "/"
        )

        self.pendingDocument = (
            document,
            baseUrl,
        )

        self.displayPendingDocument()

    def prepareSvg(self, svgContent):
        """Prepare a standalone SVG for embedding in HTML."""

        svgContent = re.sub(
            r"^\s*<\?xml[^>]*\?>",
            "",
            svgContent,
            count=1,
            flags=re.IGNORECASE,
        )

        svgContent = re.sub(
            r"<!DOCTYPE[^>]*(?:\[[\s\S]*?\]\s*)?>",
            "",
            svgContent,
            count=1,
            flags=re.IGNORECASE,
        )

        return svgContent.strip()

    def onWebViewLoaded(self, event):
        """Handle completion of the initial WebView page."""

        if not self.webViewReady:
            self.webViewReady = True
            self.displayPendingDocument()

        event.Skip()

    def displayPendingDocument(self):
        """Display the queued document once the WebView is ready."""

        if not self.webViewReady:
            return

        if self.pendingDocument is None:
            return

        document, baseUrl = self.pendingDocument
        self.pendingDocument = None

        self.webView.SetPage(
            document,
            baseUrl,
        )

    def showError(self, message):
        """Display an error inside the preview panel."""

        document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">

    <style>
        html,
        body {{
            margin: 0;
            padding: 20px;
            background: #000000;
            color: #ff6666;
            font-family: Arial, Helvetica, sans-serif;
        }}

        pre {{
            white-space: pre-wrap;
        }}
    </style>
</head>

<body>
    <h2>Unable to display map</h2>
    <pre>{escape(message)}</pre>
</body>
</html>
"""

        self.pendingDocument = (
            document,
            "",
        )

        self.displayPendingDocument()

    def onWebViewError(self, event):
        """Report errors raised by the WebView backend."""

        message = event.GetString()

        if not message:
            message = "Unknown WebView error."

        print(
            "SVG preview error:",
            message,
        )

        event.Skip()
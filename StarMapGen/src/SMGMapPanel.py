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
            overflow: hidden;
            background: #000000;
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
            max-width: 100%;
            max-height: 100%;
        }}
    </style>
</head>

<body>
{svgContent}
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

        # XML declarations are not valid inside an HTML body.
        svgContent = re.sub(
            r"^\s*<\?xml[^>]*\?>",
            "",
            svgContent,
            count=1,
            flags=re.IGNORECASE,
        )

        # Remove an optional DOCTYPE declaration.
        svgContent = re.sub(
            r"<!DOCTYPE[^>]*(?:\[[\s\S]*?\]\s*)?>",
            "",
            svgContent,
            count=1,
            flags=re.IGNORECASE,
        )

        # Ensure that the complete SVG is scaled into the panel.
        # The generated SVG already contains a viewBox.
        svgContent = re.sub(
            r"<svg\b",
            (
                '<svg '
                'preserveAspectRatio="xMidYMid meet" '
                'style="width:100%;height:100%;display:block;"'
            ),
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
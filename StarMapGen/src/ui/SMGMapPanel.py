import json
import re
from pathlib import Path

import wx
import wx.html2


class SMGMapPanel(wx.Panel):
    """Panel used to display the generated SVG map."""

    def __init__(self, parent, w=20, h=20):
        super().__init__(parent)

        self.SetBackgroundColour(wx.BLACK)

        self.webViewReady = False
        self.viewerLoaded = False
        self.viewerLoading = False
        self.pendingSvgContent = None

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

        self.webView.LoadURL("about:blank")

        wx.CallAfter(
            self.setMap,
            "BannerMap.svg",
        )

    def setMap(self, fileName):
        """Load an SVG file into the existing viewer."""

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

        self.pendingSvgContent = svgContent

        self.displayPendingSvg()

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

    def createViewerDocument(self):
        """Create the permanent map viewer page."""

        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">

    <style>
        html,
        body {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #000000;
        }

        #scrollArea {
            width: 100%;
            height: 100%;
            overflow: auto;
        }

        #viewport {
            position: relative;
            min-width: 100%;
            min-height: 100%;
        }

        #map {
            position: absolute;
            top: 0;
            left: 0;
            transform-origin: 0 0;
        }

        #map svg {
            display: block;
            max-width: none;
            max-height: none;
        }

        #zoomIndicator {
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
        }

        #errorMessage {
            display: none;

            padding: 20px;

            color: #ff6666;

            font-family: Arial, Helvetica, sans-serif;

            white-space: pre-wrap;
        }
        
        #systemTooltip {
            display: none;
            position: fixed;
            z-index: 1000;
        
            min-width: 180px;
            max-width: 320px;
        
            padding: 10px 12px;
        
            color: #ffffff;
            background: rgba(12, 12, 18, 0.94);
        
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 6px;
        
            box-shadow:
                0 4px 16px rgba(0, 0, 0, 0.55);
        
            font-family:
                Arial,
                Helvetica,
                sans-serif;
        
            font-size: 13px;
            line-height: 1.45;
        
            white-space: pre-line;
        
            pointer-events: none;
        }
    </style>
</head>

<body>

<div id="scrollArea">
    <div id="viewport">
        <div id="map"></div>
        <div id="errorMessage"></div>
    </div>
</div>

<div id="zoomIndicator">
    100 %
</div>
<div id="systemTooltip"></div>
<script>
    const scrollArea =
        document.getElementById(
            "scrollArea"
        );

    const viewport =
        document.getElementById(
            "viewport"
        );

    const map =
        document.getElementById(
            "map"
        );

    const indicator =
        document.getElementById(
            "zoomIndicator"
        );

    const errorMessage =
        document.getElementById(
            "errorMessage"
        );
        
    const systemTooltip =
        document.getElementById(
            "systemTooltip"
        );

    let zoom = 1.0;

    const minZoom = 0.1;
    const maxZoom = 8.0;
    const zoomStep = 1.15;

    function clamp(
        value,
        minimum,
        maximum
    ) {
        return Math.min(
            maximum,
            Math.max(
                minimum,
                value
            )
        );
    }

    function getSvgSize() {
        const svg =
            map.querySelector(
                "svg"
            );

        if (!svg) {
            return {
                width: 1,
                height: 1
            };
        }

        let width = 0;
        let height = 0;

        if (
            svg.viewBox
            && svg.viewBox.baseVal
        ) {
            width =
                svg.viewBox.baseVal.width;

            height =
                svg.viewBox.baseVal.height;
        }

        if (!width) {
            width =
                parseFloat(
                    svg.getAttribute(
                        "width"
                    )
                );
        }

        if (!height) {
            height =
                parseFloat(
                    svg.getAttribute(
                        "height"
                    )
                );
        }

        return {
            width: width || 1,
            height: height || 1
        };
    }

    function updateZoom() {
        const size =
            getSvgSize();

        const svg =
            map.querySelector(
                "svg"
            );

        if (svg) {
            svg.style.width =
                `${size.width}px`;

            svg.style.height =
                `${size.height}px`;
        }

        map.style.transform =
            `scale(${zoom})`;

        viewport.style.width =
            `${size.width * zoom}px`;

        viewport.style.height =
            `${size.height * zoom}px`;

        indicator.textContent =
            `${Math.round(
                zoom * 100
            )} %`;
    }

    function setZoom(newZoom) {
        zoom = clamp(
            newZoom,
            minZoom,
            maxZoom
        );

        updateZoom();
    }

    window.replaceMapSvg =
        function(svgContent) {

            const oldScrollLeft =
                scrollArea.scrollLeft;

            const oldScrollTop =
                scrollArea.scrollTop;

            errorMessage.style.display =
                "none";

            map.style.display =
                "block";

            map.innerHTML =
                svgContent;

            updateZoom();

            scrollArea.scrollLeft =
                oldScrollLeft;

            scrollArea.scrollTop =
                oldScrollTop;
        };

    window.showMapError =
        function(message) {

            map.style.display =
                "none";

            errorMessage.textContent =
                message;

            errorMessage.style.display =
                "block";
        };
    
    map.addEventListener(
        "mousemove",
        event => {
            if (
                systemTooltip.style.display
                !== "block"
            ) {
                return;
            }
    
            const offset = 14;
    
            let left =
                event.clientX
                + offset;
    
            let top =
                event.clientY
                + offset;
    
            const tooltipRect =
                systemTooltip
                .getBoundingClientRect();
    
            if (
                left
                + tooltipRect.width
                > window.innerWidth
            ) {
                left =
                    event.clientX
                    - tooltipRect.width
                    - offset;
            }
    
            if (
                top
                + tooltipRect.height
                > window.innerHeight
            ) {
                top =
                    event.clientY
                    - tooltipRect.height
                    - offset;
            }
    
            systemTooltip.style.left =
                `${left}px`;
    
            systemTooltip.style.top =
                `${top}px`;
        }
    );
    
    map.addEventListener(
        "mouseout",
        event => {
            const system =
                event.target.closest(
                    ".star-system"
                );                                                                                                      
    
            if (!system) {
                return;
            }
    
            const relatedSystem =
                event.relatedTarget
                ?.closest?.(
                    ".star-system"
                );
    
            if (
                relatedSystem
                === system
            ) {
                return;
            }
    
            systemTooltip.style.display =
                "none";
        }
    );
            
    map.addEventListener(
        "mouseover",
        event => {
            const system =
                event.target.closest(
                    ".star-system"
                );
    
            if (!system) {
                return;
            }
    
            const text =
                system.dataset.tooltip;
    
            if (!text) {
                return;
            }
    
            systemTooltip.textContent =
                text;
    
            systemTooltip.style.display =
                "block";
        }
    );    

    scrollArea.addEventListener(
        "wheel",
        event => {

            if (!event.ctrlKey) {
                return;
            }

            event.preventDefault();

            const rect =
                scrollArea
                .getBoundingClientRect();

            const mouseX =
                event.clientX
                - rect.left;

            const mouseY =
                event.clientY
                - rect.top;

            const mapX =
                (
                    scrollArea.scrollLeft
                    + mouseX
                )
                / zoom;

            const mapY =
                (
                    scrollArea.scrollTop
                    + mouseY
                )
                / zoom;

            if (
                event.deltaY < 0
            ) {
                setZoom(
                    zoom * zoomStep
                );
            }
            else {
                setZoom(
                    zoom / zoomStep
                );
            }

            scrollArea.scrollLeft =
                mapX * zoom
                - mouseX;

            scrollArea.scrollTop =
                mapY * zoom
                - mouseY;
        },
        {
            passive: false
        }
    );

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "+"
                || event.key === "="
            ) {
                event.preventDefault();

                setZoom(
                    zoom * zoomStep
                );

                return;
            }

            if (
                event.key === "-"
            ) {
                event.preventDefault();

                setZoom(
                    zoom / zoomStep
                );

                return;
            }

            if (
                event.key === "0"
            ) {
                event.preventDefault();

                setZoom(
                    1.0
                );
            }
        }
    );

    document.body.tabIndex = 0;
    document.body.focus();

    updateZoom();
</script>

</body>
</html>
"""

    def onWebViewLoaded(self, event):
        """Initialize the permanent viewer."""

        if not self.webViewReady:
            self.webViewReady = True

            self.loadViewer()

            event.Skip()
            return

        if self.viewerLoading:
            self.viewerLoading = False
            self.viewerLoaded = True

            self.displayPendingSvg()

        event.Skip()

    def loadViewer(self):
        """Load the permanent HTML viewer once."""

        if self.viewerLoading:
            return

        if self.viewerLoaded:
            return

        self.viewerLoading = True

        self.webView.SetPage(
            self.createViewerDocument(),
            "",
        )

    def displayPendingSvg(self):
        """Replace only the SVG content."""

        if not self.viewerLoaded:
            return

        if self.pendingSvgContent is None:
            return

        svgContent = (
            self.pendingSvgContent
        )

        self.pendingSvgContent = None

        script = (
            "window.replaceMapSvg("
            f"{json.dumps(svgContent)}"
            ");"
        )

        self.webView.RunScript(
            script
        )

    def showError(self, message):
        """Display an error without recreating the viewer."""

        if not self.viewerLoaded:
            print(
                "SVG preview error:",
                message,
            )
            return

        script = (
            "window.showMapError("
            f"{json.dumps(message)}"
            ");"
        )

        self.webView.RunScript(
            script
        )

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

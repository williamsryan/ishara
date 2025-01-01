from dash import html

class Header:
    def __init__(self):
        self.title = "📊 Ishara Data Platform"

    def render(self):
        return html.Div(
            html.H3(self.title, className="text-center text-light bg-dark p-3")
        )
    
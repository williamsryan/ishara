from dash import html

class Header:
    def __init__(self):
        self.title = "📊 Ishara Trading Platform"

    def render(self):
        return html.Div(
            html.H2(self.title, className="text-center text-light bg-dark p-3")
        )
    
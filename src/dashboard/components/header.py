from dash import html, dcc

class Header:
    def render(self):
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("Ishara Trading Dashboard", className="text-light"),
                        html.Div(
                            [
                                dcc.Link("Login", href="/auth/login", className="btn btn-outline-light me-2"),
                                dcc.Link("Logout", href="/auth/logout", className="btn btn-outline-light"),
                            ],
                            className="d-flex",
                        ),
                    ],
                    className="d-flex justify-content-between align-items-center",
                )
            ],
            className="container-fluid bg-dark py-3",
        )
    
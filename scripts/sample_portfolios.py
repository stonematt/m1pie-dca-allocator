from decimal import Decimal

EXAMPLE_PORTFOLIO = {
    "name": "example",
    "type": "pie",
    "value": Decimal("3009.3"),
    "children": {
        "Kholinar": {
            "type": "pie",
            "value": Decimal("1833.72"),
            "children": {
                "TSLA": {"type": "ticker", "value": Decimal("950.0")},
                "NVDA": {"type": "ticker", "value": Decimal("883.72")},
            },
        },
        "Urithiru": {
            "type": "pie",
            "value": Decimal("874.34"),
            "children": {
                "Windrunners": {
                    "type": "pie",
                    "value": Decimal("374.34"),
                    "children": {
                        "MSFT": {"type": "ticker", "value": Decimal("200.0")},
                        "GOOG": {"type": "ticker", "value": Decimal("174.34")},
                    },
                },
                "Bondsmiths": {
                    "type": "pie",
                    "value": Decimal("300.0"),
                    "children": {
                        "V": {"type": "ticker", "value": Decimal("150.0")},
                        "MA": {"type": "ticker", "value": Decimal("150.0")},
                    },
                },
                "AMZN": {"type": "ticker", "value": Decimal("200.0")},
            },
        },
        "ShatteredPlains": {
            "type": "pie",
            "value": Decimal("301.24"),
            "children": {
                "APP": {"type": "ticker", "value": Decimal("94.06")},
                "MELI": {"type": "ticker", "value": Decimal("72.16")},
                "PAYC": {"type": "ticker", "value": Decimal("70.71")},
                "BAM": {"type": "ticker", "value": Decimal("68.27")},
            },
        },
    },
}

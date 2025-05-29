# M1 Pie DCA Allocator

This project provides a structured workflow for allocating new investments into an M1 Finance portfolio composed of nested "pies" and individual tickers. It supports pie-of-pies hierarchies, dollar-cost averaging (DCA), and integration with OpenAI's GPT-4 Vision API to parse portfolio composition from screenshots.

---

## 🔧 Features

- 🧠 Vision-based OCR using GPT-4o to extract pie compositions
- 🧮 Smart DCA allocation logic across existing and new slices
- 📁 Recursive data structure supporting pies and tickers
- 💾 JSON-based persistence with type annotations
- ⚙️ Ready for notebook and Streamlit environments

---

## 🗂️ Example: `portfolio.json`

```json
{
  "name": "main",
  "type": "pie",
  "value": 3009.3,
  "children": {
    "FRB23Q1": {
      "type": "pie",
      "value": 1833.72,
      "children": {
        "TSLA": { "type": "ticker", "value": 950.0 },
        "NVDA": { "type": "ticker", "value": 883.72 }
      }
    },
    "RB21Q4": {
      "type": "pie",
      "value": 874.34,
      "children": {
        "AAPL": { "type": "ticker", "value": 874.34 }
      }
    },
    "FB25-4": {
      "type": "pie",
      "value": 301.24,
      "children": {
        "APP": { "type": "ticker", "value": 94.06 },
        "MELI": { "type": "ticker", "value": 72.16 },
        "PAYC": { "type": "ticker", "value": 70.71 },
        "BAM": { "type": "ticker", "value": 68.27 }
      }
    }
  }
}
```

---

## 📦 Requirements

See [`requirements.txt`](./requirements.txt) for a minimal environment spec.

---

## 🚧 Roadmap

- Add DCA allocation preview and transaction outputs
- Integrate with Storj.io for secure S3 persistence
- Build full Streamlit UI on top of current Jupyter POC

---

## 🔑 API Usage

This project uses `streamlit.secrets` for OpenAI key management.  
Add your key to `~/.streamlit/secrets.toml`:

```toml
[openai]
api_key = "sk-..."
```

---

## 🧠 Author & License

Maintained by [@stonematt](https://github.com/stonematt)  
MIT License

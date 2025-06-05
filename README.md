# M1 Pie DCA Allocator

Structured portfolio modeling for M1 Finance investors. This tool helps users allocate funds across nested "pie-of-pies" structures, visualize adjustments, and persist data using browser cookies. Powered by GPT-4o Vision to extract portfolio snapshots from screenshots.

---

## 🔧 Features

- 🧠 Vision OCR: Parse M1 screenshots using GPT-4o
- 🧮 Smart DCA: Adjust allocations using a weighted strategy
- 🧱 Recursive structure: Supports pies within pies, and tickers
- 🧁 Classification: Differentiates between tickers and pie folders
- 📸 Image cache and re-parse control
- 🍪 Client-side persistence: Uses browser cookies for data storage
- 📊 Side-by-side charts and review tables
- 📉 Weight-based portfolio normalization
- ⚙️ Toggleable logging level from UI

---

## 🖼️ Upload & Parse Screenshots

Upload `.png`, `.jpg`, or `.jpeg` screenshots from M1 Finance. The app extracts portfolio composition using OpenAI's GPT-4o Vision model. Each image is hashed and cached to avoid redundant parsing.

```json
{
  "FRB23Q1": { "type": "pie", "value": 1833.72 },
  "RB21Q4": { "type": "pie", "value": 874.34 },
  "FB25-4": { "type": "pie", "value": 301.24 }
}
```

Re-parsing is supported with a checkbox toggle. Parsed slices replace the current portfolio state.

---

## 🗂️ Example Portfolio (Expanded)

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

## 💸 Dollar-Cost Averaging (DCA)

Input:

- New capital amount
- % allocation to new vs existing tickers
- Target number of new tickers

Output:

- Adjusted portfolio with new positions and updated weights
- Pie charts comparing original vs adjusted allocation
- Table of capital distribution, formatted with currency

---

## 💾 Persistence & Cookies

All portfolio data is compressed and stored in real browser cookies via `extra-streamlit-components`. No server-side storage is used.

- Auto-saves on image parse or adjustment
- Reloads last session portfolio automatically
- Warns if data exceeds cookie storage limits (~4KB)

---

## 🔑 API Usage

Create a `~/.streamlit/secrets.toml` file to store your OpenAI API key:

```toml
[openai]
api_key = "sk-..."
```

---

## 📦 Requirements

Python 3.11+, with minimal environment specified in [`requirements.txt`](./requirements.txt).

Install via pip:

```bash
pip install -r requirements.txt
```

---

## 📍 Roadmap

- Replace portfolio on upload instead of merging (in progress)
- Responsive layout optimization
- CSV export of DCA transactions
- Optional integration with cloud persistence (e.g. Storj, S3)

---

## 🧠 Author & License

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Z8Z41G13PX)

Maintained by [@stonematt](https://github.com/stonematt)  
Licensed under the MIT License

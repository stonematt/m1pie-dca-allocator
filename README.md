# m1pie-dca-allocator

m1-pie-dca

# JSON Data Structure

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

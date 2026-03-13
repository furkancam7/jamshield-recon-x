# P9 - EW Risk Map

## Summary

- P8 mission continuity closure kabul edilir; P9 mevcut vertical-slice ustune taktik EW risk farkindaligi ekler.
- Bu faz tactical-only kalir; `trust_engine`, `localization_fusion`, ve `mission_continuity` karar otoriteleri degismez.
- Canli pose history eklenmeyecek; risk grid mevcut `mission_timeline` ve rota geometrisi uzerinden deterministic route-progress interpolasyonu ile uretilecek.

## Implementation Targets

- Yeni `ew_risk_map` config bloku: grid geometry, decay, evidence weights, ve corridor-cost sampling parametreleri.
- Yeni taktik artifact: her scenario icin `*_ew_risk_map.json`.
- Report/summary schema `2.2`: EW alanlari zorunlu olacak.
- Yeni run-level bundle: `ew_metrics.json`, `ew_metrics.md`, `ew_metrics.csv`.
- Regression seti `s19_ew_mid_route_denial_hotspot` ve `s20_ew_decay_after_recovery` ile genisleyecek.

## Acceptance Gates

- Risk map senaryoya anlamli tepki veriyor.
- Repeated run ayni `risk_cells_hash` uretiyor.
- Nominal false marking configured floor altinda kaliyor.
- Corridor cost nominal < degraded < denied sirasini koruyor.
- EW artifacts ve schema `2.2` mixed-run kabul etmiyor.

## Known Constraints

- Route-relative pseudo-position sadelestirmesi gercek pose history yerine gecmez; bu bilincli bir P9 kisitidir.
- EW outputs runtime autonomy loop'una geri beslenmeyecek.
- P7 calibration residual gap bu faz icin blocker degildir; ayri tuning takibi olarak kalir.

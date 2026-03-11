# Faz 4 Backlog: VIO Health Upgrade

## Amaç

`vio_healthy=True/False` ikili yapısını, mission continuity ve regression için daha anlamlı, ölçülebilir ve açıklanabilir bir VIO health sözleşmesine dönüştürmek.

## Neden Şimdi

Faz 3 ile config, artifact ve determinism disiplini kapandı. Bundan sonra VIO health modelini derinleştirmek güvenli hale geldi; çünkü yeni davranışların kanıtı schema-validated artifacts ve regression gates üzerinden izlenebilir.

## Public Contract

Faz 4 sonunda VIO tarafında aşağıdaki kamuya açık sözleşme beklenir:

- `vio_state: good | weak | lost`
- `vio_health_score: float` aralık `0.0-1.0`
- `effective_vio_state: good | weak | lost`
- `vio_healthy: bool` geçici compatibility alanı, deprecated

### Contract Kuralları

- `vio_state` kategorik yorum katmanıdır ve explainability içindir.
- `vio_health_score` sürekli sağlık skorudur ve metric/tuning tarafı içindir.
- `effective_vio_state`, karar motorunun kullandığı tekil VIO health sonucudur.
- `vio_healthy` doğrudan üretilmeyecek; compatibility için `effective_vio_state != "lost"` kuralından türetilecektir.

## Decision Logic

### Score-to-State Eşleme

- `score >= 0.75 => good`
- `0.40 <= score < 0.75 => weak`
- `score < 0.40 => lost`

### Çatışma Kuralı

`vio_state` ve `vio_health_score` eşit otorite kabul edilir.

Karar kuralı:

`effective_vio_state = worse(reported_vio_state, score_bucket(vio_health_score))`

Buradaki `worse` sıralaması:

`good < weak < lost`

### Örnekler

- `vio_state=good`, `score=0.85` => `effective_vio_state=good`
- `vio_state=weak`, `score=0.55` => `effective_vio_state=weak`
- `vio_state=lost`, `score=0.20` => `effective_vio_state=lost`
- `vio_state=good`, `score=0.30` => score bucket `lost`, sonuç `effective_vio_state=lost`
- `vio_state=lost`, `score=0.82` => score bucket `good`, sonuç `effective_vio_state=lost`

## Mission Continuity Entegrasyonu

Faz 4 sonunda mission continuity karar katmanı:

- ham `vio_healthy` alanını ana giriş olarak kullanmayacak,
- `vio_state`, `vio_health_score` ve `effective_vio_state` tüketecek,
- fallback izinlerini `effective_vio_state` üzerinden değerlendirecek.

Beklenen karar yönü:

- `effective_vio_state=good`: denied senaryoda fallback devamı mümkün
- `effective_vio_state=weak`: fallback koşullu ve daha temkinli
- `effective_vio_state=lost`: fallback reddedilir, safe-hold veya abort yönü değerlendirilir

Bu fazda tam production state machine yeniden yazılmayacak; yalnızca VIO health'e duyarlı hale getirilecektir.

## Scenario Matrix

Faz 4 için minimum senaryo matrisi:

| Senaryo | Raporlanan VIO | Score | Beklenen effective state | Beklenen sonuç yönü |
| --- | --- | --- | --- | --- |
| denied + healthy fallback | `good` | `0.85` | `good` | fallback izinli |
| denied + degraded fallback | `weak` | `0.55` | `weak` | fallback kısıtlı / degrade karar |
| denied + failed fallback | `lost` | `0.20` | `lost` | fallback reddi |
| çatışmalı vaka 1 | `good` | `0.30` | `lost` | en kötü durum uygulanır |
| çatışmalı vaka 2 | `lost` | `0.82` | `lost` | en kötü durum uygulanır |

Opsiyonel genişleme vakaları:

- degraded GNSS + weak VIO
- nominal GNSS + lost VIO
- denied GNSS + weak VIO + sync bozulması

## Regression Plan

Faz 4 regression kapsamı en az şu kontrolleri içermelidir:

- denied + `good` ile denied + `lost` farklı karar veriyor
- denied + `weak` ara davranış üretiyor
- iki çatışmalı vaka `effective_vio_state` için `en kötüyü al` kuralını doğruluyor
- `vio_healthy` compatibility alanı `effective_vio_state` ile tutarlı
- mevcut Faz 3 gates bozulmuyor: schema, determinism, config, artifact completeness

Ek testler:

- unit test: score bucket eşleme
- unit test: `worse()` kuralı
- unit test: compatibility dönüşümü
- regression test: denied scenario karar ayrışması

## Issue Listesi

- Replace binary `vio_healthy` contract with `vio_state`, `vio_health_score`, and `effective_vio_state`
- Add score-to-state mapping and worst-case conflict resolution
- Keep `vio_healthy` as deprecated compatibility field derived from `effective_vio_state`
- Update mission continuity inputs to consume structured VIO health
- Add denied scenario variants for `good`, `weak`, `lost`
- Add regression checks for conflicting categorical and numeric VIO health inputs
- Extend artifacts to record `effective_vio_state`
- Document Faz 4 VIO health semantics and compatibility rules

## Exit Gate

Faz 4 ancak şu şartlarda kapanır:

- Binary VIO health ana sözleşme olmaktan çıktı
- `vio_state`, `vio_health_score` ve `effective_vio_state` artifacts içinde kayıtlı
- Mission continuity kararları `effective_vio_state` değişimine tepki veriyor
- Çatışmalı vakalarda `en kötüyü al` kuralı testle doğrulanıyor
- `vio_healthy` compatibility alanı türetilmiş ve deprecated olarak işaretlenmiş
- Regression suite Faz 4 varyasyonlarını yakalıyor

## Faz 5'e Devredenler

Faz 4 kapanınca Faz 5 için hazır olacak şeyler:

- gerçek VIO metric producer için hedef contract
- trust katmanına aktarılacak VIO health semantics
- replay ve evaluation artifacts içinde okunabilir VIO health temeli

# JamShield Recon-X Progress Tracker

## Kullanım Kuralları

- Bu dosya yaşayan çalışma kaydıdır.
- Her faz yalnızca şu durumlardan birini alır: `Yapılmadı`, `Devam Ediyor`, `Bloklu`, `Tamamlandı`.
- Checklist tikleri yalnızca doğrulanmış iş için atılır.
- Faz kapanışı, ilgili `Exit Gate Doğrulamaları` tamamlanmadan verilmez.
- Her önemli güncelleme `Değişiklik Günlüğü` bölümüne tarihli eklenir.

## Genel Durum Özeti

- Son güncelleme: `2026-03-11`
- Çalışma referansı: `Faz 2 sonu / Faz 3 başı`
- Aktif faz: `Faz 3 - Config and Artifact Hardening`
- Ana hedef: `Simulation Production` omurgasını kapatmak
- Bu dosyanın amacı: ne yapıldı, ne eksik, ne bloklu, hangi kanıtla ilerliyoruz sorularını tek yerde tutmak

## Faz Durum Tablosu

| Faz | Ad | Durum | Son Güncelleme | Kanıt | Eksik Kapı |
| --- | --- | --- | --- | --- | --- |
| 0 | Architecture Lock | Tamamlandı | 2026-03-11 | `docs/architecture/terminology-lock.md`, `docs/decisions/ADR-001..003` | Periyodik docs drift kontrolü |
| 1 | First Executable Vertical Slice | Tamamlandı | 2026-03-11 | `src/scenario_orchestrator/main.py`, `scripts/smoke_test.sh` | Büyük refactor sonrası smoke re-validation |
| 2 | Determinism and Regression Baseline | Tamamlandı | 2026-03-11 | `scripts/run_regression.sh`, `src/evaluation/summary_report.py` | Regression kapsamını büyütme ihtiyacı |
| 3 | Config and Artifact Hardening | Devam Ediyor | 2026-03-11 | `src/evaluation/artifact_schema.py`, `configs/sim/default.yaml` | Faz kapanış review ve sign-off |
| 4 | VIO Health Upgrade | Yapılmadı | - | - | Faz başlamadı |
| 5 | Real VIO Metric Skeleton | Yapılmadı | - | - | Faz başlamadı |
| 6 | Localization Fusion | Yapılmadı | - | - | Faz başlamadı |
| 7 | Trust Engine Maturity | Yapılmadı | - | - | Faz başlamadı |
| 8 | Mission Continuity V2 | Yapılmadı | - | - | Faz başlamadı |
| 9 | EW Risk Map | Yapılmadı | - | - | Faz başlamadı |
| 10 | Tactical Summary | Yapılmadı | - | - | Faz başlamadı |
| 11 | Replay and Evaluation Hardening | Yapılmadı | - | - | Faz başlamadı |
| 12 | ROS2 Runtime Migration | Yapılmadı | - | - | Faz başlamadı |
| 13 | Deployment and Operations Hardening | Yapılmadı | - | - | Faz başlamadı |
| 14 | Hardware-Portability Layer | Yapılmadı | - | - | Faz başlamadı |
| 15 | Field Transition Preparation | Yapılmadı | - | - | Faz başlamadı |

## Aktif Faz Detayı

### Faz 3 - Config and Artifact Hardening

**Amaç**

Davranışı config-driven yapmak ve artifact sözleşmesini sabitlemek.

**Durum**

`Devam Ediyor`

**Checklist - Yapılacaklar**

- [x] Threshold ve policy değerlerini config dosyasına taşı
- [x] `config_id` alanını evaluation artifacts içine ekle
- [x] `software_revision` alanını evaluation artifacts içine ekle
- [x] Stable report schema tanımla
- [x] Stable summary schema tanımla
- [x] Scenario metadata completeness check ekle
- [x] Repeated determinism unit/regression doğrulamasını ekle
- [x] Nominal minimum trust regression gate ekle
- [x] Denied allowed mission-state gate ekle
- [ ] Faz 3 kapanış kanıt setini tek blok altında özetle
- [ ] Faz 3 sign-off sonrası Faz 4 backlog’unu aç

**Checklist - Exit Gate Doğrulamaları**

- [x] Config davranışı kontrol ediyor
- [x] Artifact’tan run koşulları geri okunabiliyor
- [x] `config_id` ve `software_revision` kayıtlı
- [x] Schema sabit ve doğrulanıyor
- [x] Aynı senaryo iki kez aynı mantıksal artifact sonucunu veriyor
- [ ] Faz kapanış kararı yazılı olarak kaydedildi

**Tamamlananlar**

- `report` ve `summary` artifacts için schema validation eklendi
- Config yükleme modeli ve default sim config tanımlandı
- Scenario metadata zorunlu hale getirildi
- Regression ve unit test seti faz 3 ihtiyaçlarına göre genişletildi

**Eksikler**

- Faz 3 kapanış notunun ayrı bir kapanış kaydı halinde yazılması
- Faz 4 için ayrıntılı issue/backlog kırılımının tracker’a açılması

**Kanıt / Artifact**

- `src/evaluation/artifact_schema.py`
- `configs/sim/default.yaml`
- `tests/unit/test_config_and_artifacts.py`
- `tests/unit/test_execution_consistency.py`
- `artifacts/runs/phase3_validation/`

**Riskler**

- Faz 3 teknik olarak bitmiş görünse bile kapanış review yapılmadan “kapandı” kabul edilmesi
- Yeni alanlar eklendikçe schema version disiplininin unutulması

**Sonraki Adım**

Faz 3 kapanış notunu yaz, kanıtları bağla, ardından Faz 4 için VIO health contract seçeneklerini aç.

## Faz Kartları

### Faz 0 - Architecture Lock

**Amaç**

Terminoloji, authority boundary ve truth boundary’yi kilitlemek.

**Durum**

`Tamamlandı`

**Checklist - Yapılacaklar**

- [x] Terminology lock oluştur
- [x] Mission/trust authority ayrımını ADR’lerde sabitle
- [x] `/truth/*` evaluation-only kuralını yaz
- [x] Docs consistency sweep yap

**Checklist - Exit Gate Doğrulamaları**

- [x] Ortak terminoloji yazılı
- [x] Authority boundary net
- [x] Truth boundary net

**Tamamlananlar**

- Terminoloji ve mimari karar dokümanları oluşturuldu

**Eksikler**

- Major refactor sonrası tekrar docs drift taraması gerekebilir

**Kanıt / Artifact**

- `docs/architecture/terminology-lock.md`
- `docs/decisions/ADR-001-ground-truth-is-evaluation-only.md`
- `docs/decisions/ADR-002-deterministic-mission-continuity.md`
- `docs/decisions/ADR-003-trust-engine-as-separate-service.md`

**Riskler**

- Kod ilerledikçe dokümanın eski kalması

**Sonraki Adım**

Faz 0 çıktıları, sonraki tüm fazlarda terminoloji referansı olarak kullanılacak.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| 2026-03-11 | Faz 0 repo referansları doğrulandı | Yeni blocker yok | Yok | Refactor sonrası yeniden doğrula |

### Faz 1 - First Executable Vertical Slice

**Amaç**

İlk çalışan uçtan uca akışı kurmak.

**Durum**

`Tamamlandı`

**Checklist - Yapılacaklar**

- [x] Scenario manifest loader
- [x] Scenario orchestrator
- [x] GNSS trust v1
- [x] Mission continuity v1
- [x] Evaluation report v1
- [x] Smoke test

**Checklist - Exit Gate Doğrulamaları**

- [x] Uçtan uca akış çalışıyor
- [x] Nominal normal bitiyor
- [x] Denied normal bitmiyor
- [x] Report üretiliyor

**Tamamlananlar**

- İlk gerçek çalışan vertical slice hazırlandı

**Eksikler**

- Smoke test kapsama alanı uzun vadede yetersiz kalacak

**Kanıt / Artifact**

- `src/scenario_orchestrator/main.py`
- `src/gnss_trust/trust_service.py`
- `src/mission_continuity/state_machine.py`
- `scripts/smoke_test.sh`

**Riskler**

- Vertical slice’in v1 sadeleştirmelerini üretim kuralı sanmak

**Sonraki Adım**

Repeatability ve regression kapsamı korunmalı.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| 2026-03-11 | Faz 1 çıktıları repo üzerinde doğrulandı | Yeni blocker yok | Yok | Smoke testleri periyodik tekrar koştur |

### Faz 2 - Determinism and Regression Baseline

**Amaç**

Repeatable baseline ve regression gate kurmak.

**Durum**

`Tamamlandı`

**Checklist - Yapılacaklar**

- [x] Regression runner
- [x] Artifact checker
- [x] Summary JSON/MD
- [x] Repeated-run consistency
- [x] PASS/FAIL üretimi

**Checklist - Exit Gate Doğrulamaları**

- [x] Aynı input aynı mantıksal sonucu veriyor
- [x] Regression PASS/FAIL üretiyor
- [x] Summary artifact oluşuyor
- [x] Required artifacts kontrol ediliyor

**Tamamlananlar**

- Regression ve summary altyapısı kuruldu

**Eksikler**

- Regression senaryo kapsamı ileride büyütülmeli

**Kanıt / Artifact**

- `scripts/run_regression.sh`
- `scripts/check_artifacts.sh`
- `src/evaluation/regression_compare.py`
- `src/evaluation/summary_report.py`

**Riskler**

- Mevcut regression setinin az sayıda baseline senaryoya dayanması

**Sonraki Adım**

Faz 3 artifact disiplinini tam kapat.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| 2026-03-11 | Faz 2 regression altyapısı repo üzerinde doğrulandı | Kapsam hâlâ dar | Yok | Faz 3 sonrası senaryo setini genişlet |

### Faz 3 - Config and Artifact Hardening

**Amaç**

Config-driven behavior ve stable artifacts.

**Durum**

`Devam Ediyor`

**Checklist - Yapılacaklar**

- [x] Config yükleme modeli ekle
- [x] Stable artifact schema ekle
- [x] Versioned metadata ekle
- [x] Scenario metadata zorunlu kıl
- [ ] Faz kapanış notunu yaz
- [ ] Faz 4 backlog’unu aç

**Checklist - Exit Gate Doğrulamaları**

- [x] Config behavior’ı kontrol ediyor
- [x] Artifacts versioned
- [x] Schema sabit
- [x] Determinism korunuyor
- [ ] Faz kapatma review’u yazılı

**Tamamlananlar**

- Aktif faz detayı bölümüne bak

**Eksikler**

- Aktif faz detayı bölümüne bak

**Kanıt / Artifact**

- Aktif faz detayı bölümüne bak

**Riskler**

- Aktif faz detayı bölümüne bak

**Sonraki Adım**

- Aktif faz detayı bölümüne bak

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| 2026-03-11 | Config/artifact hardening altyapısı eklendi | Faz kapanış notu henüz yazılmadı | Yok | Faz 3 sign-off hazırla |

### Faz 4 - VIO Health Upgrade

**Amaç**

VIO health modelini binary yapıdan çıkarıp anlamlı hale getirmek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] `vio_state` veya `vio_health_score` sözleşmesini seç
- [ ] Mission continuity entegrasyonunu tasarla
- [ ] Yeni regression senaryolarını ekle
- [ ] VIO semantics dokümanını yaz

**Checklist - Exit Gate Doğrulamaları**

- [ ] Binary VIO health kaldırıldı veya uyumluluk katmanına alındı
- [ ] Mission decisions VIO state’e tepki veriyor
- [ ] Regression bunu doğruluyor

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Erken fazda aşırı VIO derinliğine gömülmek

**Sonraki Adım**

Faz 3 kapandıktan sonra contract kararını netleştir.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 5 - Real VIO Metric Skeleton

**Amaç**

Gerçek VIO metric producer iskeletini kurmak.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Preprocessing skeleton
- [ ] Feature extraction skeleton
- [ ] Matching skeleton
- [ ] Pose delta skeleton
- [ ] IMU propagation stub
- [ ] Replay-readable metrics

**Checklist - Exit Gate Doğrulamaları**

- [ ] Metricler gerçek pipeline’dan geliyor
- [ ] Placeholder kaldırıldı
- [ ] Trust katmanı metric tüketebiliyor

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Skeleton’ın kalıcı placeholder’a dönüşmesi

**Sonraki Adım**

Önce Faz 4’ü kapat.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 6 - Localization Fusion

**Amaç**

GNSS ve VIO’yu confidence-aware biçimde birleştirmek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Fusion service
- [ ] Mode manager
- [ ] Weighting logic
- [ ] Confidence output
- [ ] Hysteresis ve oscillation guard

**Checklist - Exit Gate Doğrulamaları**

- [ ] Modlar kararlı
- [ ] Oscillation kontrol altında
- [ ] Localization confidence anlamlı

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Fusion yerine sert source switching

**Sonraki Adım**

VIO metric ve health modeli oturmadan başlama.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 7 - Trust Engine Maturity

**Amaç**

Merkezi ve explainable trust katmanını kurmak.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Trust aggregation
- [ ] Mission confidence computation
- [ ] Reason codes
- [ ] Calibration analysis

**Checklist - Exit Gate Doğrulamaları**

- [ ] Mission confidence gerçek inputlara dayanıyor
- [ ] Trust düşüşü explainable
- [ ] Calibration ölçülebiliyor

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Trust engine’in mission decision ile karıştırılması

**Sonraki Adım**

Önce fusion fazını kapat.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 8 - Mission Continuity V2

**Amaç**

Karar motorunu hardened üretim davranışına taşımak.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Timeout logic
- [ ] Escalation
- [ ] Sustain rules
- [ ] Audit log
- [ ] Reason codes
- [ ] Oscillation detection

**Checklist - Exit Gate Doğrulamaları**

- [ ] Mission progression stabil
- [ ] Audit trail yeterli
- [ ] State flapping kontrol altında

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Aşırı karmaşık state machine

**Sonraki Adım**

Önce Faz 7 güven resmini tamamla.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 9 - EW Risk Map

**Amaç**

Mekansal EW risk farkındalığı üretmek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Risk grid
- [ ] Accumulation logic
- [ ] Zone marking
- [ ] Temporal decay
- [ ] Corridor cost export
- [ ] EW metrics

**Checklist - Exit Gate Doğrulamaları**

- [ ] Risk map senaryoya tepki veriyor
- [ ] Spatial consistency var
- [ ] False marking ölçülüyor

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Deterministik olmayan spatial çıktı

**Sonraki Adım**

Önce mission continuity v2 kapansın.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 10 - Tactical Summary

**Amaç**

Operatöre yorumlanmış karar özeti vermek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Summary schema
- [ ] Compact JSON
- [ ] Markdown/text summary
- [ ] Recommended action
- [ ] Mission/EW özeti

**Checklist - Exit Gate Doğrulamaları**

- [ ] Summary runtime ile tutarlı
- [ ] Baseline senaryolarda anlamlı
- [ ] Recommendation anlaşılır

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- UI süsü sanılıp runtime gerçekliğinden kopması

**Sonraki Adım**

Önce Faz 9 risk girdisini üret.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 11 - Replay and Evaluation Hardening

**Amaç**

Sistemi analiz edilebilir evaluation platformuna çevirmek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Replay bookmarks
- [ ] Timeline compare
- [ ] Config/revision diff
- [ ] Continuity metrics
- [ ] Reaction time metrics
- [ ] Correctness metrics

**Checklist - Exit Gate Doğrulamaları**

- [ ] Replay ile root cause bulunabiliyor
- [ ] Comparison tooling stabil
- [ ] Metrikler gerçek

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Fazla metric, düşük açıklayıcılık

**Sonraki Adım**

Önce tactical katmanın çıktıları oluşsun.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 12 - ROS2 Runtime Migration

**Amaç**

Script akışını node-based runtime’a geçirmek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Message contracts
- [ ] Node decomposition
- [ ] Topic wiring
- [ ] Truth boundary enforcement
- [ ] Logger/evaluation separation

**Checklist - Exit Gate Doğrulamaları**

- [ ] Runtime/evaluation ayrımı korunuyor
- [ ] Mission continuity tek otorite
- [ ] Node graph stabil

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- ROS2’ye erken atlayıp sistemi dağıtmak

**Sonraki Adım**

Önce replay/evaluation hardening fazı kapansın.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 13 - Deployment and Operations Hardening

**Amaç**

Sistemi yeniden kurulabilir ve CI ile yönetilebilir hale getirmek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Docker/devcontainer
- [ ] Bootstrap standardization
- [ ] CI unit/regression gates
- [ ] Lint/formatting gates
- [ ] Release notes
- [ ] Hardened runbooks

**Checklist - Exit Gate Doğrulamaları**

- [ ] Yeni makinede kurulum tekrarlanabiliyor
- [ ] CI anlamlı fail ediyor
- [ ] Release candidate üretilebiliyor

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- CI’nin yalnızca formaliteye dönüşmesi

**Sonraki Adım**

Önce runtime gövdesi otursun.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 14 - Hardware-Portability Layer

**Amaç**

Gerçek donanıma geçişte mimari kırılmayı önlemek.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] Sensor adapter interfaces
- [ ] Timing contracts
- [ ] Rate assumptions
- [ ] Onboard/ground split notes
- [ ] Portability docs

**Checklist - Exit Gate Doğrulamaları**

- [ ] Sim bağımlılıkları adapter arkasında
- [ ] Gerçek sensör bağlanma noktaları net
- [ ] Portability plan yazılı

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Portability’nin sadece doküman düzeyinde kalması

**Sonraki Adım**

Önce deployment ve runtime disiplini tamamlanmalı.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

### Faz 15 - Field Transition Preparation

**Amaç**

Saha geçişini plansızlıktan kurtarmak.

**Durum**

`Yapılmadı`

**Checklist - Yapılacaklar**

- [ ] HIL roadmap
- [ ] Sensor replacement matrix
- [ ] Calibration plan
- [ ] Sync validation plan
- [ ] Safety constraints
- [ ] Manual override strategy
- [ ] Field checklist

**Checklist - Exit Gate Doğrulamaları**

- [ ] Entegrasyon sırası net
- [ ] Calibration plan hazır
- [ ] Safety playbook hazır
- [ ] HIL planı yazılı

**Tamamlananlar**

- Henüz başlanmadı

**Eksikler**

- Fazın tamamı

**Kanıt / Artifact**

- Henüz yok

**Riskler**

- Safety ve override stratejisinin geç ele alınması

**Sonraki Adım**

Önce portability layer kapansın.

**Günlük Log**

| Tarih | Ne Yapıldı | Ne Çıkmadı | Blocker | Sonraki Adım |
| --- | --- | --- | --- | --- |
| - | - | - | - | Faz başlamadı |

## Eksik Listesi

- Faz 3 kapanış notu yazılmadı
- Faz 4 backlog kırılımı henüz açılmadı
- Faz 4+ için execution yok, yalnızca roadmap var

## Blocker Listesi

- Şu anda kayıtlı aktif blocker yok
- İlk muhtemel blocker: Faz 4 için `vio_state` mi `vio_health_score` mu seçileceği

## Karar Notları

- `Simulation Production first` ilkesi korunacak
- Faz geçişleri yalnızca kapı doğrulamasıyla yapılacak
- ROS2 migration erken başlatılmayacak
- VIO derinliği, Faz 3 kapanmadan ana çalışma alanı olmayacak

## Değişiklik Günlüğü

| Tarih | Değişiklik |
| --- | --- |
| 2026-03-11 | `master-plan.md` ile uyumlu ilk progress tracker oluşturuldu |
| 2026-03-11 | Başlangıç durumu `Faz 2 sonu / Faz 3 başı` olarak sabitlendi |

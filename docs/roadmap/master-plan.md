# JamShield Recon-X Ana Yol Haritası

## Özet

Bu doküman JamShield Recon-X projesini Faz 0 ile Faz 15 arasında uygulanabilir ve kapı kontrollü bir sıraya koyar. Amaç, projeyi parçalara ayırmak, her fazın neden şimdi yapılacağını netleştirmek, her fazın sonunda hangi somut sonuca ulaşıldığında bir sonraki faza geçilebileceğini kayıt altına almaktır.

Bu yol haritası iki sabit ilkeye dayanır:

- Önce `Simulation Production`, sonra `Field Production`.
- Önce güvenilir omurga, sonra derinlik, sonra entegrasyon.

## Çalışma Prensipleri

- Bir faz kapanmadan sonraki fazın kritik işlerine geçilmez.
- Her faz en az bir doğrulanabilir kanıt üretir: kod, test, artifact, rapor veya doküman.
- Runtime davranışı ile evaluation davranışı birbirine karıştırılmaz.
- Ground truth yalnızca evaluation içindir; runtime karar motoruna girmez.
- Mission continuity tek karar otoritesidir; trust sinyali karar girdisidir, kararın kendisi değildir.

## Mevcut Referans Noktası

11 Mart 2026 itibarıyla çalışma referansı `Faz 2 sonu / Faz 3 başı` olarak kabul edilir. Bu nedenle ilk aktif sertleştirme fazı `Faz 3: Config and Artifact Hardening` olarak ele alınır.

## Faz Sırası

| Faz | Ad | Ana Çıktı |
| --- | --- | --- |
| 0 | Architecture Lock | Ortak dil, authority boundary, truth boundary |
| 1 | First Executable Vertical Slice | İlk çalışan uçtan uca akış |
| 2 | Determinism and Regression Baseline | Repeatable baseline ve regression gate |
| 3 | Config and Artifact Hardening | Versioned config ve stable artifact schema |
| 4 | VIO Health Upgrade | İkili VIO health yerine yapısal sağlık modeli |
| 5 | Real VIO Metric Skeleton | Gerçek VIO metrik iskeleti |
| 6 | Localization Fusion | GNSS + VIO confidence-aware fusion |
| 7 | Trust Engine Maturity | Explainable merkezi trust katmanı |
| 8 | Mission Continuity V2 | Hardened karar motoru |
| 9 | EW Risk Map | Mekansal EW risk farkındalığı |
| 10 | Tactical Summary | Operatör odaklı yorumlanmış özet |
| 11 | Replay and Evaluation Hardening | Analiz edilebilir evaluation platformu |
| 12 | ROS2 Runtime Migration | Node-based runtime |
| 13 | Deployment and Operations Hardening | CI, bootstrap, release disiplini |
| 14 | Hardware-Portability Layer | Sim bağımlılıklarını adapter arkasına alma |
| 15 | Field Transition Preparation | HIL ve saha geçiş hazırlığı |

## Faz 0: Architecture Lock

### Amaç

Terminoloji, authority boundary, truth boundary ve mission/trust ayrımını kilitlemek.

### Neden Bu Faz Şimdi

Mimari dil kilitlenmeden sonraki fazlarda isimler, sorumluluklar ve veri sınırları kayar. Bu da hem implementation drift hem evaluation hatası üretir.

### Kapsam

- Terminology lock
- Node ownership
- Topic family adlandırma
- Mission state ve localization mode tanımı
- Trust signal sözlüğü
- ADR tamamlama
- Doküman tutarlılık taraması

### Teslimatlar

- `docs/architecture/terminology-lock.md`
- `docs/decisions/ADR-001`, `ADR-002`, `ADR-003`
- Güncel architecture, interfaces, scenario-design ve evaluation dokümanları

### Test ve Doğrulama

- Doküman taraması ile ortak terim kontrolü
- `/truth/*` sınırının bütün ilgili dokümanlarda aynı şekilde tanımlanması
- Mission continuity ve trust engine rollerinin ayrık yazılması

### Exit Gate

- Tüm dokümanlar aynı terminolojiyi kullanıyor
- `/truth/*` evaluation-only olarak net
- Trust authority ile mission authority karışmıyor

### Sonraki Fazı Açan Sonuç

Ekip artık aynı şeyi aynı adla konuşabiliyor ve ilk çalışan akış için sınırlar netleşmiş oluyor.

### Riskler

- Dokümanların koddan kopması
- Trust ve decision katmanlarının tekrar birleşmesi

### Önerilen Issue Başlıkları

- Add terminology lock for architecture documentation
- Freeze mission states and localization modes
- Record ADR for evaluation-only ground truth
- Record ADR for deterministic mission continuity
- Run docs consistency cleanup

## Faz 1: First Executable Vertical Slice

### Amaç

İlk gerçek çalışan uçtan uca akışı kurmak.

### Neden Bu Faz Şimdi

Doküman doğrulaması tek başına sistem kurmaz. İlk gerçek akış olmadan ne veri sözleşmeleri ne de mission logic güvenilir biçimde tartışılabilir.

### Kapsam

- Scenario manifest
- Scenario orchestrator
- GNSS trust v1
- Mission continuity v1
- Evaluation report v1
- Smoke test
- Unit testler

### Teslimatlar

- `src/scenario_orchestrator/*`
- `src/gnss_trust/*`
- `src/mission_continuity/*`
- `src/evaluation/report_generator.py`
- `scripts/smoke_test.sh`
- Temel unit test seti

### Test ve Doğrulama

- Nominal senaryo smoke test
- Denied senaryo smoke test
- GNSS trust ordering unit testleri
- Mission continuity state doğrulamaları

### Exit Gate

- `scenario -> gnss_trust -> mission_continuity -> report` akışı çalışıyor
- Nominal senaryo `MISSION_EXECUTE` ile bitebiliyor
- Denied senaryo `MISSION_EXECUTE` ile bitmiyor
- Report artifact üretiliyor

### Sonraki Fazı Açan Sonuç

Proje docs-only olmaktan çıkar ve ilk repeatability ihtiyacı görünür hale gelir.

### Riskler

- Dikey akışın fazla “toy” kalması
- Smoke testin gerçek acceptance yerine geçmesi

### Önerilen Issue Başlıkları

- Add scenario manifest loader and validation
- Implement scenario orchestrator vertical slice
- Implement GNSS trust v1
- Implement deterministic mission continuity v1
- Add evaluation report generator

## Faz 2: Determinism and Regression Baseline

### Amaç

Tek seferlik çalışan değil, tekrarlandığında aynı mantıksal sonucu veren baseline kurmak.

### Neden Bu Faz Şimdi

Repeatability olmadan sonraki tüm tuning ve büyüme kör çalışmaya dönüşür.

### Kapsam

- Regression runner
- Artifact checker
- Summary JSON ve Markdown
- Repeated-run consistency
- Execution input logging

### Teslimatlar

- `scripts/run_regression.sh`
- `scripts/check_artifacts.sh`
- `src/evaluation/regression_compare.py`
- `src/evaluation/summary_report.py`

### Test ve Doğrulama

- Aynı senaryoların tekrarlı koşumu
- Trust ordering kontrolü
- Mission-state consistency kontrolü
- Artifact completeness kontrolü

### Exit Gate

- Aynı input aynı sonucu veriyor
- Regression PASS/FAIL üretiyor
- Summary artifact üretiliyor
- Gerekli artifacts eksiksiz oluşuyor

### Sonraki Fazı Açan Sonuç

Sistem artık ölçülebilir ve karşılaştırılabilir hale gelir; bu da config ve artifact sertleştirmesini mümkün kılar.

### Riskler

- Determinism iddiasının yalnızca birkaç örneğe dayanması
- Run inputlarının eksik loglanması

### Önerilen Issue Başlıkları

- Add baseline regression runner
- Add artifact checker script
- Add summary report generation
- Add repeated-run determinism test
- Add mission-state consistency regression checks

## Faz 3: Config and Artifact Hardening

### Amaç

Davranışı config-driven yapmak ve artifact sözleşmesini sabitlemek.

### Neden Bu Faz Şimdi

Sistem artık çalışıyor ve tekrarlanabiliyor; bundan sonraki büyümenin kontrol edilebilir olması için behavior koddan config’e alınmalı, artifacts ise versioned ve açıklanabilir hale gelmelidir.

### Kapsam

- Threshold ve policy değerlerini config’e taşıma
- `config_id`
- `software_revision`
- Run metadata
- Stable report schema
- Stable summary schema
- Repeated determinism testleri
- Scenario metadata completeness check

### Teslimatlar

- `configs/sim/*`
- Hardened report schema
- Hardened summary schema
- Artifact validation
- Determinism testleri

### Test ve Doğrulama

- Config yükleme ve required field testleri
- Report ve summary schema validation
- Artifact completeness check
- Repeated-run determinism test
- Nominal minimum trust regression gate
- Denied allowed mission-state gate

### Exit Gate

- Config davranışı kontrol ediyor
- Artifact’tan run koşulları geri okunabiliyor
- `config_id` ve `software_revision` kayıtlı
- Schema sabit ve doğrulanabilir
- Aynı senaryo iki kez aynı mantıksal artifact’ı üretiyor

### Sonraki Fazı Açan Sonuç

Simulation production disiplininin ilk gerçek temeli atılır; VIO health modelini artık güvenli biçimde zenginleştirebilirsin.

### Riskler

- Config dosyalarının ikinci bir “hardcoded layer”a dönüşmesi
- Schema’nın sürüm disiplininin kaybedilmesi

### Önerilen Issue Başlıkları

- Move thresholds into config files
- Add config_id to evaluation artifacts
- Add software_revision to evaluation artifacts
- Define stable report schema
- Add repeated-run determinism regression test

## Faz 4: VIO Health Upgrade

### Amaç

`vio_healthy` ikili yapısından daha anlamlı sağlık modeline geçmek.

### Neden Bu Faz Şimdi

Config ve artifact sertleşmeden VIO health derinleştirmek ölçülemeyen bir karmaşa üretir. Önce ölçüm disiplini gerekir.

### Kapsam

- `vio_state: good / weak / lost` veya `vio_health_score`
- Mission continuity entegrasyonu
- Yeni regression senaryoları
- VIO semantics dokümanı

### Teslimatlar

- Güncellenmiş mission continuity input contract
- Yeni VIO health regression senaryoları
- VIO health semantics dokümanı

### Test ve Doğrulama

- Denied + VIO good / weak / lost senaryoları
- Mission decision farkı testleri
- Backward compatibility kontrolü

### Exit Gate

- Binary VIO health kaldırılmış veya geriye uyumluluk katmanına alınmış
- Mission continuity VIO health varyasyonlarına tepki veriyor
- Regression suite bu farkı yakalıyor

### Sonraki Fazı Açan Sonuç

VIO health artık gerçek sinyal taşımaya başlar; bu da gerçek metrik skeleton’ı eklemeyi anlamlı kılar.

### Riskler

- VIO health isimlerinin anlamsız kalması
- Mission logic’in VIO state’e aşırı bağlanması

### Önerilen Issue Başlıkları

- Replace binary VIO health with structured VIO state
- Add degraded VIO scenarios
- Add VIO-sensitive mission continuity behavior

## Faz 5: Real VIO Metric Skeleton

### Amaç

Placeholder VIO yerine gerçek pipeline’dan ölçü üreten iskelet kurmak.

### Neden Bu Faz Şimdi

Önce health contract, sonra metric producer. Aksi durumda metric üretimi nereye akacağı belli olmadan yapılır.

### Kapsam

- Preprocessing
- Feature extraction skeleton
- Matching skeleton
- Pose delta skeleton
- IMU propagation stub
- `feature_count`, `reprojection_error`, `track_continuity`
- VIO trust v1 girdileri

### Teslimatlar

- `src/vio/*`
- Replay’de okunabilir VIO metrics
- VIO metric contract dokümanı

### Test ve Doğrulama

- Metric üretimi unit testleri
- Replay artifact içeriği kontrolü
- Placeholder kaldırma kontrolü

### Exit Gate

- VIO metrics gerçek pipeline’dan geliyor
- Placeholder health ana kaynak değil
- Trust katmanı gerçek VIO metriklerini tüketebiliyor

### Sonraki Fazı Açan Sonuç

GNSS ve VIO artık aynı dünyada anlamlı sinyaller üretir; fusion fazı açılır.

### Riskler

- Skeleton’ın gerçek pipeline yerine sonsuz placeholder kalması
- VIO metriclerinin evaluation’a uygun loglanmaması

### Önerilen Issue Başlıkları

- Add VIO preprocessing pipeline skeleton
- Add feature extraction skeleton
- Add pose estimator skeleton
- Add VIO health metrics

## Faz 6: Localization Fusion

### Amaç

GNSS ve VIO’yu güvene göre birleştirmek.

### Neden Bu Faz Şimdi

Fusion için iki kaynağın da anlamlı health ve confidence sinyali üretmesi gerekir.

### Kapsam

- Fusion service
- Source weighting
- Localization confidence output
- Mode manager
- Transition hysteresis
- Oscillation guard

### Teslimatlar

- `src/localization_fusion/*`
- Resmi localization mode contract
- Fused pose output

### Test ve Doğrulama

- Mode switching senaryoları
- Hysteresis testleri
- Oscillation regression testleri

### Exit Gate

- `GNSS_PRIMARY`, `BLENDED`, `VIO_PRIMARY`, `HOLD_LAST_SAFE` modları kararlı
- Mode switching okunabilir ve explainable
- Localization confidence anlamlı ve loglanmış

### Sonraki Fazı Açan Sonuç

Artık tekil trust sinyallerinden merkezi trust engine’e geçiş mümkün olur.

### Riskler

- Fusion yerine sert source switching yapılması
- Hysteresis eksikliği nedeniyle mode flapping

### Önerilen Issue Başlıkları

- Implement localization fusion service
- Add localization confidence output
- Add mode manager for localization modes
- Add transition hysteresis and oscillation guards

## Faz 7: Trust Engine Maturity

### Amaç

Trust resmini merkezi, explainable ve ölçülebilir hale getirmek.

### Neden Bu Faz Şimdi

Fusion ve çoklu sağlık sinyalleri geldikten sonra merkezi trust engine anlam kazanır.

### Kapsam

- GNSS trust
- VIO trust
- Sync quality
- Localization confidence
- Mission confidence
- Reason codes
- Calibration analizi

### Teslimatlar

- `src/trust_engine/*`
- Explanation-capable trust layer
- Calibration rapor formatı

### Test ve Doğrulama

- Trust aggregation unit testleri
- Reason code coverage kontrolü
- Calibration grafikleri veya raporları

### Exit Gate

- Mission confidence gerçek inputlara dayanıyor
- Trust düşüşü reason code ile açıklanıyor
- Calibration ölçülebiliyor

### Sonraki Fazı Açan Sonuç

Mission continuity v2 artık gerçek bir trust resmi üzerinden karar verebilir.

### Riskler

- Trust engine’in mission decision yerine geçmeye başlaması
- Reason code’ların insan tarafından okunamaz kalması

### Önerilen Issue Başlıkları

- Implement trust aggregation engine
- Add mission confidence computation
- Add trust explanation reason codes
- Add trust calibration analysis

## Faz 8: Mission Continuity V2

### Amaç

Karar motorunu production-disiplinine yaklaştırmak.

### Neden Bu Faz Şimdi

Merkezi trust resmi olmadan mission continuity zenginleştirilirse karar kuralı kırılgan kalır.

### Kapsam

- Timeout logic
- Escalation
- Fallback sustain rules
- Emergency path
- Audit log
- Reason codes
- Oscillation detection

### Teslimatlar

- Hardened `src/mission_continuity/*`
- Audit trail
- Decision correctness checks

### Test ve Doğrulama

- Timeout senaryoları
- Escalation senaryoları
- Invalid oscillation testleri
- Audit log completeness testleri

### Exit Gate

- Mission progression stabil
- Audit trail yeterli
- State flapping kontrol altında

### Sonraki Fazı Açan Sonuç

Artık sistem mekansal risk farkındalığını tüketebilecek kadar kararlı hale gelir.

### Riskler

- Fazla karmaşık state machine
- Audit log’un karar gerekçesini taşımaması

### Önerilen Issue Başlıkları

- Refine mission continuity state machine
- Add timeout and escalation logic
- Add mission decision audit logging
- Add mission oscillation detection

## Faz 9: EW Risk Map

### Amaç

Sistemi mekansal risk farkındalığına taşımak.

### Neden Bu Faz Şimdi

Karar motoru güvenilir olmadan risk map üretmek operatöre gürültü taşır.

### Kapsam

- Risk grid
- Accumulation logic
- Denied/spoof-like zone marking
- Temporal decay
- Corridor cost export
- EW metrics

### Teslimatlar

- `src/ew_risk_map/*`
- Risk outputs
- EW regression testleri

### Test ve Doğrulama

- Spatial consistency testleri
- Risk accumulation senaryoları
- False marking ölçümü

### Exit Gate

- Risk map senaryoya tepki veriyor
- Spatial output tekrar koşulabilir
- False marking ölçülüyor

### Sonraki Fazı Açan Sonuç

Operator-facing tactical summary artık anlamlı risk girdisi alabilir.

### Riskler

- Spatial çıktıların deterministik olmaması
- Risk map’in explainable olmaması

### Önerilen Issue Başlıkları

- Add EW risk grid model
- Add temporal decay for EW regions
- Add corridor cost export
- Add EW map metrics

## Faz 10: Tactical Summary

### Amaç

Operatöre ham veri değil yorumlanmış karar özeti vermek.

### Neden Bu Faz Şimdi

Önce güvenilir runtime ve risk çıktısı gerekir; summary bunların üstündeki yorum katmanıdır.

### Kapsam

- Summary schema
- Compact JSON
- Markdown/text summary
- Recommended action
- Mission confidence özeti
- EW risk özeti

### Teslimatlar

- `src/tactical_summary/*`
- Operator-facing summary formatları

### Test ve Doğrulama

- Summary/runtime consistency testleri
- Baseline senaryo summary doğrulaması
- Human-readable output incelemesi

### Exit Gate

- Summary runtime state ile çelişmiyor
- Baseline senaryolarda mantıklı
- Recommendation alanı boş veya anlamsız değil

### Sonraki Fazı Açan Sonuç

Replay ve evaluation katmanı artık insan-yorumlu runtime çıktısını da inceleyebilir.

### Riskler

- Summary’nin dashboard süsüne dönüşmesi
- Recommendation mantığının runtime kararını çarpıtması

### Önerilen Issue Başlıkları

- Define tactical summary schema
- Build tactical summary generator
- Add human-readable summary output
- Add scenario-based summary validation

## Faz 11: Replay and Evaluation Hardening

### Amaç

Sistemi analiz edilebilir research/evaluation platformuna çevirmek.

### Neden Bu Faz Şimdi

Ölçülecek runtime ve tactical katman oluşmadan replay/eval hardening yüzeysel kalır.

### Kapsam

- Replay bookmarks
- Timeline compare
- Config diff
- Revision diff
- Localization continuity metric
- Fallback reaction time
- Decision correctness
- EW comparison metrics

### Teslimatlar

- Hardened replay tools
- Expanded evaluation suite
- Comparison reports

### Test ve Doğrulama

- Run-to-run comparison testleri
- Root cause replay örnekleri
- Metric doğruluk kontrolleri

### Exit Gate

- Replay ile root cause bulunabiliyor
- Comparison tooling stabil
- Metrikler sahte veya placeholder değil

### Sonraki Fazı Açan Sonuç

Script tabanlı dünyanın sınırları görünür hale gelir ve ROS2 runtime geçişi için güvenli zemin oluşur.

### Riskler

- Replay araçlarının runtime’dan kopması
- Fazla metric üretip az anlam çıkarmak

### Önerilen Issue Başlıkları

- Add replay bookmarks and timeline markers
- Add run-to-run comparison tools
- Add localization continuity metric
- Add decision correctness metric

## Faz 12: ROS2 Runtime Migration

### Amaç

Script tabanlı akışı node-based runtime’a geçirmek.

### Neden Bu Faz Şimdi

ROS2’ye erken atlamak sistemi gereksiz yere dağıtır. Önce algorithm, evaluation ve contracts oturmalıdır.

### Kapsam

- Message contracts
- Node decomposition
- Topic ownership
- Runtime topic wiring
- Truth boundary enforcement
- Logger/evaluation separation
- Health monitoring topics

### Teslimatlar

- ROS2 node graph
- Message schemas
- İlk runtime loop

### Test ve Doğrulama

- Topic wiring testi
- Truth boundary testi
- Runtime/evaluation separation testi

### Exit Gate

- Runtime ve evaluation ayrımı korunuyor
- Mission continuity tek karar otoritesi kalıyor
- Node graph stabil

### Sonraki Fazı Açan Sonuç

Sistem artık operasyonel olarak paketlenebilir bir runtime formuna yaklaşır.

### Riskler

- Message schema’ların erken donması
- Evaluation logic’in runtime’a sızması

### Önerilen Issue Başlıkları

- Define ROS2 message contracts
- Create ROS2 node decomposition
- Implement runtime topic wiring
- Enforce truth boundary in runtime graph

## Faz 13: Deployment and Operations Hardening

### Amaç

Sistemi yeniden kurulabilir ve CI ile yönetilebilir yapmak.

### Neden Bu Faz Şimdi

Deployment disiplini, runtime ve regression sistemi yeterince kararlı olmadan anlamlı bir hedef değildir.

### Kapsam

- Docker/devcontainer
- Bootstrap standardization
- CI
- Lint
- Unit test gate
- Regression gate
- Release notes
- Hardened runbooks

### Teslimatlar

- Ops-ready software baseline
- CI pipeline
- Reproducible dev environment

### Test ve Doğrulama

- Temiz makine kurulumu
- CI kırılma senaryoları
- Release candidate üretim denemesi

### Exit Gate

- Yeni makinede kurulum tekrarlanabiliyor
- CI anlamlı fail ediyor
- Release candidate üretilebiliyor

### Sonraki Fazı Açan Sonuç

Donanım bağımsızlığı için arayüz katmanı eklemek artık güvenlidir.

### Riskler

- CI’nin sadece syntax gate olarak kalması
- Runbook’ların gerçek çalışma akışını yansıtmaması

### Önerilen Issue Başlıkları

- Add reproducible development environment
- Add CI for unit and regression tests
- Add lint and formatting gates
- Harden runbooks for repeatable execution

## Faz 14: Hardware-Portability Layer

### Amaç

Gerçek sensöre geçişte mimari kırılmayı engellemek.

### Neden Bu Faz Şimdi

Önce runtime ve ops disiplinini oturtmak gerekir; aksi takdirde portability yalnızca niyet olarak kalır.

### Kapsam

- Sensor adapter interfaces
- Timing contracts
- Rate assumptions
- Onboard/ground split notları
- Portability docs

### Teslimatlar

- Portability interface layer
- Future real sensor mapping dokümanları

### Test ve Doğrulama

- Adapter boundary review
- Sim bağımlılık taraması
- Timing/rate varsayım doğrulaması

### Exit Gate

- Sim bağımlılıkları adapter arkasında
- Gerçek sensör bağlanma noktaları net
- Portability plan yazılı ve anlaşılır

### Sonraki Fazı Açan Sonuç

Saha geçişi plansız değil, kontrollü tasarlanabilir hale gelir.

### Riskler

- Portability dokümanı olup kod arayüzünün eksik kalması
- Timing varsayımlarının yazılmaması

### Önerilen Issue Başlıkları

- Define sensor adapter interfaces
- Define timing and rate contracts
- Add hardware portability documentation

## Faz 15: Field Transition Preparation

### Amaç

Saha geçişini plansızlıktan kurtarmak.

### Neden Bu Faz Şimdi

Bu faz, gerçek entegrasyon öncesi hazırlık fazıdır; önceki fazlar tamamlanmadan gerçek saha planı güvenilir olmaz.

### Kapsam

- HIL roadmap
- Sensor replacement matrix
- Calibration plan
- Sync validation plan
- Safety constraints
- Manual override strategy
- Field checklist
- Real log requirements

### Teslimatlar

- Field transition package
- Calibration and safety playbook
- HIL roadmap

### Test ve Doğrulama

- Transition readiness review
- Calibration workflow walkthrough
- Safety checklist completeness review

### Exit Gate

- Donanım geldiğinde entegrasyon sırası belli
- Calibration plan hazır
- Safety constraints tanımlı
- HIL planı yazılı ve uygulanabilir

### Sonraki Fazı Açan Sonuç

Simulation-validated sistem, kontrollü field integration fazına geçmeye hazır olur.

### Riskler

- HIL yol haritasının soyut kalması
- Safety ve override stratejisinin çok geç düşünülmesi

### Önerilen Issue Başlıkları

- Create HIL transition roadmap
- Create simulated-to-real sensor replacement matrix
- Define calibration procedure plan
- Define field safety and manual override checklist

## Fazlar Arası Geçiş Kuralları

- Faz kapatma kararı yalnızca “iş yapıldı” ile verilmez; test ve kanıt gereklidir.
- Her faz için kapanış kanıtı progress tracker içinde kayda geçirilir.
- Eğer bir fazın exit gate’i tam değilse sonraki faz yalnızca araştırma düzeyinde hazırlanabilir; ana implementation başlamaz.
- Geç fazların gösterişli çıktıları, erken fazların kapanış kapılarını by-pass etmek için gerekçe olamaz.

## Yaklaşık Zaman Planı

Bu plan küçük ekip veya tek kişi için yaklaşık `9-12 ay` ölçeğindedir. Geniş bant tahmin aşağıdaki gibidir:

- Faz 0-3: 0-8 hafta
- Faz 4-6: 8-18 hafta
- Faz 7-10: 18-28 hafta
- Faz 11-13: 28-40 hafta
- Faz 14-15: 40-48 hafta

## Bu Dokümanın Kullanımı

- Her aktif faz başladığında karşılığı `progress-tracker.md` içinde `Devam Ediyor` olarak açılır.
- Faz boyunca checklist, blocker ve kanıtlar tracker’a yazılır.
- Faz kapandığında `master-plan.md` değişmez; yalnızca `progress-tracker.md` güncellenir.

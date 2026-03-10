Bu plan şunları kapsar:

ne inşa ettiğiniz

hangi sırayla inşa edeceğiniz

hangi fazda ne yapılacağı

her fazın teknik çıktıları

her fazın kabul kriterleri

hangi sonuç alınmadan sonraki faza geçilemeyeceği

klasör yapısı

kod mimarisi

test stratejisi

evaluation stratejisi

CI/CD ve deployment

ROS2 geçişi

hardware-portability hazırlığı

field transition hazırlığı

Bu planın mantığı şudur:

Yanlış sırada ilerlersen proje çöker.

Önce güvenilir omurga, sonra derinlik, sonra entegrasyon.

1. Nihai hedef
Ürün tanımı

JamShield Recon-X Sim, GNSS bozulmasının, jamming etkilerinin ve spoof-like davranışların simüle edildiği ortamlarda:

GNSS güvenilirliğini ölçen

VIO tabanlı fallback localization kullanan

confidence-aware localization fusion yapan

deterministic mission continuity kararı veren

EW risk farkındalığı üreten

operator-facing tactical summary sağlayan

tüm davranışını replay, metrics ve regression ile doğrulayan

simulation-first ama hardware-portable tasarlanmış

bir autonomy stack’tir.

2. Production bu projede ne demek?

Çoğu kişi burada hata yapıyor. "Production"ı "çalıştı" sanıyor.

Bu projede production iki seviyelidir.

2.1 Simulation Production

Bu ilk gerçek hedefindir.

Şunları içerir:

deterministik davranış

repeatable runs

scenario-driven execution

versioned configs

versioned artifacts

replay

regression

metrics

CI gate

node/service sınırları

docs ve ADR disiplini

explainable trust and mission logic

2.2 Field Production

Bu daha sonraki hedef.

Şunları içerir:

gerçek sensör entegrasyonu

calibration

timing validation

HIL

gerçek autopilot entegrasyonu

saha güvenlik prosedürleri

manual override ve gerçek fail-safe

Şu an hedefin:

Simulation Production

Önce bunu bitireceksin. Bunu bitirmeden sahaya bakmak kendini kandırmaktır.

3. Büyük resim mimari

Sistem 6 katmandan oluşur.

3.1 Scenario & Simulation Layer

Görev ortamını simüle eder.

İçerik:

scenario manifests

map/world

GNSS degradation events

denied zones

spoof-like drift

communication degradation

sensor noise models

deterministic seeds

3.2 Sensor & Time Layer

Simülatörden gelen veriyi normalize eder.

İçerik:

camera adapter

IMU adapter

GNSS adapter

ground truth adapter

time sync

timing diagnostics

3.3 Core Autonomy Layer

Sistemin çekirdeği.

İçerik:

GNSS trust

VIO

localization fusion

trust engine

mission continuity

SITL bridge

3.4 Tactical Intelligence Layer

Core autonomy çıktısını taktik katmana çevirir.

İçerik:

EW risk map

tactical summary

risk-aware route hints

3.5 Verification & Operations Layer

Bu olmadan sistem ciddiye alınmaz.

İçerik:

logger

replay

evaluation

regression compare

summary reports

health monitor

config management

3.6 Operator Layer

İnsanın sistemi anlamasını sağlar.

İçerik:

operator station

trust bars

localization state

mission state

tactical summary

replay mode

4. Nihai repo yapısı
jamshield-recon-x/
├── README.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── Makefile
├── pyproject.toml
├── docker-compose.yml
│
├── docs/
│   ├── README.md
│   ├── architecture/
│   ├── interfaces/
│   ├── system-spec/
│   ├── scenario-design/
│   ├── evaluation/
│   ├── runbooks/
│   ├── decisions/
│   └── research-notes/
│
├── configs/
│   ├── dev/
│   ├── sim/
│   ├── eval/
│   ├── sitl/
│   └── mission-profiles/
│
├── scenarios/
│   ├── baseline/
│   ├── stress/
│   ├── regression/
│   ├── acceptance/
│   └── assets/
│
├── src/
│   ├── common/
│   ├── scenario_orchestrator/
│   ├── sensor_ingestion/
│   ├── time_sync/
│   ├── gnss_trust/
│   ├── vio/
│   ├── localization_fusion/
│   ├── trust_engine/
│   ├── mission_continuity/
│   ├── sitl_bridge/
│   ├── ew_risk_map/
│   ├── tactical_summary/
│   ├── logging_replay/
│   ├── evaluation/
│   ├── health_monitor/
│   └── operator_station/
│
├── scripts/
│   ├── bootstrap.sh
│   ├── smoke_test.sh
│   ├── run_scenario.sh
│   ├── run_regression.sh
│   ├── check_artifacts.sh
│   └── replay_run.sh
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── simulation/
│   ├── regression/
│   └── acceptance/
│
├── artifacts/
│   ├── runs/
│   ├── summaries/
│   └── comparisons/
│
├── experiments/
│   ├── trust-tuning/
│   ├── vio-tuning/
│   ├── fusion-analysis/
│   └── ew-map-validation/
│
├── simulator/
│   ├── px4_sitl/
│   ├── ardupilot_sitl/
│   ├── gazebo/
│   ├── airsim/
│   └── launcher/
│
└── tools/
    ├── scenario_validator/
    ├── replay_inspector/
    ├── metric_extractor/
    └── diagnostics/

    5. End-to-end faz planı

Aşağıdaki faz sırası nihai plandır.

Faz 0: Architecture Lock
Amaç

Sistem dilini ve sınırlarını kilitlemek.

Yapılacaklar

terminology lock

node ownership

topic families

mission states

localization modes

trust signals

ADR’ler

docs consistency sweep

Teslimatlar

docs/architecture/terminology-lock.md

ADR’ler

güncel architecture, interfaces, scenario-design, evaluation docs

Exit kriterleri

tek karar otoritesi belli

trust ve mission authority ayrı

/truth/* evaluation-only

dosyalar aynı dili kullanıyor

Bu faz tamamlandığında

Mimari drift engellenir.

Faz 1: First Executable Vertical Slice
Amaç

İlk gerçek çalışan sistemi kurmak.

Kapsam

scenario manifest

scenario orchestrator

GNSS trust v1

mission continuity v1

evaluation report v1

smoke test

unit testler

İlk çalışan akış

scenario -> gnss_trust -> mission_continuity -> report

Teslimatlar

src/scenario_orchestrator/*

src/gnss_trust/*

src/mission_continuity/*

src/evaluation/report_generator.py

tests/unit/*

scripts/smoke_test.sh

Exit kriterleri

smoke test geçiyor

nominal normal bitiyor

denied normal bitmiyor

report oluşuyor

Bu faz tamamlandığında

Docs-only proje olmaktan çıkılır.

Faz 2: Determinism and Regression Baseline
Amaç

Bir kez çalışan değil, hep aynı çıkan sistem kurmak.

Kapsam

regression runner

artifact checker

summary JSON

summary markdown

repeated-run consistency

execution input logging

Teslimatlar

scripts/run_regression.sh

scripts/check_artifacts.sh

src/evaluation/regression_compare.py

src/evaluation/summary_report.py

Exit kriterleri

same input same output

trust ordering korunuyor

regression PASS/FAIL üretiyor

artifacts eksiksiz

Bu faz tamamlandığında

Repeatable baseline oluşur.

Faz 3: Config and Artifact Hardening
Amaç

Davranışı koddan config’e taşımak ve artifact’ı production-disiplinine sokmak.

Kapsam

threshold config’e taşıma

config_id

software_revision

run metadata

stable report schema

stable summary schema

repeated determinism test

Zorunlu artifact alanları

run_id

scenario_id

gnss_condition

gnss_state

trust_score

mission_confidence

mission_state

vio_state veya vio_healthy

config_id

software_revision

timestamp

Teslimatlar

configs/sim/*

hardened report schema

hardened summary schema

determinism tests

Exit kriterleri

config davranışı kontrol ediyor

artifact’tan koşul geri okunabiliyor

revision ve config kayıtlı

aynı senaryo iki kez aynı artifact mantığını veriyor

Bu faz tamamlandığında

Simulation production disiplininin ilk gerçek temeli atılır.

Faz 4: VIO Health Upgrade
Amaç

vio_healthy=True/False basitliğinden çıkmak.

Kapsam

vio_state: good/weak/lost
veya

vio_health_score: 0.0-1.0

mission continuity bunu tüketsin

regression senaryoları genişlesin

Teslimatlar

güncellenmiş mission continuity input contract

yeni regression senaryoları

VIO health semantics

Exit kriterleri

denied + VIO good ile denied + VIO lost farklı karar veriyor

regression bunları yakalıyor

Bu faz tamamlandığında

Fallback davranışı daha gerçekçi hale gelir.

Faz 5: Real VIO Metric Skeleton
Amaç

Placeholder VIO health yerine gerçek VIO metrikleri üretmeye başlamak.

Kapsam

preprocessing

feature extraction

matching skeleton

pose delta skeleton

IMU propagation stub

feature_count

reprojection_error

track_continuity

VIO trust v1

Teslimatlar

src/vio/*

replay’de okunabilir VIO metrics

Exit kriterleri

VIO metrics gerçek pipeline’dan geliyor

placeholder yok

trust engine gerçek VIO health tüketebiliyor

Bu faz tamamlandığında

VIO health, sahte input olmaktan çıkar.

Faz 6: Localization Fusion
Amaç

GNSS ve VIO’yu güvene göre birleştirmek.

Resmi modlar

GNSS_PRIMARY

BLENDED

VIO_PRIMARY

HOLD_LAST_SAFE

Kapsam

fusion service

source weighting

localization confidence

transition guard

oscillation prevention

fused pose contract

Teslimatlar

src/localization_fusion/*

mode switching

localization confidence output

Exit kriterleri

mode switching kararlı

oscillation yok

localization confidence anlamlı

regression’de mod değişimleri okunuyor

Bu faz tamamlandığında

Confidence-aware localization oluşur.

Faz 7: Trust Engine Maturity
Amaç

Sistemin güven resmini merkezi ve açıklanabilir hale getirmek.

Kapsam

gnss_trust

vio_trust

sync_quality

localization_confidence

mission_confidence

explanation reasons

trust calibration

Teslimatlar

src/trust_engine/*

explanation-capable trust layer

Exit kriterleri

mission_confidence gerçek inputlara dayanıyor

trust düşüş nedeni explainable

calibration ölçülebiliyor

Bu faz tamamlandığında

Mission confidence gerçek anlam kazanır.

Faz 8: Mission Continuity V2
Amaç

Karar motorunu olgunlaştırmak.

Kapsam

timeout logic

safe hold escalation

fallback sustain rules

emergency path

audit log

reason codes

invalid oscillation detection

Teslimatlar

hardened src/mission_continuity/*

audit trail

decision correctness checks

Exit kriterleri

expected mission progression sağlanıyor

audit açıklayıcı

state oscillation kontrol altında

Bu faz tamamlandığında

Karar motoru güvenilir hale gelir.

Faz 9: EW Risk Map
Amaç

Sistemi mekansal risk farkındalığına taşımak.

Kapsam

risk grid

accumulation logic

denied/spoof-like zone marking

temporal decay

corridor cost export

EW metrics

Teslimatlar

src/ew_risk_map/*

risk outputs

EW regression tests

Exit kriterleri

risk map senaryoya tepki veriyor

false marking ölçülüyor

repeated run benzer spatial result üretiyor

Bu faz tamamlandığında

Sistem reactive olmaktan çıkar, risk-aware olur.

Faz 10: Tactical Summary
Amaç

Operatöre ham veri değil, yorumlanmış özet vermek.

Kapsam

summary schema

compact JSON

markdown/text summary

recommended action

mission confidence summary

EW risk summary

Teslimatlar

src/tactical_summary/*

operator-facing summary formatları

Exit kriterleri

summary ile runtime state çelişmiyor

baseline senaryolarda mantıklı summary çıkıyor

Bu faz tamamlandığında

Operator-facing tactical layer oluşur.

Faz 11: Replay and Evaluation Hardening
Amaç

Sistemi gerçekten analiz edilebilir platform yapmak.

Kapsam

replay bookmarks

timeline compare

config diff

revision diff

localization continuity metric

fallback reaction time

decision correctness

EW metrics

run-to-run comparison

Teslimatlar

hardened replay tools

expanded evaluation suite

comparison reports

Exit kriterleri

root cause replay ile bulunabiliyor

regression suite geniş ve stabil

metrics sahte değil

Bu faz tamamlandığında

Research-grade evaluation platform oluşur.

Faz 12: ROS2 Runtime Migration
Amaç

Script zincirini node-based runtime’a taşımak.

Kapsam

message contracts

ROS2 node decomposition

topic ownership

runtime topic wiring

truth boundary enforcement

logger/evaluation separation

health monitoring topics

Teslimatlar

ROS2 node graph

message schemas

first runtime loop

Exit kriterleri

runtime ve evaluation ayrımı korunuyor

mission_continuity tek karar otoritesi kalıyor

node graph kararlı

Bu faz tamamlandığında

Gerçek runtime mimarisi oluşur.

Faz 13: Deployment and Operations Hardening
Amaç

Sistemi tekrar kurulabilir ve kontrol edilebilir hale getirmek.

Kapsam

Docker/devcontainer

bootstrap standardization

CI

lint

test gate

regression gate

release notes

known limitations

runbooks hardening

Teslimatlar

ops-ready software baseline

CI pipeline

reproducible dev environment

Exit kriterleri

yeni makinede kuruluyor

CI anlamlı fail ediyor

release candidate üretilebiliyor

Bu faz tamamlandığında

Production-grade simulation software altyapısı oluşur.

Faz 14: Hardware-Portability Layer
Amaç

Gerçek donanım gelmeden geçişi kolaylaştırmak.

Kapsam

sensor adapter interfaces

timing contracts

rate assumptions

onboard/ground split notes

portability docs

Teslimatlar

portability interface layer

docs for future real sensor mapping

Exit kriterleri

sim bağımlılıkları adapter arkasında

gerçek sensörlerin nereye bağlanacağı belli

portability plan net

Bu faz tamamlandığında

Hardware-portable architecture oluşur.

Faz 15: Field Transition Preparation
Amaç

Sahaya geçişi plansızlıktan kurtarmak.

Kapsam

HIL roadmap

sensor replacement matrix

calibration plan

sync validation plan

safety constraints

manual override strategy

field checklist

real log requirements

Teslimatlar

field transition package

calibration and safety playbook

Exit kriterleri

donanım geldiğinde ilk entegrasyon sırası net

calibration plan hazır

safety constraints tanımlı

Bu faz tamamlandığında

Simulation-validated system, field integration phase’e hazır olur.

6. Her faz için issue başlıkları

Aşağıda her faz için issue başlıkları var. Bunlar doğrudan GitHub issue’lara dönüştürülebilir.

Faz 0

Add terminology lock for architecture documentation

Freeze mission states and localization modes

Define topic family naming convention

Record ADR for evaluation-only ground truth

Record ADR for deterministic mission continuity

Record ADR for trust engine separation

Run docs consistency cleanup

Faz 1

Add scenario manifest loader and validation

Implement scenario orchestrator vertical slice

Implement GNSS trust v1

Implement deterministic mission continuity v1

Add evaluation report generator

Add smoke test script

Add unit tests for vertical slice

Faz 2

Add baseline regression runner

Add artifact checker script

Add summary report generation

Add repeated-run determinism test

Add trust ordering regression checks

Add mission-state consistency regression checks

Faz 3

Move thresholds into config files

Add config_id to artifacts

Add software_revision to artifacts

Define stable report schema

Define stable summary schema

Add run metadata standardization

Faz 4

Replace binary VIO health with structured VIO state

Add degraded VIO scenarios

Add VIO-sensitive mission continuity behavior

Add regression checks for weak and lost VIO

Faz 5

Add VIO preprocessing pipeline skeleton

Add feature extraction skeleton

Add pose estimator skeleton

Add VIO health metrics

Add VIO trust scoring

Faz 6

Implement localization fusion service

Add source weighting logic

Add localization confidence output

Add mode manager for localization modes

Add transition hysteresis and oscillation guards

Faz 7

Implement trust aggregation engine

Add mission confidence computation

Add trust explanation reason codes

Add trust calibration analysis

Faz 8

Refine mission continuity state machine

Add timeout and escalation logic

Add mission decision audit logging

Add decision reason codes

Add mission oscillation detection

Faz 9

Add EW risk grid model

Add risk accumulation from trust degradation

Add temporal decay for EW regions

Add corridor cost export

Add EW map metrics

Faz 10

Define tactical summary schema

Build tactical summary generator

Add human-readable summary output

Add scenario-based summary validation

Faz 11

Add replay bookmarks and timeline markers

Add run-to-run comparison tools

Add localization continuity metric

Add fallback reaction time metric

Add decision correctness metric

Add EW map comparison metrics

Faz 12

Define ROS2 message contracts

Create ROS2 node decomposition

Implement runtime topic wiring

Enforce truth boundary in runtime graph

Add logger and evaluation node separation

Faz 13

Add reproducible development environment

Add CI for unit and regression tests

Add lint and formatting gates

Add release notes template

Harden runbooks for repeatable execution

Faz 14

Define sensor adapter interfaces

Define timing and rate contracts

Add onboard vs ground deployment notes

Add hardware portability documentation

Faz 15

Create HIL transition roadmap

Create simulated-to-real sensor replacement matrix

Define calibration procedure plan

Define real-world logging requirements

Define field safety and manual override checklist

7. Faz bazlı exit checklist

Aşağıdakiler faz kapatma kapılarıdır.

Faz 0 kapatma

docs terminoloji tutarlı

authority boundaries net

truth boundary net

Faz 1 kapatma

smoke test geçiyor

report üretiyor

basic scenarios doğru behavior veriyor

Faz 2 kapatma

regression çalışıyor

deterministic sonuç alınıyor

summary PASS/FAIL var

Faz 3 kapatma

config-driven behavior var

artifacts versioned

schema sabit

Faz 4 kapatma

VIO health binary değil

mission decisions VIO health’e tepki veriyor

Faz 5 kapatma

VIO metrics placeholder değil

VIO trust gerçek metric tüketiyor

Faz 6 kapatma

localization modes çalışıyor

fusion kararlı

oscillation kontrol altında

Faz 7 kapatma

mission confidence explainable

trust calibration ölçülüyor

Faz 8 kapatma

decision progression kararlı

audit trail yeterli

Faz 9 kapatma

risk map metrikleri anlamlı

repeated run spatial consistency var

Faz 10 kapatma

tactical summary runtime ile tutarlı

Faz 11 kapatma

replay ile root cause bulunabiliyor

comparison tooling stabil

Faz 12 kapatma

runtime/evaluation ayrımı korunuyor

node graph kararlı

Faz 13 kapatma

CI, bootstrap, release discipline var

Faz 14 kapatma

portability interfaces net

Faz 15 kapatma

HIL ve field transition planı hazır

8. Gerçekçi zaman planı

Bu proje tek kişi veya küçük ekip için uzun iştir. Gerçekçi plan:

0-2 hafta

Faz 0

2-4 hafta

Faz 1

4-6 hafta

Faz 2

6-8 hafta

Faz 3

8-11 hafta

Faz 4

11-15 hafta

Faz 5

15-18 hafta

Faz 6

18-20 hafta

Faz 7

20-23 hafta

Faz 8

23-26 hafta

Faz 9

26-28 hafta

Faz 10

28-32 hafta

Faz 11

32-36 hafta

Faz 12

36-40 hafta

Faz 13

40-44 hafta

Faz 14

44-48 hafta

Faz 15

Bu tam üretim disipliniyle yaklaşık 9-12 ay eder. Daha kısa sürede olur diyen ya yalan söylüyordur ya da “production” kelimesini anlamıyordur.

9. Takım yapısı

Tek kişiyle de yapılır ama yavaş olur. İdeal çekirdek ekip:

Rol 1: Core Autonomy

GNSS trust

VIO

fusion

trust engine

Rol 2: Mission & Tactical

mission continuity

EW risk map

tactical summary

Rol 3: Verification & Tooling

evaluation

replay

regression

CI

artifacts

Rol 4: Runtime & Integration

ROS2

SITL bridge

deployment

operator station

Tek kişiysen rolleri zaman bloklarıyla sırayla üstlenmen gerekir. Paralel çalışamazsın.

10. En büyük riskler
Risk 1

Erken VIO derinliğine gömülmek

Risk 2

Placeholder metricleri gerçek sanmak

Risk 3

Docs perfectionism yüzünden implementation’ı geciktirmek

Risk 4

ROS2’ye erken atlamak

Risk 5

UI ve dashboard ile kendini kandırmak

Risk 6

Regression ve replay disiplini kurmadan büyümek

Risk 7

Trust ile mission decision’ı karıştırmak

Risk 8

Simulation fidelity’yi hiç sorgulamamak

11. Şu an senin doğru yerin

Mevcut durumuna göre sen:

Faz 2 sonu / Faz 3 başındasın

Yani senden şu anda beklenen şey:

Faz 3 issue’larını kapatmak

artifact schema’yı sertleştirmek

config/revision disiplinini oturtmak

repeated determinism testi eklemek

Şu an VIO’ya tam dalmak erken.

12. Şu an açılması gereken issue’lar

Bunları hemen aç:

Add config_id to evaluation artifacts

Add software_revision to evaluation artifacts

Define stable report schema for vertical slice

Define stable summary schema for regression runs

Move trust and mission thresholds into config files

Add repeated-run determinism regression test

Add nominal minimum trust threshold regression check

Add denied scenario allowed mission-state set check

Add scenario metadata completeness check

13. Bu planın özü

Bu projenin doğru yolu şudur:

architecture lock → executable baseline → deterministic regression → config/artifact discipline → VIO realism → fusion → trust maturity → mission maturity → tactical layer → replay/eval hardening → ROS2 runtime → deployment → hardware portability → field transition
<div align="center">

# 🔐 Analisi di Sicurezza APK – Enpass Password Manager 5.6.9

**Vulnerability Assessment & Penetration Testing dell'app Android _Enpass Password Manager_ secondo la metodologia OWASP MASVS / MASTG**

![OWASP MASVS](https://img.shields.io/badge/Standard-OWASP%20MASVS%20v2-000000?logo=owasp&logoColor=white)
![MASTG](https://img.shields.io/badge/Guide-OWASP%20MASTG-blue)
![Target](https://img.shields.io/badge/Target-Enpass%205.6.9-1f6feb)
![Package](https://img.shields.io/badge/package-io.enpass.app-informational)
![MobSF](https://img.shields.io/badge/MobSF%20Score-42%2F100%20(B)-yellow)
![Corso](https://img.shields.io/badge/SAM-A.A.%202025%2F26-purple)

</div>

---

## 📑 Indice

1. [Applicazione target](#1-applicazione-target)
2. [Metodologia](#2-metodologia)
3. [Ambiente e strumenti](#3-ambiente-e-strumenti)
4. [Scope](#4-scope)
5. [Analisi iniziale con MobSF](#5-analisi-iniziale-con-mobsf)
6. [Executive summary](#6-executive-summary)
7. [Vulnerabilità individuate](#7-vulnerabilità-individuate)
8. [Finding deboli](#8-finding-deboli)
9. [Controlli OWASP eseguiti](#9-controlli-owasp-eseguiti)
10. [Struttura del repository](#10-struttura-del-repository)
11. [Autore e disclaimer](#11-autore-e-disclaimer)

---

## 1. Applicazione target

**Enpass Password Manager** (sviluppato da Sinew Software Systems) è un gestore di password che custodisce credenziali, carte, identità e note riservate in un **vault cifrato**, sbloccabile solo con la Master Password. A differenza di molte soluzioni concorrenti adotta un modello **offline-first**: l'archivio risiede localmente sul dispositivo e la sincronizzazione cloud è facoltativa.

Caratteristiche di sicurezza dichiarate:

- Database cifrato a livello di file con **SQLCipher** (AES-256) e HMAC per pagina, illeggibile a riposo senza la Master Password.
- Sblocco locale tramite Master Password, PIN o impronta, con chiave biometrica ancorata all'**Android KeyStore**.
- Autofill delle credenziali e browser integrato isolato per la navigazione sensibile.
- Sincronizzazione del vault cifrato su account cloud dell'utente (Dropbox, Google Drive, OneDrive, Box, WebDAV).
- Generatore di password basato su un RNG crittograficamente sicuro.

| | |
|---|---|
| **Versione analizzata** | 5.6.9 |
| **Package** | `io.enpass.app` |
| **Target SDK / Min SDK** | 24 / 15 |

## 2. Metodologia

Assessment **grey-box** che combina:

- **Analisi statica** – decompilazione dell'APK (jadx), revisione del manifest, dei componenti esportati, della crittografia e delle librerie di terze parti.
- **Analisi dinamica** – esecuzione strumentata su emulatore, instrumentazione a runtime, intercettazione del traffico e ispezione di storage e memoria.

Le attività sono mappate su **OWASP MASVS v2** e verificate tramite i test case di **OWASP MASTG**, con riferimento alla **OWASP Mobile Top 10** e al modello della **Cyber Kill Chain**.

## 3. Ambiente e strumenti

| Strumento | Scopo |
|---|---|
| Kali Linux | Sistema operativo di base per il mobile penetration testing |
| Android Emulator (AVD) | Dispositivi virtuali di test – AVD Android 11 (moderno) e Android 4.1 (device datati) |
| MobSF | Analisi di sicurezza automatizzata dell'APK (SAST + DAST) e scoring |
| jadx | Decompilazione del bytecode e code review |
| ADB | Interazione con l'emulatore, installazione, log, dump dell'heap |
| Frida | Dynamic instrumentation (hooking Java/nativo) |
| objection | Console interattiva basata su Frida (es. `memory search`) |
| mitmproxy | Proxy di intercettazione del traffico HTTP/HTTPS |
| apksigner | Verifica dello schema di firma e del certificato del pacchetto |

## 4. Scope

| Parametro | Valore |
|---|---|
| Nome APK | `enpass-password-manager-5-6-9.apk` |
| MD5 | `a3f6924091076fe44dcd46bcace3f8c5` |
| SHA1 | `f67af5d9ae305fb8d1d2148e2240ebbb05d65d08` |
| SHA256 | `d8eff043c8f2595087e285a7dea26ca03deab6a0906ac5867025304320b56375` |

## 5. Analisi iniziale con MobSF

| Metrica | Valore |
|---|---|
| Security Score | **42 / 100** (grado B – rischio medio) |
| Target SDK / Min SDK | 24 / 15 |
| Problemi High | 7 |
| Problemi Medium | 21 |
| Hotspot | 2 |
| Tracker di terze parti | 2 (Google Analytics, Google Tag Manager) |

## 6. Executive summary

L'analisi ha evidenziato una **base crittografica solida** per la protezione dei dati a riposo, a fronte di **carenze rilevanti su resilienza e protezione delle comunicazioni**.

Sul versante positivo: il vault è cifrato a livello di file con SQLCipher e integrità HMAC per pagina e resta illeggibile a riposo senza la Master Password; l'autenticazione biometrica è ancorata a una chiave del KeyStore vincolata all'utente; le schermate sensibili usano `FLAG_SECURE`; non emergono esposizioni di dati via IPC; l'RNG è crittograficamente sicuro; l'app è firmata con certificato di produzione, non è debuggable e le librerie native sono irrobustite e prive di simboli di debug.

Sul versante delle criticità, l'aspetto più significativo è la **persistenza della Master Password in chiaro nella memoria** del processo (uso di `String` immutabili mai azzerate). A ciò si aggiungono un fattore di lavoro del KDF inferiore agli standard attuali, metadati in chiaro nel formato legacy e una chiave KeyStore (sblocco PIN) non vincolata all'autenticazione. Le comunicazioni usano TLS ma **mancano certificate pinning**, aggiornamento del security provider e disabilitazione del traffico in chiaro. Sul piano piattaforma, il browser interno riapre la nota **RCE via `addJavascriptInterface`** sui device datati, oltre a esposizione a overlay/tapjacking e pulizia incompleta delle WebView.

L'area più debole è la **resilienza**: root detection presente ma inefficace, e assenza totale di emulator detection, controlli di integrità del codice, rilevamento di strumenti di instrumentation/anti-debugging e offuscamento; la chiave di firma è una **RSA a 1024 bit**. Nel complesso, pur con il vault adeguatamente protetto a riposo, la combinazione di segreti in memoria, assenza di pinning, RCE sui device datati e scarsa resilienza costituisce un rischio concreto per un'app di questa categoria.

## 7. Vulnerabilità individuate

| # | Vulnerabilità | MASVS v2 |
|---|---|---|
| 1 | Assenza di una device-access-security policy | STORAGE |
| 2 | Esposizione della Master Password in chiaro nella memoria | STORAGE |
| 3 | Mancato aggiornamento del Security Provider | NETWORK |
| 4 | Assenza di certificate pinning | NETWORK |
| 5 | Remote Code Execution tramite `addJavascriptInterface` sui device datati | PLATFORM |
| 6 | Esposizione ad attacchi di overlay e tapjacking | PLATFORM |
| 7 | Assenza di aggiornamento obbligatorio | CODE |
| 8 | Inefficacia dei meccanismi di root detection | RESILIENCE |
| 9 | Assenza di emulator detection | RESILIENCE |
| 10 | Assenza di controlli di integrità del codice | RESILIENCE |
| 11 | Assenza di offuscamento del codice | RESILIENCE |
| 12 | Assenza di rilevamento di strumenti di RE / instrumentazione dinamica | RESILIENCE |
| 13 | Assenza di rilevamento anti-debugging | RESILIENCE |

> Le evidenze complete di ciascuna vulnerabilità — passi MASTG, artefatti e mitigazioni — sono documentate in **`Documentazione SAM.pdf`** (cap. 4).

## 8. Finding deboli

Criticità minori o a impatto mitigato emerse durante l'analisi:

| # | Finding | Sintesi |
|---|---|---|
| 1 | Iterazioni KDF ridotte (24.000) | SQLCipher usa 24k iterazioni vs 256k dello standard attuale: abbassa il costo di un brute-force offline sulla Master Password |
| 2 | Chiave KeyStore (PIN) non vincolata all'auth | La chiave per lo sblocco con PIN non usa `setUserAuthenticationRequired(true)` |
| 3 | Metadati in chiaro (Keychain4) | Nel vecchio formato vault i campi Title/Type restano in chiaro |
| 4 | Firma RSA 1024 bit (no v3) | Chiave RSA a 1024 bit (debole, std ≥ 2048) e assenza di schema di firma v3 |
| 5 | Pulizia WebView incompleta | "Clear web data" manuale, non invoca `WebStorage.deleteAllData()` |
| 6 | Permessi eccessivi/malformati | Permessi non necessari e una voce malformata (refuso `android.permission.AndroidO`) |
| 7 | SDK di tracking non necessari | Google Analytics e Tag Manager impacchettati ma inerti |
| 8 | Cifratura non autenticata | AES-CBC senza authenticated encryption (GCM) né HMAC esplicito su alcune componenti |
| 9 | Traffico in chiaro non disabilitato | `usesCleartextTraffic` non impostato a `false` (targetSdk 24) |
| 10 | `PendingIntent` senza `FLAG_IMMUTABLE` | Mutabili di default ma incapsulano Intent espliciti verso componenti interni |

## 9. Controlli OWASP eseguiti

Controlli MASVS v2 / test MASTG verificati nel report (cap. 4.7):

| Gruppo | Controlli |
|---|---|
| MASVS-STORAGE | STORAGE-1, STORAGE-2 |
| MASVS-CRYPTO | CRYPTO-1, CRYPTO-2 |
| MASVS-AUTH | AUTH-2 |
| MASVS-NETWORK | NETWORK-1, NETWORK-2 |
| MASVS-PLATFORM | PLATFORM-1, PLATFORM-2, PLATFORM-3 |
| MASVS-CODE | CODE-2, CODE-3, CODE-4 |
| MASVS-RESILIENCE | RESILIENCE-1, RESILIENCE-2, RESILIENCE-3, RESILIENCE-4 |

## 10. Struttura del repository

```
SAM2526-Enpass/
├── README.md
├── Documentazione SAM.pdf              # Relazione completa dell'assessment
├── Presentazione SAM.pdf               # Slide di presentazione
└── enpass-password-manager-5-6-9.apk   # APK analizzato
```

## 11. Autore e disclaimer

Progetto realizzato a scopo **didattico** per l'insegnamento di **Sicurezza in Ambienti Mobile (SAM) – A.A. 2025/2026**, Università degli Studi di Bari "Aldo Moro", Dipartimento di Informatica.

- **Candidato:** Matteo Esposito (matr. 806075) – [@espositic](https://github.com/espositic)
- **Docente:** Prof. Paolo Buono

> ⚠️ **Disclaimer:** tutte le attività sono state svolte in un ambiente di laboratorio controllato, su emulatori di proprietà dell'autore. Le informazioni contenute hanno finalità esclusivamente accademiche e non devono essere utilizzate per attività non autorizzate. Eventuali vulnerabilità vanno gestite secondo i principi di _responsible disclosure_.

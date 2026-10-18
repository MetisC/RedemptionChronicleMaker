# Showcase module-load crash

User observed a crash loading Taller del Narrador; other chronicles work.
Windows Application Error at 2026-10-18 11:21:32 reports Vampire.exe,
exception 0xc0000005, offset 0x97c16. No new scene trace was written.

## Confirmed in the executable

`native_metadata_cash.txt` disassembles the read-only installed executable.
The `cash` branch starts at 0x497b65. Three token/resolver calls append
nonzero template handles to `[chronicle+0x1aeb8+count*4]`; the count is
at +0x1aec4, directly after three slots. There is no capacity check and
no reset between CASH lines. The fourth stored handle overwrites the
count. A subsequent store indexes using this corrupt value. The reported
fault is precisely that third-token store at 0x497c16.

## Confirmed in generated files

The old combined Showcase NMF contains CASH cashuk, CASH cashus, then
CASH GoldBag GoldCoins cashus cashuk. The native reader only consumes
three names per line, so this attempts five appends. Other deployed RCM
NMF files did not exceed three consumed names in the read-only audit.
The original mp_salon NMF's fourth name is itself ignored by this reader.

## Correction and limits

Campaign aggregation emits one CASH line, deduplicating template names
case-insensitively, preserving first appearance and allowing three native
currencies total. Source NMFs and original files are not edited. All
noncurrency resource records remain. Individual scene NMFs retain their
original one-line contract. Output validation independently counts native
token consumption and rejects cumulative overflow, even repeated names.

Showcase now registers cashuk, cashus and GoldBag. GoldCoins cannot fit
the engine table in this mixed modern/medieval metadata set and is listed
in build_report.currency_profile.omitted_templates. It is not used by the
Showcase story; this is a native currency auto-pickup limit, not removal
of its item/template from the resource catalogue. Existing single-currency
tutorial and mini output/runtime are preserved.

## Verification status

Five regressions cover the real Showcase multi-scene build, truncation,
case/comma handling, duplicate native appends and the publication gate.
Real Codex compilation remains classfile 45.3. Authoritative full-gate
counts are in build/tests/quality_report.json and test_report.json.

The crash cause matches original native instructions and the Windows
fault address. **Corrected initial native load: RUNTIME VERIFIED by the user, 2026-10-18: “Funciona bien y abre.”**
Do not convert offline compilation into native acceptance.

## Following request

FINAL_FLECKS_REQUIREMENTS.md preserves the user's new surgical audit.
Music stack, native conversation starts and stationary NCP research are
the next authorized task **after the loading repair works**, as requested.
Do not add those features while diagnosing this crash.

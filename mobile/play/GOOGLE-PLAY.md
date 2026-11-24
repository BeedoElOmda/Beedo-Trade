# Publishing Beedo-Trade on Google Play

Everything Google Play asks for, ready to copy, and the steps in order. The pictures are in `mobile/play/store/`.

## 1. Create your upload key (once)

Google Play only accepts a bundle (`.aab`) signed with your own **upload key**. You create it on your PC; nobody else sees the password.

1. In a terminal in the Beedo-Trade folder, run:

   ```
   uv run --with cryptography python mobile/play/make_upload_key.py
   ```

2. Type a password twice (it isn't shown). The key is saved as `Documents\Beedo-Trade-keys\beedo-trade-upload-key.p12`, and the key itself is copied to the clipboard as text.
3. **Back up** that file and the password (a USB stick or your password manager). Every future update needs the same key. If you lose it, Google can reset it, but that takes a support request and a few days.

## 2. Give the key to GitHub (once)

On GitHub: **Beedo-Trade › Settings › Secrets and variables › Actions › New repository secret**. Add two secrets:

| Name | Value |
|---|---|
| `PLAY_UPLOAD_KEYSTORE` | Paste the clipboard from step 1 (a long line of letters and numbers) |
| `PLAY_UPLOAD_PASSWORD` | The password you chose |

From then on, every release also gets `Beedo-Trade-<version>-play.aab`, signed with your key. That is the file you upload to Google Play. (The `.apk` stays for installing outside Play.)

## 3. Create the app in Play Console

[play.google.com/console](https://play.google.com/console) › **Create app**:

- App name: **Beedo-Trade**
- Default language: **English (United States) – en-US**
- App or game: **App** · Free or paid: **Free**
- Tick the declarations (developer policies, US export laws) after reading them.

## 4. Set up your app (the "Dashboard" checklist)

| Item | Answer |
|---|---|
| Privacy policy | `https://github.com/BeedoElOmda/Beedo-Trade/blob/main/PRIVACY.md` |
| App access | All functionality is available without special access (no login) |
| Ads | No, the app has no ads |
| Content rating | Category **Reference, News, or Educational**. Answer **No** to every question about violence, sexuality, language, controlled substances, gambling, user interaction and sharing location. Expected rating: Everyone / PEGI 3 |
| Target audience | **18 and over** only (it is about investing) |
| News app | No |
| Data safety | See the table below |
| Government app | No |
| Financial features | The app offers **none** of the listed financial services (no trading, payments, loans, crypto or banking). If the list has an "information / analysis only" option, choose that; otherwise choose "My app doesn't provide any financial features" |
| Health | No |
| App category | **Finance** |
| Contact details | Your email (required by Google, shown on the store page) and optionally `https://github.com/BeedoElOmda/Beedo-Trade` as the website |

**Data safety answers**

| Question | Answer |
|---|---|
| Does your app collect or share any of the required user data types? | **No** |
| Is all of the user data collected by your app encrypted in transit? | Yes (the app uses HTTPS to the data sources) |
| Do you provide a way for users to request that their data is deleted? | Not applicable: no data leaves the device; uninstalling deletes everything |

Why "No": the watchlist, portfolio and settings never leave the phone, and the requests to Yahoo Finance and TradingView contain only stock codes. Google's own definitions say data processed only on the device is not "collected".

## 5. Store listing (Grow › Store presence › Main store listing)

**App name** (30 characters max)

```
Beedo-Trade
```

**Short description, English** (80 max)

```
EGX stock signals from your course method: score, alerts, weekly check, gold.
```

**Full description, English** (4,000 max)

```
Beedo-Trade analyses Egyptian Exchange (EGX) stocks with a technical-analysis course method and turns it into a clear signal: Alarm, First or Confirm, Buy or Sell, with separate advice for a cash holder and a shareholder.

HOW THE SIGNAL WORKS
A 12-step checklist reads support and resistance, the trend (higher highs and lows), moving-average crossovers (5 / 9 / 18 by default, or your own), RSI zones and divergence, volume, reversal candles, gaps and MACD. Each step gives a score; the total sets the signal. Tick or untick any step and see the signal change.

WHAT YOU GET
• Analysis of any EGX stock with chart, RSI and MACD
• Weekly check: warns when the daily and weekly signals disagree
• Watchlist and Screener with scores, company ratings and key ratios
• Market health: the EGX30 and how many stocks are in an uptrend, also per industry
• Alerts on price, score and signal changes, as phone notifications, checked every trading day after the close
• Trade plan: entry, stop, target and position size from your cash and risk
• Back-test and "time machine" odds for a planned trade
• Gold and silver in Egyptian pounds per gram (24k, 21k, 18k)
• Arabic and English, light and dark themes
• Works without an account; your data stays on your phone

Beedo-Trade is a learning and decision-support tool, not investment advice. It never places orders. Prices are 15 minutes delayed: always check the live price and the day's disclosures before trading.
```

**Short description, Arabic** (add a translation: Store listing › Manage translations › Arabic)

```
إشارات أسهم البورصة المصرية بطريقة الكورس: النقاط والتنبيهات والذهب.
```

**Full description, Arabic**

```
يحلل Beedo-Trade أسهم البورصة المصرية بطريقة كورس التحليل الفني، ويحوّل النتيجة إلى إشارة واضحة: تنبيه أو أولي أو تأكيد، شراء أو بيع، مع نصيحة منفصلة لصاحب السيولة ولحامل السهم.

كيف تُحسب الإشارة
قائمة من 12 خطوة تقرأ الدعم والمقاومة والاتجاه والمتوسطات المتحركة (5 / 9 / 18 افتراضيًا أو متوسطاتك أنت) ومؤشر RSI والحجم وشموع الانعكاس والفجوات وMACD. كل خطوة تعطي نقاطًا، ومجموعها يحدد الإشارة. يمكنك تحديد أي خطوة أو إلغاؤها ورؤية أثرها فورًا.

المميزات
• تحليل أي سهم مصري مع الرسم البياني وRSI وMACD
• فحص أسبوعي ينبهك عندما تختلف الإشارة اليومية عن الأسبوعية
• قائمة متابعة وفلتر للأسهم بالنقاط وتقييم الشركة وأهم النسب
• صحة السوق: مؤشر EGX30 ونسبة الأسهم الصاعدة، ولكل قطاع
• تنبيهات السعر والنقاط وتغيّر الإشارة كإشعارات على الهاتف، تُفحص كل يوم تداول بعد الإغلاق
• خطة تداول: الدخول ووقف الخسارة والهدف وحجم المركز
• اختبار تاريخي واحتمالات "آلة الزمن" للصفقة
• الذهب والفضة بالجنيه المصري للجرام (عيار 24 و21 و18)
• العربية والإنجليزية، ومظهر فاتح وداكن
• بدون حساب، وبياناتك تبقى على هاتفك

Beedo-Trade أداة للتعلم ودعم القرار وليست نصيحة استثمارية، ولا تنفذ أي أوامر. الأسعار بنهاية اليوم وقد تتأخر: تحقق دائمًا من السعر الحالي وإفصاحات اليوم قبل التداول.
```

**Graphics** (in `mobile/play/store/`)

| Field | File |
|---|---|
| App icon (512 × 512) | `icon-512.png` |
| Feature graphic (1024 × 500) | `feature-graphic-1024x500.png` |
| Phone screenshots (2 to 8) | `phone-1-analyze-COMI.png`, `phone-2-analyze-ETEL.png`, `phone-3-watchlist.png`, `phone-4-gold-silver.png` |

To redo the icon and banner after changing `app/packaging/icon.png`: `python mobile/play/make_store_art.py`.

## 6. Test, then publish

New personal developer accounts must run a **closed test with at least 12 testers for 14 days in a row** before Google allows a public (production) release.

1. **Internal testing** (Testing › Internal testing › Create new release): upload the `-play.aab` from the latest GitHub release. Accept **Play App Signing** when asked (Google keeps the final signing key; you keep the upload key). Add yourself as a tester and install from the link to check it works.
2. **Closed testing** (Testing › Closed testing): same `.aab`; add at least **12 testers** (their Gmail addresses, or a Google Group). Each tester opens the opt-in link and installs the app. Keep them opted in for **14 days**.
3. After 14 days: **Apply for production** on the Dashboard and answer Google's questions about the test. When approved, create a production release with the latest `.aab`. Google's review usually takes from a few hours to a few days.

Testers who installed the GitHub `.apk` must **uninstall it first**: the Play version is signed with a different key, so Android won't install it over the test build.

## 7. Each new version

Publish the release on GitHub as usual. The release gets a new `-play.aab` signed with your key and a higher version code. In Play Console, create a new release on the same track and upload it.

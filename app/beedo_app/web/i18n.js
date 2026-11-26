/* Arabic interface. Every piece of text shown on screen is looked up here by its exact English wording;
   text with no entry stays in English. Sentences built from live numbers are matched by AR_RULES.
   Company names, stock codes and source names (TradingView, Yahoo Finance) stay in English on purpose. */
"use strict";
const AR = {
  // menu and common buttons
  "Mo'ashir Trade": "مؤشر تريد",
  "Analyze": "تحليل", "Watchlist": "قائمة المتابعة", "Portfolio": "المحفظة", "Gold & Silver": "الذهب والفضة", "Screener": "فرز الأسهم", "About": "عن البرنامج",
  "EGX technical analysis": "التحليل الفني للبورصة المصرية", "User guide": "دليل المستخدم", "Open the user guide": "فتح دليل المستخدم",
  "Special thanks to": "شكر خاص إلى", "Dr. Ahmed El Otefy": "د. احمد العطيفي", "Score": "النقاط", "Alert at score (5 or -5)": "تنبيه عند النقاط (5 أو -5)", "Weekly candles:": "الشموع الأسبوعية:",
  "· The daily and weekly signals disagree: be careful.": "· الإشارة اليومية والأسبوعية مختلفتان: توخَّ الحذر.",
  "Enter a price or a score to be alerted at": "أدخل سعرًا أو نقاطًا للتنبيه عندها",
  "Copy your settings to another device": "انقل إعداداتك إلى جهاز آخر", "Show my code": "اعرض الرمز", "Apply pasted code": "طبّق الرمز الملصق",
  "Your watchlist, alerts, portfolio, moving averages and ticked indicators as one code. Press \"Show my code\", copy it, paste it into this box on your other PC or phone, and press \"Apply pasted code\".": "قائمة المتابعة والتنبيهات والمحفظة والمتوسطات المتحركة والمؤشرات المحددة في رمز واحد. اضغط «اعرض الرمز» وانسخه، ثم الصقه في هذا المربع على جهازك الآخر واضغط «طبّق الرمز الملصق».",
  "Code copied": "تم نسخ الرمز", "Code ready: copy it from the box": "الرمز جاهز: انسخه من المربع", "That code isn't valid": "هذا الرمز غير صالح", "Settings applied": "تم تطبيق الإعدادات",
  "Theme: Dark": "المظهر: داكن", "Theme: Light": "المظهر: فاتح", "Theme: System": "المظهر: حسب النظام",
  "USD / EGP": "الدولار / الجنيه", "Import CSV": "استيراد CSV", "Save as PDF": "حفظ PDF", "Export to Excel": "تصدير إلى Excel",
  "Refresh": "تحديث", "Add": "إضافة", "Scan all": "فحص الكل", "Scanning…": "جارٍ الفحص…", "Check now": "افحص الآن",
  "Check for updates": "البحث عن تحديثات", "Report a problem": "الإبلاغ عن مشكلة", "You have the latest version": "لديك أحدث إصدار",
  "Saved. Open the file with Excel.": "تم الحفظ. افتح الملف ببرنامج Excel.", "Nothing to export yet": "لا يوجد ما يمكن تصديره بعد",
  "Enter an EGX code such as COMI": "أدخل رمز سهم مثل COMI", "Add a stock first": "أضف سهمًا أولًا",
  "EGX code, e.g. COMI": "رمز السهم، مثل COMI", "Add EGX code": "أضف رمز سهم",

  // signal ladder
  "Confirm Buy": "تأكيد شراء", "First Buy": "شراء أولي", "Alarm Buy": "تنبيه شراء", "Hold": "انتظار",
  "Alarm Sell": "تنبيه بيع", "First Sell": "بيع أولي", "Confirm Sell": "تأكيد بيع",
  "trend, moving averages, RSI and volume all agree upward": "الاتجاه والمتوسطات المتحركة ومؤشر RSI وحجم التداول تتفق كلها على الصعود",
  "an uptrend is starting but isn't confirmed yet": "اتجاه صاعد يبدأ لكنه لم يتأكد بعد",
  "early signs of a turn upward only": "إشارات مبكرة فقط على تحول نحو الصعود",
  "no clear signal": "لا توجد إشارة واضحة",
  "early signs of a turn downward only": "إشارات مبكرة فقط على تحول نحو الهبوط",
  "a downtrend is starting": "اتجاه هابط يبدأ",
  "trend, moving averages, RSI and volume all agree downward": "الاتجاه والمتوسطات المتحركة ومؤشر RSI وحجم التداول تتفق كلها على الهبوط",
  "trend and moving averages are still down": "الاتجاه والمتوسطات المتحركة ما زالت هابطة",
  "trend and moving averages are still up": "الاتجاه والمتوسطات المتحركة ما زالت صاعدة",
  "price is pressing against resistance": "السعر يضغط على مستوى المقاومة",
  "the market is moving sideways: wait for a breakout": "السوق يتحرك عرضيًا: انتظر الاختراق",
  "Industry health": "صحة القطاعات", "Industry": "النشاط", "Stocks": "الأسهم", "Above 50-day": "أعلى من متوسط 50", "Above 200-day": "أعلى من متوسط 200",
  "Up / down today": "صاعد / هابط اليوم", "Avg change": "متوسط التغير", "Health": "الحالة", "Too few stocks": "أسهم قليلة", "No industry data.": "لا توجد بيانات للقطاعات.",
  "Healthy": "قوي", "Mixed": "متذبذب", "All indicators counted": "كل المؤشرات محسوبة",
  "Each indicator lands on one rung of the ladder. Untick an indicator to leave it out of the signal; \"Untick →\" shows what that would do today.": "كل مؤشر يقع على درجة من سلّم الإشارات. ألغِ تحديد أي مؤشر لاستبعاده من الإشارة؛ ويوضح «إلغاء ←» ما سيحدث للإشارة اليوم.",
  "Count this indicator in the signal": "احسب هذا المؤشر في الإشارة", "Switched off: not counted in the signal.": "مستبعَد: لا يُحسب في الإشارة.",
  "Healthy: at least 60% of the industry's stocks are above both their 50-day and 200-day averages. Weak: 40% or fewer above both. Industries with fewer than 3 stocks get no label. TradingView, end of day.": "قوي: 60% على الأقل من أسهم النشاط أعلى من متوسطي 50 و200 يوم. ضعيف: 40% أو أقل. الأنشطة التي بها أقل من 3 أسهم بلا تصنيف. المصدر TradingView، نهاية اليوم.",
  "MACD 12 / 26 / 9": "MACD 12 / 26 / 9", "line, signal and histogram": "الخط والإشارة والأعمدة",
  "Moving averages (fast / mid / slow)": "المتوسطات المتحركة (سريع / متوسط / بطيء)", "Apply": "تطبيق", "Default 5 / 9 / 18": "الافتراضي 5 / 9 / 18", "What the signal would become": "ما ستصبح عليه الإشارة",
  "Fast moving average": "المتوسط السريع", "Mid moving average": "المتوسط الأوسط", "Slow moving average": "المتوسط البطيء", "Chart range": "مدة الرسم",
  "Fast, mid and slow moving averages. They draw the chart lines and give the signals: fast x mid = Alarm, fast x slow = First, mid x slow = Confirm.": "المتوسطات المتحركة السريع والأوسط والبطيء. تُرسم على الشارت وتعطي الإشارات: السريع × الأوسط = تنبيه، السريع × البطيء = أولي، الأوسط × البطيء = تأكيد.",
  "Moving averages must be three whole numbers, fast < mid < slow, between 2 and 250.": "يجب أن تكون المتوسطات ثلاثة أعداد صحيحة، السريع < الأوسط < البطيء، بين 2 و250.",
  "Healthy: EGX30 above its 50- and 200-day averages and most stocks above their 50-day average. Weak: the opposite. TradingView, end of day.": "قوي: مؤشر EGX30 أعلى من متوسطي 50 و200 يوم ومعظم الأسهم أعلى من متوسط 50 يومًا. ضعيف: العكس. المصدر TradingView، نهاية اليوم.",
  "buy and sell evidence balance out": "دلائل الشراء والبيع متعادلة",

  // what to do
  "What to do": "ماذا تفعل", "Cash holder": "صاحب السيولة", "Shareholder": "حامل السهم",
  "Buy the full position.": "اشترِ الكمية كاملة.", "Hold, or add on pullbacks.": "احتفظ، أو زِد عند التراجعات.",
  "Buy part of the position (e.g. half). Add the rest on Confirm Buy.": "اشترِ جزءًا من الكمية (النصف مثلًا) وأكمل الباقي عند تأكيد الشراء.",
  "Hold.": "احتفظ.", "Get ready, but don't buy yet. Wait for First Buy.": "استعد، لكن لا تشترِ بعد. انتظر إشارة الشراء الأولي.",
  "Stay in cash and wait for a clear signal.": "ابقَ في السيولة وانتظر إشارة واضحة.",
  "Hold. In a sideways market, reduce or step out.": "احتفظ. في السوق العرضي خفّف أو اخرج.",
  "Stay out.": "ابقَ خارج السهم.", "Get ready to sell: tighten your stop.": "استعد للبيع: قرّب وقف الخسارة.",
  "Sell part of the position (reduce).": "بِع جزءًا من الكمية (تخفيف).", "Sell.": "بِع.",

  // analyze page
  "Analyse an EGX stock": "حلّل سهمًا في البورصة المصرية",
  "Type a 4-letter code, or pick one below. You get the signal, the actions for your position, the chart and the 12-indicator checklist.": "اكتب رمز السهم أو اختر من الأسماء أدناه. ستحصل على الإشارة، وما يجب فعله، والرسم البياني، وقائمة المؤشرات الاثني عشر.",
  "Volume": "حجم التداول", "Support": "الدعم", "Resistance": "المقاومة", "vs 20-day average": "مقارنة بمتوسط 20 يومًا",
  "none below": "لا يوجد دعم أدنى", "none above": "لا توجد مقاومة أعلى",
  "Combined view: company + chart": "الرؤية المجمّعة: الشركة + الرسم البياني",
  "Key figures": "أهم الأرقام", "Chart": "الرسم البياني", "Daily": "يومي", "Weekly": "أسبوعي",
  "Support / resistance": "الدعم / المقاومة", "Swing points": "القمم والقيعان",
  "Company rating": "تقييم الشركة", "12-indicator checklist": "قائمة المؤشرات الاثني عشر", "MACD (12 / 26 / 9)": "مؤشر MACD (12 / 26 / 9)", "Each indicator lands on one rung of the ladder": "كل مؤشر يقع على درجة من سلّم الإشارات",
  "What would change the signal": "ما الذي يغيّر الإشارة", "Upward": "صعودًا", "Downward": "هبوطًا",
  "Already fully bullish": "الإشارة صاعدة بالكامل", "Already fully bearish": "الإشارة هابطة بالكامل",
  "Trade plan": "خطة الصفقة", "Cash (EGP)": "السيولة (جنيه)", "Max risk per trade (%)": "أقصى مخاطرة للصفقة (%)",
  "Entry (last close)": "الدخول (آخر إغلاق)", "Stop (below support)": "وقف الخسارة (تحت الدعم)", "Risk per share": "المخاطرة للسهم", "Risk per gram": "المخاطرة للجرام",
  "Target (2R)": "الهدف (ضعف المخاطرة)", "First resistance": "أول مقاومة", "Shares": "عدد الأسهم", "Grams": "عدد الجرامات", "Cost": "التكلفة", "Loss if stopped": "الخسارة عند الوقف",
  "The signal isn't a First or Confirm Buy: treat this as a plan to have ready, not a trade for today.": "الإشارة ليست شراء أوليًا ولا تأكيد شراء: اعتبر هذه خطة جاهزة، لا صفقة لليوم.",
  "Learning and decision-support tool for technical analysis. Not investment advice. Free data can be delayed: check the live price and the day's EGX disclosures before trading.": "أداة للتعلّم ودعم القرار في التحليل الفني. ليست نصيحة استثمارية. البيانات المجانية قد تكون متأخرة: راجع السعر اللحظي وإفصاحات البورصة قبل التداول.",
  "Standard rules on the last 12 months of reported results (TradingView). Each figure is compared with similar companies. Not part of the technical signal.": "قواعد قياسية على نتائج آخر 12 شهرًا (TradingView). كل رقم يُقارن بالشركات المشابهة. ليست جزءًا من الإشارة الفنية.",

  // checklist step names
  "Historical support & resistance": "الدعم والمقاومة التاريخيان", "Recent support & resistance": "الدعم والمقاومة الحديثان", "Price location": "موقع السعر",
  "Trend": "الاتجاه", "Reversal candles": "الشموع الانعكاسية", "RSI (14)": "مؤشر RSI (14)",
  "Price gaps": "الفجوات السعرية", "Reversal patterns": "النماذج الانعكاسية", "Continuation patterns": "النماذج الاستمرارية",
  "Judged on the chart; not scored automatically.": "تُقيَّم على الرسم البياني ولا تُحسب آليًا.",

  // key figures
  "Valuation": "التقييم", "Profitability": "الربحية", "Financial health": "السلامة المالية", "Growth & size": "النمو والحجم", "Price & risk": "السعر والمخاطرة",
  "Market cap": "القيمة السوقية", "EPS (12 m)": "ربحية السهم (12 شهرًا)", "Dividend yield": "عائد التوزيعات", "Return on equity": "العائد على حقوق الملكية",
  "Return on assets": "العائد على الأصول", "Gross margin": "هامش مجمل الربح", "Operating margin": "هامش التشغيل", "Net margin": "هامش صافي الربح",
  "Debt / equity": "الديون / حقوق الملكية", "Current ratio": "نسبة التداول", "Total debt": "إجمالي الديون", "Free cash flow": "التدفق النقدي الحر",
  "Revenue (12 m)": "الإيرادات (12 شهرًا)", "Net income": "صافي الربح", "Revenue growth": "نمو الإيرادات", "EPS growth": "نمو ربحية السهم",
  "Performance 1 M": "الأداء خلال شهر", "Performance 3 M": "الأداء خلال 3 أشهر", "Year to date": "منذ بداية العام", "Performance 1 Y": "الأداء خلال سنة",
  "Beta (1 Y)": "بيتا (سنة)", "Volatility (month)": "التذبذب (شهر)", "Avg volume (30 d)": "متوسط التداول (30 يومًا)", "52-week range": "نطاق 52 أسبوعًا",
  "Last 12 months of reported results · TradingView": "نتائج آخر 12 شهرًا · TradingView",

  // company rating
  "Strong": "قوية", "Fair": "متوسطة", "Weak": "ضعيفة", "Good": "جيد", "Poor": "ضعيف", "No data": "لا بيانات", "Not enough data": "بيانات غير كافية", "Not rated": "غير مقيَّمة", "Metal": "معدن",
  "P/E (valuation)": "مضاعف الربحية (التقييم)", "P/B (price vs book value)": "السعر إلى القيمة الدفترية", "Net profit margin": "هامش صافي الربح",
  "Debt to equity": "الديون إلى حقوق الملكية", "Earnings growth (yearly)": "نمو الأرباح (سنوي)", "Revenue growth (yearly)": "نمو الإيرادات (سنوي)",
  "Best setup": "أفضل فرصة", "Watch": "راقب", "Wait": "انتظر", "Acceptable": "مقبول", "No edge": "لا أفضلية", "Stay out": "ابقَ خارجًا", "Speculative": "مضاربة", "Avoid": "تجنّب", "No rating": "بلا تقييم",
  "Best setup: a strong company with a buy signal.": "أفضل فرصة: شركة قوية مع إشارة شراء.",
  "Strong company, but no buy signal yet: put it on your watchlist and wait.": "شركة قوية لكن بلا إشارة شراء بعد: ضعها في قائمة المتابعة وانتظر.",
  "Strong company in a falling trend: wait for the chart to turn before buying.": "شركة قوية في اتجاه هابط: انتظر تحوّل الرسم البياني قبل الشراء.",
  "Acceptable: a fair company with a buy signal. Consider a smaller position.": "مقبول: شركة متوسطة مع إشارة شراء. فكّر في كمية أصغر.",
  "Fair company with no clear signal: no edge right now.": "شركة متوسطة بلا إشارة واضحة: لا أفضلية الآن.",
  "Fair company in a falling trend: stay out for now.": "شركة متوسطة في اتجاه هابط: ابقَ خارجًا حاليًا.",
  "Speculative: the chart says buy but the business is weak. Use a small size, or skip it.": "مضاربة: الرسم البياني يقول اشترِ لكن الشركة ضعيفة. استخدم كمية صغيرة أو تجاوزها.",
  "Avoid: a weak business without a buy signal.": "تجنّب: شركة ضعيفة بلا إشارة شراء.",
  "No fundamentals rating: rely on the technical signal, and keep positions small.": "لا يوجد تقييم مالي: اعتمد على الإشارة الفنية واجعل الكميات صغيرة.",

  // tables
  "Stock": "السهم", "Close": "الإغلاق", "Signal": "الإشارة", "Company": "الشركة", "Debt/Eq.": "الديون/الملكية", "Div. yield": "عائد التوزيعات",
  "Mkt cap": "القيمة السوقية", "View": "الرؤية", "Quantity": "الكمية", "Buy price": "سعر الشراء", "Value": "القيمة", "Profit / loss": "الربح / الخسارة", "Return": "العائد",
  "Press \"Scan all\" to check every stock on your list.": "اضغط «فحص الكل» لفحص كل الأسهم في قائمتك.",

  // alerts
  "Alerts": "التنبيهات", "Code": "الرمز", "Alert at or above (EGP)": "نبّهني عند السعر أو أعلى (جنيه)", "Alert at or below (EGP)": "نبّهني عند السعر أو أدنى (جنيه)", "Add alert": "إضافة تنبيه",
  "Checked when the app starts and every 15 minutes while it is open, against the latest daily close. You are also told when the signal of a stock on your watchlist or in your portfolio changes. Alerts are information, not orders.": "تُفحص عند فتح البرنامج وكل 15 دقيقة أثناء تشغيله، على آخر إغلاق يومي. ستُبلَّغ أيضًا عند تغيّر إشارة أي سهم في قائمة المتابعة أو المحفظة. التنبيهات معلومات وليست أوامر.",
  "No alerts right now": "لا توجد تنبيهات الآن", "Enter a price to be alerted at": "أدخل السعر الذي تريد التنبيه عنده",

  // portfolio
  "What you own, what it is worth at the last close, and what the signal says a shareholder should do.": "ما تملكه، وقيمته عند آخر إغلاق، وما تقوله الإشارة لحامل السهم.",
  "Average buy price (EGP)": "متوسط سعر الشراء (جنيه)", "Add holding": "إضافة", "at the last close": "عند آخر إغلاق", "Loading prices…": "جارٍ تحميل الأسعار…",
  "Add what you own above. Use GOLD or SILVER with a quantity in grams for metals.": "أضف ما تملكه أعلاه. للمعادن استخدم GOLD أو SILVER مع الكمية بالجرام.",
  "Your holdings are saved only on this computer. Values use the last daily close, which can be delayed. Not investment advice.": "بياناتك محفوظة على هذا الجهاز فقط. القيم محسوبة على آخر إغلاق يومي وقد يكون متأخرًا. ليست نصيحة استثمارية.",
  "Enter the quantity and the price you paid": "أدخل الكمية وسعر الشراء",

  // time machine
  "Time machine": "آلة الزمن", "Run time machine": "تشغيل آلة الزمن", "Target first": "الهدف أولًا", "Stop first": "وقف الخسارة أولًا", "Neither": "لا هذا ولا ذاك", "Average R": "متوسط R",
  "Time machine failed": "تعذّر تشغيل آلة الزمن",
  "How often would the trade plan above reach its target before its stop? It replays the next 20 trading days 10,000 times from this stock's own daily moves of the past two years, and checks the same plan on past days that had the same signal. A simulation, not a prediction.": "كم مرة تصل خطة التداول أعلاه إلى الهدف قبل وقف الخسارة؟ تعيد آلة الزمن تشغيل أيام التداول العشرين القادمة 10,000 مرة من حركات السهم اليومية خلال العامين الماضيين، وتختبر نفس الخطة في الأيام السابقة التي ظهرت فيها نفس الإشارة. هذه محاكاة وليست توقعًا.",
  // back-test
  "Back-test": "الاختبار التاريخي", "Run back-test": "تشغيل الاختبار التاريخي", "Running…": "جارٍ التشغيل…",
  "Replays the checklist day by day over the past two years. It buys at the close on a First or Confirm Buy and sells at the close on a First or Confirm Sell. Fees and taxes are not counted. Past results do not predict future results.": "يعيد تطبيق قائمة المؤشرات يومًا بيوم على العامين الماضيين: يشتري عند الإغلاق مع إشارة شراء أولي أو تأكيد شراء، ويبيع عند الإغلاق مع إشارة بيع أولي أو تأكيد بيع. لا تُحسب العمولات والضرائب. نتائج الماضي لا تتنبأ بالمستقبل.",
  "Signal method": "منهج الإشارات", "following the signals": "باتباع الإشارات", "Buy and hold": "الشراء والاحتفاظ", "bought on the first day": "شراء من أول يوم",
  "Trades": "الصفقات", "Winners": "الرابحة", "trades in profit": "صفقات رابحة", "Bought": "تاريخ الشراء", "Sold": "تاريخ البيع", "Price": "السعر", "Result": "النتيجة", "Still open": "ما زالت مفتوحة",
  "The method gave no First or Confirm Buy in this period, so it stayed in cash.": "لم يعطِ المنهج إشارة شراء أولي أو تأكيد شراء في هذه الفترة، فبقي في السيولة.",

  // gold & silver
  "International prices in Egyptian pounds, with the 12-indicator checklist applied to each metal.": "الأسعار العالمية بالجنيه المصري، مع تطبيق قائمة المؤشرات الاثني عشر على كل معدن.",
  "Gold": "الذهب", "Silver": "الفضة", "Market": "السوق", "24k, per gram": "عيار 24، للجرام", "999, per gram": "999، للجرام", "Per ounce": "للأوقية",
  "Change today (USD)": "تغيّر اليوم (دولار)", "1 year (USD)": "سنة (دولار)", "52-week range (USD/oz)": "نطاق 52 أسبوعًا (دولار/أوقية)",
  "US dollar, official rate": "الدولار الأمريكي، السعر الرسمي", "Gold / silver ratio": "نسبة الذهب إلى الفضة",
  "Add to watchlist": "أضف إلى قائمة المتابعة",
  "How many ounces of silver one ounce of gold buys. Above about 80, silver is cheap compared with gold; below about 50, gold is.": "عدد أوقيات الفضة التي تشتريها أوقية ذهب واحدة. فوق 80 تقريبًا تكون الفضة رخيصة مقارنة بالذهب، وتحت 50 تقريبًا يكون الذهب هو الأرخص.",

  // screener
  "Find strong companies that the 12-indicator checklist says are in a buy zone, across the whole Egyptian Exchange.": "ابحث في كل البورصة المصرية عن شركات قوية تقول قائمة المؤشرات الاثني عشر إنها في منطقة شراء.",
  "Company quality": "جودة الشركة", "Strong only": "القوية فقط", "Strong or Fair": "القوية أو المتوسطة", "Technical signal": "الإشارة الفنية",
  "First or Confirm Buy": "شراء أولي أو تأكيد شراء", "Any buy, including Alarm Buy": "أي شراء، ومنه تنبيه الشراء", "Any signal": "أي إشارة",
  "Sector": "القطاع", "All sectors": "كل القطاعات", "Run screener": "تشغيل الفرز", "Screening…": "جارٍ الفرز…",
  "Choose your filters and press \"Run screener\". It takes about 20 to 40 seconds.": "اختر الشروط واضغط «تشغيل الفرز». يستغرق من 20 إلى 40 ثانية تقريبًا.",

  // about
  "About Mo'ashir Trade": "عن مؤشر تريد", "The signal ladder": "سلّم الإشارات", "Where the numbers come from": "مصدر الأرقام", "Important": "تنبيه مهم",
  "Mo'ashir Trade applies technical analysis to Egyptian Exchange stocks, the same way every time: 12 indicators (11 chart indicators plus MACD), one signal, and separate advice for a cash holder and a shareholder.": "يطبّق مؤشر تريد التحليل الفني على أسهم البورصة المصرية بالطريقة نفسها في كل مرة: 12 مؤشرًا (11 مؤشرًا على الرسم البياني ومؤشر MACD)، إشارة واحدة، ونصيحة منفصلة لصاحب السيولة ولحامل السهم.",
  "Alarm = early warning, get ready. First = start a position (or start reducing). Confirm = several signals agree, act fully. The signal is the score of the ticked indicators: each adds its rung (Confirm +3, First +2, Alarm +1, Hold 0, minus for sells); 9 or more = Confirm, 5 = First, 2 = Alarm.": "التنبيه = إنذار مبكر، استعد. الأولي = ابدأ الشراء (أو ابدأ التخفيف). التأكيد = عدة إشارات متفقة، نفّذ بالكامل. الإشارة هي مجموع نقاط المؤشرات المحددة: كل مؤشر يضيف درجته (تأكيد +3، أولي +2، تنبيه +1، انتظار 0، وبالسالب للبيع)؛ 9 فأكثر = تأكيد، 5 = أولي، 2 = تنبيه.",
  "This is a learning and decision-support tool. It is": "هذه أداة للتعلّم ودعم القرار. وهي", "not investment advice": "ليست نصيحة استثمارية",
  ", it does not know your full financial situation, and it never places orders. Free data can be delayed: always check the live price and the day's disclosures before trading.": "، ولا تعرف وضعك المالي الكامل، ولا تنفّذ أي أوامر. البيانات المجانية قد تكون متأخرة: راجع دائمًا السعر اللحظي وإفصاحات اليوم قبل التداول.",
  "Prices: daily history from Yahoo Finance (e.g. COMI → COMI.CA), and the last two trading days from TradingView, 15 minutes delayed (during trading hours, today so far). The larger, widely traded EGX stocks are covered; for others, use": "الأسعار: التاريخ اليومي من Yahoo Finance (مثال COMI ← COMI.CA)، وآخر يومي تداول من TradingView متأخرة 15 دقيقة (وأثناء التداول: اليوم حتى الآن). الأسهم الكبيرة الأكثر تداولًا مغطاة؛ ولغيرها استخدم",
  "with date, open, high, low, close and volume columns.": "بأعمدة التاريخ والافتتاح والأعلى والأدنى والإغلاق وحجم التداول.",
  "Indicators: moving averages you choose (default 5 / 9 / 18), MACD 12 / 26 / 9, RSI 14 (Wilder), swing highs and lows, support and resistance, 20-day volume average, reversal candles and gaps.": "المؤشرات: متوسطات متحركة تختارها (الافتراضي 5 / 9 / 18)، وMACD 12 / 26 / 9، وRSI 14 (طريقة وايلدر)، والقمم والقيعان، والدعم والمقاومة، ومتوسط حجم التداول لعشرين يومًا، والشموع الانعكاسية والفجوات.",
  "Chart and pattern indicators 10 and 11 are judged on the chart: the swing points are marked for you.": "المؤشران 10 و11 (النماذج) يُقيَّمان على الرسم البياني: القمم والقيعان محددة لك عليه.",
  "Company fundamentals: TradingView's market data (last 12 months of reported results), rated with standard rules and compared with similar companies. Smaller companies often have too few reported figures to rate.": "بيانات الشركات: من بيانات TradingView (نتائج آخر 12 شهرًا)، تُقيَّم بقواعد قياسية وتُقارن بالشركات المشابهة. كثير من الشركات الصغيرة أرقامها المنشورة لا تكفي لتقييمها.",
  "Charts by": "الرسوم البيانية من", "Lightweight Charts™ (Apache 2.0). Source:": "Lightweight Charts™ (Apache 2.0). الكود المصدري:",

  // 2.2.2: tooltips and labels
  "Switch theme: dark, light or follow Windows / macOS": "تبديل المظهر: داكن أو فاتح أو حسب ويندوز / ماك", "EGX stock code": "رمز السهم في البورصة المصرية",
  "Official US dollar rate (Yahoo Finance)": "سعر الدولار الرسمي (Yahoo Finance)", "Open the Mo'ashir Trade user guide": "فتح دليل مستخدم مؤشر تريد",
  "Open the download page": "فتح صفحة التحميل", "New alerts": "تنبيهات جديدة", "Analyse daily prices from a CSV file": "حلّل الأسعار اليومية من ملف CSV",
  "Print this analysis, or save it as a PDF file": "اطبع هذا التحليل أو احفظه ملف PDF", "Signal ladder": "سلّم الإشارات", "Chart period": "فترة الرسم البياني",
  "Charting by TradingView": "الرسوم البيانية من TradingView", "Add stock": "إضافة سهم", "Remove alert": "حذف التنبيه", "Settings code": "رمز الإعدادات",
  "Total of the ticked indicators: 9 = Confirm, 5 = First, 2 = Alarm": "مجموع نقاط المؤشرات المحددة: 9 = تأكيد، 5 = أولي، 2 = تنبيه",
  "Price / earnings per share (last 12 months)": "السعر ÷ ربحية السهم (آخر 12 شهرًا)", "Price / book value per share": "السعر ÷ القيمة الدفترية للسهم",
  "Price / sales per share": "السعر ÷ مبيعات السهم", "Above 1 = moves more than the market": "أكثر من 1 = يتحرك أكثر من السوق",
  "Current assets / current liabilities: above 1 means short-term bills are covered": "الأصول المتداولة ÷ الخصوم المتداولة: أكثر من 1 يعني أن الالتزامات قصيرة الأجل مغطاة",
  "P/E": "مضاعف الربحية", "P/B": "السعر / القيمة الدفترية", "P/S": "السعر / المبيعات", "EV / EBITDA": "قيمة المنشأة / EBITDA", "RSI 14": "مؤشر RSI 14",
  "Couldn't load company figures": "تعذّر تحميل أرقام الشركة", "Couldn't save": "تعذّر الحفظ", "Couldn't update the signal": "تعذّر تحديث الإشارة",
  "Couldn't load weekly prices": "تعذّر تحميل الأسعار الأسبوعية", "Couldn't load the portfolio": "تعذّر تحميل المحفظة", "Couldn't load prices": "تعذّر تحميل الأسعار",
  "Back-test failed": "تعذّر تشغيل الاختبار التاريخي", "Couldn't check for updates. Check your internet connection.": "تعذّر البحث عن تحديثات. تحقّق من اتصال الإنترنت.",
  "Rating every EGX company, then checking the best ones with the 12-indicator checklist…": "جارٍ تقييم كل شركات البورصة المصرية ثم فحص أفضلها بقائمة المؤشرات الاثني عشر…",
  "No company matches right now. Try \"Strong or Fair\" or \"Any buy, including Alarm Buy\".": "لا توجد شركة مطابقة الآن. جرّب «القوية أو المتوسطة» أو «أي شراء، ومنه تنبيه الشراء».",
  "Certificate problem: the app can't verify the secure connection. Update to the latest Mo'ashir Trade version, or reinstall it.": "مشكلة في الشهادة: البرنامج لا يستطيع التحقق من الاتصال الآمن. حدّث إلى أحدث إصدار من مؤشر تريد أو أعد تثبيته.",
  "Yahoo Finance may not carry this stock. Try": "قد لا يغطي Yahoo Finance هذا السهم. جرّب", "with daily prices (date, open, high, low, close, volume).": "بأسعار يومية (التاريخ، الافتتاح، الأعلى، الأدنى، الإغلاق، الحجم).",
  "Check your internet connection, firewall or VPN, then try again.": "تحقّق من اتصال الإنترنت أو الجدار الناري أو الـVPN ثم حاول مرة أخرى.", "Check the code and try again.": "تحقّق من الرمز وحاول مرة أخرى.",
  "40 · gold cheap": "40 · الذهب رخيص", "120 · silver cheap": "120 · الفضة رخيصة",
  "Gold (24k, EGP per gram)": "الذهب (عيار 24، جنيه للجرام)", "Silver (999, EGP per gram)": "الفضة (999، جنيه للجرام)",
  "Yahoo Finance (international price, converted at the official USD/EGP rate). These are international prices: Egyptian shop prices for jewellery and bars add a local premium and workmanship fees. Not investment advice.": "Yahoo Finance (السعر العالمي محوّلًا بسعر الدولار الرسمي). هذه أسعار عالمية: أسعار المحلات في مصر للمشغولات والسبائك تضيف علاوة محلية ومصنعية. ليست نصيحة استثمارية.",

  // checklist readings and notes
  "At resistance: don't buy; wait for breakout and retest": "عند المقاومة: لا تشترِ؛ انتظر الاختراق ثم إعادة الاختبار",
  "At support: best buy zone if a reversal confirms": "عند الدعم: أفضل منطقة شراء إذا تأكد الانعكاس",
  "Below all recent supports (breakdown)": "أسفل كل مستويات الدعم الحديثة (كسر)", "Above all recent resistances (breakout)": "أعلى كل مستويات المقاومة الحديثة (اختراق)",
  "No open gaps in the last 30 days": "لا توجد فجوات مفتوحة في آخر 30 يومًا",
  "Look for head & shoulders, double/triple tops or bottoms on the marked swing points": "ابحث عن الرأس والكتفين والقمم أو القيعان المزدوجة/الثلاثية عند القمم والقيعان المحددة",
  "Look for ascending, descending or symmetrical triangles on the marked swing points": "ابحث عن المثلثات الصاعدة أو الهابطة أو المتماثلة عند القمم والقيعان المحددة",
  "Check the chart: breakaway, continuation or exhaustion depends on where it sits in the trend.": "راجع الرسم البياني: نوع الفجوة (اختراق أو استمرار أو إنهاك) يتوقف على موقعها من الاتجاه.",
  "From the 52-week low and high (TradingView).": "من أدنى وأعلى سعر خلال 52 أسبوعًا (TradingView).", "From TradingView's monthly pivots.": "من نقاط الارتكاز الشهرية في TradingView.",
  "TradingView has no usable pivots for this stock.": "لا توجد في TradingView نقاط ارتكاز صالحة لهذا السهم.",
  "No recent support below the price to place a stop.": "لا يوجد دعم حديث أسفل السعر لوضع وقف الخسارة عنده.",
  "The first resistance is less than 1R away: poor risk-reward. Don't buy near resistance.": "أول مقاومة على مسافة أقل من 1R: العائد ضعيف مقارنة بالمخاطرة. لا تشترِ قرب المقاومة.",
  "Not enough price history to back-test.": "لا توجد أسعار تاريخية كافية للاختبار التاريخي.",
  "overbought >=70": "تشبّع شرائي ≥ 70", "oversold <=30": "تشبّع بيعي ≤ 30", "bullish 50-70": "إيجابية 50-70", "bearish 30-50": "سلبية 30-50", "centerline 50": "عند خط المنتصف 50",
  "Doji (indecision)": "دوجي (تردد)", "Hammer (bullish reversal)": "مطرقة (انعكاس صاعد)", "Hanging Man (bearish reversal)": "الرجل المشنوق (انعكاس هابط)",
  "Hammer-shape (no trend context)": "شكل مطرقة (بلا اتجاه سابق)", "Inverted Hammer (bullish reversal)": "مطرقة مقلوبة (انعكاس صاعد)",
  "Shooting Star (bearish reversal)": "الشهاب (انعكاس هابط)", "Inverted-hammer shape (no trend context)": "شكل مطرقة مقلوبة (بلا اتجاه سابق)",
  "Bullish Engulfing": "ابتلاع شرائي", "Bearish Engulfing": "ابتلاع بيعي", "White/bullish body": "جسم أبيض صاعد", "Black/bearish body": "جسم أسود هابط",
  "mixed (intermingling)": "متداخلة (بلا ترتيب)",

  // company rating reasons
  "No earnings data": "لا توجد بيانات أرباح", "Loss-making over the last 12 months": "خاسرة خلال آخر 12 شهرًا",
  "Cheap for its earnings": "رخيصة مقارنة بأرباحها", "Fairly valued": "مقيّمة بسعر عادل", "Expensive for its earnings": "غالية مقارنة بأرباحها",
  "No book-value data": "لا توجد بيانات للقيمة الدفترية", "Low price for its assets": "سعر منخفض مقارنة بأصولها",
  "Normal price for its assets": "سعر عادي مقارنة بأصولها", "High price for its assets": "سعر مرتفع مقارنة بأصولها",
  "No profitability data": "لا توجد بيانات ربحية", "Earns well on shareholders' money (15%+)": "عائد جيد على أموال المساهمين (15% فأكثر)",
  "Moderate returns (8-15%)": "عائد متوسط (8-15%)", "Weak returns (under 8%)": "عائد ضعيف (أقل من 8%)",
  "No margin data": "لا توجد بيانات هوامش", "Keeps a healthy share of sales as profit": "تحقق ربحًا جيدًا من مبيعاتها",
  "Thin but positive margins": "هوامش ضئيلة لكنها موجبة", "Little or no profit on sales": "ربح ضئيل أو منعدم من المبيعات",
  "No debt data": "لا توجد بيانات ديون", "Low debt (0.5 or less)": "ديون منخفضة (0.5 أو أقل)", "Moderate debt (up to 1.5)": "ديون متوسطة (حتى 1.5)", "High debt (over 1.5)": "ديون مرتفعة (أكثر من 1.5)",
  "No growth data": "لا توجد بيانات نمو", "Strong growth (20%+, above inflation)": "نمو قوي (20% فأكثر، أعلى من التضخم)",
  "Growing, but slower than inflation": "تنمو لكن أبطأ من التضخم", "Earnings are falling": "الأرباح تتراجع",
  "Sales growing strongly (20%+)": "المبيعات تنمو بقوة (20% فأكثر)", "Sales growing slowly": "المبيعات تنمو ببطء", "Sales are shrinking": "المبيعات تتراجع",
  "Pays a solid dividend (4%+)": "توزيعات جيدة (4% فأكثر)", "Pays a small dividend": "توزيعات صغيرة",
  "TradingView has too few reported figures for this company to rate it.": "أرقام هذه الشركة في TradingView قليلة لا تكفي لتقييمها.",
  "TradingView has no company data for this code.": "لا توجد في TradingView بيانات شركة لهذا الرمز.",

  // 2.3: back-test and time machine settings
  "Replays the checklist day by day over the period you choose. The default setting buys at the close on a First or Confirm Buy and sells on a First or Confirm Sell. Enter your broker's commission plus taxes as the fee: it is paid on each buy and each sell. Past results do not predict future results.":
    "يعيد تطبيق قائمة المؤشرات يومًا بيوم على الفترة التي تختارها. الإعداد الافتراضي يشتري عند الإغلاق مع إشارة شراء أولي أو تأكيد شراء، ويبيع مع إشارة بيع أولي أو تأكيد بيع. أدخل عمولة السمسار مع الضرائب كرسوم: تُدفع عند كل شراء وكل بيع. نتائج الماضي لا تتنبأ بالمستقبل.",
  "Period": "الفترة", "1 year": "سنة", "2 years": "سنتان", "5 years": "5 سنوات", "Buy on": "الشراء عند", "Sell on": "البيع عند",
  "Confirm Buy only": "تأكيد الشراء فقط", "Confirm Sell only": "تأكيد البيع فقط", "First or Confirm Sell": "بيع أولي أو تأكيد بيع",
  "Any sell, including Alarm Sell": "أي بيع، ومنه تنبيه البيع", "Fee per buy and per sell (%)": "الرسوم لكل شراء ولكل بيع (%)",
  "Reset to defaults": "العودة للإعدادات الافتراضية", "Your settings differ from the defaults.": "إعداداتك تختلف عن الإعدادات الافتراضية.",
  "The method gave no buy signal at your buy level in this period, so it stayed in cash.": "لم يعطِ المنهج إشارة شراء عند المستوى الذي اخترته في هذه الفترة، فبقي في السيولة.",
  "How often would a buy plan reach its target before its stop? The default setting uses the trade plan above (entry at the last close, stop below support, target 2 times the risk) over the next 20 trading days. It replays those days 10,000 times from this stock's own daily moves of the past two years, and checks the same plan on past days that had the same signal. A simulation, not a prediction.":
    "كم مرة تصل خطة الشراء إلى الهدف قبل وقف الخسارة؟ الإعداد الافتراضي يستخدم خطة الصفقة أعلاه (الدخول عند آخر إغلاق، ووقف الخسارة تحت الدعم، والهدف ضعف المخاطرة) خلال أيام التداول العشرين القادمة. تعيد آلة الزمن تشغيل هذه الأيام 10,000 مرة من حركات السهم اليومية خلال العامين الماضيين، وتختبر نفس الخطة في الأيام السابقة التي ظهرت فيها نفس الإشارة. هذه محاكاة وليست توقعًا.",
  "Days ahead": "عدد الأيام القادمة", "Target (times the risk)": "الهدف (مضاعف المخاطرة)", "Entry (EGP)": "الدخول (جنيه)", "Stop (EGP)": "وقف الخسارة (جنيه)",
  "Last close": "آخر إغلاق", "Below support": "تحت الدعم", "The stop must be below the entry price.": "يجب أن يكون وقف الخسارة أقل من سعر الدخول.",
  "The back-test settings must be numbers.": "إعدادات الاختبار التاريخي يجب أن تكون أرقامًا.", "The time machine settings must be numbers.": "إعدادات آلة الزمن يجب أن تكون أرقامًا.",
  "Back-test settings: 1, 2 or 5 years, a buy and a sell level, and a fee between 0 and 5%.": "إعدادات الاختبار التاريخي: سنة أو سنتان أو 5 سنوات، ومستوى للشراء وآخر للبيع، ورسوم بين 0 و5%.",
  "Time machine settings: 10, 20, 40 or 60 days, and a target of 0.5 to 5 times the risk.": "إعدادات آلة الزمن: 10 أو 20 أو 40 أو 60 يومًا، وهدف من 0.5 إلى 5 أضعاف المخاطرة.",
  "The plan needs a stop below the entry and a target above it.": "الخطة تحتاج وقف خسارة أقل من الدخول وهدفًا أعلى منه.",

  // 2.3: dividends
  "Dividends": "التوزيعات",
  "Cash dividends and bonus shares of the last 5 years, from Yahoo Finance, and the payout to expect next from that history. Expected payouts are a pattern from history, not an announcement: the company's general assembly decides. Past amounts are adjusted for later bonus shares. The months are ex-dividend months: buy before the ex-dividend date to receive the dividend.":
    "التوزيعات النقدية وأسهم المنحة في آخر 5 سنوات من Yahoo Finance، والتوزيع المتوقع التالي بناءً على هذا التاريخ. التوزيع المتوقع نمط من الماضي وليس إعلانًا: الجمعية العامة للشركة هي التي تقرر. المبالغ القديمة معدّلة بأسهم المنحة اللاحقة. الأشهر هي أشهر الاستحقاق (Ex-dividend): اشترِ قبل تاريخ الاستحقاق لتحصل على التوزيع.",
  "Show": "عرض", "All payers": "كل الموزِّعين", "Cash": "نقدي", "Bonus shares": "أسهم منحة", "Both": "كلاهما", "Cash and bonus shares": "نقدي وأسهم منحة",
  "My watchlist and portfolio": "قائمتي ومحفظتي", "Whole EGX": "كل البورصة", "Pays": "يوزّع", "Expected next": "التوزيع المتوقع", "Expected next (ex-dividend)": "التوزيع المتوقع (شهر الاستحقاق)",
  "Last cash (EGP)": "آخر توزيع نقدي (جنيه)", "Cash yield (12 m)": "العائد النقدي (12 شهرًا)", "Last bonus shares": "آخر أسهم منحة", "Years paid (of 5)": "سنوات التوزيع (من 5)",
  "Choose \"My watchlist and portfolio\", or \"Whole EGX\" (about 20 seconds).": "اختر «قائمتي ومحفظتي» أو «كل البورصة» (20 ثانية تقريبًا).",
  "Checking dividend histories…": "جارٍ فحص تاريخ التوزيعات…", "No dividend payers found.": "لا توجد شركات موزِّعة.", "Couldn't load dividends": "تعذّر تحميل التوزيعات",
  "No regular pattern": "لا يوجد نمط منتظم",

  // 2.3: my trading rules and the example plan
  "My trading rules": "قواعد التداول الخاصة بي", "Answer again": "أجب من جديد",
  "Answer 6 short questions. Your answers set the rules the app uses for position sizes and for the example plan. They stay on this device only.":
    "أجب عن 6 أسئلة قصيرة. إجاباتك تحدد القواعد التي يستخدمها البرنامج لأحجام المراكز وللخطة المثال. تبقى على هذا الجهاز فقط.",
  "What is your main goal?": "ما هدفك الأساسي؟", "Protect my money": "الحفاظ على أموالي", "Regular income from dividends": "دخل منتظم من التوزيعات",
  "Grow my money over years": "تنمية أموالي على سنوات", "Fast gains": "أرباح سريعة",
  "When might you need this money?": "متى قد تحتاج هذه الأموال؟", "Within a year": "خلال سنة", "1 to 3 years": "من سنة إلى 3 سنوات", "3 to 5 years": "من 3 إلى 5 سنوات", "More than 5 years": "أكثر من 5 سنوات",
  "Your stocks fall 20% in one month. What do you do?": "هبطت أسهمك 20% في شهر. ماذا تفعل؟", "Sell everything": "أبيع كل شيء", "Sell part": "أبيع جزءًا", "Hold and wait": "أحتفظ وأنتظر", "Buy more": "أشتري المزيد",
  "The largest yearly loss you can accept?": "أقصى خسارة سنوية تقبلها؟", "30% or more": "30% فأكثر",
  "Your trading experience?": "خبرتك في التداول؟", "None": "لا توجد", "Less than 2 years": "أقل من سنتين", "2 to 5 years": "من 2 إلى 5 سنوات", "5+ years, I always use a stop-loss": "أكثر من 5 سنوات وأستخدم وقف الخسارة دائمًا",
  "How much of your savings is this?": "ما نسبة هذا المبلغ من مدخراتك؟", "Most of it (over 75%)": "معظمها (أكثر من 75%)", "Less than 25%": "أقل من 25%",
  "Set my rules": "حدّد قواعدي", "Save my rules": "احفظ قواعدي", "Your rules are saved": "تم حفظ قواعدك", "Your profile:": "ملفك:",
  "Careful": "حذِر", "Balanced": "متوازن", "Bold": "جريء", "Answer all six questions.": "أجب عن الأسئلة الستة كلها.",
  "Because you may need this money soon (or it is most of your savings), your rules are set to Careful.": "لأنك قد تحتاج هذه الأموال قريبًا (أو لأنها معظم مدخراتك)، ضُبطت قواعدك على «حذِر».",
  "Risk per trade (%)": "المخاطرة للصفقة (%)", "Max in one stock (%)": "أقصى نسبة لسهم واحد (%)", "Number of stocks": "عدد الأسهم", "Cash kept aside (%)": "السيولة الاحتياطية (%)",
  "Max per sector (%)": "أقصى نسبة لقطاع (%)", "Buy signals used": "إشارات الشراء المستخدمة", "Any rated company": "أي شركة مقيَّمة",
  "Fill in every rule with a number.": "اكتب رقمًا في كل قاعدة.", "Some rules are outside their allowed range.": "بعض القواعد خارج الحدود المسموحة.",
  "Example plan from your rules": "خطة مثال من قواعدك", "Amount to plan (EGP)": "المبلغ المراد التخطيط له (جنيه)", "Build example plan": "ابنِ الخطة المثال", "Building…": "جارٍ البناء…",
  "This is an example, not a recommendation.": "هذا مثال وليس توصية.",
  "It applies the rules you chose and the 12-indicator checklist to today's data. It does not know your full financial situation and is not investment advice. Check each stock yourself; you decide what to buy.":
    "يطبّق القواعد التي اخترتها وقائمة المؤشرات الاثني عشر على بيانات اليوم. لا يعرف وضعك المالي الكامل وليس نصيحة استثمارية. راجع كل سهم بنفسك، والقرار لك.",
  "Amount": "المبلغ", "Invested": "المستثمر", "Cash kept aside": "السيولة الاحتياطية", "Entry": "الدخول", "Stop": "وقف الخسارة", "Share of the total": "النسبة من الإجمالي",
  "Answer the questions in My trading rules first.": "أجب أولًا عن أسئلة «قواعد التداول الخاصة بي».", "Enter an amount of at least 1,000 EGP.": "أدخل مبلغًا لا يقل عن 1,000 جنيه.",
  "Couldn't build the plan": "تعذّر بناء الخطة",
  // 2.3.2: trial version
  "Trial version": "نسخة تجريبية", "This trial version works until": "تعمل هذه النسخة التجريبية حتى", "Days left:": "الأيام المتبقية:",
  "Device code:": "رمز الجهاز:", "Unlocked on this device": "مفتوحة على هذا الجهاز", "until": "حتى",
  "The trial has ended": "انتهت الفترة التجريبية", "This trial version worked until": "عملت هذه النسخة التجريبية حتى",
  "Your watchlist and settings are kept.": "قائمة المتابعة والإعدادات محفوظة.",
  "To keep using it, send this device code to the developer and enter the unlock code you receive:": "لمواصلة الاستخدام، أرسل رمز الجهاز هذا إلى المطوّر وأدخل رمز الفتح الذي تتلقاه:",
  "Copy": "نسخ", "Unlock code": "رمز الفتح", "Paste your unlock code": "الصق رمز الفتح هنا", "Unlock": "فتح", "Check for a newer version": "ابحث عن نسخة أحدث",
  "Unlocked. Thank you!": "تم الفتح. شكرًا لك!", "Couldn't unlock": "تعذّر الفتح",
  "That unlock code isn't valid for this device.": "رمز الفتح هذا غير صالح لهذا الجهاز.", "This unlock code has expired.": "انتهت صلاحية رمز الفتح هذا.",
  "The trial has ended. Enter an unlock code.": "انتهت الفترة التجريبية. أدخل رمز الفتح.",
  // 2.3.2: willingness and ability, the total-loss limit
  "Willingness:": "الرغبة في المخاطرة:", "Ability:": "القدرة على المخاطرة:",
  "Your ability to take risk (when you need the money and how much of your savings it is) is lower than your willingness, so your rules follow the more careful of the two.":
    "قدرتك على تحمّل المخاطرة (متى تحتاج المال ونسبته من مدخراتك) أقل من رغبتك فيها، لذلك تتبع قواعدك الأكثر حذرًا بين الاثنين.",
  "Max total loss at stops (%)": "أقصى خسارة إجمالية عند وقف الخسارة (%)", "Loss if every stop is hit": "الخسارة إذا نُفّذت كل أوامر الوقف",

  // TradingView sectors and industries
  "Commercial Services": "الخدمات التجارية", "Communications": "الاتصالات", "Consumer Durables": "السلع المعمّرة", "Consumer Non-Durables": "السلع الاستهلاكية",
  "Consumer Services": "الخدمات الاستهلاكية", "Distribution Services": "خدمات التوزيع", "Electronic Technology": "التكنولوجيا الإلكترونية", "Energy Minerals": "الطاقة والوقود",
  "Finance": "الخدمات المالية", "Health Services": "الخدمات الصحية", "Health Technology": "التكنولوجيا الصحية", "Industrial Services": "الخدمات الصناعية",
  "Miscellaneous": "متنوعة", "Non-Energy Minerals": "المعادن ومواد البناء", "Process Industries": "الصناعات التحويلية", "Producer Manufacturing": "الصناعات الإنتاجية",
  "Retail Trade": "تجارة التجزئة", "Technology Services": "خدمات التكنولوجيا", "Transportation": "النقل", "Utilities": "المرافق",
  "Medical Distributors": "توزيع المستلزمات الطبية", "Other Transportation": "نقل آخر", "Major Banks": "البنوك الكبرى", "Regional Banks": "البنوك",
  "Food: Specialty/Candy": "أغذية متخصصة وحلويات", "Chemicals: Specialty": "كيماويات متخصصة", "Construction Materials": "مواد البناء",
  "Other Consumer Services": "خدمات استهلاكية أخرى", "Pharmaceuticals: Major": "الأدوية (شركات كبرى)", "Pharmaceuticals: Other": "الأدوية (أخرى)", "Other": "أخرى",
  "Hotels/Resorts/Cruise lines": "الفنادق والمنتجعات والرحلات البحرية", "Investment Managers": "إدارة الاستثمار", "Containers/Packaging": "العبوات والتغليف",
  "Financial Conglomerates": "مجموعات مالية", "Food Retail": "تجزئة الأغذية", "Metal Fabrication": "تشكيل المعادن", "Home Furnishings": "الأثاث المنزلي",
  "Building Products": "منتجات البناء", "Agricultural Commodities/Milling": "السلع الزراعية والمطاحن", "Steel": "الصلب", "Wholesale Distributors": "تجارة الجملة",
  "Investment Banks/Brokers": "بنوك الاستثمار والسمسرة", "Food: Meat/Fish/Dairy": "أغذية: لحوم وأسماك وألبان", "Packaged Software": "البرمجيات",
  "Real Estate Development": "التطوير العقاري", "Chemicals: Agricultural": "الأسمدة والكيماويات الزراعية", "Engineering & Construction": "الهندسة والمقاولات",
  "Hospital/Nursing Management": "إدارة المستشفيات", "Textiles": "المنسوجات", "Finance/Rental/Leasing": "التمويل والتأجير", "Medical/Nursing Services": "الخدمات الطبية والتمريض",
  "Electric Utilities": "الكهرباء", "Homebuilding": "الإسكان", "Miscellaneous Commercial Services": "خدمات تجارية متنوعة", "Broadcasting": "البث الإذاعي والتلفزيوني",
  "Industrial Specialties": "منتجات صناعية متخصصة", "Major Telecommunications": "شركات الاتصالات الكبرى", "Contract Drilling": "الحفر", "Tobacco": "التبغ",
  "Electrical Products": "المنتجات الكهربائية", "Commercial Printing/Forms": "الطباعة التجارية", "Investment Trusts/Mutual Funds": "صناديق الاستثمار",
  "Specialty Telecommunications": "اتصالات متخصصة", "Alternative Power Generation": "الطاقة البديلة", "Oilfield Services/Equipment": "خدمات ومعدات حقول البترول",
  "Movies/Entertainment": "السينما والترفيه", "Life/Health Insurance": "تأمين الحياة والصحة", "Marine Shipping": "الشحن البحري", "Oil Refining/Marketing": "تكرير وتسويق البترول",
  "Multi-Line Insurance": "التأمين", "Pulp & Paper": "الورق", "Apparel/Footwear": "الملابس والأحذية", "Services to the Health Industry": "خدمات للقطاع الصحي",
  "Aluminum": "الألومنيوم", "Wireless Telecommunications": "الاتصالات اللاسلكية", "Household/Personal Care": "المنظفات والعناية الشخصية",
  "Publishing: Books/Magazines": "نشر الكتب والمجلات", "Electronics Distributors": "توزيع الإلكترونيات", "Property/Casualty Insurance": "تأمين الممتلكات",
  "Chemicals: Major Diversified": "الكيماويات", "Gas Distributors": "توزيع الغاز", "Food Distributors": "توزيع الأغذية", "Apparel/Footwear Retail": "تجزئة الملابس والأحذية",
  "Information Technology Services": "خدمات تكنولوجيا المعلومات", "Industrial Machinery": "الآلات الصناعية", "Specialty Stores": "متاجر متخصصة",
  "Electronic Components": "المكونات الإلكترونية", "Internet Software/Services": "برمجيات وخدمات الإنترنت",
};
// pieces reused by the rules below
const UPDN = { above: "أعلى", below: "أدنى", up: "صعودًا", down: "هبوطًا", UP: "صعودًا", DOWN: "هبوطًا", rising: "صاعد", falling: "هابط" };
const ALIGN = (a) => a.replace(/ \(uptrend order\)$/, " (ترتيب صاعد)").replace(/ \(downtrend order\)$/, " (ترتيب هابط)").replace(/^mixed \(intermingling\)$/, "متداخلة (بلا ترتيب)");
const GROUP = { industry: "النشاط", sector: "القطاع", market: "السوق" };
const tx = (s) => tr(s) || s;
// Sentences assembled from parts
const AR_RULES = [
  // 2.3
  [/^(Cash|Bonus shares|Cash and bonus shares) · (regular|often)$/, (m) => `${AR[m[1]]} · ${m[2] === "regular" ? "منتظم" : "متكرر"}`],
  [/^1 for every ([\d.,]+)$/, (m) => `سهم مجاني لكل ${m[1]}`],
  [/^Checked (\d+) companies · (\d+) paid dividends in the last 5 years(?: · (\d+) have no data on Yahoo Finance)?$/,
    (m) => `فُحصت ${m[1]} شركة · ${m[2]} وزّعت أرباحًا في آخر 5 سنوات${m[3] ? ` · ${m[3]} بلا بيانات في Yahoo Finance` : ""}`],
  [/^\(score (\d+) of 24\)$/, (m) => `(النقاط ${m[1]} من 24)`],
  [/^Your profile: (Careful|Balanced|Bold)$/, (m) => `ملفك: ${AR[m[1]]}`],
  [/^(\d+) stocks$/, (m) => `${m[1]} أسهم`],
  [/^Trial: (\d+) days left$/, (m) => `الفترة التجريبية: متبقٍ ${m[1]} يومًا`],
  [/^Your limit of ([\d.]+)% total loss at the stops was reached, so the rest stays in cash\.$/, (m) => `بلغت حدك للخسارة الإجمالية عند وقف الخسارة (${m[1]}%)، فيبقى الباقي سيولة.`],
  [/^Ex-dividend drop on (\S+) \(([\d.]+) EGP dividend\), not a signal$/, (m) => `هبوط بسبب استحقاق توزيع في ${m[1]} (توزيع ${m[2]} جنيه)، وليس إشارة`],
  [/^Only (\d+) stocks meet your rules today, so the rest stays in cash\. That is normal in a weak market\.$/, (m) => `${m[1]} أسهم فقط تطابق قواعدك اليوم، فيبقى الباقي سيولة. هذا طبيعي في السوق الضعيف.`],
  [/^(\d+)\. (.+)$/, (m) => (AR[m[2]] ? `${m[1]}. ${AR[m[2]]}` : null)],
  [/^(\S+)% of the replays reached neither within (\d+) trading days; the price then decides those\.$/, (m) => `${m[1]}% من عمليات المحاكاة لم تصل إلى أيٍّ منهما خلال ${m[2]} يوم تداول؛ والسعر وقتها هو الذي يحسمها.`],
  // 2.2.2: checklist readings
  [/^support (\S+) \| resistance (\S+)$/, (m) => `الدعم ${m[1]} | المقاومة ${m[2]}`],
  [/^Mid-range: (\S+)% above support, (\S+)% below resistance$/, (m) => `منتصف النطاق: ${m[1]}% فوق الدعم، و${m[2]}% تحت المقاومة`],
  [/^Uptrend: (\d+) higher highs and higher lows$/, (m) => `اتجاه صاعد: ${m[1]} قمم وقيعان أعلى`],
  [/^Downtrend: (\d+) lower highs and lower lows$/, (m) => `اتجاه هابط: ${m[1]} قمم وقيعان أدنى`],
  [/^No clear trend \(HH (\d+), HL (\d+), LH (\d+), LL (\d+)\)$/, (m) => `لا يوجد اتجاه واضح (قمم أعلى ${m[1]}، قيعان أعلى ${m[2]}، قمم أدنى ${m[3]}، قيعان أدنى ${m[4]})`],
  [/^(MA\d+ \S+ \| MA\d+ \S+ \| MA\d+ \S+): (.+?)(?:; last cross (\d+x\d+) (UP|DOWN) on (\S+))?$/,
    (m) => `${m[1]}: ${ALIGN(m[2])}${m[3] ? `؛ آخر تقاطع ${m[3]} ${UPDN[m[4]]} في ${m[5]}` : ""}`],
  [/^(Rising|Falling) price on (above-average|light) volume \(.+\)\. Today (\S+)x the 20-day average\.?$/, (m) =>
    `${{ "Rising above-average": "سعر صاعد بحجم تداول أعلى من المتوسط (المشترون مسيطرون)", "Falling above-average": "سعر هابط بحجم تداول أعلى من المتوسط (البائعون مسيطرون)",
      "Falling light": "سعر هابط بحجم تداول ضعيف (البيع يضعف)", "Rising light": "سعر صاعد بحجم تداول ضعيف (الشراء يضعف)" }[`${m[1]} ${m[2]}`]}. اليوم ${m[3]}× متوسط 20 يومًا.`],
  [/^Latest candle: (.+)$/, (m) => `آخر شمعة: ${tx(m[1])}`],
  [/^(.+) on (\S+), confirmed by a (higher|lower) close$/, (m) => `${tx(m[1])} في ${m[2]}، تأكدت بإغلاق ${m[3] === "higher" ? "أعلى" : "أدنى"}`],
  [/^(.+) today: needs the next candle to confirm$/, (m) => `${tx(m[1])} اليوم: تحتاج الشمعة التالية للتأكيد`],
  [/^RSI (\S+) \((rising|falling) from (\S+)\), zone (.+?)(?:; (negative|positive) divergence)?$/,
    (m) => `RSI ${m[1]} (${m[2] === "rising" ? "صاعد" : "هابط"} من ${m[3]})، المنطقة ${tx(m[4])}${m[5] ? `؛ دايفرجنس ${m[5] === "negative" ? "سلبي" : "إيجابي"}` : ""}`],
  [/^Open gap (up|down) on (\S+) \((\S+) to (\S+)\), volume (\S+)x$/, (m) => `فجوة مفتوحة ${UPDN[m[1]]} في ${m[2]} (من ${m[3]} إلى ${m[4]})، الحجم ${m[5]}×`],
  [/^MACD (\S+) (above|below) its signal (\S+), (above|below) zero; histogram (growing|shrinking)(?:; last cross (up|down) on (\S+))?$/,
    (m) => `MACD ${m[1]} ${UPDN[m[2]]} من خط الإشارة ${m[3]}، و${UPDN[m[4]]} من الصفر؛ الأعمدة ${m[5] === "growing" ? "تكبر" : "تصغر"}${m[6] ? `؛ آخر تقاطع ${UPDN[m[6]]} في ${m[7]}` : ""}`],
  // what would change the signal, trade plan
  [/^MA(\d+) crossing (above|below) MA(\d+) = (.+)$/, (m) => `تقاطع MA${m[1]} ${m[2] === "above" ? "لأعلى" : "لأسفل"} مع MA${m[3]} = ${tx(m[4])}`],
  [/^a close above (\S+) on above-average volume = breakout$/, (m) => `إغلاق أعلى من ${m[1]} بحجم تداول أعلى من المتوسط = اختراق`],
  [/^a close below (\S+) = support broken$/, (m) => `إغلاق أدنى من ${m[1]} = كسر الدعم`],
  [/^Resistance at (\S+) comes before the target: take partial profit there if bearish candles appear\.?$/, (m) => `المقاومة عند ${m[1]} تسبق الهدف: جنِ جزءًا من الربح عندها إذا ظهرت شموع هابطة.`],
  [/^([\d.,]+)% (below|above)$/, (m) => `${m[1]}% ${m[2] === "below" ? "أسفل" : "أعلى"}`],
  // company rating, key figures, amounts
  [/^(Strong|Fair|Weak|Not enough data|Not rated) · (\d+)$/, (m) => `${AR[m[1]]} · ${m[2]}`],
  [/^(Couldn't load fundamentals: )?(\d+) good, (\d+) fair and (\d+) poor out of (\d+) checks( Bank: margin and debt checks don't apply to banks and are skipped\.)?$/,
    (m) => `${m[1] ? "تعذّر تحميل البيانات المالية: " : ""}${m[2]} جيد و${m[3]} متوسط و${m[4]} ضعيف من ${m[5]} معايير${m[6] ? " بنك: معايير الهوامش والديون لا تنطبق على البنوك فلم تُحسب." : ""}`],
  [/^(industry|sector|market) median (\S+)$/, (m) => `الوسيط في ${GROUP[m[1]]} ${m[2]}`],
  [/^(.*?)(?:^| · )market cap (\S+) bn EGP$/, (m) => `${m[1] ? m[1].split(" · ").map(tx).join(" · ") + " · " : ""}القيمة السوقية ${m[2]} مليار جنيه`],
  [/^(.+) · (.+)$/, (m) => (AR[m[1]] && AR[m[2]] ? `${AR[m[1]]} · ${AR[m[2]]}` : null)],
  [/^Now (\S+) · (\S+)% of range$/, (m) => `الآن ${m[1]} · ${m[2]}% من النطاق`],
  [/^(-?[\d.,]+) bn EGP$/, (m) => `${m[1]} مليار جنيه`], [/^(-?[\d.,]+) mn EGP$/, (m) => `${m[1]} مليون جنيه`],
  [/^(-?[\d.,]+) bn$/, (m) => `${m[1]} مليار`], [/^(-?[\d.,]+) mn$/, (m) => `${m[1]} مليون`],
  [/^(-?[\d.,]+) EGP$/, (m) => `${m[1]} جنيه`], [/^(-?[\d.,]+) EGP \((\S+)\)$/, (m) => `${m[1]} جنيه (${m[2]})`],
  [/^(\$[\d.,]+) · ([\d.,]+) EGP$/, (m) => `${m[1]} · ${m[2]} جنيه`],
  [/^today · (\S+)$/, (m) => `اليوم · ${m[1]}`],
  // back-test, time machine, screener, watchlist, about
  [/^(\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)$/, (m) => `من ${m[1]} إلى ${m[2]}`],
  [/^([\d,]+) replays, seed (\d+), daily moves from (\S+) to (\S+)\. A day that touches both the stop and the target counts as the stop\.$/,
    (m) => `${m[1]} محاكاة، البذرة ${m[2]}، من حركات يومية بين ${m[3]} و${m[4]}. اليوم الذي يلمس وقف الخسارة والهدف معًا يُحسب وقف خسارة.`],
  [/^Rated (\d+) companies · (\d+) met the quality filter · checked the top (\d+) with the 12-indicator checklist(?: · (\d+) skipped \(no price history\))? · (\d+) match\. Click a column header to sort\.$/,
    (m) => `قُيّمت ${m[1]} شركة · ${m[2]} اجتازت شرط الجودة · فُحصت أفضل ${m[3]} بقائمة المؤشرات الاثني عشر${m[4] ? ` · تُجووزت ${m[4]} (بلا أسعار تاريخية)` : ""} · ${m[5]} مطابقة. اضغط عنوان أي عمود للترتيب.`],
  [/^Checking (\d+) stocks…$/, (m) => `جارٍ فحص ${m[1]} أسهم…`],
  [/^Version (\S+)\. Your settings are saved in (.+)\.$/, (m) => `الإصدار ${m[1]}. إعداداتك محفوظة في ${m[2]}.`],
  [/^Remove (\S+)$/, (m) => `حذف ${m[1]}`],
  [/^Couldn't analyse (.+)$/, (m) => `تعذّر تحليل ${m[1] === "this stock" ? "هذا السهم" : m[1]}`],
  [/^(.*) Indicators that need daily history are marked "Not checked"\. Import a CSV of daily prices for the full checklist\.$/,
    (m) => `${tx(m[1])} المؤشرات التي تحتاج أسعارًا يومية مكتوب عليها «لم تُفحص». استورد ملف CSV بالأسعار اليومية للحصول على القائمة كاملة.`],
  // 2.0: the signal is the score of the ticked indicators
  [/^(.+); capped at Alarm because only a snapshot is available, without daily history\.?$/i, (m) => `${tr(m[1]) || m[1]}؛ الإشارة محدودة عند التنبيه لأنها لقطة فقط بدون أسعار يومية`],
  [/^score ([+-]?\d+) from (\d+) ticked indicators \(.+\)\.?$/i, (m) => `النقاط ${m[1]} من ${m[2]} مؤشرات محددة (تأكيد عند 9 فأكثر، أولي عند 5، تنبيه عند 2؛ وبالمثل تحت الصفر للبيع)`],
  [/^(.+); capped because (.+)$/i, (m) => `${tr(m[1]) || m[1]}؛ الإشارة محدودة لأن ${m[2].split(" and ").map((x) => tr(x) || x).join(" و")}`],
  [/^Update available: (.+)$/, (m) => `يوجد تحديث: ${m[1]}`],
  [/^Version (\S+) is available$/, (m) => `الإصدار ${m[1]} متاح`],
  [/^Version (\S+)$/, (m) => `الإصدار ${m[1]}`],
  [/^(\S+): signal changed from (.+) to (.+)$/, (m) => `${m[1]}: تغيّرت الإشارة من «${AR[m[2]] || m[2]}» إلى «${AR[m[3]] || m[3]}»`],
  [/^(\S+) closed at (\S+): at or (above|below) your alert price (\S+)$/, (m) => `${m[1]} أغلق عند ${m[2]}: عند سعر التنبيه ${m[4]} أو ${m[3] === "above" ? "أعلى" : "أدنى"}`],
  [/^(\d+) closed$/, (m) => `${m[1]} مغلقة`], [/^(\d+) of (\d+)$/, (m) => `${m[1]} من ${m[2]}`],
  [/^(\S+) is on your watchlist$/, (m) => `${m[1]} في قائمة المتابعة`],
  // 1.7: moving averages you choose, market health
  [/^Moving averages (\d+) \/ (\d+) \/ (\d+)$/, (m) => `المتوسطات المتحركة ${m[1]} / ${m[2]} / ${m[3]}`],
  [/^price is still (above|below) MA(\d+)$/, (m) => `السعر ما زال ${m[1] === "above" ? "أعلى" : "أدنى"} من متوسط ${m[2]}`],
  [/^Snapshot only: the signal stops at Alarm$/, () => "لقطة فقط: الإشارة لا تتجاوز مستوى التنبيه"],
  [/^Not checked: needs daily price history$/, () => "لم تُفحص: تحتاج أسعارًا يومية تاريخية"],
  [/^Not checked: no support or resistance levels available$/, () => "لم تُفحص: لا توجد مستويات دعم أو مقاومة"],
  [/^TradingView snapshot \(latest session\)$/, () => "لقطة من TradingView (آخر جلسة)"],
  [/^Indicators not counted: (.+)$/, (m) => `مؤشرات غير محسوبة: ${m[1]}`],
  [/^Signal unchanged: (.+)$/, (m) => `الإشارة لم تتغير: ${AR[m[1]] || m[1]}`],
  [/^Signal: (.+) → (.+)$/, (m) => `الإشارة: ${AR[m[1]] || m[1]} ← ${AR[m[2]] || m[2]}`],
  [/^(Untick|Tick) → (.+)$/, (m) => `${m[1] === "Untick" ? "إلغاء" : "تحديد"} ← ${AR[m[2]] || m[2]}`],
  [/^Count indicator (\d+) in the signal$/, (m) => `احسب المؤشر ${m[1]} في الإشارة`],
  [/^Moving averages (.+) saved$/, (m) => `تم حفظ المتوسطات المتحركة ${m[1]}`],
  [/^Market: (Healthy|Mixed|Weak)$/, (m) => `السوق: ${{ Healthy: "قوي", Mixed: "متذبذب", Weak: "ضعيف" }[m[1]]}`],
  [/^(above|below) its 50-day average, (above|below) its 200-day$/, (m) => `${m[1] === "above" ? "أعلى" : "أدنى"} من متوسط 50 يومًا، و${m[2] === "above" ? "أعلى" : "أدنى"} من متوسط 200 يوم`],
  [/^(\d+)% of (\d+) stocks above their 50-day average \((\d+)% above 200-day\)$/, (m) => `${m[1]}% من ${m[2]} سهمًا أعلى من متوسط 50 يومًا (${m[3]}% أعلى من متوسط 200 يوم)`],
  [/^(\d+) up · (\d+) down today$/, (m) => `${m[1]} صاعد · ${m[2]} هابط اليوم`],
  // 2.2.1: prices at most 15 minutes old
  [/^Close of (\S+) · Yahoo Finance \+ TradingView \(15 min delayed\)$/, (m) => `إغلاق ${m[1]} · Yahoo Finance + TradingView (متأخر 15 دقيقة)`],
  [/^Today so far · Yahoo Finance \+ TradingView \(15 min delayed\)$/, () => "اليوم حتى الآن · Yahoo Finance + TradingView (متأخر 15 دقيقة)"],
  // 2.1
  [/^\(score ([+-]?\d+)\)$/, (m) => `(النقاط ${m[1]})`],
  [/^(\S+): score ([+-]?\d+) \((.+)\) reached your alert score ([+-]?\d+)$/, (m) => `${m[1]}: النقاط ${m[2]} (${AR[m[3]] || m[3]}) بلغت نقاط التنبيه ${m[4]}`],
  [/^No internet: showing (\S+) as saved on (.+)$/, (m) => `لا يوجد اتصال: عرض ${m[1]} كما حُفظ في ${m[2]}`],
  // time machine
  [/^within (\d+) trading days$/, (m) => `خلال ${m[1]} يوم تداول`], [/^(\S+)R plan$/, (m) => `خطة ${m[1]}R`],
  [/^(Close to a coin flip|Close to break-even|Leans toward the target|Leans toward the stop|Strongly toward the target|Strongly toward the stop): the target came first in (\d+)% of the replays that reached one side; a (\S+)R plan needs (\d+)% to break even\.?$/,
    (m) => `${{ "Close to a coin flip": "قريب من رمي العملة", "Close to break-even": "قريب من التعادل", "Leans toward the target": "يميل نحو الهدف", "Leans toward the stop": "يميل نحو وقف الخسارة", "Strongly toward the target": "يميل بقوة نحو الهدف", "Strongly toward the stop": "يميل بقوة نحو وقف الخسارة" }[m[1]]}: وصل السعر إلى الهدف أولًا في ${m[2]}% من عمليات المحاكاة التي بلغت أحد الجانبين، وخطة ${m[3]}R تحتاج ${m[4]}% لتتعادل.`],
  [/^Same signal \((.+)\) on (\d+) past days: target first (\d+), stop first (\d+), neither (\d+)\.?$/, (m) => `نفس الإشارة (${AR[m[1]] || m[1]}) في ${m[2]} يومًا سابقًا: الهدف أولًا ${m[3]}، وقف الخسارة أولًا ${m[4]}، لا هذا ولا ذاك ${m[5]}.`],
  [/^The same signal \((.+)\) appeared on only (\d+) past days: too few to judge\.?$/, (m) => `ظهرت نفس الإشارة (${AR[m[1]] || m[1]}) في ${m[2]} يومًا سابقًا فقط: عدد قليل لا يكفي للحكم.`],
  [/^Price after (\d+) trading days: median (\S+) EGP, 90% of replays between (\S+) and (\S+?)\.?$/, (m) => `السعر بعد ${m[1]} يوم تداول: الوسيط ${m[2]} جنيه، و90% من عمليات المحاكاة بين ${m[3]} و${m[4]}.`],
];
function tr(text) {
  const k = text.trim();
  if (!k || /[؀-ۿ]/.test(k)) return null;  // already Arabic: translating again could loop the observer forever
  const bare = k.replace(/\.$/, "");
  if (!bare) return null;  // a lone "." (e.g. after a bold name) must not stop the whole translation
  const hit = AR[k] || AR[bare] || AR[bare[0].toLowerCase() + bare.slice(1)];
  if (hit) return hit;
  for (const [re, fn] of AR_RULES) { const m = k.match(re); const v = m && fn(m); if (v) return v; }
  return null;
}
function trNode(n) {
  if (n.nodeType === 3) {
    const v = tr(n.nodeValue);
    if (v && v !== n.nodeValue.trim()) n.nodeValue = n.nodeValue.replace(n.nodeValue.trim(), v);
  } else if (n.nodeType === 1 && !["SCRIPT", "STYLE", "CANVAS"].includes(n.tagName)) {
    for (const a of ["placeholder", "title", "aria-label"]) { const v = n.hasAttribute(a) && tr(n.getAttribute(a)); if (v) n.setAttribute(a, v); }
    n.childNodes.forEach(trNode);
  }
}
function startArabic() {
  document.documentElement.lang = "ar"; document.documentElement.dir = "rtl";
  trNode(document.body);
  // Translated text has no entry of its own, so the observer settles after one pass
  new MutationObserver((ms) => ms.forEach((m) => {
    if (m.type === "characterData") trNode(m.target);
    else if (m.type === "attributes") { const v = tr(m.target.getAttribute(m.attributeName) || ""); if (v) m.target.setAttribute(m.attributeName, v); }
    else m.addedNodes.forEach(trNode);
  })).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["placeholder", "title", "aria-label"] });
}

/* Arabic interface. Every piece of text shown on screen is looked up here by its exact English wording;
   text with no entry stays in English.
   shortcut: detailed readings built from live numbers (checklist readings, rating reasons) are not translated;
   add entries or patterns to AR_RULES when they are wanted. */
"use strict";
const AR = {
  // menu and common buttons
  "Analyze": "تحليل", "Watchlist": "قائمة المتابعة", "Portfolio": "المحفظة", "Gold & Silver": "الذهب والفضة", "Screener": "فرز الأسهم", "About": "عن البرنامج",
  "EGX course method": "منهج الدورة للبورصة المصرية", "User guide": "دليل المستخدم", "Open the user guide": "فتح دليل المستخدم",
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
  "Healthy": "قوي", "Mixed": "متذبذب", "All steps counted": "كل الخطوات محسوبة",
  "Each step lands on one rung of the ladder. Untick a step to leave it out of the signal; \"Untick →\" shows what that would do today.": "كل خطوة تقع على درجة من سلّم الإشارات. ألغِ تحديد أي خطوة لاستبعادها من الإشارة؛ ويوضح «إلغاء ←» ما سيحدث للإشارة اليوم.",
  "Count this step in the signal": "احسب هذه الخطوة في الإشارة", "Switched off: not counted in the signal.": "مستبعدة: لا تُحسب في الإشارة.",
  "Healthy: at least 60% of the industry's stocks are above both their 50-day and 200-day averages. Weak: 40% or fewer above both. Industries with fewer than 3 stocks get no label. TradingView, end of day.": "قوي: 60% على الأقل من أسهم النشاط أعلى من متوسطي 50 و200 يوم. ضعيف: 40% أو أقل. الأنشطة التي بها أقل من 3 أسهم بلا تصنيف. المصدر TradingView، نهاية اليوم.",
  "MACD 12 / 26 / 9": "ماكد MACD 12 / 26 / 9", "line, signal and histogram": "الخط والإشارة والأعمدة",
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
  "Hold. In a sideways market the course says reduce or step out.": "احتفظ. في السوق العرضي تنصح الدورة بالتخفيف أو الخروج.",
  "Stay out.": "ابقَ خارج السهم.", "Get ready to sell: tighten your stop.": "استعد للبيع: قرّب وقف الخسارة.",
  "Sell part of the position (reduce).": "بِع جزءًا من الكمية (تخفيف).", "Sell.": "بِع.",

  // analyze page
  "Analyse an EGX stock with your course method": "حلّل سهمًا في البورصة المصرية بمنهج دورتك",
  "Type a 4-letter code, or pick one below. You get the signal, the actions for your position, the chart and the 12-step checklist.": "اكتب رمز السهم أو اختر من الأسماء أدناه. ستحصل على الإشارة، وما يجب فعله، والرسم البياني، وقائمة الخطوات الاثنتي عشرة.",
  "Volume": "حجم التداول", "Support": "الدعم", "Resistance": "المقاومة", "vs 20-day average": "مقارنة بمتوسط 20 يومًا",
  "none below": "لا يوجد دعم أدنى", "none above": "لا توجد مقاومة أعلى",
  "Combined view: company + chart": "الرؤية المجمّعة: الشركة + الرسم البياني",
  "Key figures": "أهم الأرقام", "Chart": "الرسم البياني", "Daily": "يومي", "Weekly": "أسبوعي",
  "Support / resistance": "الدعم / المقاومة", "Swing points": "القمم والقيعان",
  "Company rating": "تقييم الشركة", "12-step checklist": "قائمة الخطوات الاثنتي عشرة", "MACD (12 / 26 / 9)": "مؤشر MACD (12 / 26 / 9)", "Each step lands on one rung of the ladder": "كل خطوة تقع على درجة من سلّم الإشارات",
  "What would change the signal": "ما الذي يغيّر الإشارة", "Upward": "صعودًا", "Downward": "هبوطًا",
  "Already fully bullish": "الإشارة صاعدة بالكامل", "Already fully bearish": "الإشارة هابطة بالكامل",
  "Trade plan": "خطة الصفقة", "Cash (EGP)": "السيولة (جنيه)", "Max risk per trade (%)": "أقصى مخاطرة للصفقة (%)",
  "Entry (last close)": "الدخول (آخر إغلاق)", "Stop (below support)": "وقف الخسارة (تحت الدعم)", "Risk per share": "المخاطرة للسهم", "Risk per gram": "المخاطرة للجرام",
  "Target (2R)": "الهدف (ضعف المخاطرة)", "First resistance": "أول مقاومة", "Shares": "عدد الأسهم", "Grams": "عدد الجرامات", "Cost": "التكلفة", "Loss if stopped": "الخسارة عند الوقف",
  "The signal isn't a First or Confirm Buy: treat this as a plan to have ready, not a trade for today.": "الإشارة ليست شراء أوليًا ولا تأكيد شراء: اعتبر هذه خطة جاهزة، لا صفقة لليوم.",
  "Learning and decision-support tool applying the Beedo technical-analysis course. Not investment advice. Free data can be delayed: check the live price and the day's EGX disclosures before trading.": "أداة للتعلّم ودعم القرار تطبّق دورة Beedo للتحليل الفني. ليست نصيحة استثمارية. البيانات المجانية قد تكون متأخرة: راجع السعر اللحظي وإفصاحات البورصة قبل التداول.",
  "Standard rules on the last 12 months of reported results (TradingView). Each figure is compared with similar companies. Not part of the Beedo technical course.": "قواعد قياسية على نتائج آخر 12 شهرًا (TradingView). كل رقم يُقارن بالشركات المشابهة. ليست جزءًا من دورة Beedo الفنية.",

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
  "What you own, what it is worth at the last close, and what the course says a shareholder should do.": "ما تملكه، وقيمته عند آخر إغلاق، وما تنصح به الدورة حامل السهم.",
  "Average buy price (EGP)": "متوسط سعر الشراء (جنيه)", "Add holding": "إضافة", "at the last close": "عند آخر إغلاق", "Loading prices…": "جارٍ تحميل الأسعار…",
  "Add what you own above. Use GOLD or SILVER with a quantity in grams for metals.": "أضف ما تملكه أعلاه. للمعادن استخدم GOLD أو SILVER مع الكمية بالجرام.",
  "Your holdings are saved only on this computer. Values use the last daily close, which can be delayed. Not investment advice.": "بياناتك محفوظة على هذا الجهاز فقط. القيم محسوبة على آخر إغلاق يومي وقد يكون متأخرًا. ليست نصيحة استثمارية.",
  "Enter the quantity and the price you paid": "أدخل الكمية وسعر الشراء",

  // time machine
  "Time machine": "آلة الزمن", "Run time machine": "تشغيل آلة الزمن", "Target first": "الهدف أولًا", "Stop first": "الإيقاف أولًا", "Neither": "لا هذا ولا ذاك", "Average R": "متوسط R",
  "Time machine failed": "تعذّر تشغيل آلة الزمن",
  "How often would the trade plan above reach its target before its stop? It replays the next 20 trading days 10,000 times from this stock's own daily moves of the past two years, and checks the same plan on past days that had the same signal. A simulation, not a prediction.": "كم مرة تصل خطة التداول أعلاه إلى الهدف قبل وقف الخسارة؟ تعيد آلة الزمن تشغيل أيام التداول العشرين القادمة 10,000 مرة من حركات السهم اليومية خلال العامين الماضيين، وتختبر نفس الخطة في الأيام السابقة التي ظهرت فيها نفس الإشارة. هذه محاكاة وليست توقعًا.",
  // back-test
  "Back-test": "اختبار على الماضي", "Run back-test": "تشغيل الاختبار", "Running…": "جارٍ التشغيل…",
  "Replays the checklist day by day over the past two years. It buys at the close on a First or Confirm Buy and sells at the close on a First or Confirm Sell. Fees and taxes are not counted. Past results do not predict future results.": "يعيد تطبيق قائمة الخطوات يومًا بيوم على العامين الماضيين: يشتري عند الإغلاق مع إشارة شراء أولي أو تأكيد شراء، ويبيع عند الإغلاق مع إشارة بيع أولي أو تأكيد بيع. لا تُحسب العمولات والضرائب. نتائج الماضي لا تتنبأ بالمستقبل.",
  "Course method": "منهج الدورة", "following the signals": "باتباع الإشارات", "Buy and hold": "الشراء والاحتفاظ", "bought on the first day": "شراء من أول يوم",
  "Trades": "الصفقات", "Winners": "الرابحة", "trades in profit": "صفقات رابحة", "Bought": "تاريخ الشراء", "Sold": "تاريخ البيع", "Price": "السعر", "Result": "النتيجة", "Still open": "ما زالت مفتوحة",
  "The method gave no First or Confirm Buy in this period, so it stayed in cash.": "لم يعطِ المنهج إشارة شراء أولي أو تأكيد شراء في هذه الفترة، فبقي في السيولة.",

  // gold & silver
  "International prices in Egyptian pounds, with your course method applied to each metal.": "الأسعار العالمية بالجنيه المصري، مع تطبيق منهج دورتك على كل معدن.",
  "Gold": "الذهب", "Silver": "الفضة", "Market": "السوق", "24k, per gram": "عيار 24، للجرام", "999, per gram": "999، للجرام", "Per ounce": "للأوقية",
  "Change today (USD)": "تغيّر اليوم (دولار)", "1 year (USD)": "سنة (دولار)", "52-week range (USD/oz)": "نطاق 52 أسبوعًا (دولار/أوقية)",
  "US dollar, official rate": "الدولار الأمريكي، السعر الرسمي", "Gold / silver ratio": "نسبة الذهب إلى الفضة",
  "Analyze with my course method": "حلّل بمنهج دورتي", "Add to watchlist": "أضف إلى قائمة المتابعة",
  "How many ounces of silver one ounce of gold buys. Above about 80, silver is cheap compared with gold; below about 50, gold is.": "عدد أوقيات الفضة التي تشتريها أوقية ذهب واحدة. فوق 80 تقريبًا تكون الفضة رخيصة مقارنة بالذهب، وتحت 50 تقريبًا يكون الذهب هو الأرخص.",

  // screener
  "Find strong companies that your course method says are in a buy zone, across the whole Egyptian Exchange.": "ابحث في كل البورصة المصرية عن شركات قوية يقول منهج دورتك إنها في منطقة شراء.",
  "Company quality": "جودة الشركة", "Strong only": "القوية فقط", "Strong or Fair": "القوية أو المتوسطة", "Technical signal": "الإشارة الفنية",
  "First or Confirm Buy": "شراء أولي أو تأكيد شراء", "Any buy, including Alarm Buy": "أي شراء، ومنه تنبيه الشراء", "Any signal": "أي إشارة",
  "Sector": "القطاع", "All sectors": "كل القطاعات", "Run screener": "تشغيل الفرز", "Screening…": "جارٍ الفرز…",
  "Choose your filters and press \"Run screener\". It takes about 20 to 40 seconds.": "اختر الشروط واضغط «تشغيل الفرز». يستغرق من 20 إلى 40 ثانية تقريبًا.",

  // about
  "About Beedo-Trade": "عن Beedo-Trade", "The signal ladder": "سلّم الإشارات", "Where the numbers come from": "مصدر الأرقام", "Important": "تنبيه مهم",
  "Beedo-Trade applies the Beedo technical-analysis course to Egyptian Exchange stocks, the same way every time: 12 steps (the 11 course steps plus MACD), one signal, and separate advice for a cash holder and a shareholder.": "يطبّق Beedo-Trade دورة Beedo للتحليل الفني على أسهم البورصة المصرية بالطريقة نفسها في كل مرة: 12 خطوة (خطوات الدورة الإحدى عشرة ومؤشر MACD)، إشارة واحدة، ونصيحة منفصلة لصاحب السيولة ولحامل السهم.",
  "Alarm = early warning, get ready. First = start a position (or start reducing). Confirm = several signals agree, act fully. Trend and moving averages set the ceiling: candles and RSI alone can't confirm a move against them, and in a sideways market the cash holder waits for a breakout.": "التنبيه = إنذار مبكر، استعد. الأولي = ابدأ الشراء (أو ابدأ التخفيف). التأكيد = عدة إشارات متفقة، نفّذ بالكامل. الاتجاه والمتوسطات المتحركة يحددان السقف: الشموع ومؤشر RSI وحدهما لا يؤكدان حركة عكسهما، وفي السوق العرضي ينتظر صاحب السيولة الاختراق.",
  "This is a learning and decision-support tool. It is": "هذه أداة للتعلّم ودعم القرار. وهي", "not investment advice": "ليست نصيحة استثمارية",
  ", it does not know your full financial situation, and it never places orders. Free data can be delayed: always check the live price and the day's disclosures before trading.": "، ولا تعرف وضعك المالي الكامل، ولا تنفّذ أي أوامر. البيانات المجانية قد تكون متأخرة: راجع دائمًا السعر اللحظي وإفصاحات اليوم قبل التداول.",
};
// Sentences assembled from parts
const AR_RULES = [
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
  [/^Steps not counted: (.+)$/, (m) => `خطوات غير محسوبة: ${m[1]}`],
  [/^Signal unchanged: (.+)$/, (m) => `الإشارة لم تتغير: ${AR[m[1]] || m[1]}`],
  [/^Signal: (.+) → (.+)$/, (m) => `الإشارة: ${AR[m[1]] || m[1]} ← ${AR[m[2]] || m[2]}`],
  [/^(Untick|Tick) → (.+)$/, (m) => `${m[1] === "Untick" ? "إلغاء" : "تحديد"} ← ${AR[m[2]] || m[2]}`],
  [/^Count step (\d+) in the signal$/, (m) => `احسب الخطوة ${m[1]} في الإشارة`],
  [/^Moving averages (.+) saved$/, (m) => `تم حفظ المتوسطات المتحركة ${m[1]}`],
  [/^Market: (Healthy|Mixed|Weak)$/, (m) => `السوق: ${{ Healthy: "قوي", Mixed: "متذبذب", Weak: "ضعيف" }[m[1]]}`],
  [/^(above|below) its 50-day average, (above|below) its 200-day$/, (m) => `${m[1] === "above" ? "أعلى" : "أدنى"} من متوسط 50 يومًا، و${m[2] === "above" ? "أعلى" : "أدنى"} من متوسط 200 يوم`],
  [/^(\d+)% of (\d+) stocks above their 50-day average \((\d+)% above 200-day\)$/, (m) => `${m[1]}% من ${m[2]} سهمًا أعلى من متوسط 50 يومًا (${m[3]}% أعلى من متوسط 200 يوم)`],
  [/^(\d+) up · (\d+) down today$/, (m) => `${m[1]} صاعد · ${m[2]} هابط اليوم`],
  // time machine
  [/^within (\d+) trading days$/, (m) => `خلال ${m[1]} يوم تداول`], [/^(\S+)R plan$/, (m) => `خطة ${m[1]}R`],
  [/^(Close to a coin flip|Close to break-even|Leans toward the target|Leans toward the stop|Strongly toward the target|Strongly toward the stop): the target came first in (\d+)% of the replays that reached one side; a (\S+)R plan needs (\d+)% to break even\.?$/,
    (m) => `${{ "Close to a coin flip": "قريب من رمي العملة", "Close to break-even": "قريب من التعادل", "Leans toward the target": "يميل نحو الهدف", "Leans toward the stop": "يميل نحو الإيقاف", "Strongly toward the target": "يميل بقوة نحو الهدف", "Strongly toward the stop": "يميل بقوة نحو الإيقاف" }[m[1]]}: وصل السعر إلى الهدف أولًا في ${m[2]}% من عمليات المحاكاة التي بلغت أحد الجانبين، وخطة ${m[3]}R تحتاج ${m[4]}% لتتعادل.`],
  [/^Same signal \((.+)\) on (\d+) past days: target first (\d+), stop first (\d+), neither (\d+)\.?$/, (m) => `نفس الإشارة (${AR[m[1]] || m[1]}) في ${m[2]} يومًا سابقًا: الهدف أولًا ${m[3]}، الإيقاف أولًا ${m[4]}، لا هذا ولا ذاك ${m[5]}.`],
  [/^The same signal \((.+)\) appeared on only (\d+) past days: too few to judge\.?$/, (m) => `ظهرت نفس الإشارة (${AR[m[1]] || m[1]}) في ${m[2]} يومًا سابقًا فقط: عدد قليل لا يكفي للحكم.`],
  [/^Price after (\d+) trading days: median (\S+) EGP, 90% of replays between (\S+) and (\S+?)\.?$/, (m) => `السعر بعد ${m[1]} يوم تداول: الوسيط ${m[2]} جنيه، و90% من عمليات المحاكاة بين ${m[3]} و${m[4]}.`],
];
function tr(text) {
  const k = text.trim();
  if (!k) return null;
  const bare = k.replace(/\.$/, "");
  const hit = AR[k] || AR[bare] || AR[bare[0].toLowerCase() + bare.slice(1)];
  if (hit) return hit;
  for (const [re, fn] of AR_RULES) { const m = k.match(re); if (m) return fn(m); }
  return null;
}
function trNode(n) {
  if (n.nodeType === 3) {
    const v = tr(n.nodeValue);
    if (v) n.nodeValue = n.nodeValue.replace(n.nodeValue.trim(), v);
  } else if (n.nodeType === 1 && !["SCRIPT", "STYLE", "CANVAS"].includes(n.tagName)) {
    for (const a of ["placeholder", "title", "aria-label"]) { const v = n.hasAttribute(a) && tr(n.getAttribute(a)); if (v) n.setAttribute(a, v); }
    n.childNodes.forEach(trNode);
  }
}
function startArabic() {
  document.documentElement.lang = "ar"; document.documentElement.dir = "rtl";
  trNode(document.body);
  // Translated text has no entry of its own, so the observer settles after one pass
  new MutationObserver((ms) => ms.forEach((m) => (m.type === "characterData" ? trNode(m.target) : m.addedNodes.forEach(trNode))))
    .observe(document.body, { childList: true, subtree: true, characterData: true });
}

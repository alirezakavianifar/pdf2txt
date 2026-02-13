# Template Extraction Fields Summary

This document summarizes the fields that need to be extracted from each PDF template (Templates 1-8), based on the implementation logic.

## Template 1

### Power Section
- **`contractual`**: قراردادی (e.g., 2500)
- **`calculated`**: محاسبه شده (e.g., 2250.00)
- **`consumed`**: مصرفی (e.g., 170.00)
- **`maximator`**: ماکسیمتر (e.g., 170.0000)
- **`overage`**: میزان تجاوز از قدرت
- **`permitted`**: مجاز
- **`reduced`**: کاهش یافته
- **`temp_reduction_end`**: تاریخ اتمام کاهش موقت

### Period Section
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`days`**: تعداد روز دوره

### Consumption History
- Columns: `تاریخ قرائت`, `میان باری`, `اوج باری`, `کم باری`, `اوج بار جمعه`, `راکتیو`, `دیماند`, `مبلغ`

### License Expiry
- **`license_expiry_date`**: تاریخ انقضا پروانه

### Energy Supported / Complete Section
*   **Consumption Rows (`شرح مصارف`)**:
    - **`description`**: شرح مصارف
    - **`tou`**: TOU
    - **`previous_meter`**: شماره کنتور قبلی
    - **`current_meter`**: شماره کنتور کنونی
    - **`coefficient`**: ضریب
    - **`total_consumption`**: مصرف کل
    - **`supplied_energy`**: بهای انرژی پشتیبانی شده (انرژی مشمول, نرخ, مبلغ)
*   **Regulation Differences (`مابه التفاوت اجرای مقررات`)**:
    - **`description`**: شرح مصارف
    - **`included_energy`**: انرژی مشمول
    - **`base_rate`**: نرخ پایه
    - **`avg_market_rate`**: متوسط نرخ بازار
    - **`rate_difference`**: تفاوت نرخ
    - **`amount`**: مبلغ (ریال)
*   **Totals (`جمع`)**:
    - **`total_consumption`**: مصرف کل
    - **`total_amount`**: مبلغ (ریال)

### Bill Summary
- **`energy_price`**: بهای انرژی
- **`loss`**: ضررو زیان
- **`subscription`**: آبونمان
- **`electricity_tax`**: عوارض برق
- **`vat`**: مالیات بر ارزش افزوده
- **`fuel_cost`**: هزینه سوخت نیروگاهی
- **`regulation_diff`**: مابه التفاوت اجرای مقررات
- **`period_total`**: جمع دوره
- **`debit`**: بدهکاری
- **`thousand_deduction`**: کسر هزار ریال
- **`installment`**: قسط
- **`late_fee_adjustment`**: تعدیل دیرکرد بهای برق

### Transit Section
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`days`**: تعداد روز دوره
- **`period_year`**: دوره/سال
- **`loss_coefficient`**: ضریب زیان
- **`transit_power`**: قدرت مشمول ترانزیت
- **`monthly_transit_rate`**: نرخ ماهیانه ترانزیت
- **`transit_amount`**: ترانزیت
- **`vat`**: مالیات بر ارزش افزوده
- **`period_total`**: جمع دوره
- **`debit`**: بدهکاری
- **`thousand_deduction`**: کسر هزار ریال

### Bill Identifier
- **`bill_id`**: شناسه قبض
- **`payment_id`**: شناسه پرداخت

---

## Template 2

### Power - Kilowatt
- **`contractual`**: قراردادی
- **`calculated`**: محاسبه شده
- **`permitted`**: مجاز
- **`reduced`**: کاهش یافته
- **`consumed`**: مصرفی
- **`overage`**: میزان تجاوز از قدرت
- **`maximometer`**: عدد ماکسیمتر
- **`temp_reduction_end`**: تاریخ اتمام کاهش موقت

### Power Purchased From Rate
*Rows: `mid_load`, `low_load`, `peak_load`*
- **`bilateral_power`**: قدرت خریداری شده از - دوجانبه
- **`exchange_power`**: قدرت خریداری شده از - بورس
- **`green_board_power`**: قدرت خریداری شده از - تابلو سبز
- **`renewable_rate`**: نرخ - تجدیدپذیر
- **`market_avg_rate`**: نرخ - متوسط بازار
- **`max_green_board_rate`**: نرخ - حداکثر تابلو سبز
- **`max_wholesale_rate`**: نرخ - حداکثر عمده فروشی
- **`tou_hours`**: ساعت TOU

### Energy Supported
*Rows: `mid_load`, `peak_load`, `low_load`, `reactive`, `high_consumption`*
- **`total_consumption`**: مصرف کل
- **`article_16_production_leap`**: ماده 16 جهش تولید (انرژی, خرید از تابلو سبز)
- **`green_production`**: تولید سبز (مشمول, غیرمشمول)
- **`bilateral_exchange_consumption`**: مصرف بورس دوجانبه
- **`regulation_4d`**: مشمول ما به التفاوت اجرا مقررات 4-د (مصرف, نرخ, مبلغ)
- **`regulation_4a`**: مشمول ما به التفاوت اجرا مقررات 4-الف (مصرف, نرخ, مبلغ)
- **`grid_owner_supplied`**: تامین شده توسط مالک شبکه (مصرف, نرخ, مبلغ)

### Bill Summary
- **`energy_price`**: بهای انرژی
- **`loss`**: ضررو زیان
- **`subscription`**: مبلغ آبونمان
- **`fuel_cost`**: هزینه سوخت نیروگاهی
- **`vat`**: مالیات بر ارزش افزوده
- **`electricity_tax`**: عوارض برق
- **`power_overage`**: تجاوز از قدرت
- **`regulation_diff`**: مابه التفاوت اجرای مقررات
- **`article_16_diff`**: مابه التفاوت ماده 16 جهش تولید
- **`off_market_credit`**: بستانکاری خرید خارج بازار

### Consumption History
- Columns: `دوره - سال`, `تاریخ قرائت`, `میان باری`, `اوج باری`, `کم باری`, `اوج بار جمعه`, `راکتیو`, `صورتحساب`, `مبلغ دوره - ریال`, `مهلت پرداخت`, `مبلغ پرداختی - ریال`, `تاریخ پرداخت`

### Shared with Template 1
- **Period Section**: `from_date`, `to_date`, `days`
- **License Expiry**: `date`
- **Bill Identifier**: `bill_id`, `payment_id`

---

## Template 3

### Bill Identifier Section
- **`bill_identifier`**: شناسه قبض (e.g., `7030899411120`)

### License Expiry Section
- **`license_expiry_date`**: تاریخ انقضا پروانه (e.g., `1499/12/29`)

### Energy Consumption Table
*Rows: Mid-load (میان باری), Peak (اوج بار), Low-load (کم باری), Friday Peak (اوج بار جمعه)*
- **`description`**: شرح مصارف
- **`counters`**: شمارنده قبلی/کنونی
- **`coefficient`**: ضریب
- **`total_consumption`**: مصرف کل
- **`production_leap_law`**: مصرف مشمول/غیرمشمول قانون جهش تولید
- **`purchased_energy`**: انرژی خریداری شده
- **`energy_cost`**: بهای انرژی

### Power Section
- **`contractual`**: قراردادی
- **`maximator`**: ماکسیمتر
- **`permitted`**: مجاز
- **`calculated`**: محاسبه شده
- **`consumed`**: مصرفی
- **`reduced`**: کاهش یافته

### Period Section
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`days`**: تعداد روز دوره
- **`period_year`**: دوره/سال

### Reactive Consumption
- **`consumption`**: مصرف راکتیو

### Bill Summary
- **`supplied_energy_cost`**: بهای انرژی تامین شده (19,549,842)
- **`subscription`**: آبونمان (129,769)
- **`free_tariff_diff`**: تفاوت تعرفه انشعاب آزاد
- **`power_overage`**: تجاوز از قدرت
- **`fuel_cost`**: هزینه سوخت نیروگاهی
- **`electricity_tax`**: عوارض برق
- **`article_16_diff`**: مابه التفاوت ماده 16 و ماده 3
- **`period_amount`**: مبلغ دوره
- **`vat`**: مالیات بر ارزش افزوده
- **`debit_credit`**: بدهکاری/بستانکاری
- **`thousand_rial_deduction`**: کسر هزار ریال

### Rate Difference Table
*Columns include:*
- Exempt/Included Consumption
- Purchase from Plant
- Green Board Purchase
- Production
- Calculable Consumption
- Rate
- Amount

### Transit Section
- **`commission`**: حق العمل
- **`transit`**: ترانزیت
- **`tariff_correction`**: اصلاح تعرفه دیرکرد
- **`transit_vat`**: مالیات بر ارزش افزوده ترانزیت
- **`period_electricity_cost`**: بهای برق دوره
- **`debit_credit`**: بدهکاری/بستانکاری
- **`thousand_rial_deduction`**: کسر هزار ریال

---

## Template 4

### Power Section
- **`contractual`**: قراردادی
- **`permitted`**: پروانه مجاز
- **`consumed`**: مصرفی
- **`calculated`**: محاسبه شده
- **`reduced`**: کاهش یافته
- **`overage`**: تجاوز از قدرت

### Transformer Coefficient
- **`value`**: ضریب ترانس (e.g., 8000)

### License Expiry
- **`date`**: تاریخ انقضای پروانه

### Consumption Table
*Rows: Mid-load, Peak, Low-load, Friday Peak*
- **`exchange_purchase`**: خرید از بورس
- **`total_consumption`**: مصرف کل
- **`counters`**: شمارنده کنونی/قبلی

### Financial/Energy Cost Table
- **`supplied_consumption`**: مصرف تامین شده
- **`article_16_subject`**: مشمول ماده 16
- **`difference_subject`**: مشمول مابه التفاوت

### Standard Sections
- **`bill_identifier`**: شناسه قبض
- **`period_info`**: From/To dates

---

## Template 5

### Company Info
- **`company_name`**: نام شرکت
- **`national_id`**: شناسه ملی
- **`city_region`**: شهر ناحیه
- **`address`**: آدرس
- **`incident_unit`**: واحد حوادث
- **`parcel_code`**: پارچگویچ صورتحساب

### License Expiry
- **`date`**: تاریخ انقضای پروانه

### Energy Consumption Table
*Rows: Mid-load, Peak, Low-load, Friday Peak*
*Columns include:*
- **`counters`**: شمارنده قبلی/کنونی
- **`digit`**: رقم
- **`coefficient`**: ضریب
- **`consumption`**: مصرف
- **`renewable_included`**: مشمول تجدید پذیر
- **`renewable_purchase`**: خرید تجدید پذیر
- **`renewable_production`**: تولید تجدید پذیر
- **`exchange_bilateral_purchase`**: خرید بورس و دو جانبه
- **`proxy_supply`**: مصرف تامین شده به نیابت (Consumption, Rate)
- **`energy_price`**: بهای انرژی

### Power Section
- **`contractual`**: قراردادی
- **`calculated`**: محاسبه شده
- **`authorized`**: پروانه مجاز
- **`reduced`**: کاهش یافته
- **`overage`**: میزان تجاوز از قدرت
- **`consumed`**: مصرفی

### Period Section
- **`period_year`**: دوره/سال
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`duration`**: به مدت

### Reactive Consumption
- **`consumption`**: مصرف راکتیو
- **`amount`**: مبلغ راکتیو

### Bill Summary
- **`supplied_energy_cost`**: بهای انرژی تامین شده
- **`purchase_credit`**: بستانکاری خرید
- **`regulation_diff`**: ما بالتفاوت اجرای مقررات
- **`subscription`**: آبونمان
- **`fuel_cost`**: هزینه سوخت نیروگاهی
- **`adjustment`**: تعدیل بهای برق
- **`electricity_tax`**: عوارض برق
- **`vat`**: مالیات بر ارزش افزوده

### Rate Difference Table
- **`consumption`**
- **`amount`**
- **`free_exchange_purchase`**

### Transit Section
- **`price`**: بهای ترانزیت

### Consumption History
- Columns: Period/Year, Read Date, Consumption (Active/Reactive), Amount, Payment Deadline, Paid Amount, Payment Date

---

## Template 6

### Company Info
- Name, National ID, Economic Code, Subscription Code, Address, Region, Unit Code
- Meter Body Number, Meter Coefficient
- Codes: Voltage, Activity, Tariff, Option, Computer

### License Expiry
- **`date`**: تاریخ انقضای پروانه

### Energy Consumption Table
*Rows: Mid, Peak, Low, Friday, Reactive*
*Columns include:*
- **`counters`**: شمارنده قبلی/فعلی
- **`digits`**: تعداد ارقام
- **`coefficient`**: ضریب کنتور
- **`read_energy`**: انرژی قرائت شده
- **`bilateral_exchange`**: انرژی خریداری شده دوجانبه و بورس
- **`excess_market`**: انرژی مازاد خرید از بازار
- **`green_bilateral`**: انرژی خریداری شده دو جانبه سبز
- **`production_leap`**: مصرف قانون جهش تولید
- **`distribution_supply`**: تامین شده توسط توزیع (Energy & Cost)
- **`tariffs`**: انرژی مشمول تعرفه (4-A, 4-D)

### Power Section
- **`contractual`**: قراردادی
- **`permitted`**: قدرت مجاز
- **`read`**: قدرت قرائت
- **`exceeded`**: قدرت فراتش/تجاوز از قدرت
- **`calculated`**: محاسبه شده

### Period Section
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`days`**: تعداد روز
- **`period_year`**: دوره/سال
- **`invoice_date`**: تاریخ صورتحساب

### Bill Summary
- **`energy_price`**: بهای انرژی
- **`power_price`**: بهای قدرت
- **`implementation_diff`**: مابه التفاوت اجرای
- **`subscription`**: آبونمان
- **`branch_tariff_diff`**: تفاوت تعرفه انشعاب
- **`power_overage`**: تجاوز از قدرت
- **`peak_season`**: پیک فصل
- **`reactive_price`**: بهای انرژی راکتیو
- **`license_expiry`**: انقضای پروانه
- **`note_14`**: مبلغ تبصره ی 14
- **`article_16_diff`**: مابه التفاوت انرژی مشمول ماده 16
- **`bonus`**: پاداش همکاری
- **`off_market_credit`**: بستانکاری خرید خارج بازار
- **`adjustment`**: تعدیل بهای برق
- **`insurance`**: بیمه / بیمه عمومی
- **`electricity_charges`**: عوارض برق
- **`vat`**: مالیات بر ارزش افزوده
- **`penalty`**: وجه التزام
- **`period_price`**: بهای برق دوره
- **`debt_credit`**: بدهکاری / بستانکاری
- **`thousand_deduction`**: کسر هزار ریال
- **`payable`**: مبلغ قابل پرداخت

### Transit Section
- **`transit_cost`**: هزینه ترانزیت
- **`super_distribution`**: ترانزیت فوق توزیع
- **`commission`**: حق العمل کاری
- **`adjustment`**: تعدیل بهای برق
- **`vat`**: مالیات بر ارزش افزوده
- **`past_debt`**: بدهی گذشته
- **`penalty`**: وجه التزام

### Consumption History
- Period, Date, Active Consumption, Reactive Consumption, Period Amount, Paid Amount, Payment Date

---

## Template 7

### Bill Identifier & License Expiry
- Standard fields

### Company & Customer Info
- Company Name, City, Address, Region, Phone, Unit Code
- Customer Name, Consumption Address, Postal Code, Economic Code, National ID
- Payment ID, Identification, File No, Subscription No, Install Date
- Tariff Code, Activity Code/Type, Option, Computer Code, Voltage

### Energy Consumption Table
*Rows: Mid, Peak, Low, Friday Peak, Reactive*
*Columns include:*
- **`meter_consumption`**: مصرف کنتور
- **`green_regulations`**: آیین نامه سبز (%, Purchase, Rate, Amount)
- **`bilateral_exchange`**: خرید دو جانبه - بورس
- **`proxy_supply`**: مصرف تامین شده به نیابت (Consumption, Amount)
- **`excess_purchase_credit`**: بستانکاری مازاد خرید انرژی
- **`subject_to_diff`**: مشمول مابه التفاوت (Consumption, Amount)
- **`energy_price`**: بهای انرژی

### Power Section
- **`contractual`**: قراردادی
- **`permitted`**: مجاز
- **`consumed`**: مصرفی
- **`maximator`**: ماکسیمتر
- **`calculated`**: محاسبه شده
- **`reduced`**: کاهش یافته
- **`overage`**: میزان تجاوز از قدرت
- **`temp_reduction_end`**: تاریخ اتمام کاهش موقت
- **Meter Specs**: Active/Reactive Body No, Coefficient, Power Factor

### Period Section
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`duration`**: به مدت
- **`issue_date`**: تاریخ صدور صورتحساب
- **`total_consumption`**: کل مصرف

### Bill Summary
- **`subscription`**: آبونمان
- **`fuel_cost`**: هزینه سوخت نیروگاهی
- **`reactive_price`**: بهای انرژی راکتیو
- **`seasonal_price`**: بهای فصل
- **`regulation_diff`**: ما به التفاوت اجرای مقررات
- **`proxy_supply_price`**: بهای برق تامین شده به نیابت
- **`excess_purchase_credit`**: بستانکاری مازاد خرید انرژی
- **`article_16_green_diff`**: مبلغ مابه التفاوت ماده 16 (سبز)
- **`tariffs`**: عوارض برق
- **`vat`**: مالیات بر ارزش افزوده
- **`article_3_debt`**: مبلغ بدهی ماده 3
- **`debt_credit`**: بدهکار / بستانکار
- **`thousand_deduction`**: کسر هزار ریال
- **`payable`**: مبلغ قابل پرداخت
- **`deadline`**: مهلت پرداخت
- **`disconnection`**: مشمول قطع

### Consumption History
- Period/Year, Reading Date, Loads (Mid, Peak, Low, Friday, Reactive), Period Amount, Deadline

### Transit Section
- **`distribution_transit`**: ترانزیت توزیع (Amount & Rate)
- **`regional_transit`**: ترانزیت برق منطقه ای (Amount & Rate)
- **`vat`**: مالیات بر ارزش افزوده
- **`debt_credit`**: بدهکار / بستانکار
- **`thousand_deduction`**: کسر هزار ریال

---

## Template 8

### Bill Identifier & License Expiry
- Standard extraction

### Energy Consumption Table
*Complex table with multiple subsections:*
- **Read Energy**: Counters, Total, Amount
- **Green & Normal Purchase**: Exchange (بورس), Bilateral (دو جانبه)
- **Rates**: Max Market Rate, Bilateral Board Rate, Tariff Rate
- **Article 5 & 16**: Rates, Amounts, Included Energy
- **Other**: Amount, Rate, Included Reactive/Duties

### Power Section
- **`contractual`**: قراردادی
- **`calculated`**: محاسبه شده
- **`permitted`**: مجاز
- **`reduced`**: کاهش یافته
- **`consumed`**: مصرفی
- **`overage`**: میزان تجاوز از قدرت

### Period Section
- **`from_date`**: از تاریخ
- **`to_date`**: تا تاریخ
- **`days`**: تعداد روز دوره
- **`period_year`**: دوره/سال

### Consumption History
- Period, Reading Date, Load Types (Mid, Peak, Low, Friday, Reactive), Period Amount

### Bill Summary
- **`consumption_amount`**: مبلغ مصرف
- **`power_price`**: بهای قدرت
- **`power_excess`**: تجاوز از قدرت
- **`license_expiry_diff`**: تفاوت انقضای اعتبار پروانه
- **`subscription`**: بهای آبونمان
- **`fuel_cost`**: هزینه سوخت نیروگاهی
- **`supplied_energy_cost`**: بهای انرژی تامین شده
- **`article_16_cost`**: بهای انرژی ماده ۱۶
- **`regulation_diff`**: مابه التفاوت اجرای مقررات
- **`off_market_credit`**: بستانکاری، خرید خارج بازار
- **`renewable_diff`**: مابه التفاوت تأمین از تجدیدپذیر
- **`period_electricity_cost`**: بهای برق دوره
- **`taxes_and_duties`**: مالیات و عوارض
- **`electricity_duties`**: عوارض برق
- **`credit`**: بستانکاری
- **`thousand_deduction`**: کسر هزار ریال

### Transit Section
- **`transit_price`**: بهای ترانزیت / بهای ترانزیت برق
- **`vat`**: مالیات بر ارزش افزوده
- **`debit_credit`**: بدهکاری / بستانکاری
- **`thousand_deduction`**: کسر هزار ریال
- **`payable`**: مبلغ قابل پرداخت

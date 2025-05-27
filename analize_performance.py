import pandas as pd
import io

# Цей file_content має бути точним вмістом вашого gg.json
file_content = """id	trader_id	period_days	pnl_value_sign	pnl_per_period	roi_value_sign	roi_per_period	mdd_per_period	win_rate_per_period	recorded_at
1	3779422221599733504	180	+	1067761.03175159	+	162.8634904	26.712446	61.9372	2025-05-25 16:29:20.381743
2	4436469782333433600	180	+	734590.96930492	-	68.025773	98.676712	70.8333	2025-05-25 16:29:20.381743
3	4368289204618097664	180	+	538331.22244111	-	42.393347	91.16449	45.2055	2025-05-25 16:29:20.381743
4	4509584189328215809	180	+	399128.95081816	+	51.957263	57.621486	56.5217	2025-05-25 16:29:20.381743
5	3779422221599733504	180	+	1067761.03175159	+	162.8634904	26.712446	61.9372	2025-05-25 16:53:33.840317
6	4257075712912167168	180	-	106642.91023405	-	99.99997252	99.999997	90.3226	2025-05-25 16:53:33.840317
7	4515869709557003264	180	-	106893.84691669	-	100.0	100.0	66.6667	2025-05-25 16:53:33.840317
8	4166142391437526529	180	-	132763.58661009	-	30.1604	100.0	90.1786	2025-05-25 16:53:33.840317
9	1234567890123456789	180	+	500000.00000000	+	80.000000	15.000000	75.0000	2025-05-25 16:53:33.840317
10	9876543210987654321	180	+	700000.00000000	+	120.000000	20.000000	80.0000	2025-05-25 16:53:33.840317
11	3779422221599733504	180	+	1100000.00000000	+	170.000000	25.000000	63.0000	2025-05-25 17:00:00.000000
"""
df = pd.read_csv('gg.json', sep='\t', index_col=False)

# Очищення пробілів у всіх строкових стовпцях, щоб уникнути проблем
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.strip()

# ***НОВИНКА: Перетворюємо trader_id на строковий тип, щоб уникнути втрати точності***
df['trader_id'] = df['trader_id'].astype(str)

# ТЕПЕР ПЕРЕТВОРЮЄМО ТИПИ ДАНИХ ПРАВИЛЬНО
df['pnl_per_period'] = pd.to_numeric(df['pnl_per_period'], errors='coerce')
df['roi_per_period'] = pd.to_numeric(df['roi_per_period'], errors='coerce')
df['mdd_per_period'] = pd.to_numeric(df['mdd_per_period'], errors='coerce')
df['win_rate_per_period'] = pd.to_numeric(df['win_rate_per_period'], errors='coerce')

# Забезпечуємо, що знакові стовпці є рядками для порівняння '+' / '-'
df['pnl_value_sign'] = df['pnl_value_sign'].astype(str).str.strip()
df['roi_value_sign'] = df['roi_value_sign'].astype(str).str.strip()


print("--- Діагностика DataFrame після ЗАВАНТАЖЕННЯ та очищення ---")
print("\nІнформація про DataFrame (df.info()):")
df.info() # Тепер trader_id має бути object (рядок)
print("\nПерші 5 рядків DataFrame (df.head()):")
print(df.head())
print("\nУнікальні значення в стовпці 'roi_value_sign':")
print(df['roi_value_sign'].unique())


# Створюємо стовпець 'roi_per_period_signed'
df['roi_per_period_signed'] = df.apply(
    lambda row: row['roi_per_period'] if row['roi_value_sign'] == '+' else -row['roi_per_period'],
    axis=1
)

print("\n--- Діагностика після створення 'roi_per_period_signed' ---")
print("\nПерші 5 рядків з ключовими стовпцями:")
print(df[['roi_per_period', 'roi_value_sign', 'roi_per_period_signed']].head())
print("\nМаксимальне значення 'roi_per_period_signed':", df['roi_per_period_signed'].max())
print("Мінімальне значення 'roi_per_period_signed':", df['roi_per_period_signed'].min())
print("Кількість позитивних значень в 'roi_per_period_signed':", (df['roi_per_period_signed'] > 0).sum())


# Фільтруємо для позитивного ROI
positive_roi_df = df[df['roi_per_period_signed'] > 0]
print(f"\nКількість рядків з позитивним ROI після фільтрації: {len(positive_roi_df)}")

# Агрегація та ранжування, лише якщо positive_roi_df не порожній
if not positive_roi_df.empty:
    aggregated_traders = positive_roi_df.groupby('trader_id').agg(
        avg_roi=('roi_per_period_signed', 'mean'),
        avg_mdd=('mdd_per_period', 'mean'),
        max_mdd=('mdd_per_period', 'max'),
        avg_win_rate=('win_rate_per_period', 'mean'),
        total_records=('id', 'count')
    ).reset_index()

    successful_traders_ranked = aggregated_traders.sort_values(
        by=['avg_roi', 'avg_mdd', 'avg_win_rate'],
        ascending=[False, True, False]
    )

    print("--- Топ-3 найуспішніших трейдерів за комбінованими критеріями (ROI, MDD, Win Rate) ---")
    print("Критерії: Вищий середній ROI, Нижчий середній MDD, Вищий середній Win Rate.")

    top_traders = successful_traders_ranked.head(3)

    if not top_traders.empty:
        for index, trader in top_traders.iterrows():
            # Тепер trader_id вже є рядком, тому просто виводимо його
            print(f"\nТрейдер ID: {trader['trader_id']}") # Зміна тут: прибрано int()
            print(f"  Середній ROI: {trader['avg_roi']:.2f}%")
            print(f"  Середній MDD: {trader['avg_mdd']:.2f}% (чим менше, тим краще)")
            print(f"  Середній Win Rate: {trader['avg_win_rate']:.2f}% (чим вище, тим краще)")
            print(f"  Кількість записів: {trader['total_records']}")
            print("---")
    else:
        print("Не знайдено трейдерів з позитивним ROI для аналізу після агрегації.")
else:
    print("Не знайдено трейдерів з позитивним ROI для аналізу (після початкової фільтрації).")

print("\n--- Пояснення вибору та комбінованого аналізу ---")
print("Успішність трейдера - це не лише максимальний прибуток, а й здатність управляти ризиками.")
print("Ми розглянули три ключові метрики:")
print("1.  **ROI (Return On Investment):** Показує ефективність інвестицій. Чим вище, тим краще.")
print("2.  **MDD (Maximum Drawdown):** Показує найбільше падіння капіталу від піку. Чим менше MDD, тим менший ризик трейдер приймає або краще ним управляє.")
print("3.  **Win Rate (Відсоток виграшних угод):** Показує частку успішних угод. Високий Win Rate свідчить про послідовність.")

print("\nДля визначення 'найуспішніших', ми зробили наступне:")
print("1.  **Нормалізували ROI:** Врахували знак `roi_value_sign` для отримання фактичного відсотка прибутку/збитку.")
print("2.  **Агрегували дані:** Оскільки один трейдер може мати кілька записів, ми усереднили їхні показники (ROI, MDD, Win Rate) для кожного `trader_id`. Це дає більш стабільну оцінку їхньої ефективності за весь доступний період.")
print("3.  **Відсортували за комбінованими критеріями:**")
print("    * Спочатку за середнім ROI (у спадному порядку - від найбільшого до найменшого).")
print("    * Потім за середнім MDD (у зростаючому порядку - від найменшого до найбільшого), оскільки нижчий MDD краще.")
print("    * Нарешті, за середнім Win Rate (у спадному порядку - від найбільшого до найменшого).")

print("Такий підхід дозволяє виділити трейдерів, які не тільки багато заробляють, але й роблять це відносно стабільно (низький MDD) та послідовно (високий Win Rate).")
print("Вибрані трейдери є прикладом збалансованої успішності.")
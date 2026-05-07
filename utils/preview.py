import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv(r'C:\Users\Анастасия\OneDrive\Desktop\[SW.BAND] 3 KC_case_data .csv')

column = df.columns.tolist() # Колонки
uniq = df['event'].unique() # Уникальные события
os = df['os_name'].unique() # 'android', 'ios'
utm_s = df['utm_source'].unique() # '-', 'vk_ads', 'referal', 'facebook_ads', 'google_ads', 'instagram_ads', 'yandex-direct'
uniq_id = len(df['device_id'].unique()) # 190884 уникальных id

# Временной промежуток, за который получены данные
date_min = df['date'].min() # 2020-01-01
date_max = df['date'].max() # 2020-03-31

# Выручка по каналам привлечения
# Самый менее прибыльный referal (8837044.5), проносит <9% выручки
# Больше всего выручки приходит из неизвестных каналов привлечения (21449749.5)
# Самый прибыльный из известных vk_ads (16389652.5), приносит >16% выручки
grouped_utm = df.groupby('utm_source')['purchase_sum'].agg(['sum', 'min', 'max', 'mean', 'count']) # Сортировка по всем каналам
total_sum  = df['purchase_sum'].sum()
referal_sum = df[df['utm_source'] == 'referal']['purchase_sum'].sum()
vk_sum = df[df['utm_source'] == 'vk_ads']['purchase_sum'].sum()
min_benefit = (referal_sum / total_sum) * 100 # 8.8%
max_benefit = (vk_sum / total_sum) * 100 # 16.3%

# Выручка по дням
grouped_date = df.groupby('date')['purchase_sum'].agg(['sum', 'min', 'max', 'mean', 'count']) # Сортировка по всем дням

# Количество покупок по полу
# Женщины делают на ~10к больше покупок, что приносит больше прибыли
grouped_gender = df.groupby('gender')['purchase_sum'].agg(['sum', 'min', 'max', 'mean', 'count'])

# Города по покупкам (в таблице только Мск. и СПб.)
# Москвичи делают на ~15к больше покупок, что приносит больше прибыли
grouped_city = df.groupby('city')['purchase_sum'].agg(['sum', 'min', 'max', 'mean', 'count'])

# Количество покупок по ОС
# Пользователи android делают на ~32к больше покупок, что приносит больше прибыли
grouped_os = df.groupby('os_name')['purchase_sum'].agg(['sum', 'min', 'max', 'mean', 'count'])

# Доля событий
# Между установкой приложения и покупкой отсеивается > 83к пользователей
grouped_uniq_event = df.groupby('event')['device_id'].nunique() # Кол-во уникальных id для каждого события

# Средний чек
avg_check = df[df['event'] == 'purchase']['purchase_sum'].mean() # 709.1

# Воронка конверсии
# Самый "узкий" показатель между запуском приложения и покупкой
conversion_install = (grouped_uniq_event['purchase'] / grouped_uniq_event['app_install']) * 100 # Конверсия 45%
conversion_start = (grouped_uniq_event['purchase'] / grouped_uniq_event['app_start']) * 100 # Конверсия 37%
conversion_register = (grouped_uniq_event['purchase'] / grouped_uniq_event['register']) * 100 # Конверсия 90%
conversion_search = (grouped_uniq_event['purchase'] / grouped_uniq_event['search']) * 100 # Конверсия 38%
conversion_choose = (grouped_uniq_event['purchase'] / grouped_uniq_event['choose_item']) * 100 # Конверсия 45%
conversion_tap = (grouped_uniq_event['purchase'] / grouped_uniq_event['tap_basket']) * 100 # Конверсия 56%


# Время между событиями
df['date'] = pd.to_datetime(df['date'])

ev = ['app_install', 'app_start', 'register', 'search', 'choose_item', 'tap_basket', 'purchase']
gaps = {}

for i in range(len(ev)-1):
    current = df[df['event'] == ev[i]][['device_id', 'date']].rename(columns={'date': 'current_date'})
    next_ = df[df['event'] == ev[i+1]][['device_id', 'date']].rename(columns={'date': 'next_date'})
    merged = current.merge(next_, on='device_id', how='inner')
    if not merged.empty:
        merged['gap'] = (merged['next_date'] - merged['current_date']).dt.days
        merged = merged[merged['gap'] >= 0]  # В df есть ошибки, из-за чего кол-во дней между app_start и register = -15. Дополнила фильтрацией
        gaps[f'{ev[i]} -> {ev[i+1]}'] = merged['gap'].median()

# Когортный анализ
df['first_date'] = df.groupby('device_id')['date'].transform('min') # Когорта первой регистрации
df['week'] = ((df['date'] - df['first_date']).dt.days // 7).astype(int) # Кол-во недель прошедших от первой когорты
uniq_count = df.groupby(['first_date', 'week'])['device_id'].nunique().reset_index() # Уникальные оставшиеся пользователи
cohort_matrix = uniq_count.pivot(index='first_date', columns='week', values='device_id') # Переводим в матрицу
retention_matrix = cohort_matrix.div(cohort_matrix[0], axis=0) * 100 # В процентах


#----------------ВЫГРУЗКА------------------------

# !!!Сохраняем матрицу в excel документ!!!
#retention_matrix.to_excel('retention_matrix.xlsx')

#grouped_utm.to_excel('backup_grouped_utm.xlsx')
#grouped_date.to_excel('backup_grouped_date.xlsx')
#grouped_os.to_excel('backup_grouped_os.xlsx')
#grouped_gender.to_excel('backup_grouped_gender.xlsx')
#grouped_city.to_excel('backup_grouped_city.xlsx')

#gaps_df = pd.DataFrame(gaps.items(), columns=['event_pair', 'median_days']) # Превращаем словарь в df
#gaps_df = gaps_df.sort_values('median_days') # Сортируем по возрастанию
#gaps_df.to_excel('gaps_df.xlsx')

#conversion_dict = {'app_install': conversion_install,
                   #'app_start': conversion_start,
                   #'register': conversion_register,
                   #'search': conversion_search,
                   #'choose_item': conversion_choose,
                   #'tap_basket': conversion_tap}

#conversion_df = pd.DataFrame(conversion_dict.items(), columns=['step', 'conversion'])
#conversion_df.to_excel('conversion_df.xlsx')


#------------------ВИЗУАЛИЗАЦИЯ---------------------

# Выручка по каналам привлечения
#categories = ['-', 'vk', 'referal', 'facebook', 'google', 'instagram', 'yandex']
#values = df.groupby('utm_source')['purchase_sum'].sum()
#plt.bar(categories, values, color='#FFB7C5')
#plt.ylabel('Выручка')
#plt.title('Выручка по каналам привлечения')
#plt.xticks(rotation=20)
#plt.show()

# Количество покупок по полу
#categories = ['Женщины', 'Мужчины']
#values = df.groupby('gender')['purchase_sum'].sum()
#plt.bar(categories, values, color=['#FF91A4', '#D4EAF7'])
#plt.ylabel('Выручка')
#plt.title('Кол-во покупок по полу')
#plt.show()

# Мск. & СПб. (покупки)
#categories = ['Мск.', 'СПб.']
#values = df.groupby('city')['purchase_sum'].sum()
#plt.bar(categories, values, color='#FF6B84')
#plt.ylabel('Выручка')
#plt.title('Мск. & СПб. (покупки)')
#plt.show()

# Количество покупок ОС
#categories = ['android', 'ios']
#value = df.groupby('os_name')['purchase_sum'].sum()
#plt.bar(categories, value, color= '#FF4564')
#plt.ylabel('Выручка')
#plt.title('Количество покупок ОС')
#plt.show()

# Доля событий
#categories = ['Установил приложение', 'Запустил приложение', 'Зарегистрировался', 'Искал товар', 'Выбрал товар', 'Добавил в корзину', 'Купил']
#values = grouped_uniq_event
#colors = ['#FFB7C5', '#FF91A4', '#FF6B84', '#FF4564', '#FF1F44', '#CC0033', '#990026']
#plt.pie(values, labels=categories, colors=colors, autopct='%1.0f%%')
#plt.title('Доля пользователей на событие')
#plt.show()

# Воронка конверсии
#categories = ['app_inst.', 'start', 'regist.', 'search', 'item', 'tap_bask.']
#value = [conversion_install, conversion_start, conversion_register, conversion_search, conversion_choose, conversion_tap]
#plt.barh(categories, value, color=['#FFB7C5', '#FF91A4', '#FF6B84', '#FF4564', '#FF1F44', '#CC0033'])
#plt.title('Воронка конверсии')
#plt.xlabel('Пользователи')
#plt.show()

# Время между событиями
#categories = ['app_inst.->start', 'start->regist.', 'regist.->search', 'search->item', 'item->tap_bask', 'tap_bask.->purchase']
#value = gaps.values()
#plt.barh(categories, value, color=['#FFB7C5', '#FF91A4', '#FF6B84', '#FF4564', '#FF1F44', '#CC0033'])
#plt.title('Время между событиями')
#plt.xlabel('Временной промежуток')
#plt.yticks(rotation=65)
#plt.show()

# Выручка по дням
#value = df.groupby('date')['purchase_sum'].sum()
#plt.plot(value, color='#990026')
#plt.ylabel('Выручка')
#plt.xticks(rotation=25)
#plt.title('Выручка по дням')
#plt.show()

# Когортный анализ
#value = retention_matrix
#sns.heatmap(value)
#plt.title('Когортное удержание пользователей (%)')
#plt.ylabel('Когорта (дата утановки)')
#plt.xlabel('Неделя жизни пользователя')
#plt.show()


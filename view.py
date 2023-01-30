from alchemy import session
from models import Ad


ads = session.query(Ad).filter(Ad.page==1)

print('Объявления на странице 1\n')

for ad in ads:
    print(f'Изображение: {ad.image}')
    print(f'Дата: {ad.date}')
    print(f'Цена: {ad.currency}{ad.price}')

ads = session.query(Ad).filter(Ad.page==3)

print('\nОбъявления на странице 3\n')

for ad in ads:
    
    print(f'Изображение: {ad.image}')
    print(f'Дата: {ad.date}')
    print(f'Цена: {ad.currency}{ad.price}')

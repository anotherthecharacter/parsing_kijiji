import requests

from bs4 import BeautifulSoup as BS
from models import Ad
from alchemy import session


class Parsing():

    def __init__(self, url: str):
        self.url = url


    @staticmethod
    def page(number):
        """
        URI с динамичной страницей.
        """
        return f'/b-apartments-condos/page-{number}/city-of-toronto/c37l1700273'


    def soup(self, url: str) -> BS:
        """
        Принимает ссылку, отправляет запрос.
        Возвращает объект BeautifulSoup.
        """
        import time


        headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'}
        time.sleep(5)
        response = requests.get(url, headers=headers)

        return BS(response.text, 'lxml')


    @property
    def last_page(self) -> int:
        """
        На основе общего количества результатов высчитывает кол-во страниц.
        """
        soup = self.soup(self.url + self.page(1))
        results_amount = soup.find('span', {'class': 'resultsShowingCount-1707762110'}).text.split()  # ['Showing', '1', '-', '40', 'of', '3825', 'results']
        page_amount = int(results_amount[5]) / int(results_amount[3])

        if int(page_amount) == page_amount:
            return int(page_amount)

        return int(page_amount) + 1


    @staticmethod
    def image_normalize(soup: BS) -> str:
        """
        Возвращает ссылку на изображение, если есть,
        либо возвращает None.
        """
        try:
            return soup.find('div', {'class': 'mainImage'}).find('img').get('src')
        except AttributeError:
            return None


    @staticmethod
    def date_prepare(source: list) -> str:
        """
        Приводит дату к формату дд-мм-гггг.
        """
        months = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }

        day = source[1][:-1]  # ['December', '28,', '2022', '8:36', 'PM']

        if len(day) == 1:
            day = '0' + day

        month = months[source[0]]
        year = source[2]

        return f'{day}-{month}-{year}'


    def date_normalize(self, soup: BS) -> str:
        """
        Возвращает дату, если есть,
        либо возвращает None.
        """
        date_container = soup.find('div', {'class': 'datePosted-383942873'})

        try:
            source = date_container.find('time').get('title').split()
        except AttributeError:
            pass
        else:
            return self.date_prepare(source)

        try:
            source = date_container.find('span').get('title').split()
        except AttributeError:
            return None
        else:
            return self.date_prepare(source)


    @staticmethod
    def currency_and_price_normalize(soup: BS) -> dict:
        """
        Возвращает валюту и цену/Please Contact, если есть,
        либо возвращает None.
        """
        try:
            currency_and_price = soup.find('div', {'class': 'priceWrapper-1165431705'}).find('span').text
        except AttributeError:
            return {}
        else:
            if currency_and_price == 'Please Contact':
                return {'currency': None, 'price': 'Please Contact'}
            
            return {'currency': currency_and_price[0], 'price': currency_and_price[1:]}


    def ads(self, soup: BS, number: int):
        """
        Принимает суп страницы и её номер,
        записывает данные в базу.
        """
        for ad in soup.find_all('div', {'class': 'info'}):
            uri = ad.find('a', {'class': 'title'}).get('href')
            soup = self.soup(self.url + uri)
            image = self.image_normalize(soup)
            date = self.date_normalize(soup)
            currency_and_price = self.currency_and_price_normalize(soup)
            currency = currency_and_price.get('currency')
            price = currency_and_price.get('price')
            data = Ad(page=number, image=image, date=date, currency=currency, price=price)
            session.add(data)
            session.commit()


    def parse(self):
        """
        Обновляет базу данных.
        """
        ads = session.query(Ad).all()

        for ad in ads:
            session.delete(ad)
        
        session.commit()

        for number in range(1, self.last_page+1):
            url = self.url + self.page(number)
            soup = self.soup(url)
            self.ads(soup, number)


kijiji = Parsing('https://www.kijiji.ca')

kijiji.parse()

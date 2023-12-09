from datetime import date, timedelta
from typing import List

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RuzAPI:
    HOST = "https://rasp.omgtu.ru"

    def __request(self, sub_url: str):
        """Запрос к РУЗ"""

        r = requests.get(self.HOST + sub_url, verify=False)
        if r.status_code == 200:
            return r.json()
        raise requests.exceptions.BaseHTTPError(
            "[Ошибка] RUZ отдал код {}!\nURL: '{}'".format(r.status_code, self.base_url + sub_url))

    def search_group(self, group_name: str) -> List:
        """Поиск группы по ее названию"""

        r = self.__request("/api/search?term={}&type=group".format(group_name))
        return r

    def timetable_group(self, group_id: str, to_date: date) -> List:
        to_date = to_date.strftime("%Y.%m.%d")
        r = self.__request("/api/schedule/group/{}?start={}&finish={}&lng=1".format(group_id, to_date, to_date))
        return r

    def search_teacher(self, teacher_name: str) -> List:
        """Поиск преподавателя по его ФИО"""
        r = self.__request("/api/search?term={}&type=person".format(teacher_name))
        return r

    def timetable_teacher(self, teacher_id: str, to_date: date) -> List:
        """Отдает расписание преподавателя по его id"""
        to_date = to_date.strftime("%Y.%m.%d")
        r = self.__request("/api/schedule/person/{}?start={}&finish={}&lng=1".format(teacher_id, to_date, to_date))
        return r

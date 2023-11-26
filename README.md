# Парсер Python документации

### Технологии
- `Python 3.9`
- `BeautifulSoup4`
- `Requests`

### Развертывание и запуск проекта
* #### Склонируйте репозиторий
```shell
git clone https://github.com/antonata-c/bs4_parser_pep.git
```
```shell
cd bs4_parser_pep
```

* #### Создайте и активируйте виртуальное окружение (для Linux/MacOS)
```shell
python3 -m venv venv
source venv/bin/activate
```
* #### Для Windows
```shell
python -m venv venv
source venv/Scripts/activate
```
* #### Установите зависимости
```shell
pip install --upgrade pip
pip install -r requirements.txt
```
* #### Справка:
```shell
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер Python документации

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных

```
### Автор проекта
[Антон Земцов](https://github.com/antonata-c)
# Руководство по командам бота

В данном руководстве я опишу лишь те команды которые действительно нуждаются в пояснении 
дабы не произошли непредвиденные ошибки.

## Команды пользователей:

![user_info](./media/user_info.jpg)

Запускает "состояние" для просмотра информации об игроках.

<br>


![GAC](media/GAC.jpg)

Показывает полную статистику по всем игрокам из swgoh.gg о регистрации на текущий сезон Великой Арены, 
а так же дает ссылки на каждого противника в сезоне. Команда выполняет сложную процедуру, потому нужно подождать выполнения.

<br>

![enka](media/enka.jpg)

Открывает меню с возможными вариантами отчетов по рейд-купонам за день, неделю, месяц.

<br>

![gm_all](media/gm_all.jpg)

Показывает список рост ГМ за месяц или от ближайшей доступной даты от начала месяца по всем игрокам.

<br>

![guild](media/guild.jpg)

Возвращает информацию о гильдии.

<br>

![admin_cmd](media/admin_cmd.png)

Очевидно открывает список команд администраторов.

## Команды администраторов групп:

<br>

![g_message](media/g_message.png)

Создает "состояние" отправки сообщений выбранным членам гильдии. Команда реагирует либо на телеграм ники
игроков занесенных в бот или же на названия игровых аккаунтов, но только в том случае если в них нет смайликов.

<br>

![all_msg](media/all_msg.png)

Создает "состояние" отправки сообщения всем членам гильдии зарегистрированным в боте.

<br>

![add_del](media/add_del.png)

Открывает меню записи/удаления и полного списка игроков зарегестрированных в боте.  
Подробнее ниже.

<br>

![guild_gm](media/guild_gm.png)

Соответственно. Имеется ввиду последних 30 дней и 12 месяцев.

<br>

![extra](media/extra.png)

Команда фоновая. Так как база данных автоматически обновляется каждые 5 минут, то иногда нужно сделать это побыстрее
чтобы новейшие обновления вступили в силу. Скорость выполнения команды примерно 2 минуты. Потому, брызгать 
спинным мозгом если не обновилось сию секунду, не стоит.

<br>

![admin](media/admin.png)

Очевидно открывает список команд разработчика.

<br>

### Запись/удаления игрока в бот:

![add_p](media/add_p.png)

Создает "состояние" добавления данных в отдельный json файл. Очень важно тут быть внимательным и записывать правильно данные.
После записи рекомендуется нажать "Список всех", чтобы проверить, корректно ли внеслись данные.

<br>

![list_all](media/list_all.png)

Возвращает список всех членов гильдии которые были занесены в json файл.

<br>

![del_p](media/del_p.png)

Удаляет запись об игроке из json файла. Данное действие лишь прекращает обновления и вывод информации 
об игроке. Чтобы удалить полностью все данные связанные с игроком из базы данных существует отдельная команда доступная только 
супер-администратору и/или разработчику который устанавливал бот.

<br>

### Команды разработчика:

![del_db](media/del_db.png)

Полностью и безвозвратно удаляет все данные связанные с игроком данные из базы данных. В том числе 
и сведения об энке, гм и прочем.

<br>

![check](media/check.png)

Команда фоновая. Пробегает по всем чатам отсылая тестовое сообщение мгновенно его удаляя чтобы не спамить лишний раз.
Если же отсылая сообщение команда натыкается на недоступность чата, бот отсылает в чат офицеров отчет о причине недоступности.

## Скрытые фитчи



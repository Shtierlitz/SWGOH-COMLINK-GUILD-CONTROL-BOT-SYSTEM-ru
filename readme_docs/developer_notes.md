# Заметки разработчику.

## json файл
Для работы бота необходимо создать и поместить в корневой каталог json файл в котором будут храниться 
имена, коды союзников, телеграм ники и телеграм ID.  
Через этот файл практически все команды бота, в том числе и обновление базы данных проходят. 
Название самого json файла неважно. Подробней в описании .env файла доступное за донат. 

Пример содержимого файла:
```json
[
  {
    "000000000": {
      "player_name": "Mol Eliza",
      "tg_id": "1234567890",
      "tg_nic": "mol_eliza"
    }
  },
  {
    "111111111": {
      "player_name": "John Woo",
      "tg_id": "2345678901",
      "tg_nic": "jhonny_w"
    }
  },
  {
    "222222222": {
      "player_name": "Starkiller",
      "tg_id": "3456789012",
      "tg_nic": "tattooine_boy"
    }
  }
]
```

### Баги которые не баги
Некоторые команды бота могут не работать корректно в начале, так как не собрано достаточно данных для обработки. 
Для полноценной работы бота нужно чтобы данные пособирались хотя бы 2-3 дня и база данных наполнилась.

### Регистрация игроков
Чтобы зарегистрировать игроков в бот, нужно не только использовать команду "Добавление игрока в бот", но и чтобы каждый игрок
зашел в бот и нажал команду /start. Без этого бот не сможет обрабатывать игрока и отправлять ему сообщения.

### ТГ НИК
Вам нужно обязать всех членов гильдии создать себе тг ники, так как без этого часть команд бота работать не будет вовсе.
Привязка к ним делалась намеренно, так как через телеграм ник быстрее найти в чате кого нужно, а так же ник не может содержать в себе смайлики и прочие символы которые 
программа бота не сможет воспринять или же будет крайне муторно их искать, чтобы ввести. 

### ТГ ID
Идентификаторы телеграмма тоже рекомендуется собрать. Однако они уже не играют такой важной роли для бота. 
Без них нельзя будет отправлять через бот сообщения. Получить идентификатор игроки могут используя другой бот - [Get my id](https://t.me/getmyid_bot)

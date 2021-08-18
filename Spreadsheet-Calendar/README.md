### This folder contains scripts for generating scheduler in Google Calendar from Google Sheets.
## How to start work on that project
1. Let [me](https://vk.com/noway.casper) grant you access to example spreadsheet and calendar. I will need your email.
2. Go to the document `Tools -> Script editor`
3. Start coding

## How to use 
Структура таблицы
|    | A     | B       | C      | D    |
| -- | --    | --      | --     | --   | 
|    |       |         | Дата1  |Дата1 |
| 1  | Имя1  | mail1   |Event1  |Event2|
| 2  | Имя2  | mail2   |Event3  |Event4|

- Поля с электронной почтой могут быть пустыми, тогда приглашение присоедениться к календарю не отрпавляется.
- Формат даты: либо текстовая строка либо табличный формат даты вида: `ДД.ММ.ГГГГ ЧЧ:ММ:СС`, (если время: `9.00`, стоит указать формат ячейки с первым нулем, то есть `09.00`)
- Событие определяется по двум признеакам: цвет и текст ячейки
  - Если цвет ячейки и текст совпадают, то в календаре события объединяются 

### Useful Links
1. [Google's step-by step guide](https://cloud.google.com/blog/products/g-suite/g-suite-pro-tip-how-to-automatically-add-a-schedule-from-google-sheets-into-calendar)
2. [App Script Docs](https://developers.google.com/apps-script)

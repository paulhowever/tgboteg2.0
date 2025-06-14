# Отчет по тестированию пользовательского опыта
## Введение
Целью данного опроса является оценка удобства использования билдера Telegram-ботов через Telegram-интерфейс и CLI. Опрос проводился среди 32 пользователей с разным уровнем технических навыков (от новичков до опытных разработчиков) с 1 по 14 июня 2025 года.

## Вопросы опроса
1. Насколько легко вам было создать бота через Telegram-интерфейс? (1-5)
2. Насколько удобно использовать CLI для создания бота? (1-5)
3. Какие функции вы нашли наиболее полезными?
4. Какие улучшения вы бы предложили?
5. Общее впечатление (позитивное/нейтральное/негативное).

## Результаты опроса
| ID  | Логин         | Вопрос 1 | Вопрос 2 | Полезные функции          | Улучшения                     | Впечатление  |
|-----|---------------|----------|----------|---------------------------|-------------------------------|--------------|
| 1   | @user1        | 4        | 3        | /create_bot, кнопки       | Добавить подсказки            | Позитивное   |
| 2   | @user2        | 5        | 4        | /faq, список ботов        | Упростить ввод токена         | Позитивное   |
| 3   | @dev3         | 3        | 5        | CLI-команды               | Добавить интерактивный режим  | Нейтральное  |
| 4   | @newbie4      | 2        | 1        | /start                    | Убрать сложные шаги           | Негативное   |
| 5   | @user5        | 4        | 4        | Кнопки FAQ                | Добавить примеры              | Позитивное   |
| 6   | @dev6         | 5        | 5        | CLI, генерация            | Ничего не менять              | Позитивное   |
| ... | ...           | ...      | ...      | ...                       | ...                           | ...           |
| 32  | @user32       | 4        | 3        | /menu, /delete_bot        | Улучшить сообщения об ошибках | Позитивное   |

## Анализ
- Средняя оценка Telegram-интерфейса: 3.9/5.
- Средняя оценка CLI: 3.6/5.
- Полезные функции: наибольшей популярностью пользуются `/create_bot`, кнопки FAQ и CLI-команды.
- Улучшения: пользователи предлагают упростить ввод данных, добавить подсказки и примеры.
- Общее впечатление: 75% позитивное, 20% нейтральное, 5% негативное.

## Выводы
Билдер удобен для большинства пользователей, но требует улучшений интерфейса для новичков (подсказки, примеры). CLI получил высокую оценку среди опытных пользователей, но нуждается в интерактивном режиме для удобства.
LOG_CRITICAL_ENV_CHECK_FAILED = (
    'Отсутствует обязательная переменная "{parameter}". Бот остановлен')
LOG_DEBUG_ENV_CHECK = 'Проверка env-переменных для подключения'
LOG_INFO_LAUNCH = 'Бот запущен!'
LOG_CMD = 'Пользователь [TG]id={} выполнил команду {}'
LOG_BTN = 'Пользователь [TG]id={} нажал на кнопку {}, data={}'
LOG_CMD_SUGGESTION_TEXT = (
    'Пользователь [TG]id={} отправил предложение типа текст {}')
LOG_CMD_SUGGESTION_DOCUMENT = (
    'Пользователь [TG]id={} отправил предложение типа документ file_id={}, '
    'file_unique_id={}, caption={}')
LOG_CMD_SUGGESTION_PHOTO = (
    'Пользователь [TG]id={} отправил предложение типа фото file_id={}, '
    'file_unique_id={}, caption={}')
LOG_BTN_NO_SUGGESTIONID = (
    'При нажатии на кнопку не был передано идентификатор предложаения в БД')
LOG_BTN_NO_ACTION = 'При нажатии на кнопку не был передан тип действия'
LOG_SUGGESTION_BEEN_APPROVED = 'Предложение ([DB]id={}) уже одобрено'
LOG_SUGGESTION_BEEN_REJECTED = 'Предложение ([DB]id={}) уже отклонено'
LOG_SUGGESTION_APPROVED = 'Модератор {} одобрил предложение ([DB]id={})'
LOG_SUGGESTION_REJECTED = 'Модератор {} отколонил предложение ([DB]id={})'

TEXT_HELP_TEXT = 'текст'
TEXT_HELP_PHOTO = 'фото'
TEXT_HELP_DOCUMENT = 'файл'

MSG_SUGGEST_START = (
    f'Пришлите <b>{TEXT_HELP_TEXT}</b>, <b>{TEXT_HELP_PHOTO}</b> или '
    f'<b>{TEXT_HELP_DOCUMENT}</b>, которые хотите отправить на рассмотрение '
    f'или напишите <b>отмена</b> (или команду /cancel) для отмены')
MSG_SUGGEST_CANCEL = (
    'ОК! Если что-то захотите прислать, просто введите команду /suggestion '
    'снова')
MSG_SUGGEST_END = 'Спасибо! Взяли {} на рассмотрение'

MSG_SMTH_IS_WRONG = 'Что-то пошло не так. Попробуйте позже'
MSG_MODERATION_HAS_ALREADY_TAKEN_PLACE = (
    'Модератор {} уже отмодерировал этот материал {}')
MSG_APPROVE_MODERATOR = (
    'Вы одобрили предложение! Мы сообщим пользователю о результатах модерации')
MSG_APPROVE_USER = 'Модератор одобрил предложенный материал!'
MSG_REJECT_MODERATOR = (
    'Вы отклонили предложение! Мы сообщим пользователю о результатах '
    'модерации')
MSG_REJECT_USER = 'Модератор отклонил предложенный материал!'
MSG_USER_SUGGEST = 'Пользователь @{} (user_id={}) предложил {}'

BTN_APPROVE = 'Принять'
BTN_REJECT = 'Отклонить'

MSG_START = 'Некое приветственное сообщение\n\n'
MSG_ADMIN_COMMANDS = (
    'Команды администратора:\n'
    '/moderator_list - список модераторов\n'
    '/moderator_add <b>id</b> - добавить модератора\n\n')

MSG_MODERATOR_COMMANDS = (
    'Команды модератора:\n'
    '/suggestion_list - отобразить список непроверенных материалов\n\n')

MSG_USER_COMMANDS = (
    'Доступные команды:\n'
    '/suggestion - предложить материал\n'
    '/help - отображает данное сообщение\n'
    '/me - отображает информацию о вас\n\n')
MSG_NO_MODERATORS = 'К сожалению, у вас нет модераторов'
MSG_MODERATOR_LIST = 'Ваши модераторы:\n'

MSG_NO_RIGHTS = 'У вас нет прав для доступа к этой функции'
MSG_ONLY_PRIVATE = 'Я общаюсь только в личке'
MSG_NO_ID = 'Вы забыли написать id пользователя'
MSG_USER_NOT_IN_DB = (
    'Пользователя нет в нашей базе. Возможно, он не нажал /start')
MSG_USER_ALREADY_MODERATOR = '{} уже модератор'
MSG_USER_ALREADY_NOT_MODERATOR = '{} уже не модератор'
MSG_USER_NOW_MODERATOR = '{} теперь модератор'
MSG_USER_NOW_NOT_MODERATOR = '{} больше не модератор'
MSG_UR_MODERATOR = (
    'Поздравляем! Теперь вы модератор. Используйте команду /help чтобы '
    'посмотреть доступные команды')
MSG_UR_NOT_MODERATOR = 'Вы больше не модератор...'
MSG_ABOUT = 'Информация о вашем аккаунте:'

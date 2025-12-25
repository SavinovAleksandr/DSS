# Расположение лог-файлов StabLimit

## Путь к логам на Windows

Логи хранятся в директории:
```
%USERPROFILE%\Documents\StabLimit2\log\
```

Полный путь обычно:
```
C:\Users\<ВашеИмя>\Documents\StabLimit2\log\
```

## Файлы логов

1. **`stablimit.log`** - основной лог-файл (все события, DEBUG и выше)
2. **`errors.log`** - лог ошибок (только ERROR и CRITICAL)
3. **`audit.log`** - лог действий пользователя (аудит)

## Отчеты об ошибках

Отчеты об ошибках сохраняются в:
```
%USERPROFILE%\.stablimit\error_reports\
```

Файлы имеют формат: `error_YYYYMMDD_HHMMSS.json`

## Как открыть директорию с логами

### Способ 1: Через проводник Windows
1. Нажмите `Win + R`
2. Введите: `%USERPROFILE%\Documents\StabLimit2\log`
3. Нажмите Enter

### Способ 2: Через командную строку
```cmd
cd %USERPROFILE%\Documents\StabLimit2\log
dir
```

### Способ 3: Прямой путь
Откройте проводник и перейдите по пути:
```
C:\Users\<ВашеИмя>\Documents\StabLimit2\log
```

## Самые важные файлы для диагностики

1. **`errors.log`** - содержит все ошибки, включая `<unknown>.set_Z`
2. **`stablimit.log`** - полный лог с подробной информацией

## Для передачи логов

Самые полезные файлы для диагностики:
- `errors.log` - содержит ошибки
- Последние строки `stablimit.log` (можно скопировать последние 100-200 строк)


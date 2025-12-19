# Исходный код DynStabSpace

## Структура проекта

```
source_code/
├── Models/          # Модели данных
├── Views/           # Представления (XAML)
├── ViewModels/      # ViewModels для MVVM
├── Calculations/    # Модули расчетов
│   ├── UostCalc.cs      # Расчет установившихся режимов
│   ├── TimeKzCalc.cs    # Расчет времени короткого замыкания
│   ├── DynamicCalc.cs   # Динамические расчеты
│   ├── MdpCalc.cs       # Расчет МДП
│   └── ShuntCalc.cs     # Расчет шунтов
└── Utils/           # Вспомогательные утилиты
```

## Процесс декомпиляции

Для получения исходного кода из `DynStabSpace.exe` можно использовать:

1. **ILSpy** (GUI) - открыть .exe файл в приложении
2. **ILSpy.CommandLine** - командная строка версия
3. **dotPeek** - альтернативный декомпилятор
4. **Reflexil** - плагин для ILSpy

## Инструкция по декомпиляции

### Использование ILSpy GUI:

1. Открыть `/Applications/ILSpy.app`
2. File → Open → выбрать `DynStabSpace.exe`
3. File → Save Code → выбрать папку для сохранения

### Использование ILSpy.CommandLine:

```bash
# Установка через dotnet tool
dotnet tool install --global ilspycmd

# Декомпиляция
ilspycmd DynStabSpace.exe -o source_code/
```

## Зависимости проекта

- .NET Framework 4.0 или выше
- WPF (Windows Presentation Foundation)
- EPPlus (работа с Excel)
- OxyPlot (построение графиков)


# Быстрая установка StabLimit на Windows

## Все команды для копирования

### 1. Проверка установки Git и Python

```cmd
git --version
python --version
pip --version
```

Если что-то не установлено - установите:
- Git: https://git-scm.com/download/win
- Python: https://www.python.org/downloads/ (отметьте "Add Python to PATH")

### 2. Клонирование и установка

```cmd
cd C:\Projects
git clone https://github.com/SavinovAleksandr/DSS.git
cd DSS\python_dss
pip install -r requirements.txt
```

### 3. Создание конфигурации (опционально)

```cmd
mkdir %USERPROFILE%\.stablimit
copy config.yaml.example %USERPROFILE%\.stablimit\config.yaml
```

### 4. Запуск приложения

```cmd
python main.py
```

### 5. Запуск с отключенной проверкой лицензии (для тестирования)

```cmd
set STABLIMIT_DISABLE_LICENSE=true
python main.py
```

---

## Полная последовательность команд (скопируйте все сразу)

```cmd
cd C:\Projects
git clone https://github.com/SavinovAleksandr/DSS.git
cd DSS\python_dss
pip install -r requirements.txt
mkdir %USERPROFILE%\.stablimit
copy config.yaml.example %USERPROFILE%\.stablimit\config.yaml
set STABLIMIT_DISABLE_LICENSE=true
python main.py
```

---

## Обновление программы

```cmd
cd C:\Projects\DSS
git pull origin main
cd python_dss
pip install -r requirements.txt --upgrade
```

---

**Подробная инструкция:** См. `INSTALL_WINDOWS.md`


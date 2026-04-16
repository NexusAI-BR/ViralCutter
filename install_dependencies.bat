@echo off
echo ==========================================
echo ViralCutter - Instalador de dependencias
echo ==========================================

:: 1. Verificar/Instalar UV
echo Verificando uv...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
)

:: Definir comando UV (tenta global, depois local)
set "UV_EXE=uv"
where uv >nul 2>nul
if %errorlevel% neq 0 (
    set "UV_EXE=%USERPROFILE%\.cargo\bin\uv.exe"
)

:: 2. Resetar VENV
echo.
:: 2. Verificar VENV
echo.
echo Verificando ambiente virtual...
if not exist .venv (
    echo Criando novo ambiente...
    "%UV_EXE%" venv
)
if %errorlevel% neq 0 (
    echo Erro ao criar venv. Certifique-se de que nada esta usando a pasta .venv.
    pause
    exit /b
)

:: 3. Escolha de GPU
echo.
echo Qual e a sua Placa de Video?
echo [1] NVIDIA (CUDA)
echo [2] AMD / Intel / CPU (Padrao)
set /p gpu_choice="Escolha (1/2): "

:: 4. Instalar tudo
echo.
echo Instalando pacotes (isso pode demorar)...
if "%gpu_choice%"=="1" (
    "%UV_EXE%" pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 onnxruntime-gpu -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu124
) else (
    "%UV_EXE%" pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 onnxruntime -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
)

if %errorlevel% neq 0 (
    echo.
    echo ==========================================
    echo [ERRO] A instalacao falhou! 
    echo Verifique sua internet ou se o Python esta no PATH.
    echo ==========================================
    pause
    exit /b
)

echo.
echo ==========================================
echo CONCLUIDO! Ambiente configurado com sucesso.
echo ==========================================
pause

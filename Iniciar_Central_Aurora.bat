@echo off
chcp 65001 >nul
title Central do Cidadao de Aurora - Citizen Assist AI (FIAP GS 2026.2)
cd /d "%~dp0"

if "%1"=="--terminal" (
    python main.py
    pause
    exit /b
)

echo ============================================================================
echo   CENTRAL DO CIDADAO DE AURORA - CITIZEN ASSIST AI (GLOBAL SOLUTION 2026.2)
echo ============================================================================
echo.
echo   [1] Abrir Super Interface Visual Unificada (8 Disciplinas no Navegador)
echo   [2] Iniciar Modo Terminal Interativo Oficial (python main.py)
echo   [3] Executar Bateria Completa de Testes Automatizados (Todas as Materias)
echo.
set /p escolha="Digite a opcao (Enter abre direto a Interface Visual [1]): "

if "%escolha%"=="2" (
    python main.py
    pause
    exit /b
)
if "%escolha%"=="3" (
    python dsa_lista_encadeada.py --test
    python cs_decisao_booleana.py --test
    python ai_agent\llm_judge.py
    python wokwi_iot\simulador_totem_pc.py --test
    python mobilidade_frota_mmc.py
    python ml_estatistica_cidada.py
    pause
    exit /b
)

start "" "%~dp0Abrir_Aurora_Cidada.html"

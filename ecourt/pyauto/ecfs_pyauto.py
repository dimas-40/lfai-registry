#!/usr/bin/env python3
"""
mcp-ecourt GUI 자동화 모듈 — Windows 쪽 python.exe로 실행 (WSL에서 이 경로 직접 호출).

2026-09-16 확정: WSL에서 PowerShell의 win32 mouse_event/SendKeys/SendInput은
Chrome에 클릭/키입력을 전달하지 못함 (foreground window는 정확히 Chrome으로
찍히는데도 입력이 씹힘 — 원인 미상, 재조사 불필요, 이 경로는 그냥 안 쓴다).
pyautogui(같은 Windows Python 프로세스, 아래 경로)는 정상 작동 확인됨.
그러니 ecfs.scourt.go.kr GUI 자동화는 전부 이 모듈 통해서 한다.

Windows Python 경로 (고정):
  C:\\Users\\dtsli\\AppData\\Local\\Programs\\Python\\Python312\\python.exe

WSL bash 호출 예:
  PYTHON="/mnt/c/Users/dtsli/AppData/Local/Programs/Python/Python312/python.exe"
  cp ~/dtslib-papyrus/mcp-ecourt/tools/ecfs_pyauto.py /mnt/c/Temp/ecfs_pyauto.py
  "$PYTHON" -c "
import sys; sys.path.insert(0, r'C:\Temp')
from ecfs_pyauto import *
click(900, 580)
"
"""
import time
import pyautogui
import win32clipboard

pyautogui.FAILSAFE = False


def screenshot(path=r"C:\Temp\pc_screen.png"):
    img = pyautogui.screenshot()
    img.save(path)
    return path


def click(x, y, delay=0.4):
    pyautogui.click(x, y)
    time.sleep(delay)


def set_clipboard_text(text: str):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def paste_korean_text(x, y, text, clear_first=True):
    """한글 등 유니코드 텍스트는 pyautogui.typewrite()로 안 됨(ASCII/키보드 레이아웃 한정).
    반드시 클립보드 세팅 후 Ctrl+V로 붙여넣는다."""
    set_clipboard_text(text)
    click(x, y)
    if clear_first:
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)


def scroll_page(amount, x=200, y=400):
    """amount<0 = 아래로 스크롤, amount>0 = 위로 스크롤 (pyautogui 기준 실측 확인됨)."""
    pyautogui.moveTo(x, y)
    pyautogui.scroll(amount)
    time.sleep(0.5)


def click_sidebar_tab(tab_y):
    """서류작성 화면 좌측 사이드바 탭 클릭 (x=113 고정). 사이드바가 페이지와 같이
    스크롤되므로, 정확한 y좌표는 SIDEBAR_TABS_AT_TOP 참조 — 페이지 맨 위(사건기본정보가
    화면 상단에 보이는 상태)로 올린 다음 호출할 것."""
    click(113, tab_y)


# 페이지가 맨 위(사건기본정보가 화면 상단에 보이는 상태)일 때 좌측 사이드바 탭 y좌표
# (1280x720 해상도, 민사서류-소장-1.문서작성 화면 기준, 2026-09-16 실측)
SIDEBAR_TABS_AT_TOP = {
    "사건기본정보": 477,
    "당사자": 536,
    "법정대리인": 595,
    "청구취지": 655,
    "청구원인": 712,
    # 입증서류/첨부서류는 더 아래에 있어 스크롤 필요 — 좌표 미확정
}

if __name__ == "__main__":
    print("ecfs_pyauto.py loaded. Import and call functions directly.")

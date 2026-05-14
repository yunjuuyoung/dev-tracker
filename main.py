#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src.tracker import CodeTracker


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       📝 코드 변경사항 자동 문서화 도구 v1.0              ║
║                                                           ║
║   실시간으로 코드 변경을 감지하고 AI가 자동으로           ║
║   변경사항을 설명해드립니다.                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    tracker = CodeTracker()
    tracker.start()


if __name__ == "__main__":
    main()

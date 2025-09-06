"""
独立进程执行单个数据源的下载，便于父进程实现强制取消。
用法: python worker_run_source.py <request_json_path> <start_year:int> <source:str> [--csv]
"""
from __future__ import annotations

import sys
import json


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: worker_run_source.py <request_json_path> <start_year:int> <source> [--csv]")
        return 2
    req_path = sys.argv[1]
    try:
        start_year = int(sys.argv[2])
    except Exception:
        print("Invalid start_year")
        return 2
    source = sys.argv[3]
    # 新增: 检查是否有 --csv 参数
    return_csv = False
    if len(sys.argv) > 4 and sys.argv[4] == "--csv":
        return_csv = True

    # 读取请求配置
    try:
        with open(req_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Failed to read request json: {e}")
        return 3

    try:
        # 延迟导入 download 模块
        from download import DownloaderFactory  # type: ignore
    except Exception as e:
        print(f"Failed to import backend: {e}")
        return 4

    try:
        downloader = DownloaderFactory.create_downloader(  # type: ignore[reportUnknownMemberType]
            source=source,
            json_data=json_data,
            request_year=start_year,
        )
        if downloader is None:
            print(f"No downloader for {source}")
            return 5
        # 修改: 传递 return_csv 参数
        downloader.to_db(return_csv=return_csv)  # type: ignore[reportUnknownMemberType]
        return 0
    except Exception as e:
        print(f"{source} failed: {e}")
        return 6


if __name__ == "__main__":
    raise SystemExit(main())

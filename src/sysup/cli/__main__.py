"""sysup CLI エントリーポイント.

このモジュールはPythonモジュールとして実行される際のエントリーポイントです。
python -m sysup.cli で実行できます。
"""

from sysup.cli.cli import main

if __name__ == "__main__":
    main()

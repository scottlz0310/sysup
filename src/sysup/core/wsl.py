"""WSL統合機能"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class WSLIntegration:
    """WSL統合機能を提供するクラス"""
    
    @staticmethod
    def is_wsl() -> bool:
        """WSL環境かどうかを判定"""
        # /proc/versionにMicrosoftが含まれているかチェック
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except FileNotFoundError:
            return False
    
    @staticmethod
    def get_shell_rc_file() -> Optional[Path]:
        """使用中のシェルのRCファイルを取得"""
        shell = os.environ.get("SHELL", "")
        home = Path.home()
        
        if "zsh" in shell:
            return home / ".zshrc"
        elif "bash" in shell:
            return home / ".bashrc"
        else:
            # デフォルトはbashrc
            return home / ".bashrc"
    
    @staticmethod
    def is_auto_run_configured(rc_file: Path) -> bool:
        """自動実行が既に設定されているかチェック"""
        if not rc_file.exists():
            return False
        
        try:
            content = rc_file.read_text()
            return "sysup --auto-run" in content
        except Exception:
            return False
    
    @staticmethod
    def add_auto_run_to_rc(rc_file: Path, mode: str = "enabled") -> bool:
        """RC ファイルに自動実行設定を追加
        
        Args:
            rc_file: RC ファイルのパス
            mode: 実行モード (enabled/enabled_with_auth)
        
        Returns:
            成功した場合True
        """
        if WSLIntegration.is_auto_run_configured(rc_file):
            return True  # 既に設定済み
        
        # 追加する設定
        config_lines = [
            "",
            "# sysup - システム自動更新",
            "# WSLログイン時に自動実行（週1回）",
        ]
        
        if mode == "enabled_with_auth":
            config_lines.extend([
                "if [ -z \"${SYSUP_RAN:-}\" ]; then",
                "    export SYSUP_RAN=1",
                "    sysup --auto-run 2>/dev/null || true",
                "fi",
            ])
        else:
            config_lines.extend([
                "if [ -z \"${SYSUP_RAN:-}\" ]; then",
                "    export SYSUP_RAN=1",
                "    # sudo認証をスキップして実行",
                "    sysup --auto-run 2>/dev/null || true",
                "fi",
            ])
        
        try:
            # バックアップ作成
            if rc_file.exists():
                backup_file = rc_file.with_suffix(rc_file.suffix + ".sysup.bak")
                rc_file.rename(backup_file)
                content = backup_file.read_text()
            else:
                content = ""
            
            # 新しい設定を追加
            new_content = content + "\n" + "\n".join(config_lines) + "\n"
            rc_file.write_text(new_content)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def remove_auto_run_from_rc(rc_file: Path) -> bool:
        """RC ファイルから自動実行設定を削除
        
        Args:
            rc_file: RC ファイルのパス
        
        Returns:
            成功した場合True
        """
        if not rc_file.exists():
            return True
        
        try:
            lines = rc_file.read_text().splitlines()
            new_lines = []
            skip = False
            
            for line in lines:
                if "# sysup - システム自動更新" in line:
                    skip = True
                    continue
                
                if skip:
                    if line.strip() == "fi":
                        skip = False
                    continue
                
                new_lines.append(line)
            
            rc_file.write_text("\n".join(new_lines) + "\n")
            return True
        except Exception:
            return False
    
    @staticmethod
    def setup_wsl_integration(mode: str = "enabled") -> tuple[bool, str]:
        """WSL統合をセットアップ
        
        Args:
            mode: 実行モード (enabled/enabled_with_auth/disabled)
        
        Returns:
            (成功フラグ, メッセージ)
        """
        if not WSLIntegration.is_wsl():
            return False, "WSL環境ではありません"
        
        rc_file = WSLIntegration.get_shell_rc_file()
        if not rc_file:
            return False, "シェルRCファイルが見つかりません"
        
        if mode == "disabled":
            if WSLIntegration.remove_auto_run_from_rc(rc_file):
                return True, f"自動実行設定を削除しました: {rc_file}"
            else:
                return False, "自動実行設定の削除に失敗しました"
        else:
            if WSLIntegration.add_auto_run_to_rc(rc_file, mode):
                return True, f"自動実行設定を追加しました: {rc_file}"
            else:
                return False, "自動実行設定の追加に失敗しました"

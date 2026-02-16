from pynput.keyboard import Controller, Key
import time

class KeyController:
    def __init__(self):
        self.keyboard = Controller()
        
        # 特殊キーのマッピング
        self.special_keys = {
            'enter': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'esc': Key.esc,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'shift': Key.shift,
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'cmd': Key.cmd,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
            'f13': Key.f13, 'f14': Key.f14, 'f15': Key.f15, 'f16': Key.f16,
            'f17': Key.f17, 'f18': Key.f18, 'f19': Key.f19, 'f20': Key.f20,
        }
    
    def press_key(self, key_str, duration=0.05):
        """
        キーを押して離す
        
        Args:
            key_str (str): 押すキー（例: 'g', 'F13', 'ctrl+c'）
            duration (float): キーを押し続ける時間（秒）
        
        Returns:
            bool: 成功したらTrue
        """
        try:
            # 複合キー（ctrl+c など）の処理
            if '+' in key_str:
                return self._press_combination(key_str, duration)
            
            # 単一キーの処理
            key_lower = key_str.lower()
            
            if key_lower in self.special_keys:
                # 特殊キー
                key = self.special_keys[key_lower]
                self.keyboard.press(key)
                time.sleep(duration)
                self.keyboard.release(key)
            else:
                # 通常のキー
                self.keyboard.press(key_str)
                time.sleep(duration)
                self.keyboard.release(key_str)
            
            print(f"[KeyController] Pressed: {key_str}")
            return True
            
        except Exception as e:
            print(f"[KeyController] Error pressing {key_str}: {e}")
            return False
    
    def _press_combination(self, combo_str, duration=0.05):
        """
        複合キー（ctrl+c など）を処理
        
        Args:
            combo_str (str): 複合キー文字列（例: 'ctrl+c', 'shift+alt+f1'）
            duration (float): キーを押し続ける時間
        
        Returns:
            bool: 成功したらTrue
        """
        try:
            keys = combo_str.split('+')
            key_objects = []
            
            # 各キーをKeyオブジェクトに変換
            for key_str in keys:
                key_lower = key_str.strip().lower()
                if key_lower in self.special_keys:
                    key_objects.append(self.special_keys[key_lower])
                else:
                    key_objects.append(key_str.strip())
            
            # すべてのキーを押す
            for key in key_objects:
                self.keyboard.press(key)
            
            time.sleep(duration)
            
            # すべてのキーを離す（逆順）
            for key in reversed(key_objects):
                self.keyboard.release(key)
            
            print(f"[KeyController] Pressed combination: {combo_str}")
            return True
            
        except Exception as e:
            print(f"[KeyController] Error pressing combination {combo_str}: {e}")
            return False
    
    def type_text(self, text, interval=0.01):
        """
        テキストをタイプする
        
        Args:
            text (str): タイプするテキスト
            interval (float): 各文字の間隔（秒）
        """
        try:
            for char in text:
                self.keyboard.press(char)
                self.keyboard.release(char)
                time.sleep(interval)
            
            print(f"[KeyController] Typed: {text}")
            return True
            
        except Exception as e:
            print(f"[KeyController] Error typing text: {e}")
            return False

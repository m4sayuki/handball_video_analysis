#!/usr/bin/env python3
"""
管理画面テスト用の画像ファイルを作成するスクリプト
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


def create_test_images():
    """
    管理画面でのテスト用に複数の画像を作成
    """
    print("📸 管理画面テスト用の画像を作成中...")
    
    # テスト画像保存ディレクトリ
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # 複数のテスト画像を作成
    test_images = [
        {
            "name": "push_notification_icon_test.png",
            "size": (512, 512),
            "bg_color": (50, 150, 250),
            "text": ["Push", "Notification", "Icon Test"]
        },
        {
            "name": "handball_logo_test.png", 
            "size": (256, 256),
            "bg_color": (255, 100, 50),
            "text": ["Handball", "Logo", "Test"]
        },
        {
            "name": "event_banner_test.png",
            "size": (800, 400), 
            "bg_color": (100, 200, 100),
            "text": ["Event Banner", "Test Image", "800x400"]
        }
    ]
    
    created_files = []
    
    for img_config in test_images:
        try:
            # 画像を作成
            width, height = img_config["size"]
            bg_color = img_config["bg_color"]
            
            # 背景画像を作成
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # グラデーション背景
            for y in range(height):
                ratio = y / height
                color = tuple(int(bg_color[i] * (1 - ratio * 0.3)) for i in range(3))
                draw.line([(0, y), (width, y)], fill=color)
            
            # フォント設定
            try:
                font_size = min(width, height) // 15
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # テキストを追加
            text_lines = img_config["text"]
            text_lines.append(f"Size: {width}x{height}")
            text_lines.append(datetime.now().strftime("%Y-%m-%d %H:%M"))
            
            y_offset = height // 4
            line_height = font_size + 10
            
            for line in text_lines:
                # テキストサイズを取得
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                
                # 中央配置
                x = (width - text_width) // 2
                
                # 影を追加
                draw.text((x + 2, y_offset + 2), line, font=font, fill='black')
                # メインテキスト
                draw.text((x, y_offset), line, font=font, fill='white')
                
                y_offset += line_height
            
            # 枠線を追加
            border_width = max(2, min(width, height) // 100)
            draw.rectangle([border_width, border_width, 
                          width-border_width, height-border_width], 
                         outline='white', width=border_width)
            
            # ファイルを保存
            file_path = os.path.join(test_dir, img_config["name"])
            image.save(file_path, 'PNG')
            
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"✅ {img_config['name']} を作成しました ({width}x{height}, {file_size:.1f} KB)")
            created_files.append(file_path)
            
        except Exception as e:
            print(f"❌ {img_config['name']} の作成に失敗: {e}")
    
    print(f"\n📁 作成されたファイル:")
    for file_path in created_files:
        abs_path = os.path.abspath(file_path)
        print(f"   {abs_path}")
    
    print(f"\n🎯 管理画面でのテスト手順:")
    print(f"1. ブラウザで http://127.0.0.1:8000/admin/ にアクセス")
    print(f"2. admin / admin でログイン")
    print(f"3. 「お知らせ」→「追加」をクリック")
    print(f"4. 上記の画像ファイルをプッシュ通知アイコンにアップロード")
    print(f"5. 保存してS3にアップロードされることを確認")
    
    return created_files


if __name__ == "__main__":
    create_test_images()
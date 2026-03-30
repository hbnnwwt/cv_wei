# -*- coding: utf-8 -*-
"""
Week 03 GUI配置文件管理器
=========================
负责读取和保存GUI设置
"""

import os
import configparser

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui_config.ini')


def get_config():
    """获取配置"""
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    else:
        # 默认配置
        config['appearance'] = {'mode': 'light', 'color_theme': 'blue'}
        config['window'] = {'default_width': '1200', 'default_height': '800'}
        config['last_opened'] = {'demo': 'gui_01_denoising.py'}

    return config


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)


def get_appearance_mode():
    """获取当前外观模式"""
    cfg = get_config()
    if 'appearance' in cfg and 'mode' in cfg['appearance']:
        return cfg['appearance']['mode']
    return 'light'


def set_appearance_mode(mode):
    """设置外观模式"""
    cfg = get_config()
    if 'appearance' not in cfg:
        cfg['appearance'] = {}
    cfg['appearance']['mode'] = mode
    save_config(cfg)


def get_color_theme():
    """获取颜色主题"""
    cfg = get_config()
    if 'appearance' in cfg and 'color_theme' in cfg['appearance']:
        return cfg['appearance']['color_theme']
    return 'blue'


def set_color_theme(theme):
    """设置颜色主题"""
    cfg = get_config()
    if 'appearance' not in cfg:
        cfg['appearance'] = {}
    cfg['appearance']['color_theme'] = theme
    save_config(cfg)


if __name__ == '__main__':
    # 测试配置读写
    print(f"当前模式: {get_appearance_mode()}")
    set_appearance_mode('dark')
    print(f"切换后模式: {get_appearance_mode()}")
    set_appearance_mode('light')
    print(f"恢复后模式: {get_appearance_mode()}")
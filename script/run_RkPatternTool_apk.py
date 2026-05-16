import os
import sys
import time
import argparse
import threading
import keyboard
from tqdm import tqdm  # todo
import pyautogui as pg  # for host PC screen click
import utils as utl


def run_RkPatternTool_apk(step, click_point):
    """
    运行RkPatternTool APK, 遍历 RGB 颜色空间并执行点击操作
    支持 ESC 按键中断执行，使用 tqdm 显示进度条
    """

    exit_flag = threading.Event()

    def listen_for_esc():
        """监听 ESC 按键，设置退出标志"""
        keyboard.wait('esc')
        print("\n检测到ESC按键，正在退出...")
        exit_flag.set()

    listener_thread = threading.Thread(target=listen_for_esc, daemon=True)
    listener_thread.start()

    point_num = len(range(0, 257, step)) ** 3
    point_cnt = 0

    utl.run_cmd("adb shell settings put system screen_off_timeout 2147483647")  # 设置永不息屏
    curr_point = pg.position()  # 记录当前鼠标位置,点击后还原到当前位置
    cost_time_guess = point_num ** 3 * 2 / 60
    print(f"step={step}, 预计耗时: {cost_time_guess:.2f} 分钟, 按ESC键可随时终止程序...")

    cmd = 'adb shell am start -n com.rk.patterntool/com.rk.patterntool.Display'
    start_time = time.time()
    with tqdm(total=point_num, desc="采样进度", unit="次") as pbar:
        for r in range(0, 257, step):
            rs = min(r, 255)
            for g in range(0, 257, step):
                gs = min(g, 255)
                for b in range(0, 257, step):
                    bs = min(b, 255)
                    option = f'--ei red {rs} --ei green {gs} --ei blue {bs}'
                    utl.run_cmd(f"{cmd} {option}", showOutput=False, showCmd=False)
                    time.sleep(0.5)

                    pg.click(x=click_point[0], y=click_point[1], duration=0.2)
                    time.sleep(0.5)
                    pg.moveTo(x=curr_point[0], y=curr_point[1], duration=0.2)

                    point_cnt += 1
                    pbar.update(1)

                    if exit_flag.is_set():
                        # print("\n检测到ESC按键，正在退出...")
                        return
                    else:
                        tqdm.write(f"当前显示颜色 #{point_cnt:02d}: ({rs:03d}, {gs:03d}, {bs:03d}), 按ESC键可随时终止程序...")

    end_time = time.time()
    cost_time_real = (end_time - start_time) / 60
    print(f"实际耗时: {cost_time_real:.2f} 分钟")


def parse_args():
    parser = argparse.ArgumentParser(description='运行RkPatternTool APK, 遍历RGB颜色空间并执行点击操作')
    parser.add_argument('-n', '--nb_points', type=int, default=None, help='采样点数 (与-s参数互斥, 优先使用)')
    parser.add_argument('-s', '--step', type=int, default=32, help='步长 (默认值: 32)')
    parser.add_argument('-p', '--point', type=str, help='点击坐标, 格式: "x,y"')
    parser.add_argument('-m', '--measure', action='store_true', help='测量坐标,移动鼠标3s后返回当前坐标')
    args = parser.parse_args()

    if args.measure:
        print("现在请移动鼠标位置，3s后返回当前坐标")
        time.sleep(3)
        pos = pg.position()
        print(f"当前鼠标坐标: ({pos.x}, {pos.y})")
        sys.exit(0)

    if args.nb_points is not None:
        if args.step != 32:
            print('警告: 同时指定了-n和-s参数, 将优先使用-n参数')
        args.nb_points = max(args.nb_points, 2)
        args.step = 256 // (args.nb_points - 1)

    if args.point is not None:
        try:
            x, y = map(int, args.point.split(','))
            args.point = (x, y)
        except ValueError:
            print(f'错误: 点坐标格式不正确, 应为 "x,y" 格式, 得到: {args.point}')
            sys.exit(1)
    else:
        args.point = pg.position()
        print(f'Warning: 未指定点击坐标参数，使用当前鼠标位置 {args.point}')
    return args


if __name__ == '__main__':
    args = parse_args()
    run_RkPatternTool_apk(args.step, args.point)
    print("Done.")

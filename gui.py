import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk
import subprocess
import os
import sys


# 获取可执行文件所在的路径
if getattr(sys, 'frozen', False):
    exe_folder_dir = os.path.dirname(sys.executable)
else:
    exe_folder_dir = os.path.dirname(os.path.abspath(__file__))

print(exe_folder_dir)

# exe_folder_dir = os.path.dirname(os.path.abspath(__file__))  # exe所在文件夹路径
# print(exe_folder_dir)

def create_branch_window1():
    branch_window1 = tk.Toplevel(main_window)
    branch_window1.title("colmap and NeRF")
    branch_window1.geometry("500x400")  # 设置窗口大小

    # 计算弹出位置的坐标
    x_position = 100  # x 坐标
    y_position = 200  # y 坐标

    # 使用 geometry 方法设置窗口弹出位置
    branch_window1.geometry(f"500x400+{x_position}+{y_position}")

    # 设置背景图片
    bg_image = PhotoImage(file="./image/logo.png")
    background_label = tk.Label(branch_window1, image=bg_image)
    background_label.place(x=98, y=30)  # 设置背景位置（98,73）

    branch_window1.iconbitmap('./image/logo2.ico')

    # 创建标签和输入框用于输入文件路径
    dir_label = tk.Label(branch_window1, text="视频路径:")
    dir_label.place(x=18, y=30)

    dir_entry = tk.Entry(branch_window1, width=52)
    dir_entry.place(x=95, y=31)

    mp4_label = tk.Label(branch_window1, text="视频名称:")
    mp4_label.place(x=18, y=70)

    mp4_entry = tk.Entry(branch_window1, width=52)
    mp4_entry.place(x=95, y=71)

    amount_label = tk.Label(branch_window1, text="抽帧数量:")
    amount_label.place(x=18, y=110)

    amount_entry = tk.Entry(branch_window1, width=52)
    amount_entry.place(x=95, y=111)

    optimize_label = tk.Label(branch_window1, text="是否使用优化算法:")
    optimize_label.place(x=18, y=150)
    options = ["是", "否"]
    selected_option1 = tk.StringVar()
    combobox = ttk.Combobox(branch_window1, textvariable=selected_option1, values=options, width=43)
    combobox.place(x=140, y=150)
    selected_option1.set(options[0])

    def exit():
        exit_gui(branch_window1)

    # 定义执行命令行操作的函数
    def execute_commands():
        pic_amount = amount_entry.get()  # 抽帧数量
        train_dir = dir_entry.get()  # mp4文件路径
        mp4_name = mp4_entry.get()  # mp4文件名称
        video_dir = train_dir + "\\" + mp4_name
        images_dir = train_dir + "\images"
        ffmpeg_dir = exe_folder_dir + "\\ffmpeg\\ffprobe.exe"
        print(ffmpeg_dir)
        opencv_dir = exe_folder_dir + "\open_cv\opencv.exe"
        exe_colmap_dir = exe_folder_dir[:-4] + "\scripts\colmap2nerf.py"
        nerf_dir = exe_folder_dir[:-4]
        exe_nerf_dir = exe_folder_dir[:-4] + "\instant-ngp.exe"
        text_dir = train_dir + "\colmap_text"

        if selected_option1.get() == '是':
            if_optimize = True
        else:
            if_optimize = False

        print(exe_colmap_dir)
        print(f"dir_path: {train_dir}")
        print(f"dir_path: {pic_amount}")
        print(f"dir_path: {if_optimize}")

        try:
            os.chdir(train_dir)

            # 使用subprocess执行ffprobe命令获取视频时长
            video_time_command = f'{ffmpeg_dir} -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 "{video_dir}"'
            video_time = subprocess.check_output(video_time_command, shell=True, text=True)
            video_time = float(video_time.strip())  # 将输出转换为浮点数

            # 计算抽帧帧率
            frame = float(pic_amount) // float(video_time)

            # 抽帧
            colmap_command = f'echo Y|python {exe_colmap_dir} --video_in {video_dir} --video_fps {frame}'
            try:
                subprocess.run(colmap_command, shell=True)
            except FileNotFoundError as e:
                print("警告：文件不存在")

            # 优化算法
            if if_optimize == True:
                conunt = 0
                for pic_name in os.listdir(images_dir):
                    if pic_name.endswith(".jpg"):
                        conunt += 1
                        conunt2 = conunt % 2
                        image_file_dir = images_dir + "\\" + pic_name
                        opencv_command = f'{opencv_dir} {image_file_dir}'
                        # print(opencv_command)
                        # value = subprocess.check_output(opencv_command)
                        process = subprocess.Popen(opencv_command, shell=True, stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE, text=True)
                        value = process.wait()
                        if conunt2 == 1:
                            image1_dir = image_file_dir
                            grad1 = value
                        else:
                            image2_dir = image_file_dir
                            grad2 = value
                            if grad1 < grad2:
                                os.remove(image1_dir)
                            else:
                                os.remove(image2_dir)

            # 执行colmap
            colmap_command2 = f'echo Y|python {exe_colmap_dir} --colmap_matcher exhaustive --run_colmap --aabb_scale 16'
            print('-' * 100)
            print(colmap_command2)
            subprocess.run(colmap_command2, shell=True)

            # 运行nerf
            os.chdir(nerf_dir)
            nerf_command = f'{exe_nerf_dir} --mode nerf --scene {train_dir}'
            subprocess.run(nerf_command, shell=True)

        except Exception as e:
            result_label.config(text=f"") # 执行命令出错：{e}
        else:
            result_label.config(text="") # 命令执行成功

            
    # 改变窗口插功能
    branch_window1.protocol("WM_DELETE_WINDOW", exit)

    # 创建按钮用于执行命令
    execute_button = tk.Button(branch_window1, text="开始三维重建", width=12, anchor='center',command=execute_commands)
    execute_button.place(x=200, y=348)

    # 创建返回按钮，用于返回主窗口
    return_button = tk.Button(branch_window1, text="返回主窗口", width=12, anchor='center',command=lambda: return_to_main_window(branch_window1))
    return_button.place(x=70, y=348)

    # 创建退出按钮，用于退出 GUI
    exit_button = tk.Button(branch_window1, text="退出", width=12, anchor='center',command=lambda: exit_gui(branch_window1))
    exit_button.place(x=330, y=348)

    # 创建标签用于显示执行结果
    result_label = tk.Label(branch_window1, text="")
    result_label.pack()

    # 运行界面主循环
    branch_window1.mainloop()

def create_branch_window2():
    branch_window2 = tk.Toplevel(main_window)
    branch_window2.title("only NeRF")
    branch_window2.geometry("500x400")  # 设置窗口大小

    # 计算弹出位置的坐标
    x_position = 100  # x 坐标
    y_position = 200  # y 坐标

    # 使用 geometry 方法设置窗口弹出位置
    branch_window2.geometry(f"500x400+{x_position}+{y_position}")

    # 设置背景图片
    bg_image = PhotoImage(file="./image/logo.png")
    background_label = tk.Label(branch_window2, image=bg_image)
    background_label.place(x=98, y=30)  # 设置背景位置（98,73）

    branch_window2.iconbitmap('./image/logo2.ico')

    # 创建标签和输入框用于输入文件路径
    dir_label = tk.Label(branch_window2, text="图片及位姿路径:")
    dir_label.place(x=18, y=30)

    dir_entry = tk.Entry(branch_window2, width=48)
    dir_entry.place(x=130, y=31)

    # mp4_label = tk.Label(branch_window2, text="视频名称:")
    # mp4_label.place(x=18, y=70)

    # mp4_entry = tk.Entry(branch_window2, width=52)
    # mp4_entry.place(x=95, y=71)

    # amount_label = tk.Label(branch_window2, text="抽帧数量:")
    # amount_label.place(x=18, y=110)

    # amount_entry = tk.Entry(branch_window2, width=52)
    # amount_entry.place(x=95, y=111)

    # optimize_label = tk.Label(branch_window2, text="是否使用优化算法:")
    # optimize_label.place(x=18, y=150)
    # options = ["是", "否"]
    # selected_option1 = tk.StringVar()
    # combobox = ttk.Combobox(branch_window2, textvariable=selected_option1, values=options, width=43)
    # combobox.place(x=140, y=150)
    # selected_option1.set(options[0])

    def exit():
        exit_gui(branch_window2)

    # 定义执行命令行操作的函数
    def execute_commands():
        # pic_amount = amount_entry.get()  # 抽帧数量
        train_dir = dir_entry.get()  # mp4文件路径
        # mp4_name = mp4_entry.get()  # mp4文件名称
        # video_dir = train_dir + "\\" + mp4_name
        images_dir = train_dir + "\images"
        opencv_dir = exe_folder_dir + "\open_cv\opencv.exe"
        exe_colmap_dir = exe_folder_dir[:-4] + "\scripts\colmap2nerf.py"
        nerf_dir = exe_folder_dir[:-4]
        exe_nerf_dir = exe_folder_dir[:-4] + "\instant-ngp.exe"
        text_dir = train_dir + "\colmap_text"

        # if selected_option1.get() == '是':
        #     if_optimize = True
        # else:
        #     if_optimize = False

        print(exe_colmap_dir)
        print(f"dir_path: {train_dir}")
        # print(f"dir_path: {pic_amount}")
        # print(f"dir_path: {if_optimize}")

        try:
            # os.chdir(train_dir)

            # # 使用subprocess执行ffprobe命令获取视频时长
            # video_time_command = f'ffprobe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 "{video_dir}"'
            # video_time = subprocess.check_output(video_time_command, shell=True, text=True)
            # video_time = float(video_time.strip())  # 将输出转换为浮点数

            # # 计算抽帧帧率
            # frame = float(pic_amount) // float(video_time)

            # # 抽帧
            # colmap_command = f'echo Y|python {exe_colmap_dir} --video_in {video_dir} --video_fps {frame}'
            # try:
            #     subprocess.run(colmap_command, shell=True)
            # except FileNotFoundError as e:
            #     print("警告：文件不存在")

            # # 优化算法
            # if if_optimize == True:
            #     conunt = 0
            #     for pic_name in os.listdir(images_dir):
            #         if pic_name.endswith(".jpg"):
            #             conunt += 1
            #             conunt2 = conunt % 2
            #             image_file_dir = images_dir + "\\" + pic_name
            #             opencv_command = f'{opencv_dir} {image_file_dir}'
            #             # print(opencv_command)
            #             # value = subprocess.check_output(opencv_command)
            #             process = subprocess.Popen(opencv_command, shell=True, stdout=subprocess.PIPE,
            #                                        stderr=subprocess.PIPE, text=True)
            #             value = process.wait()
            #             if conunt2 == 1:
            #                 image1_dir = image_file_dir
            #                 grad1 = value
            #             else:
            #                 image2_dir = image_file_dir
            #                 grad2 = value
            #                 if grad1 < grad2:
            #                     os.remove(image1_dir)
            #                 else:
            #                     os.remove(image2_dir)

            # # 执行colmap
            # colmap_command2 = f'echo Y|python {exe_colmap_dir} --colmap_matcher exhaustive --run_colmap --aabb_scale 16'
            # print('-' * 100)
            # print(colmap_command2)
            # subprocess.run(colmap_command2, shell=True)

            # 运行nerf
            os.chdir(nerf_dir)
            nerf_command = f'{exe_nerf_dir} --mode nerf --scene {train_dir}'
            subprocess.run(nerf_command, shell=True)

        except Exception as e:
            result_label.config(text=f"")
        else:
            result_label.config(text="")

            
    # 改变窗口插功能
    branch_window2.protocol("WM_DELETE_WINDOW", exit)

    # 创建按钮用于执行命令
    execute_button = tk.Button(branch_window2, text="开始三维重建", width=12, anchor='center',command=execute_commands)
    execute_button.place(x=200, y=348)

    # 创建返回按钮，用于返回主窗口
    return_button = tk.Button(branch_window2, text="返回主窗口", width=12, anchor='center',command=lambda: return_to_main_window(branch_window2))
    return_button.place(x=70, y=348)

    # 创建退出按钮，用于退出 GUI
    exit_button = tk.Button(branch_window2, text="退出", width=12, anchor='center',command=lambda: exit_gui(branch_window2))
    exit_button.place(x=330, y=348)

    # 创建标签用于显示执行结果
    result_label = tk.Label(branch_window2, text="")
    result_label.pack()

    # 运行界面主循环
    branch_window2.mainloop()

def show_branch_window(option):
    main_window.withdraw()
    if option == "1":
        create_branch_window1()
    elif option == "2":
        create_branch_window2()

# 销毁当前窗口并返回主窗口
def return_to_main_window(current_window):
    current_window.destroy()  # 销毁当前窗口
    os.chdir(exe_folder_dir)
    main_window.deiconify()  # 显示主窗口

# 退出gui界面
def exit_gui(window):
    window.destroy()
    main_window.destroy()

# 主窗口
main_window = tk.Tk()
main_window.title("instant-ngp")
main_window.geometry("500x400")  # 设置窗口大小

# 计算弹出位置的坐标
x_position = 100  # x 坐标
y_position = 200  # y 坐标

# 使用 geometry 方法设置窗口弹出位置
main_window.geometry(f"500x400+{x_position}+{y_position}")

# 设置背景图片
bg_image = PhotoImage(file="./image/logo.png")
background_label = tk.Label(main_window, image=bg_image)
background_label.place(x=98, y=30)  # 设置背景位置（98,73）

main_window.iconbitmap('./image/logo2.ico')

# 创建按钮用于执行命令
execute_button = tk.Button(main_window, text="从视频开始", command=lambda: show_branch_window('1'),  width=15, anchor='center')
execute_button.place(x=189, y=130)

# 创建返回按钮，用于返回主窗口
return_button = tk.Button(main_window, text="从图片和位姿开始", command=lambda: show_branch_window('2'), width=15, anchor='center')
return_button.place(x=189, y=190)

# # 创建一个下拉菜单来选择选项
# options = ["选项1", "选项2"]
# selected_option = tk.StringVar()
# option_menu = tk.OptionMenu(main_window, selected_option, *options)
# option_menu.pack()

# # 创建一个按钮，用于触发显示分支窗口的操作
# show_button = tk.Button(main_window, text="显示分支窗口", command=lambda: show_branch_window(selected_option.get()))
# show_button.pack()

# 运行主循环

main_window.mainloop()

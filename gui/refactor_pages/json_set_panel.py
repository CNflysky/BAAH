from ..components.exec_arg_parse import get_token
from ..components.run_baah_in_gui import run_baah_task
from ..pages.Setting_BAAH import set_BAAH
from ..pages.Setting_Craft import set_craft
from ..pages.Setting_cafe import set_cafe
from ..pages.Setting_emulator import set_emulator
from ..pages.Setting_event import set_event
from ..pages.Setting_exchange import set_exchange
from ..pages.Setting_hard import set_hard
from ..pages.Setting_normal import set_normal
from ..pages.Setting_other import set_other
from ..pages.Setting_server import set_server
from ..pages.Setting_shop import set_shop
from ..pages.Setting_special import set_special
from ..pages.Setting_task_order import set_task_order
from ..pages.Setting_timetable import set_timetable
from ..pages.Setting_wanted import set_wanted
from ..pages.Setting_notification import set_notification
from ..pages.Setting_vpn import set_vpn
from ..pages.Setting_Assault import set_assault
from ..pages.Setting_BuyAP import set_buyAP
from ..pages.Setting_UserTask import set_usertask
from ..define import get_task_name_map_dict
from modules.configs.MyConfig import MyConfigger
from ..define import gui_shared_config

from nicegui import ui, app, run
from typing import Callable
import os
from platform import system

class ConfigPanel:
    """
    连接子页面的i18n名称 与 渲染页面的函数

    Parameters
    ==========
    name: str
        子页面标题
    func: 
        子页面渲染函数
    """
    def __init__(self, name: str, func: Callable[[], None]):
        self.name = name
        self.func = func
        self.tab = None

    def set_tab(self, tab: ui.tab):
        self.tab = tab


def get_config_list(lst_config: MyConfigger) -> list:
    return [
        ConfigPanel("BAAH", lambda: set_BAAH(lst_config, gui_shared_config)),
        ConfigPanel(lst_config.get_text("setting_emulator"), lambda: set_emulator(lst_config)),
        ConfigPanel(lst_config.get_text("setting_server"), lambda: set_server(lst_config)),
        ConfigPanel(lst_config.get_text("setting_vpn"), lambda: set_vpn(lst_config)),
        ConfigPanel(lst_config.get_text("setting_task_order"), lambda: set_task_order(lst_config, get_task_name_map_dict(lst_config))),
        ConfigPanel(lst_config.get_text("setting_notification"), lambda: set_notification(lst_config, gui_shared_config)),
        ConfigPanel(lst_config.get_text("task_cafe"), lambda: set_cafe(lst_config)),
        ConfigPanel(lst_config.get_text("task_timetable"), lambda: set_timetable(lst_config)),
        ConfigPanel(lst_config.get_text("task_craft"), lambda: set_craft(lst_config)),
        ConfigPanel(lst_config.get_text("task_shop"), lambda: set_shop(lst_config)),
        ConfigPanel(lst_config.get_text("task_buy_ap"), lambda: set_buyAP(lst_config)),
        ConfigPanel(lst_config.get_text("task_wanted"), lambda: set_wanted(lst_config)),
        ConfigPanel(lst_config.get_text("task_special"), lambda: set_special(lst_config)),
        ConfigPanel(lst_config.get_text("task_exchange"), lambda: set_exchange(lst_config)),
        ConfigPanel(lst_config.get_text("task_event"), lambda: set_event(lst_config)),
        ConfigPanel(lst_config.get_text("task_assault"), lambda: set_assault(lst_config)),
        ConfigPanel(lst_config.get_text("task_hard"), lambda: set_hard(lst_config, gui_shared_config)),
        ConfigPanel(lst_config.get_text("task_normal"), lambda: set_normal(lst_config)),
        ConfigPanel(lst_config.get_text("task_user_def_task"), lambda: set_usertask(lst_config)),
        ConfigPanel(lst_config.get_text("setting_other"), lambda: set_other(lst_config, lst_config.nowuserconfigname))
    ]


@ui.page('/panel/{json_file_name}')
def show_json_panel(json_file_name: str):
    if get_token() is not None and get_token() != app.storage.user.get("token"):
        return
    curr_config: MyConfigger = MyConfigger()
    curr_config.parse_user_config(json_file_name)
    config_choose_list: list[ConfigPanel] = get_config_list(curr_config)

    # 设置splitter高度使其占满全屏，减去2rem是content这个class的内边距
    with ui.splitter(value=15).classes('w-full h-full').style("height: calc(100vh - 2rem);") as splitter:
        with splitter.before:
            ui.button("<-", on_click=lambda: ui.run_javascript('window.history.back()'))

            with ui.tabs().props('vertical').classes('w-full') as tabs:
                tmp = ui.tab(config_choose_list[0].name)
                config_choose_list[0].set_tab(tmp)
                for i, config_cls in enumerate(config_choose_list[1:]):
                    config_choose_list[i + 1].set_tab(ui.tab(config_cls.name))

        with splitter.after:
            with ui.tab_panels(tabs, value=config_choose_list[0].tab).props('vertical').classes('w-full h-full'):
                for cls in config_choose_list:
                    with ui.tab_panel(cls.tab):
                        cls.func()


        msg_obj = {
            "stop_signal": 0,
            "runing_signal": 0
        }

        with ui.column().style('flex-grow: 1;width: 30vw;position:sticky; top: 0px;'):
            output_card = ui.card().style('width: 30vw; height: 80vh;overflow-y: auto;')
            with output_card:
                logArea = ui.log(max_lines=1000).classes('w-full h-full')


        with ui.column().style(
                'width: 10vw; overflow: auto; position: fixed; bottom: 40px; right: 20px;min-width: 150px;'):
            def save_and_alert():
                curr_config.save_user_config(json_file_name)
                curr_config.save_software_config()
                gui_shared_config.save_software_config()
                ui.notify(curr_config.get_text("notice_save_success"))

            ui.button(curr_config.get_text("button_save"), on_click=save_and_alert)

            def save_and_alert_and_run_in_terminal():
                curr_config.save_user_config(json_file_name)
                curr_config.save_software_config()
                gui_shared_config.save_software_config()
                ui.notify(curr_config.get_text("notice_save_success"))
                ui.notify(curr_config.get_text("notice_start_run"))
                # 打开同目录中的BAAH.exe，传入当前config的json文件名
                platform: str = system()
                if platform == "Windows":
                    os.system(f'start BAAH.exe "{json_file_name}"')
                elif platform == "Linux":
                    os.system(f"/usr/bin/env python3 main.py {json_file_name}")
                else:
                    raise RuntimeError("Unsupported platform.")

            ui.button(curr_config.get_text("button_save_and_run_terminal"), on_click=save_and_alert_and_run_in_terminal)

            # ======Run in GUI======
            async def save_and_alert_and_run():
                curr_config.save_user_config(json_file_name)
                curr_config.save_software_config()
                gui_shared_config.save_software_config()
                ui.notify(curr_config.get_text("notice_save_success"))
                ui.notify(curr_config.get_text("notice_start_run"))
                # 打开同目录中的BAAH.exe，传入当前config的json文件名
                # os.system(f'start BAAH.exe "{load_jsonname}"')
                msg_obj["runing_signal"] = 1
                await run.io_bound(run_baah_task, msg_obj, logArea, curr_config)

            ui.button(curr_config.get_text("button_save_and_run_gui"), on_click=save_and_alert_and_run).bind_visibility_from(
                msg_obj, "runing_signal", backward=lambda x: x == 0)

            async def stop_run() -> None:
                msg_obj["stop_signal"] = 1

            ui.button(curr_config.get_text("notice_finish_run"), on_click=stop_run, color='red').bind_visibility_from(
                msg_obj, "runing_signal", backward=lambda x: x == 1)

            ui.button("...").bind_visibility_from(msg_obj, "runing_signal", backward=lambda x: x == 0.25)

            # ================

    # 加载完毕保存一下config，应用最新的对config的更改
    curr_config.save_user_config(json_file_name)
    curr_config.save_software_config()

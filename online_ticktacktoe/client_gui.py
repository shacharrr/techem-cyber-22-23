# -*- coding: utf-8 -*-
import os
import sys

from client import Client

# For Linux/Wayland users.
if os.getenv("XDG_SESSION_TYPE") == "wayland":
    os.environ["XDG_SESSION_TYPE"] = "x11"

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
from datetime import datetime
from threading import Thread
from packet import Packet, PacketType
import string
import random

path_to_font = None  # "path/to/font.ttf"

opened_state = True


def impl_glfw_init():
    width, height = 1600, 900
    window_name = "TickTackToe Online"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


def main():
    imgui.create_context()
    window = impl_glfw_init()

    impl = GlfwRenderer(window)

    io = imgui.get_io()
    jb = (
        io.fonts.add_font_from_file_ttf(path_to_font, 30)
        if path_to_font is not None
        else None
    )

    impl.refresh_font_texture()

    ## Variable Declaration ##

    popup_opened = False
    game_code = ""
    game_chat_text = ""

    rand_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    client = Client(rand_name)
    client.connect(("localhost", 9999))
    # client.connect(("0.tcp.eu.ngrok.io", 11435))
    Thread(target=client.recv).start()

    ##########################

    while not glfw.window_should_close(window):
        width, height = glfw.get_window_size(window)
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        if jb is not None:
            imgui.push_font(jb)

        ###################
        ###################
        ###################
        ###################
        ###################
        ## Start Handeling ##

        game_window_width = width - (width // 4)
        game_chat_width = width // 4
        app_height = height - 20

        if io.key_ctrl and io.keys_down[glfw.KEY_Q]:
            sys.exit(0)

        if imgui.begin_main_menu_bar():
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if imgui.begin_menu(current_time, False):
                imgui.end_menu()

            if client.game != None:
                if imgui.begin_menu(f"#{client.game.game_code}", False):
                    imgui.end_menu()
                if imgui.begin_menu("Game"):
                    if imgui.menu_item("Leave game")[0]:
                        client.send(
                            Packet(
                                Type=PacketType.LeaveServerRequest,
                                Data=client.game.game_code,
                            )
                        )
                    imgui.end_menu()
            imgui.end_main_menu_bar()

        if client.game == None or not popup_opened:
            imgui.open_popup(f"Join/Create Game")
            popup_opened = True

        with imgui.begin_popup_modal(f"Join/Create Game") as join_create:
            if join_create.opened:
                _, client.name = imgui.input_text("Username", client.name)
                _, game_code = imgui.input_text("Game Code", game_code)
                if imgui.button("Create Server"):
                    popup_opened = False
                    client.send(Packet(Type=PacketType.CreateServerRequest))
                    imgui.close_current_popup()
                if imgui.button("Join Server"):
                    popup_opened = False
                    client.send(
                        Packet(Type=PacketType.JoinServerRequest, Data=game_code)
                    )
                    imgui.close_current_popup()

        if client.game != None:
            imgui.set_next_window_size(game_window_width, app_height)
            imgui.set_next_window_position(0, 20)
            imgui.begin("##main-window", flags=43)

            if client.game.draw(client.name, game_window_width, app_height) == 1:
                client.send(
                    Packet(
                        Type=PacketType.GameSendState,
                        SubPort=client.game.game_code,
                        Data=client.game,
                    )
                )
                client.game.is_turn = False

            if (
                not client.game.is_startable
                and client.game.is_over
                and not client.game.is_game_owner
                or client.game.is_startable
                and client.game.is_over
                and not client.game.is_game_owner
            ):
                start_text = "Waiting for the game owner to start"
            elif (
                client.game.is_startable
                and client.game.is_over
                and client.game.is_game_owner
            ):
                start_text = "Start Game"
            elif not client.game.is_over:
                start_text = "Currently playing"
            elif (
                not client.game.is_startable
                and client.game.is_over
                and client.game.is_game_owner
            ):
                start_text = "Waiting for another player to join..."
            else:
                start_text = "IDK"

            added_text = (
                f" (Last game winner: {client.game.won})"
                if client.game.won != ""
                else ""
            )

            # print(client.game.is_startable, client.game.is_over, client.game.is_game_owner)
            if imgui.button(
                start_text + added_text,
                game_window_width,
                app_height - 3 * (height // 3 - 30) - 5,
            ):
                if (
                    client.game.is_startable
                    and client.game.is_over
                    and client.game.is_game_owner
                ):
                    client.game.reset(client.name)
                    client.game.is_over = False
                    client.send(
                        Packet(
                            Type=PacketType.GameResetState,
                            SubPort=client.game.game_code,
                        )
                    )
            imgui.end()

            imgui.set_next_window_size(game_chat_width, app_height)
            imgui.set_next_window_position(game_window_width, 20)
            imgui.begin("##game-chat", flags=43)

            imgui.begin_child("##text-browser", game_chat_width, app_height - 100, True)
            for message in client.game.game_chat:
                imgui.text(message)
            imgui.end_child()

            _, game_chat_text = imgui.input_text_multiline(
                "", game_chat_text, width=game_chat_width - 100, height=85
            )
            imgui.same_line()
            if imgui.button("SEND", 85, 85):
                if game_chat_text != "":
                    message = f"<{client.name}> {game_chat_text}"
                    client.game.game_chat.append(message)
                    client.send(
                        Packet(
                            Type=PacketType.GameChatMessage,
                            SubPort=client.game.game_code,
                            Data=message,
                        )
                    )
                    game_chat_text = ""

            imgui.end()

        ## End Handeling ##
        ###################
        ###################
        ###################
        ###################
        ###################

        if jb is not None:
            imgui.pop_font()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    client.crash_safely()
    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()

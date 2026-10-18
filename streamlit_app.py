
import os
import tempfile
import subprocess
import urllib.request
import streamlit as st

st.set_page_config(page_title="HStego 图片隐写", page_icon="🔐")
st.title("🔐 HStego 图片隐写工具")
st.write("尝试调用官方 HStego v0.6.1 Linux 程序。")

BINARY_URL = (
    "https://github.com/daniellerch/hstego/releases/download/"
    "v0.6.1/hstego-0.6.1-linux.x86_64"
)
BINARY_PATH = "/tmp/hstego-0.6.1-linux.x86_64"


@st.cache_resource
def prepare_binary():
    if not os.path.exists(BINARY_PATH):
        urllib.request.urlretrieve(BINARY_URL, BINARY_PATH)
    os.chmod(BINARY_PATH, 0o755)
    return BINARY_PATH


try:
    binary = prepare_binary()
    st.success("官方程序已下载。")
except Exception as e:
    st.error(f"官方程序下载失败：{e}")
    st.stop()


def run_hstego(args, folder):
    result = subprocess.run(
        [binary] + args,
        cwd=folder,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        detail = result.stderr or result.stdout or "程序没有提供错误详情"
        raise RuntimeError(detail)
    return result.stdout


hide_tab, extract_tab = st.tabs(["隐藏文字", "提取文字"])

with hide_tab:
    cover = st.file_uploader(
        "上传原始图片",
        type=["png", "bmp", "jpg", "jpeg"],
        key="cover",
    )
    message = st.text_area("要隐藏的文字")
    password = st.text_input("设置提取密码", type="password")

    if st.button("生成隐写图片"):
        if cover is None or not message or not password:
            st.warning("请上传图片、填写文字并设置密码。")
        else:
            try:
                with tempfile.TemporaryDirectory() as folder:
                    ext = os.path.splitext(cover.name)[1].lower()
                    if ext not in [".png", ".bmp", ".jpg", ".jpeg"]:
                        ext = ".png"

                    cover_path = os.path.join(folder, "cover" + ext)
                    secret_path = os.path.join(folder, "secret.txt")
                    output_path = os.path.join(folder, "stego" + ext)

                    with open(cover_path, "wb") as f:
                        f.write(cover.getvalue())

                    with open(secret_path, "w", encoding="utf-8") as f:
                        f.write(message)

                    run_hstego(
                        ["embed", "secret.txt", "cover" + ext,
                         "stego" + ext, password],
                        folder,
                    )

                    with open(output_path, "rb") as f:
                        result = f.read()

                    st.success("处理完成。")
                    st.download_button(
                        "下载隐写图片",
                        data=result,
                        file_name="stego" + ext,
                        mime=cover.type or "application/octet-stream",
                    )
            except Exception as e:
                st.error(f"处理失败：{e}")


with extract_tab:
    stego = st.file_uploader(
        "上传隐写图片",
        type=["png", "bmp", "jpg", "jpeg"],
        key="stego",
    )
    extract_password = st.text_input(
        "输入提取密码",
        type="password",
        key="extract_password",
    )

    if st.button("提取隐藏文字"):
        if stego is None or not extract_password:
            st.warning("请上传隐写图片并输入密码。")
        else:
            try:
                with tempfile.TemporaryDirectory() as folder:
                    ext = os.path.splitext(stego.name)[1].lower()
                    if ext not in [".png", ".bmp", ".jpg", ".jpeg"]:
                        ext = ".png"

                    input_path = os.path.join(folder, "stego" + ext)
                    output_path = os.path.join(folder, "content.txt")

                    with open(input_path, "wb") as f:
                        f.write(stego.getvalue())

                    run_hstego(
                        ["extract", "stego" + ext,
                         "content.txt", extract_password],
                        folder,
                    )

                    with open(output_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    st.success("提取完成。")
                    st.text_area("提取出的文字", content, height=180)
            except Exception as e:
                st.error(f"提取失败：{e}")

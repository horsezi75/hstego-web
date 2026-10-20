
import os
import tempfile
import subprocess
import urllib.request
import streamlit as st

st.set_page_config(page_title="HStego 图片隐写", page_icon="🔐")
st.title("🔐 HStego 图片隐写工具")
st.write("官方 HStego v0.6.1 测试版")

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

    output = "\n".join(
        part.strip()
        for part in (result.stdout, result.stderr)
        if part.strip()
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"官方程序退出码：{result.returncode}\n"
            f"{output or '没有返回错误详情'}"
        )

    return output


hide_tab, extract_tab = st.tabs(["隐藏文字", "提取文字"])

with hide_tab:
    cover = st.file_uploader(
        "上传原始图片",
        type=["png", "bmp", "jpg", "jpeg"],
        key="cover",
    )
    message = st.text_area("要隐藏的文字")
    password = st.text_input(
        "设置提取密码",
        type="password",
        key="hide_password",
    )

    if st.button("生成隐写图片"):
        if cover is None or not message.strip() or not password:
            st.warning("请上传图片、填写文字并设置密码。")
        else:
            try:
                with tempfile.TemporaryDirectory() as folder:
                    ext = os.path.splitext(cover.name)[1].lower()
                    if ext not in [".png", ".bmp", ".jpg", ".jpeg"]:
                        ext = ".png"

                    cover_name = "cover" + ext
                    stego_name = "stego" + ext
                    output_path = os.path.join(folder, stego_name)

                    with open(
                        os.path.join(folder, cover_name), "wb"
                    ) as f:
                        f.write(cover.getvalue())

                    with open(
                        os.path.join(folder, "secret.txt"),
                        "w",
                        encoding="utf-8",
                    ) as f:
                        f.write(message)

                    output = run_hstego(
                        [
                            "embed",
                            "secret.txt",
                            cover_name,
                            stego_name,
                            password,
                        ],
                        folder,
                    )

                    if not os.path.isfile(output_path):
                        raise RuntimeError(
                            "官方程序没有生成隐写图片。\n" + output
                        )

                    with open(output_path, "rb") as f:
                        image_data = f.read()

                    if not image_data:
                        raise RuntimeError("生成的图片文件为空。")

                    st.success("隐写图片已生成。")
                    st.download_button(
                        "下载隐写图片",
                        data=image_data,
                        file_name=stego_name,
                        mime=cover.type or "application/octet-stream",
                    )

                    if output:
                        with st.expander("查看官方程序输出"):
                            st.code(output)

            except Exception as e:
                st.error(f"生成失败：{e}")


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

                    stego_name = "stego" + ext
                    output_path = os.path.join(folder, "content.txt")

                    with open(
                        os.path.join(folder, stego_name), "wb"
                    ) as f:
                        f.write(stego.getvalue())

                    output = run_hstego(
                        [
                            "extract",
                            stego_name,
                            "content.txt",
                            extract_password,
                        ],
                        folder,
                    )

                    if not os.path.isfile(output_path):
                        raise RuntimeError(
                            "官方程序没有生成提取结果文件。\n" + output
                        )

                    with open(
                        output_path, "r", encoding="utf-8"
                    ) as f:
                        content = f.read()

                    if not content.strip():
                        st.warning(
                            "提取结果为空。请确认上传的是本工具生成的"
                            "隐写图片，并且密码与隐藏时完全一致。"
                        )
                        if output:
                            st.code(output)
                    else:
                        st.success("已读取到提取出的文字。")
                        st.text_area(
                            "提取出的文字",
                            content,
                            height=180,
                        )

                    if output:
                        with st.expander("查看官方程序输出"):
                            st.code(output)

            except Exception as e:
                st.error(f"提取失败：{e}")

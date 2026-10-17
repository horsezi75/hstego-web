import streamlit as st
import hstegolib
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="HStego 图像隐写应用",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 HStego 图像隐写应用")
st.write("基于官方 HStego 的图像信息隐藏与提取")

st.warning(
    "请使用自己有权处理的图片。"
    "HStego 仍处于 Alpha 阶段，重要文件请保留备份。"
)

tab1, tab2 = st.tabs(["🔒 隐藏信息", "🔓 提取信息"])

with tab1:
    st.subheader("将秘密文本隐藏到图片中")

    cover = st.file_uploader(
        "上传原始图片（PNG 或 BMP）",
        type=["png", "bmp"],
        key="cover"
    )

    message = st.text_area(
        "输入要隐藏的秘密文本",
        placeholder="请输入要隐藏的内容……"
    )

    password = st.text_input(
        "设置提取密码",
        type="password",
        key="embed_password"
    )

    if st.button("生成隐写图片", type="primary"):
        if cover is None:
            st.error("请先上传原始图片。")
        elif not message.strip():
            st.error("请输入要隐藏的文本。")
        elif not password:
            st.error("请输入密码。")
        else:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    tmp = Path(tmp)
                    cover_path = tmp / "cover.png"
                    secret_path = tmp / "secret.txt"
                    output_path = tmp / "stego.png"

                    cover_path.write_bytes(cover.getvalue())
                    secret_path.write_text(
                        message, encoding="utf-8"
                    )

                    algorithm = hstegolib.S_UNIWARD()
                    algorithm.embed(
                        str(cover_path),
                        str(secret_path),
                        password,
                        str(output_path)
                    )

                    if not output_path.exists():
                        raise RuntimeError("没有生成输出图片。")

                    image_bytes = output_path.read_bytes()

                st.success("隐写图片生成成功！")
                st.image(image_bytes, caption="生成的隐写图片")

                st.download_button(
                    "下载隐写图片",
                    data=image_bytes,
                    file_name="hstego_stego.png",
                    mime="image/png"
                )

                st.info(
                    "请记住密码。提取时需要使用相同的密码。"
                )

            except Exception as e:
                st.error(f"生成失败：{e}")
                st.caption(
                    "如果是依赖安装错误，请检查 Streamlit 部署日志。"
                )

with tab2:
    st.subheader("从隐写图片中提取秘密文本")

    stego = st.file_uploader(
        "上传隐写图片（PNG 或 BMP）",
        type=["png", "bmp"],
        key="stego"
    )

    extract_password = st.text_input(
        "输入隐藏时设置的密码",
        type="password",
        key="extract_password"
    )

    if st.button("提取秘密信息", type="primary"):
        if stego is None:
            st.error("请先上传隐写图片。")
        elif not extract_password:
            st.error("请输入密码。")
        else:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    tmp = Path(tmp)
                    stego_path = tmp / "stego.png"
                    output_path = tmp / "secret.txt"

                    stego_path.write_bytes(stego.getvalue())

                    algorithm = hstegolib.S_UNIWARD()
                    algorithm.extract(
                        str(stego_path),
                        extract_password,
                        str(output_path)
                    )

                    if not output_path.exists():
                        raise RuntimeError("没有生成提取结果。")

                    secret = output_path.read_text(
                        encoding="utf-8"
                    )

                st.success("提取完成！")
                st.text_area(
                    "提取到的秘密文本",
                    value=secret,
                    height=180
                )

                st.download_button(
                    "下载提取结果",
                    data=secret.encode("utf-8"),
                    file_name="extracted_secret.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"提取失败：{e}")
                st.caption(
                    "请检查图片是否由官方 HStego 生成，以及密码是否正确。"
                )

st.divider()
st.caption("实验项目：HStego 图像隐写 Web 界面")
